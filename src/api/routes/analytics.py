"""Analytics and reporting API routes."""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends

from src.config.database import get_database, COLLECTIONS
from src.models.moderation import (
    AnalyticsDashboard, AnalyticsOverview, SystemHealth,
    PerformanceMetrics, ToxicityCategoryStats, UserRiskDistribution
)
from src.services.moderation_service import moderation_service
from src.services.user_service import user_service
from src.services.toxicity_detector import toxicity_detector
from src.services.embedding_service import embedding_service

router = APIRouter()


@router.get("/dashboard", response_model=AnalyticsDashboard)
async def get_analytics_dashboard(
    days: int = Query(default=7, ge=1, le=365, description="Number of days for analytics"),
    db=Depends(get_database)
):
    """
    Get comprehensive analytics dashboard.

    This endpoint provides a complete overview of the moderation system
    performance, user statistics, and content analysis metrics.

    Args:
        days: Number of days to include in analytics (1-365)
        db: Database connection

    Returns:
        Complete analytics dashboard
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get overview statistics
        overview = await get_analytics_overview(days, db)

        # Get toxicity category breakdown
        toxicity_categories = await get_toxicity_category_stats(cutoff_date, db)

        # Get user risk distribution
        user_risk_dist = await get_user_risk_distribution(db)

        # Get performance metrics
        performance = await get_performance_metrics(db)

        # Get recent trends
        trends = await get_recent_trends(days, db)

        return AnalyticsDashboard(
            overview=overview,
            top_toxicity_categories=toxicity_categories,
            user_risk_distribution=user_risk_dist,
            performance_metrics=performance,
            recent_trends=trends
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics dashboard: {e}")


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    days: int = Query(default=7, ge=1, le=365, description="Number of days for overview"),
    db=Depends(get_database)
):
    """
    Get system overview statistics.

    Args:
        days: Number of days to include (1-365)
        db: Database connection

    Returns:
        System overview statistics
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get message statistics
        messages_collection = db[COLLECTIONS["messages"]]
        message_pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}}},
            {"$group": {
                "_id": None,
                "total_messages": {"$sum": 1},
                "flagged_messages": {
                    "$sum": {
                        "$cond": [
                            {"$ne": ["$moderation_action.action", "none"]},
                            1, 0
                        ]
                    }
                },
                "avg_toxicity": {"$avg": "$toxicity_analysis.overall_score"}
            }}
        ]

        message_stats = await messages_collection.aggregate(message_pipeline).to_list(None)
        msg_stats = message_stats[0] if message_stats else {
            "total_messages": 0,
            "flagged_messages": 0,
            "avg_toxicity": 0.0
        }

        # Get last 24h messages
        last_24h = datetime.utcnow() - timedelta(hours=24)
        messages_last_24h = await messages_collection.count_documents({
            "timestamp": {"$gte": last_24h}
        })

        # Get user statistics
        users_collection = db[COLLECTIONS["users"]]
        active_users = await users_collection.count_documents({
            "last_active": {"$gte": cutoff_date}
        })

        # Get conversation statistics
        conversations_collection = db[COLLECTIONS["conversations"]]
        active_conversations = await conversations_collection.count_documents({
            "updated_at": {"$gte": cutoff_date},
            "status": "active"
        })

        # Calculate rates
        total_messages = msg_stats["total_messages"]
        flagged_rate = (msg_stats["flagged_messages"] / total_messages * 100) if total_messages > 0 else 0.0

        # Get false positive rate (would need more complex query in real implementation)
        false_positive_rate = 5.0  # Placeholder

        return AnalyticsOverview(
            total_messages=total_messages,
            messages_last_24h=messages_last_24h,
            messages_last_7d=total_messages,
            flagged_rate=flagged_rate,
            false_positive_rate=false_positive_rate,
            active_users=active_users,
            active_conversations=active_conversations
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting overview: {e}")


@router.get("/toxicity-categories", response_model=List[ToxicityCategoryStats])
async def get_toxicity_category_stats(
    days: int = Query(default=7, ge=1, le=365),
    db=Depends(get_database)
):
    """
    Get breakdown of toxicity categories.

    Args:
        days: Number of days to include (1-365)
        db: Database connection

    Returns:
        List of toxicity category statistics
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return await get_toxicity_category_stats(cutoff_date, db)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting toxicity categories: {e}")


@router.get("/user-risk-distribution", response_model=UserRiskDistribution)
async def get_user_risk_distribution_endpoint(db=Depends(get_database)):
    """
    Get distribution of users by risk level.

    Args:
        db: Database connection

    Returns:
        User risk distribution statistics
    """
    try:
        return await get_user_risk_distribution(db)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user risk distribution: {e}")


@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics_endpoint(db=Depends(get_database)):
    """
    Get system performance metrics.

    Args:
        db: Database connection

    Returns:
        System performance metrics
    """
    try:
        return await get_performance_metrics(db)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance metrics: {e}")


@router.get("/moderation-trends")
async def get_moderation_trends(
    days: int = Query(default=30, ge=1, le=365, description="Number of days for trends"),
    db=Depends(get_database)
):
    """
    Get moderation trends over time.

    Args:
        days: Number of days to include (1-365)
        db: Database connection

    Returns:
        Moderation trends data
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get daily moderation statistics
        logs_collection = db[COLLECTIONS["moderation_logs"]]
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}}},
            {"$group": {
                "_id": {
                    "year": {"$year": "$timestamp"},
                    "month": {"$month": "$timestamp"},
                    "day": {"$dayOfMonth": "$timestamp"}
                },
                "total_actions": {"$sum": 1},
                "avg_score": {"$avg": "$original_score"},
                "actions": {
                    "$push": "$action"
                }
            }},
            {"$sort": {"_id": 1}}
        ]

        daily_stats = await logs_collection.aggregate(pipeline).to_list(None)

        # Process data for trends
        trends = []
        for stat in daily_stats:
            date_key = stat["_id"]
            date_str = f"{date_key['year']}-{date_key['month']:02d}-{date_key['day']:02d}"

            # Count actions by type
            action_counts = {}
            for action in stat["actions"]:
                action_counts[action] = action_counts.get(action, 0) + 1

            trends.append({
                "date": date_str,
                "total_actions": stat["total_actions"],
                "avg_score": round(stat["avg_score"], 3),
                "action_breakdown": action_counts
            })

        return {"trends": trends, "period_days": days}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting moderation trends: {e}")


