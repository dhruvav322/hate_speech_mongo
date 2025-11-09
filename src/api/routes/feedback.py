"""Feedback and learning API routes."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends

from src.config.database import get_database, COLLECTIONS
from src.models.moderation import FeedbackAppeal, ModeratorReview
from src.models.user import UserTrustAdjustment
from src.services.user_service import user_service
from src.services.moderation_service import moderation_service

router = APIRouter()


@router.post("/appeal")
async def submit_appeal(
    appeal_data: dict,
    db=Depends(get_database)
):
    """
    Submit an appeal against a moderation decision.

    This endpoint allows users to appeal moderation actions they believe
    were incorrect. Appeals are reviewed by moderators and can result
    in user trust score adjustments.

    Expected request format:
    {
        "message_id": "string",
        "original_action": "warn|hide|delete|ban",
        "appeal_reason": "string",
        "user_explanation": "string"
    }

    Args:
        appeal_data: Appeal submission data
        db: Database connection

    Returns:
        Appeal submission confirmation
    """
    try:
        import uuid

        # Validate required fields
        required_fields = ["message_id", "original_action", "appeal_reason", "user_explanation"]
        for field in required_fields:
            if field not in appeal_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )

        # Get message details
        messages_collection = db[COLLECTIONS["messages"]]
        message = await messages_collection.find_one(
            {"message_id": appeal_data["message_id"]}
        )

        if not message:
            raise HTTPException(
                status_code=404,
                detail="Message not found"
            )

        # Create appeal record
        appeal = FeedbackAppeal(
            appeal_id=f"appeal_{uuid.uuid4().hex[:8]}",
            message_id=appeal_data["message_id"],
            user_id=message.get("user_id"),
            original_action=appeal_data["original_action"],
            appeal_reason=appeal_data["appeal_reason"],
            user_explanation=appeal_data["user_explanation"],
            status="pending",
            created_at=datetime.utcnow()
        )

        # Store appeal
        feedback_collection = db[COLLECTIONS["feedback"]]
        await feedback_collection.insert_one(appeal.dict(by_alias=True))

        # Update message feedback status
        await messages_collection.update_one(
            {"message_id": appeal_data["message_id"]},
            {"$set": {"feedback.appeal_status": "pending"}}
        )

        return {
            "status": "submitted",
            "appeal_id": appeal.appeal_id,
            "message_id": appeal_data["message_id"],
            "status": "pending",
            "submitted_at": appeal.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting appeal: {e}")


@router.post("/moderator-review")
async def submit_moderator_review(
    review_data: dict,
    db=Depends(get_database)
):
    """
    Submit a moderator review of an automated moderation decision.

    This endpoint allows human moderators to review and potentially
    override automated moderation decisions.

    Expected request format:
    {
        "message_id": "string",
        "reviewer_id": "string",
        "original_action": "warn|hide|delete|ban",
        "final_action": "none|warn|hide|delete|ban",
        "review_notes": "string",
        "confidence_score": 0.0-1.0
    }

    Args:
        review_data: Moderator review data
        db: Database connection

    Returns:
        Review submission confirmation
    """
    try:
        import uuid

        # Validate required fields
        required_fields = [
            "message_id", "reviewer_id", "original_action",
            "final_action", "review_notes"
        ]
        for field in required_fields:
            if field not in review_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )

        # Get message details
        messages_collection = db[COLLECTIONS["messages"]]
        message = await messages_collection.find_one(
            {"message_id": review_data["message_id"]}
        )

        if not message:
            raise HTTPException(
                status_code=404,
                detail="Message not found"
            )

        # Create review record
        review = ModeratorReview(
            review_id=f"review_{uuid.uuid4().hex[:8]}",
            message_id=review_data["message_id"],
            reviewer_id=review_data["reviewer_id"],
            original_action=review_data["original_action"],
            final_action=review_data["final_action"],
            review_notes=review_data["review_notes"],
            confidence_score=review_data.get("confidence_score", 0.5),
            timestamp=datetime.utcnow()
        )

        # Store review
        feedback_collection = db[COLLECTIONS["feedback"]]
        await feedback_collection.insert_one(review.dict(by_alias=True))

        # Update message moderation action if changed
        if review_data["original_action"] != review_data["final_action"]:
            from src.models.message import ModerationActionData, AppliedBy

            new_action = ModerationActionData(
                action=review_data["final_action"],
                confidence=review_data.get("confidence_score", 0.5),
                reason=f"Moderator review: {review_data['review_notes']}",
                adjusted_threshold=message.get("moderation_action", {}).get("adjusted_threshold", 0.5),
                applied_by=AppliedBy.HUMAN
            )

            await messages_collection.update_one(
                {"message_id": review_data["message_id"]},
                {"$set": {"moderation_action": new_action.dict()}}
            )

        # Adjust user trust score if this was a false positive
        if (review_data["original_action"] in ["warn", "hide", "delete"] and
            review_data["final_action"] == "none"):

            user_id = message.get("user_id")
            if user_id:
                # Positive trust adjustment for false positive
                trust_adjustment = UserTrustAdjustment(
                    adjustment_amount=0.1,  # Increase trust
                    reason=f"False positive confirmed by moderator: {review_data['review_notes']}",
                    moderator_notes=review_data["review_notes"]
                )

                await user_service.adjust_user_trust(user_id, trust_adjustment)

        elif (review_data["original_action"] == "none" and
              review_data["final_action"] in ["warn", "hide", "delete"]):

            user_id = message.get("user_id")
            if user_id:
                # Negative trust adjustment for missed toxicity
                trust_adjustment = UserTrustAdjustment(
                    adjustment_amount=-0.05,  # Decrease trust
                    reason=f"Missed toxicity corrected by moderator: {review_data['review_notes']}",
                    moderator_notes=review_data["review_notes"]
                )

                await user_service.adjust_user_trust(user_id, trust_adjustment)

        return {
            "status": "submitted",
            "review_id": review.review_id,
            "message_id": review_data["message_id"],
            "final_action": review_data["final_action"],
            "reviewed_at": review.timestamp.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting moderator review: {e}")


@router.get("/appeals")
async def get_appeals(
    status: Optional[str] = Query(None, pattern="^(pending|approved|rejected)$"),
    reviewer_id: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db=Depends(get_database)
):
    """
    Get list of appeals with optional filtering.

    Args:
        status: Filter by appeal status
        reviewer_id: Filter by reviewer ID
        page: Page number (1-based)
        page_size: Results per page
        db: Database connection

    Returns:
        Paginated list of appeals
    """
    try:
        feedback_collection = db[COLLECTIONS["feedback"]]

        # Build filter
        filter_doc = {"appeal_id": {"$exists": True}}  # Only appeals
        if status:
            filter_doc["status"] = status
        if reviewer_id:
            filter_doc["reviewer_id"] = reviewer_id

        # Get total count
        total_count = await feedback_collection.count_documents(filter_doc)

        # Get appeals with pagination
        offset = (page - 1) * page_size
        cursor = feedback_collection.find(filter_doc).sort("created_at", -1).skip(offset).limit(page_size)

        appeals = []
        async for appeal_doc in cursor:
            appeals.append(FeedbackAppeal(**appeal_doc))

        return {
            "appeals": appeals,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "has_next": offset + page_size < total_count,
            "has_prev": page > 1
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting appeals: {e}")


@router.get("/reviews")
async def get_moderator_reviews(
    reviewer_id: Optional[str] = Query(None),
    message_id: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db=Depends(get_database)
):
    """
    Get list of moderator reviews with optional filtering.

    Args:
        reviewer_id: Filter by reviewer ID
        message_id: Filter by message ID
        page: Page number (1-based)
        page_size: Results per page
        db: Database connection

    Returns:
        Paginated list of moderator reviews
    """
    try:
        feedback_collection = db[COLLECTIONS["feedback"]]

        # Build filter
        filter_doc = {"review_id": {"$exists": True}}  # Only reviews
        if reviewer_id:
            filter_doc["reviewer_id"] = reviewer_id
        if message_id:
            filter_doc["message_id"] = message_id

        # Get total count
        total_count = await feedback_collection.count_documents(filter_doc)

        # Get reviews with pagination
        offset = (page - 1) * page_size
        cursor = feedback_collection.find(filter_doc).sort("timestamp", -1).skip(offset).limit(page_size)

        reviews = []
        async for review_doc in cursor:
            reviews.append(ModeratorReview(**review_doc))

        return {
            "reviews": reviews,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "has_next": offset + page_size < total_count,
            "has_prev": page > 1
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting moderator reviews: {e}")


@router.put("/appeals/{appeal_id}/review")
async def review_appeal(
    appeal_id: str,
    review_data: dict,
    db=Depends(get_database)
):
    """
    Review and resolve an appeal.

    Expected request format:
    {
        "reviewer_id": "string",
        "decision": "approved|rejected",
        "review_notes": "string"
    }

    Args:
        appeal_id: Appeal ID
        review_data: Review decision data
        db: Database connection

    Returns:
        Appeal review confirmation
    """
    try:
        # Validate required fields
        required_fields = ["reviewer_id", "decision", "review_notes"]
        for field in required_fields:
            if field not in review_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )

        if review_data["decision"] not in ["approved", "rejected"]:
            raise HTTPException(
                status_code=400,
                detail="Decision must be 'approved' or 'rejected'"
            )

        # Get appeal details
        feedback_collection = db[COLLECTIONS["feedback"]]
        appeal = await feedback_collection.find_one({"appeal_id": appeal_id})

        if not appeal:
            raise HTTPException(
                status_code=404,
                detail="Appeal not found"
            )

        if appeal["status"] != "pending":
            raise HTTPException(
                status_code=400,
                detail="Appeal has already been reviewed"
            )

        # Update appeal
        await feedback_collection.update_one(
            {"appeal_id": appeal_id},
            {
                "$set": {
                    "status": review_data["decision"],
                    "reviewer_id": review_data["reviewer_id"],
                    "review_notes": review_data["review_notes"],
                    "reviewed_at": datetime.utcnow()
                }
            }
        )

        # Update message appeal status
        messages_collection = db[COLLECTIONS["messages"]]
        await messages_collection.update_one(
            {"message_id": appeal["message_id"]},
            {"$set": {"feedback.appeal_status": review_data["decision"]}}
        )

        # Adjust user trust score based on appeal decision
        user_id = appeal.get("user_id")
        if user_id and review_data["decision"] == "approved":
            # Appeal was approved - increase trust score
            trust_adjustment = UserTrustAdjustment(
                adjustment_amount=0.15,  # Significant increase for successful appeal
                reason=f"Appeal approved: {review_data['review_notes']}",
                moderator_notes=review_data["review_notes"]
            )

            await user_service.adjust_user_trust(user_id, trust_adjustment)

        return {
            "status": "reviewed",
            "appeal_id": appeal_id,
            "decision": review_data["decision"],
            "reviewed_by": review_data["reviewer_id"],
            "reviewed_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reviewing appeal: {e}")


@router.get("/statistics")
async def get_feedback_statistics(
    days: int = Query(default=30, ge=1, le=365),
    db=Depends(get_database)
):
    """
    Get feedback and appeal statistics.

    Args:
        days: Number of days to include (1-365)
        db: Database connection

    Returns:
        Feedback statistics
    """
    try:
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        feedback_collection = db[COLLECTIONS["feedback"]]

        # Get appeal statistics
        appeal_pipeline = [
            {"$match": {
                "appeal_id": {"$exists": True},
                "created_at": {"$gte": cutoff_date}
            }},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]

        appeal_stats = await feedback_collection.aggregate(appeal_pipeline).to_list(None)

        # Get review statistics
        review_pipeline = [
            {"$match": {
                "review_id": {"$exists": True},
                "timestamp": {"$gte": cutoff_date}
            }},
            {"$group": {
                "_id": None,
                "total_reviews": {"$sum": 1},
                "overturned_actions": {
                    "$sum": {
                        "$cond": [
                            {"$ne": ["$original_action", "$final_action"]},
                            1, 0
                        ]
                    }
                },
                "avg_confidence": {"$avg": "$confidence_score"}
            }}
        ]

        review_stats = await feedback_collection.aggregate(review_pipeline).to_list(None)

        # Format appeal statistics
        appeal_breakdown = {}
        total_appeals = 0
        for stat in appeal_stats:
            appeal_breakdown[stat["_id"]] = stat["count"]
            total_appeals += stat["count"]

        # Calculate appeal approval rate
        approval_rate = (appeal_breakdown.get("approved", 0) / total_appeals * 100) if total_appeals > 0 else 0

        return {
            "period_days": days,
            "appeals": {
                "total": total_appeals,
                "breakdown": appeal_breakdown,
                "approval_rate": round(approval_rate, 2)
            },
            "reviews": {
                "total": review_stats[0]["total_reviews"] if review_stats else 0,
                "overturned_actions": review_stats[0]["overturned_actions"] if review_stats else 0,
                "avg_confidence": round(review_stats[0]["avg_confidence"], 3) if review_stats else 0,
                "overturn_rate": round(
                    (review_stats[0]["overturned_actions"] / review_stats[0]["total_reviews"] * 100)
                    if review_stats and review_stats[0]["total_reviews"] > 0 else 0, 2
                )
            },
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting feedback statistics: {e}")


@router.post("/report")
async def report_message(
    report_data: dict,
    db=Depends(get_database)
):
    """
    Report a message for moderator review.

    Expected request format:
    {
        "message_id": "string",
        "reporter_id": "string",
        "reason": "string",
        "description": "string"
    }

    Args:
        report_data: Message report data
        db: Database connection

    Returns:
        Report submission confirmation
    """
    try:
        import uuid

        # Validate required fields
        required_fields = ["message_id", "reporter_id", "reason", "description"]
        for field in required_fields:
            if field not in report_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )

        # Create report record
        report = {
            "report_id": f"report_{uuid.uuid4().hex[:8]}",
            "message_id": report_data["message_id"],
            "reporter_id": report_data["reporter_id"],
            "reason": report_data["reason"],
            "description": report_data["description"],
            "status": "pending",
            "created_at": datetime.utcnow()
        }

        # Store report
        feedback_collection = db[COLLECTIONS["feedback"]]
        await feedback_collection.insert_one(report)

        # Update message community flags
        messages_collection = db[COLLECTIONS["messages"]]
        await messages_collection.update_one(
            {"message_id": report_data["message_id"]},
            {"$inc": {"feedback.community_flags": 1}}
        )

        return {
            "status": "submitted",
            "report_id": report["report_id"],
            "message_id": report_data["message_id"],
            "status": "pending",
            "submitted_at": report["created_at"].isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting report: {e}")