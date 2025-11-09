"""Conversation management API routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends

from src.config.database import get_database, COLLECTIONS
from src.models.conversation import (
    Conversation, ConversationCreate, ConversationUpdate,
    ConversationContext, ConversationListResponse,
    ConversationSearchFilters, ModerationLevel, ConversationStatus,
    MessageSummary
)
from src.services.embedding_service import embedding_service

router = APIRouter()


@router.post("/", response_model=Conversation)
async def create_conversation(
    conversation_data: ConversationCreate,
    db=Depends(get_database)
):
    """
    Create a new conversation thread.

    Args:
        conversation_data: Conversation creation data
        db: Database connection

    Returns:
        Created conversation
    """
    try:
        import uuid
        from datetime import datetime

        # Generate conversation ID
        conversation_id = f"conv_{uuid.uuid4().hex[:8]}"

        # Create conversation document
        conversation = Conversation(
            conversation_id=conversation_id,
            participants=conversation_data.participants,
            metadata=conversation_data.metadata,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Insert into database
        conversations_collection = db[COLLECTIONS["conversations"]]
        await conversations_collection.insert_one(conversation.dict(by_alias=True))

        return conversation

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating conversation: {e}")


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    db=Depends(get_database)
):
    """
    Get conversation by ID.

    Args:
        conversation_id: Conversation ID
        db: Database connection

    Returns:
        Conversation details
    """
    try:
        conversations_collection = db[COLLECTIONS["conversations"]]
        conversation_doc = await conversations_collection.find_one(
            {"conversation_id": conversation_id}
        )

        if not conversation_doc:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return Conversation(**conversation_doc)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation: {e}")


@router.put("/{conversation_id}", response_model=Conversation)
async def update_conversation(
    conversation_id: str,
    update_data: ConversationUpdate,
    db=Depends(get_database)
):
    """
    Update conversation details.

    Args:
        conversation_id: Conversation ID
        update_data: Update data
        db: Database connection

    Returns:
        Updated conversation
    """
    try:
        conversations_collection = db[COLLECTIONS["conversations"]]

        # Build update document
        update_doc = {}
        if update_data.participants is not None:
            update_doc["participants"] = update_data.participants
        if update_data.metadata is not None:
            update_doc["metadata"] = update_data.metadata.dict()
        if update_data.status is not None:
            update_doc["status"] = update_data.status.value

        if update_doc:
            from datetime import datetime
            update_doc["updated_at"] = datetime.utcnow()

            result = await conversations_collection.update_one(
                {"conversation_id": conversation_id},
                {"$set": update_doc}
            )

            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Conversation not found")

        return await get_conversation(conversation_id, db)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating conversation: {e}")


@router.get("/{conversation_id}/context", response_model=ConversationContext)
async def get_conversation_context(
    conversation_id: str,
    window_size: int = Query(default=5, ge=1, le=20),
    db=Depends(get_database)
):
    """
    Get conversation context for moderation.

    This endpoint provides the conversation context including
    recent messages, toxicity trends, and semantic embeddings
    that help in understanding the conversation flow.

    Args:
        conversation_id: Conversation ID
        window_size: Number of recent messages to include
        db: Database connection

    Returns:
        Conversation context information
    """
    try:
        # Get conversation details
        conversations_collection = db[COLLECTIONS["conversations"]]
        conversation = await conversations_collection.find_one(
            {"conversation_id": conversation_id}
        )

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get recent messages
        messages_collection = db[COLLECTIONS["messages"]]
        recent_messages = await messages_collection.find(
            {"conversation_id": conversation_id},
            {
                "message_id": 1,
                "content": 1,
                "toxicity_analysis.overall_score": 1,
                "timestamp": 1
            }
        ).sort("timestamp", -1).limit(window_size).to_list(None)

        # Convert to message summaries
        message_summaries = []
        total_toxicity = 0.0
        toxicity_scores = []

        for msg in recent_messages:
            toxicity = msg.get("toxicity_analysis", {}).get("overall_score", 0.0)
            total_toxicity += toxicity
            toxicity_scores.append(toxicity)

            # Truncate text for context
            text = msg["content"][:200]
            if len(msg["content"]) > 200:
                text += "..."

            summary = MessageSummary(
                message_id=msg["message_id"],
                text=text,
                toxicity_score=toxicity,
                timestamp=msg["timestamp"]
            )
            message_summaries.append(summary)

        # Calculate statistics
        message_count = len(message_summaries)
        avg_toxicity = total_toxicity / message_count if message_count > 0 else 0.0

        # Determine conversation trend
        if len(toxicity_scores) >= 3:
            recent_avg = sum(toxicity_scores[-3:]) / 3
            older_avg = sum(toxicity_scores[:-3]) / len(toxicity_scores[:-3])
            if recent_avg > older_avg + 0.1:
                from src.models.conversation import ConversationTrend
                trend = ConversationTrend.ESCALATING
            elif recent_avg < older_avg - 0.1:
                trend = ConversationTrend.DEESCALATING
            else:
                trend = ConversationTrend.NEUTRAL
        else:
            from src.models.conversation import ConversationTrend
            trend = ConversationTrend.NEUTRAL

        # Get or generate context embedding
        context_embedding = conversation.get("context_embedding", [])
        if not context_embedding and message_summaries:
            # Generate context embedding from recent messages
            texts = [msg.text for msg in message_summaries]
            context_embedding = await embedding_service.calculate_context_embedding(
                texts, strategy="sliding_window"
            )

        # Create context response
        context = ConversationContext(
            conversation_id=conversation_id,
            context_embedding=context_embedding,
            recent_messages=message_summaries,
            conversation_trend=trend,
            average_toxicity=avg_toxicity,
            message_count=message_count,
            participant_count=len(conversation.get("participants", []))
        )

        return context

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversation context: {e}")


@router.get("/", response_model=ConversationListResponse)
async def search_conversations(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    language: Optional[str] = Query(None, description="Filter by language"),
    moderation_level: Optional[ModerationLevel] = Query(None, description="Filter by moderation level"),
    status: Optional[ConversationStatus] = Query(None, description="Filter by status"),
    participant_id: Optional[str] = Query(None, description="Filter by participant ID"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Results per page"),
    db=Depends(get_database)
):
    """
    Search for conversations with various filters.

    Args:
        platform: Filter by platform
        language: Filter by language
        moderation_level: Filter by moderation level
        status: Filter by status
        participant_id: Filter by participant ID
        page: Page number (1-based)
        page_size: Results per page
        db: Database connection

    Returns:
        Paginated list of conversations
    """
    try:
        conversations_collection = db[COLLECTIONS["conversations"]]

        # Build filter
        filter_doc = {}
        if platform:
            filter_doc["metadata.platform"] = platform
        if language:
            filter_doc["metadata.language"] = language
        if moderation_level:
            filter_doc["metadata.moderation_level"] = moderation_level.value
        if status:
            filter_doc["status"] = status.value
        if participant_id:
            filter_doc["participants"] = participant_id

        # Get total count
        total_count = await conversations_collection.count_documents(filter_doc)

        # Get conversations with pagination
        offset = (page - 1) * page_size
        cursor = conversations_collection.find(filter_doc).sort("updated_at", -1).skip(offset).limit(page_size)

        conversations = []
        async for conv_doc in cursor:
            conversations.append(Conversation(**conv_doc))

        return ConversationListResponse(
            conversations=conversations,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=offset + page_size < total_count,
            has_prev=page > 1
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching conversations: {e}")


@router.post("/{conversation_id}/update-context")
async def update_conversation_context(
    conversation_id: str,
    db=Depends(get_database)
):
    """
    Update the context embedding for a conversation.

    This endpoint recalculates and updates the semantic embedding
    for the conversation based on recent messages.

    Args:
        conversation_id: Conversation ID
        db: Database connection

    Returns:
        Update confirmation
    """
    try:
        # Get recent messages for context
        messages_collection = db[COLLECTIONS["messages"]]
        recent_messages = await messages_collection.find(
            {"conversation_id": conversation_id},
            {"content": 1}
        ).sort("timestamp", -1).limit(10).to_list(None)

        if not recent_messages:
            return {
                "status": "no_messages",
                "message": "No messages found to generate context"
            }

        # Generate new context embedding
        texts = [msg["content"] for msg in recent_messages]
        context_embedding = await embedding_service.calculate_context_embedding(
            texts, strategy="weighted"
        )

        # Update conversation
        conversations_collection = db[COLLECTIONS["conversations"]]
        from datetime import datetime
        await conversations_collection.update_one(
            {"conversation_id": conversation_id},
            {
                "$set": {
                    "context_embedding": context_embedding,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        return {
            "status": "updated",
            "conversation_id": conversation_id,
            "embedding_dimension": len(context_embedding),
            "message_count": len(recent_messages)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating conversation context: {e}")


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db=Depends(get_database)
):
    """
    Delete a conversation and all associated messages.

    ⚠️ This is a destructive action. Consider archiving instead.

    Args:
        conversation_id: Conversation ID
        db: Database connection

    Returns:
        Deletion confirmation
    """
    try:
        conversations_collection = db[COLLECTIONS["conversations"]]
        messages_collection = db[COLLECTIONS["messages"]]

        # Delete conversation
        conv_result = await conversations_collection.delete_one(
            {"conversation_id": conversation_id}
        )

        if conv_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Delete all messages in conversation
        msg_result = await messages_collection.delete_many(
            {"conversation_id": conversation_id}
        )

        return {
            "status": "deleted",
            "conversation_id": conversation_id,
            "messages_deleted": msg_result.deleted_count
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {e}")