@router.get("/user-activity")
async def get_user_activity_analytics(
    days: int = Query(default=7, ge=1, le=365, description="Number of days for analytics"),
    db=Depends(get_database)
):
    """
    Get user activity analytics.

    Args:
        days: Number of days to include (1-365)
        db: Database connection

    Returns:
        User activity analytics
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get top active users
        messages_collection = db[COLLECTIONS["messages"]]
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}}},
            {"$group": {
                "_id": "$user_id",
                "message_count": {"$sum": 1},
                "avg_toxicity": {"$avg": "$toxicity_analysis.overall_score"},
                "flagged_count": {
                    "$sum": {
                        "$cond": [
                            {"$ne": ["$moderation_action.action", "none"]},
                            1, 0
                        ]
                    }
                }
            }},
            {"$sort": {"message_count": -1}},
            {"$limit": 10}
        ]

        top_users = await messages_collection.aggregate(pipeline).to_list(None)

        # Get user activity by hour
        activity_pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}}},
            {"$group": {
                "_id": {"$hour": "$timestamp"},
                "message_count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]

        hourly_activity = await messages_collection.aggregate(activity_pipeline).to_list(None)

        return {
            "top_active_users": top_users,
            "hourly_activity": [
                {"hour": item["_id"], "count": item["message_count"]}
                for item in hourly_activity
            ],
            "period_days": days
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user activity analytics: {e}")


@router.get("/system-health", response_model=SystemHealth)
async def get_system_health(db=Depends(get_database)):
    """
    Get system health status.

    Returns:
        System health information
    """
    try:
        # Check database connection
        try:
            await db.command('ping')
            db_status = "healthy"
        except Exception:
            db_status = "unhealthy"

        # Check model status
        try:
            toxicity_health = await toxicity_detector.health_check()
            embedding_health = await embedding_service.health_check()
            models_loaded = (
                toxicity_health.get("status") == "healthy" and
                embedding_health.get("status") == "healthy"
            )
        except Exception:
            models_loaded = False

        # Calculate memory usage (simplified)
        import psutil
        memory_usage = psutil.virtual_memory().used / 1024 / 1024  # MB

        # Determine overall status
        overall_status = "healthy"
        if db_status != "healthy" or not models_loaded:
            overall_status = "unhealthy"

        return SystemHealth(
            status=overall_status,
            version="1.0.0",
            models_loaded=["detoxify", "sentence-transformers"] if models_loaded else [],
            database_connection=db_status,
            memory_usage_mb=memory_usage,
            uptime_seconds=0  # Would track actual uptime
        )

    except Exception as e:
        return SystemHealth(
            status="unhealthy",
            version="1.0.0",
            models_loaded=[],
            database_connection="error",
            memory_usage_mb=0,
            uptime_seconds=0,
            last_error=str(e)
        )


@router.get("/export")
async def export_analytics_data(
    format: str = Query(default="json", regex="^(json|csv)$"),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to export"),
    db=Depends(get_database)
):
    """
    Export analytics data in specified format.

    Args:
        format: Export format (json or csv)
        days: Number of days to include (1-365)
        db: Database connection

    Returns:
        Exported analytics data
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get moderation logs for export
        logs_collection = db[COLLECTIONS["moderation_logs"]]
        logs = await logs_collection.find(
            {"timestamp": {"$gte": cutoff_date}}
        ).sort("timestamp", -1).to_list(None)

        if format.lower() == "csv":
            # Convert to CSV format
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow([
                "timestamp", "message_id", "user_id", "action",
                "original_score", "adjusted_threshold"
            ])

            # Write data
            for log in logs:
                writer.writerow([
                    log["timestamp"].isoformat(),
                    log["message_id"],
                    log["user_id"],
                    log["action"],
                    log["original_score"],
                    log["adjusted_threshold"]
                ])

            csv_data = output.getvalue()
            output.close()

            return {
                "format": "csv",
                "data": csv_data,
                "record_count": len(logs),
                "period_days": days
            }
        else:
            # Return JSON format
            return {
                "format": "json",
                "data": logs,
                "record_count": len(logs),
                "period_days": days
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting analytics data: {e}")


# Helper functions
async def get_toxicity_category_stats(cutoff_date: datetime, db) -> List[ToxicityCategoryStats]:
    """Get toxicity category statistics."""
    try:
        messages_collection = db[COLLECTIONS["messages"]]
        pipeline = [
            {"$match": {
                "timestamp": {"$gte": cutoff_date},
                "toxicity_analysis.predictions.toxic": {"$exists": True}
            }},
            {"$group": {
                "_id": None,
                "total_messages": {"$sum": 1},
                "avg_toxic": {"$avg": "$toxicity_analysis.predictions.toxic"},
                "avg_severe_toxic": {"$avg": "$toxicity_analysis.predictions.severe_toxic"},
                "avg_obscene": {"$avg": "$toxicity_analysis.predictions.obscene"},
                "avg_threat": {"$avg": "$toxicity_analysis.predictions.threat"},
                "avg_insult": {"$avg": "$toxicity_analysis.predictions.insult"},
                "avg_identity_hate": {"$avg": "$toxicity_analysis.predictions.identity_hate"}
            }}
        ]

        result = await messages_collection.aggregate(pipeline).to_list(None)
        if not result:
            return []

        stats = result[0]
        total_messages = stats["total_messages"]

        categories = [
            ToxicityCategoryStats(
                category="toxic",
                count=int(total_messages * stats["avg_toxic"]),
                percentage=stats["avg_toxic"] * 100,
                avg_score=stats["avg_toxic"]
            ),
            ToxicityCategoryStats(
                category="severe_toxic",
                count=int(total_messages * stats["avg_severe_toxic"]),
                percentage=stats["avg_severe_toxic"] * 100,
                avg_score=stats["avg_severe_toxic"]
            ),
            ToxicityCategoryStats(
                category="obscene",
                count=int(total_messages * stats["avg_obscene"]),
                percentage=stats["avg_obscene"] * 100,
                avg_score=stats["avg_obscene"]
            ),
            ToxicityCategoryStats(
                category="threat",
                count=int(total_messages * stats["avg_threat"]),
                percentage=stats["avg_threat"] * 100,
                avg_score=stats["avg_threat"]
            ),
            ToxicityCategoryStats(
                category="insult",
                count=int(total_messages * stats["avg_insult"]),
                percentage=stats["avg_insult"] * 100,
                avg_score=stats["avg_insult"]
            ),
            ToxicityCategoryStats(
                category="identity_hate",
                count=int(total_messages * stats["avg_identity_hate"]),
                percentage=stats["avg_identity_hate"] * 100,
                avg_score=stats["avg_identity_hate"]
            ),
        ]

        return sorted(categories, key=lambda x: x.count, reverse=True)[:6]

    except Exception:
        return []


async def get_user_risk_distribution(db) -> UserRiskDistribution:
    """Get user risk distribution."""
    try:
        users_collection = db[COLLECTIONS["users"]]
        pipeline = [
            {"$group": {
                "_id": "$behavior_profile.risk_level",
                "count": {"$sum": 1}
            }}
        ]

        result = await users_collection.aggregate(pipeline).to_list(None)
        distribution = {"low": 0, "medium": 0, "high": 0}

        for item in result:
            risk_level = item["_id"]
            if risk_level in distribution:
                distribution[risk_level] = item["count"]

        return UserRiskDistribution(**distribution)

    except Exception:
        return UserRiskDistribution(low=0, medium=0, high=0)


async def get_performance_metrics(db) -> PerformanceMetrics:
    """Get system performance metrics."""
    try:
        # Get average processing time
        logs_collection = db[COLLECTIONS["moderation_logs"]]
        pipeline = [
            {"$group": {
                "_id": None,
                "avg_processing_time": {"$avg": "$processing_time_ms"}
            }}
        ]

        result = await logs_collection.aggregate(pipeline).to_list(None)
        avg_processing_time = result[0]["avg_processing_time"] if result else 0.0

        # Get system metrics
        import psutil
        memory_usage = psutil.virtual_memory().used / 1024 / 1024
        cpu_usage = psutil.cpu_percent()

        return PerformanceMetrics(
            avg_processing_time_ms=avg_processing_time,
            api_uptime=99.9,  # Placeholder
            model_accuracy=0.85,  # Placeholder
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage
        )

    except Exception:
        return PerformanceMetrics(
            avg_processing_time_ms=0.0,
            api_uptime=0.0,
            model_accuracy=0.0,
            memory_usage_mb=0.0,
            cpu_usage_percent=0.0
        )


async def get_recent_trends(days: int, db) -> dict:
    """Get recent trend data."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get daily message counts
        messages_collection = db[COLLECTIONS["messages"]]
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}}},
            {"$group": {
                "_id": {
                    "year": {"$year": "$timestamp"},
                    "month": {"$month": "$timestamp"},
                    "day": {"$dayOfMonth": "$timestamp"}
                },
                "count": {"$sum": 1},
                "avg_toxicity": {"$avg": "$toxicity_analysis.overall_score"}
            }},
            {"$sort": {"_id": 1}}
        ]

        daily_data = await messages_collection.aggregate(pipeline).to_list(None)

        return {
            "daily_messages": [item["count"] for item in daily_data],
            "daily_toxicity": [round(item["avg_toxicity"], 3) for item in daily_data],
            "dates": [
                f"{item['_id']['year']}-{item['_id']['month']:02d}-{item['_id']['day']:02d}"
                for item in daily_data
            ]
        }

    except Exception:
        return {"daily_messages": [], "daily_toxicity": [], "dates": []}