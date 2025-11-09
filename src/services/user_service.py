"""User behavior tracking and profile management service."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from src.config.settings import settings
from src.config.database import db_manager, COLLECTIONS
from src.models.user import (
    User, UserCreate, UserUpdate, BehaviorProfile, RiskLevel,
    UserBehaviorUpdate, UserTrustAdjustment, ModerationHistory
)
from src.models.message import ModerationAction


class UserService:
    """Service for managing user profiles and behavior tracking."""

    def __init__(self):
        """Initialize the user service."""
        pass

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user profile.

        Args:
            user_data: User creation data

        Returns:
            Created user object
        """
        try:
            # Generate user ID
            user_id = f"user_{int(datetime.utcnow().timestamp() * 1000)}"

            # Create user document
            user = User(
                user_id=user_id,
                username=user_data.username,
                email=user_data.email,
                created_at=datetime.utcnow(),
                last_active=datetime.utcnow(),
                preferences=user_data.preferences
            )

            # Insert into database
            users_collection = db_manager.async_db[COLLECTIONS["users"]]
            await users_collection.insert_one(user.dict(by_alias=True))

            return user

        except Exception as e:
            raise RuntimeError(f"Error creating user: {e}")

    async def get_user(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User object or None if not found
        """
        try:
            users_collection = db_manager.async_db[COLLECTIONS["users"]]
            user_doc = await users_collection.find_one({"user_id": user_id})

            if user_doc:
                return User(**user_doc)
            return None

        except Exception as e:
            raise RuntimeError(f"Error retrieving user: {e}")

    async def update_user(self, user_id: str, update_data: UserUpdate) -> Optional[User]:
        """
        Update user information.

        Args:
            user_id: User ID
            update_data: Update data

        Returns:
            Updated user object or None if not found
        """
        try:
            users_collection = db_manager.async_db[COLLECTIONS["users"]]

            # Build update document
            update_doc = {}
            if update_data.username is not None:
                update_doc["username"] = update_data.username
            if update_data.email is not None:
                update_doc["email"] = update_data.email
            if update_data.preferences is not None:
                update_doc["preferences"] = update_data.preferences.dict()

            if update_doc:
                update_doc["last_active"] = datetime.utcnow()
                result = await users_collection.update_one(
                    {"user_id": user_id},
                    {"$set": update_doc}
                )

                if result.matched_count > 0:
                    return await self.get_user(user_id)

            return None

        except Exception as e:
            raise RuntimeError(f"Error updating user: {e}")

    async def update_user_behavior(
        self,
        user_id: str,
        behavior_update: UserBehaviorUpdate
    ) -> None:
        """
        Update user behavior statistics.

        Args:
            user_id: User ID
            behavior_update: Behavior update data
        """
        try:
            users_collection = db_manager.async_db[COLLECTIONS["users"]]

            # Get current user profile
            user = await self.get_user(user_id)
            if not user:
                # Create new user profile if doesn't exist
                user = User(
                    user_id=user_id,
                    username=f"user_{user_id[:8]}",
                    email=f"user_{user_id[:8]}@example.com"
                )
                await users_collection.insert_one(user.dict(by_alias=True))

            # Update behavior profile
            profile = user.behavior_profile
            history = profile.moderation_history

            # Update message count and average toxicity
            total_messages = history.total_messages + 1
            current_avg = profile.average_toxicity_score
            new_avg = (current_avg * history.total_messages + behavior_update.message_toxicity_score) / total_messages

            # Update moderation history
            history.total_messages = total_messages

            action = behavior_update.moderation_action_taken
            if action in [ModerationAction.WARN.value, ModerationAction.HIDE.value,
                         ModerationAction.DELETE.value, ModerationAction.BAN.value]:
                history.flagged_messages += 1

            if behavior_update.was_false_positive:
                history.false_positives += 1

            # Update message frequency (simplified - would need more sophisticated tracking)
            profile.message_frequency = min(100, profile.message_frequency + 1)

            # Update average toxicity score
            profile.average_toxicity_score = new_avg

            # Recalculate risk level
            new_risk_level = self._calculate_risk_level(profile, history)
            profile.risk_level = new_risk_level

            # Update trust score
            new_trust_score = self._calculate_trust_score(profile, history, behavior_update)
            profile.trust_score = max(0.0, min(1.0, new_trust_score))

            # Update database
            update_doc = {
                "behavior_profile": profile.dict(),
                "last_active": datetime.utcnow()
            }

            await users_collection.update_one(
                {"user_id": user_id},
                {"$set": update_doc}
            )

        except Exception as e:
            raise RuntimeError(f"Error updating user behavior: {e}")

    async def adjust_user_trust(
        self,
        user_id: str,
        adjustment: UserTrustAdjustment
    ) -> Optional[User]:
        """
        Manually adjust user trust score.

        Args:
            user_id: User ID
            adjustment: Trust adjustment data

        Returns:
            Updated user object or None if not found
        """
        try:
            user = await self.get_user(user_id)
            if not user:
                return None

            # Adjust trust score
            new_trust = user.behavior_profile.trust_score + adjustment.adjustment_amount
            new_trust = max(0.0, min(1.0, new_trust))

            # Update behavior profile
            user.behavior_profile.trust_score = new_trust

            # Recalculate risk level based on new trust score
            if new_trust > 0.7:
                user.behavior_profile.risk_level = RiskLevel.LOW
            elif new_trust > 0.3:
                user.behavior_profile.risk_level = RiskLevel.MEDIUM
            else:
                user.behavior_profile.risk_level = RiskLevel.HIGH

            # Update database
            users_collection = db_manager.async_db[COLLECTIONS["users"]]
            await users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"behavior_profile": user.behavior_profile.dict()}}
            )

            return await self.get_user(user_id)

        except Exception as e:
            raise RuntimeError(f"Error adjusting user trust: {e}")

    def _calculate_risk_level(self, profile: BehaviorProfile, history: ModerationHistory) -> RiskLevel:
        """Calculate user risk level based on behavior."""
        # If no history, default to medium
        if history.total_messages == 0:
            return RiskLevel.MEDIUM

        # Calculate flagged rate
        flagged_rate = history.flagged_messages / history.total_messages

        # Calculate false positive rate
        false_positive_rate = history.false_positives / max(1, history.flagged_messages)

        # Consider average toxicity and trust score
        avg_toxicity = profile.average_toxicity_score
        trust_score = profile.trust_score

        # Risk level calculation
        if flagged_rate < 0.05 and avg_toxicity < 0.2 and trust_score > 0.7:
            return RiskLevel.LOW
        elif flagged_rate > 0.3 or avg_toxicity > 0.6 or trust_score < 0.3:
            return RiskLevel.HIGH
        else:
            return RiskLevel.MEDIUM

    def _calculate_trust_score(
        self,
        profile: BehaviorProfile,
        history: ModerationHistory,
        behavior_update: UserBehaviorUpdate
    ) -> float:
        """Calculate user trust score."""
        current_score = profile.trust_score

        # Base adjustment based on content quality
        toxicity = behavior_update.message_toxicity_score
        if toxicity < 0.1:
            # Very clean content
            adjustment = 0.02
        elif toxicity < 0.3:
            # Clean content
            adjustment = 0.01
        elif toxicity < 0.6:
            # Questionable content
            adjustment = -0.01
        else:
            # Toxic content
            adjustment = -0.03

        # Bonus for false positives (system was wrong about user)
        if behavior_update.was_false_positive:
            adjustment += 0.05

        # Penalty for repeated violations
        if history.flagged_messages > 10 and history.false_positives / history.flagged_messages < 0.1:
            adjustment -= 0.02

        return current_score + adjustment

    async def get_user_statistics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get detailed statistics for a user.

        Args:
            user_id: User ID
            days: Number of days to look back

        Returns:
            User statistics dictionary
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Get user profile
            user = await self.get_user(user_id)
            if not user:
                return {"error": "User not found"}

            # Get message statistics
            messages_collection = db_manager.async_db[COLLECTIONS["messages"]]
            message_pipeline = [
                {"$match": {
                    "user_id": user_id,
                    "timestamp": {"$gte": cutoff_date}
                }},
                {"$group": {
                    "_id": None,
                    "total_messages": {"$sum": 1},
                    "avg_toxicity": {"$avg": "$toxicity_analysis.overall_score"},
                    "flagged_messages": {
                        "$sum": {
                            "$cond": [
                                {"$ne": ["$moderation_action.action", "none"]},
                                1, 0
                            ]
                        }
                    }
                }}
            ]

            message_stats = await messages_collection.aggregate(message_pipeline).to_list(None)

            # Get activity by hour
            activity_pipeline = [
                {"$match": {
                    "user_id": user_id,
                    "timestamp": {"$gte": cutoff_date}
                }},
                {"$group": {
                    "_id": {"$hour": "$timestamp"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]

            activity_by_hour = await messages_collection.aggregate(activity_pipeline).to_list(None)

            # Compile statistics
            stats = {
                "user_id": user_id,
                "username": user.username,
                "period_days": days,
                "behavior_profile": user.behavior_profile.dict(),
                "message_stats": message_stats[0] if message_stats else {
                    "total_messages": 0,
                    "avg_toxicity": 0.0,
                    "flagged_messages": 0
                },
                "activity_by_hour": [
                    {"hour": item["_id"], "count": item["count"]}
                    for item in activity_by_hour[:5]  # Top 5 hours
                ],
                "generated_at": datetime.utcnow().isoformat()
            }

            return stats

        except Exception as e:
            return {"error": str(e), "user_id": user_id}

    async def search_users(
        self,
        query: Optional[str] = None,
        risk_level: Optional[RiskLevel] = None,
        min_trust_score: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[User]:
        """
        Search for users with various filters.

        Args:
            query: Search query for username/email
            risk_level: Filter by risk level
            min_trust_score: Minimum trust score
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of matching users
        """
        try:
            users_collection = db_manager.async_db[COLLECTIONS["users"]]

            # Build filter
            filter_doc = {}
            if query:
                filter_doc["$or"] = [
                    {"username": {"$regex": query, "$options": "i"}},
                    {"email": {"$regex": query, "$options": "i"}}
                ]
            if risk_level:
                filter_doc["behavior_profile.risk_level"] = risk_level.value
            if min_trust_score is not None:
                filter_doc["behavior_profile.trust_score"] = {"$gte": min_trust_score}

            # Execute query
            cursor = users_collection.find(filter_doc).sort("created_at", -1).skip(offset).limit(limit)
            users = []
            async for user_doc in cursor:
                users.append(User(**user_doc))

            return users

        except Exception as e:
            raise RuntimeError(f"Error searching users: {e}")

    async def cleanup_inactive_users(self, days: int = 90) -> int:
        """
        Cleanup inactive users (mark as archived or similar).

        Args:
            days: Number of days of inactivity before cleanup

        Returns:
            Number of users cleaned up
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            users_collection = db_manager.async_db[COLLECTIONS["users"]]

            # Find inactive users
            result = await users_collection.update_many(
                {
                    "last_active": {"$lt": cutoff_date},
                    "status": {"$ne": "archived"}  # Assuming we add status field
                },
                {"$set": {"status": "archived"}}
            )

            return result.modified_count

        except Exception as e:
            raise RuntimeError(f"Error cleaning up inactive users: {e}")

    async def get_system_user_stats(self) -> Dict[str, Any]:
        """Get system-wide user statistics."""
        try:
            users_collection = db_manager.async_db[COLLECTIONS["users"]]

            # Total users
            total_users = await users_collection.count_documents({})

            # Users by risk level
            risk_pipeline = [
                {"$group": {
                    "_id": "$behavior_profile.risk_level",
                    "count": {"$sum": 1}
                }}
            ]
            risk_distribution = await users_collection.aggregate(risk_pipeline).to_list(None)

            # Active users (last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            active_users = await users_collection.count_documents({
                "last_active": {"$gte": seven_days_ago}
            })

            # New users (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            new_users = await users_collection.count_documents({
                "created_at": {"$gte": thirty_days_ago}
            })

            return {
                "total_users": total_users,
                "active_users_7d": active_users,
                "new_users_30d": new_users,
                "risk_distribution": {
                    item["_id"]: item["count"] for item in risk_distribution
                },
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}


# Global user service instance
user_service = UserService()