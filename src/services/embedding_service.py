"""Embedding service using sentence transformers for semantic analysis."""

import time
from typing import Dict, List, Optional, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from src.config.settings import settings
from src.models.moderation import ContextEmbedding


class EmbeddingService:
    """Service for generating and managing text embeddings."""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the embedding service.

        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name or settings.sentence_transformer_model
        self.model = None
        self._model_loaded = False
        self.embedding_dimension = settings.embedding_dimension

    def _load_model(self) -> None:
        """Load the sentence transformer model if not already loaded."""
        if not self._model_loaded:
            try:
                self.model = SentenceTransformer(self.model_name)
                self._model_loaded = True
                # Update embedding dimension based on actual model
                self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            except Exception as e:
                raise RuntimeError(f"Failed to load sentence transformer model '{self.model_name}': {e}")

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to generate embedding for

        Returns:
            List of float values representing the embedding
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Load model if needed
        if not self._model_loaded:
            self._load_model()

        try:
            start_time = time.time()
            # Generate embedding
            embedding = self.model.encode(text, convert_to_tensor=False)
            processing_time = int((time.time() - start_time) * 1000)

            # Convert to list of floats
            embedding_list = embedding.astype(np.float32).tolist()

            # Verify dimension
            if len(embedding_list) != self.embedding_dimension:
                raise ValueError(f"Embedding dimension mismatch: expected {self.embedding_dimension}, got {len(embedding_list)}")

            return embedding_list

        except Exception as e:
            raise RuntimeError(f"Error generating embedding: {e}")

    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Filter out empty texts
        valid_texts = [(i, text) for i, text in enumerate(texts) if text and text.strip()]
        if not valid_texts:
            return []

        # Load model if needed
        if not self._model_loaded:
            self._load_model()

        try:
            start_time = time.time()

            # Extract just the texts for batch processing
            text_list = [text for _, text in valid_texts]

            # Generate embeddings in batch
            embeddings = self.model.encode(
                text_list,
                batch_size=settings.batch_size,
                convert_to_tensor=False,
                show_progress_bar=False
            )

            processing_time = int((time.time() - start_time) * 1000)

            # Convert to list of lists and maintain original order
            result = [None] * len(texts)
            for (original_index, _), embedding in zip(valid_texts, embeddings):
                embedding_list = embedding.astype(np.float32).tolist()
                if len(embedding_list) != self.embedding_dimension:
                    raise ValueError(f"Embedding dimension mismatch for text at index {original_index}")
                result[original_index] = embedding_list

            return result

        except Exception as e:
            raise RuntimeError(f"Error generating batch embeddings: {e}")

    async def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score between -1 and 1
        """
        if len(embedding1) != len(embedding2):
            raise ValueError("Embedding dimensions must match")

        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1).reshape(1, -1)
            vec2 = np.array(embedding2).reshape(1, -1)

            # Calculate cosine similarity
            similarity = cosine_similarity(vec1, vec2)[0][0]
            return float(similarity)

        except Exception as e:
            raise RuntimeError(f"Error calculating similarity: {e}")

    async def calculate_context_embedding(
        self,
        messages: List[str],
        strategy: str = "sliding_window"
    ) -> List[float]:
        """
        Calculate context embedding from multiple messages.

        Args:
            messages: List of message texts
            strategy: Strategy for combining embeddings ("sliding_window", "mean", "weighted")

        Returns:
            Context embedding vector
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")

        # Generate embeddings for all messages
        embeddings = await self.generate_batch_embeddings(messages)
        valid_embeddings = [emb for emb in embeddings if emb is not None]

        if not valid_embeddings:
            raise ValueError("No valid embeddings generated from messages")

        try:
            # Convert to numpy array
            embedding_array = np.array(valid_embeddings)

            if strategy == "mean":
                # Simple average of all embeddings
                context_embedding = np.mean(embedding_array, axis=0)
            elif strategy == "weighted":
                # Weight recent messages more heavily
                weights = np.linspace(0.5, 1.0, len(valid_embeddings))
                context_embedding = np.average(embedding_array, axis=0, weights=weights)
            elif strategy == "sliding_window":
                # Focus on recent messages (last N)
                window_size = min(settings.context_window_size, len(valid_embeddings))
                recent_embeddings = embedding_array[-window_size:]
                context_embedding = np.mean(recent_embeddings, axis=0)
            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            return context_embedding.astype(np.float32).tolist()

        except Exception as e:
            raise RuntimeError(f"Error calculating context embedding: {e}")

    async def find_similar_messages(
        self,
        query_embedding: List[float],
        message_embeddings: List[Dict[str, any]],
        threshold: float = 0.7,
        max_results: int = 10
    ) -> List[Dict[str, any]]:
        """
        Find messages similar to the query embedding.

        Args:
            query_embedding: Query embedding vector
            message_embeddings: List of dictionaries with 'embedding' and 'metadata'
            threshold: Similarity threshold (0-1)
            max_results: Maximum number of results to return

        Returns:
            List of similar messages with similarity scores
        """
        if not query_embedding or not message_embeddings:
            return []

        try:
            similarities = []
            query_vec = np.array(query_embedding).reshape(1, -1)

            for item in message_embeddings:
                if 'embedding' not in item:
                    continue

                embedding = np.array(item['embedding']).reshape(1, -1)
                similarity = cosine_similarity(query_vec, embedding)[0][0]

                if similarity >= threshold:
                    similarities.append({
                        'similarity': float(similarity),
                        'metadata': item.get('metadata', {}),
                        'message_id': item.get('message_id')
                    })

            # Sort by similarity (descending) and limit results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:max_results]

        except Exception as e:
            raise RuntimeError(f"Error finding similar messages: {e}")

    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "is_loaded": self._model_loaded,
            "embedding_dimension": self.embedding_dimension,
            "max_sequence_length": getattr(self.model, 'max_seq_length', 512) if self._model_loaded else None,
            "supported_strategies": ["mean", "weighted", "sliding_window"]
        }

    async def health_check(self) -> Dict[str, any]:
        """
        Perform health check on the embedding service.

        Returns:
            Health status information
        """
        try:
            # Test with a simple example
            test_text = "This is a test message for embedding."
            embedding = await self.generate_embedding(test_text)

            return {
                "status": "healthy",
                "model_loaded": self._model_loaded,
                "model_name": self.model_name,
                "embedding_dimension": len(embedding),
                "test_embedding_sample": embedding[:3]  # First 3 dimensions as sample
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model_loaded": self._model_loaded,
                "model_name": self.model_name
            }


# Global embedding service instance
embedding_service = EmbeddingService()