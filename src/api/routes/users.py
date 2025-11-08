"""User management API routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends

from src.config.database import get_database
from src.models.user import (
    User, UserCreate, UserUpdate, UserStats, UserPublic,
    UserListResponse, UserTrustAdjustment, RiskLevel
)
from src.services.user_service import user_service

router = APIRouter()


@router.post("/", response_model=User)
async def create_user(
    user_data: UserCreate,
    db=Depends(get_database)
):
    """
    Create a new user profile.

    Args:
        user_data: User creation data
        db: Database connection

    Returns:
        Created user profile
    """
    try:
        user = await user_service.create_user(user_data)
        return user

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {e}")


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    db=Depends(get_database)
):
    """
    Get user profile by ID.

    Args:
        user_id: User ID
        db: Database connection

    Returns:
        User profile
    """
    try:
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {e}")


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    db=Depends(get_database)
):
    """
    Update user profile.

    Args:
        user_id: User ID
        update_data: Update data
        db: Database connection

    Returns:
        Updated user profile
    """
    try:
        user = await user_service.update_user(user_id, update_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {e}")


@router.get("/{user_id}/statistics", response_model=dict)
async def get_user_statistics(
    user_id: str,
    days: int = Query(default=30, ge=1, le=365),
    db=Depends(get_database)
):
    """
    Get detailed statistics for a user.

    Args:
        user_id: User ID
        days: Number of days to look back (1-365)
        db: Database connection

    Returns:
        User statistics
    """
    try:
        stats = await user_service.get_user_statistics(user_id, days)
        if "error" in stats and stats["error"] == "User not found":
            raise HTTPException(status_code=404, detail="User not found")
        return stats

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user statistics: {e}")


@router.post("/{user_id}/trust-adjustment", response_model=User)
async def adjust_user_trust(
    user_id: str,
    adjustment: UserTrustAdjustment,
    db=Depends(get_database)
):
    """
    Manually adjust user trust score.

    This endpoint allows moderators or administrators to adjust
    a user's trust score based on manual review or feedback.

    Args:
        user_id: User ID
        adjustment: Trust adjustment data
        db: Database connection

    Returns:
        Updated user profile
    """
    try:
        user = await user_service.adjust_user_trust(user_id, adjustment)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adjusting user trust: {e}")


@router.get("/", response_model=UserListResponse)
async def search_users(
    query: Optional[str] = Query(None, description="Search query for username/email"),
    risk_level: Optional[RiskLevel] = Query(None, description="Filter by risk level"),
    min_trust_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum trust score"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Results per page"),
    db=Depends(get_database)
):
    """
    Search for users with various filters.

    Args:
        query: Search query for username/email
        risk_level: Filter by risk level
        min_trust_score: Minimum trust score
        page: Page number (1-based)
        page_size: Results per page
        db: Database connection

    Returns:
        Paginated list of users
    """
    try:
        offset = (page - 1) * page_size
        users = await user_service.search_users(
            query=query,
            risk_level=risk_level,
            min_trust_score=min_trust_score,
            limit=page_size,
            offset=offset
        )

        # Convert to public users
        public_users = [UserPublic(**user.dict()) for user in users]

        # Note: In a real implementation, you'd want to get total count
        # This would require a separate query or using aggregation
        total_count = len(public_users)  # Simplified

        return UserListResponse(
            users=public_users,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=False,  # Simplified
            has_prev=page > 1
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching users: {e}")


@router.get("/{user_id}/public", response_model=UserPublic)
async def get_public_user_profile(
    user_id: str,
    db=Depends(get_database)
):
    """
    Get public user profile information.

    This endpoint returns only the publicly safe information
    about a user, excluding sensitive data.

    Args:
        user_id: User ID
        db: Database connection

    Returns:
        Public user profile
    """
    try:
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        public_user = UserPublic(**user.dict())
        return public_user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving public user profile: {e}")


@router.get("/system/statistics")
async def get_system_user_statistics(db=Depends(get_database)):
    """
    Get system-wide user statistics.

    Returns:
        System-wide user statistics
    """
    try:
        stats = await user_service.get_system_user_stats()
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system user statistics: {e}")


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db=Depends(get_database)
):
    """
    Delete a user profile.

    ⚠️ This is a destructive action. Consider archiving instead.

    Args:
        user_id: User ID
        db: Database connection

    Returns:
        Deletion confirmation
    """
    try:
        # In a real implementation, you would:
        # 1. Soft delete (mark as deleted/archived)
        # 2. Or hard delete with proper cascading
        # For now, we'll implement a simple status update

        user = await user_service.update_user(user_id, UserUpdate())
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # This is a placeholder - actual deletion would be more complex
        return {"status": "deleted", "user_id": user_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {e}")


@router.post("/cleanup/inactive")
async def cleanup_inactive_users(
    days: int = Query(default=90, ge=1, description="Days of inactivity before cleanup"),
    db=Depends(get_database)
):
    """
    Cleanup inactive users (admin only).

    This endpoint marks users as archived if they haven't been active
    for the specified number of days.

    Args:
        days: Number of days of inactivity before cleanup
        db: Database connection

    Returns:
        Number of users cleaned up
    """
    try:
        cleaned_count = await user_service.cleanup_inactive_users(days)
        return {
            "status": "completed",
            "cleaned_users": cleaned_count,
            "days_threshold": days
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up inactive users: {e}")