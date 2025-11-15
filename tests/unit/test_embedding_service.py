"""Unit tests for embedding service."""

import numpy as np
import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.services.embedding_service import EmbeddingService


class TestEmbeddingService:
    """Test cases for EmbeddingService class."""

    @pytest.fixture
    def service(self):
        """
        Create a new EmbeddingService instance.
        
        Returns:
            EmbeddingService: A fresh EmbeddingService instance with default configuration.
        """
        return EmbeddingService()

    @pytest.fixture
    def mock_embedding(self):
        """
        Provide a 384-dimensional mock embedding vector.
        
        Returns:
            embedding (list[float]): A list of 384 floats (dtype float32) with values in [0, 1).
        """
        return np.random.rand(384).astype(np.float32).tolist()

    @pytest.mark.unit
    def test_initialization(self, service):
        """Test service initialization."""
        assert service.model_name == "all-MiniLM-L6-v2"
        assert service.model is None
        assert service._model_loaded is False
        assert service.embedding_dimension == 384

    @pytest.mark.unit
    def test_initialization_with_custom_model(self):
        """Test service initialization with custom model."""
        service = EmbeddingService(model_name="custom-model")
        assert service.model_name == "custom-model"

    @pytest.mark.unit
    @patch('src.services.embedding_service.SentenceTransformer')
    async def test_load_model(self, mock_transformer_class, service):
        """Test model loading."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_transformer_class.return_value = mock_model

        service._load_model()

        mock_transformer_class.assert_called_once_with("all-MiniLM-L6-v2")
        assert service.model is mock_model
        assert service._model_loaded is True
        assert service.embedding_dimension == 768

    @pytest.mark.unit
    @patch('src.services.embedding_service.SentenceTransformer')
    async def test_load_model_error(self, mock_transformer_class, service):
        """Test model loading error handling."""
        mock_transformer_class.side_effect = Exception("Model loading failed")

        with pytest.raises(RuntimeError, match="Failed to load sentence transformer model"):
            service._load_model()

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.embedding_service.SentenceTransformer')
    async def test_generate_embedding_empty_text(self, mock_transformer_class, service):
        """Test embedding generation with empty text."""
        mock_model = Mock()
        mock_transformer_class.return_value = mock_model

        with pytest.raises(ValueError, match="Text cannot be empty"):
            await service.generate_embedding("")

        with pytest.raises(ValueError, match="Text cannot be empty"):
            await service.generate_embedding("   ")

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.embedding_service.SentenceTransformer')
    async def test_generate_embedding_success(self, mock_transformer_class, service, mock_embedding):
        """Test successful embedding generation."""
        mock_model = Mock()
        mock_model.encode.return_value = np.array(mock_embedding)
        mock_transformer_class.return_value = mock_model

        result = await service.generate_embedding("Hello world")

        assert isinstance(result, list)
        assert len(result) == 384
        assert all(isinstance(x, float) for x in result)
        mock_model.encode.assert_called_once_with("Hello world", convert_to_tensor=False)

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.embedding_service.SentenceTransformer')
    async def test_generate_embedding_dimension_mismatch(self, mock_transformer_class, service):
        """Test embedding generation with dimension mismatch."""
        mock_model = Mock()
        # Return wrong dimension
        mock_model.encode.return_value = np.random.rand(256)  # Wrong dimension
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer_class.return_value = mock_model

        with pytest.raises(ValueError, match="Embedding dimension mismatch"):
            await service.generate_embedding("Hello world")

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.embedding_service.SentenceTransformer')
    async def test_generate_embedding_error(self, mock_transformer_class, service):
        """Test embedding generation error handling."""
        mock_model = Mock()
        mock_model.encode.side_effect = Exception("Encoding failed")
        mock_transformer_class.return_value = mock_model

        with pytest.raises(RuntimeError, match="Error generating embedding"):
            await service.generate_embedding("Hello world")

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.embedding_service.SentenceTransformer')
    async def test_generate_batch_embeddings_empty_list(self, mock_transformer_class, service):
        """Test batch embedding generation with empty list."""
        result = await service.generate_batch_embeddings([])
        assert result == []

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.embedding_service.SentenceTransformer')
    async def test_generate_batch_embeddings_success(self, mock_transformer_class, service, mock_embedding):
        """Test successful batch embedding generation."""
        mock_model = Mock()
        # Return embeddings for batch
        batch_embeddings = np.random.rand(2, 384).astype(np.float32)
        mock_model.encode.return_value = batch_embeddings
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer_class.return_value = mock_model

        texts = ["Hello world", "Goodbye world"]
        results = await service.generate_batch_embeddings(texts)

        assert len(results) == 2
        for result in results:
            assert isinstance(result, list)
            assert len(result) == 384
            assert all(isinstance(x, float) for x in result)

        mock_model.encode.assert_called_once_with(
            texts,
            batch_size=32,
            convert_to_tensor=False,
            show_progress_bar=False
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.embedding_service.SentenceTransformer')
    async def test_generate_batch_embeddings_with_empty_texts(self, mock_transformer_class, service, mock_embedding):
        """Test batch embedding generation with empty texts mixed in."""
        mock_model = Mock()
        batch_embeddings = np.random.rand(1, 384).astype(np.float32)
        mock_model.encode.return_value = batch_embeddings
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer_class.return_value = mock_model

        texts = ["Hello world", "", "Test message"]
        results = await service.generate_batch_embeddings(texts)

        assert len(results) == 3
        # Empty text should result in None
        assert results[1] is None
        # Valid texts should have results
        assert results[0] is not None
        assert results[2] is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_similarity_success(self, service, mock_embedding):
        """Test successful similarity calculation."""
        embedding1 = mock_embedding
        embedding2 = mock_embedding  # Same vectors should have high similarity

        result = await service.calculate_similarity(embedding1, embedding2)

        assert isinstance(result, float)
        assert result >= -1.0 and result <= 1.0
        # Same vectors should have similarity close to 1.0
        assert abs(result - 1.0) < 0.001

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_similarity_dimension_mismatch(self, service, mock_embedding):
        """Test similarity calculation with dimension mismatch."""
        embedding1 = mock_embedding
        embedding2 = mock_embedding[:100]  # Wrong dimension

        with pytest.raises(ValueError, match="Embedding dimensions must match"):
            await service.calculate_similarity(embedding1, embedding2)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_similarity_error(self, service, mock_embedding):
        """Test similarity calculation error handling."""
        embedding1 = mock_embedding
        embedding2 = None

        with pytest.raises((TypeError, AttributeError, ValueError)):
            await service.calculate_similarity(embedding1, embedding2)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_context_embedding_mean_strategy(self, service, mock_embedding):
        """Test context embedding calculation with mean strategy."""
        messages = ["Hello world", "How are you?", "Goodbye"]

        with patch.object(service, 'generate_batch_embeddings') as mock_generate:
            mock_generate.return_value = [mock_embedding[:384], mock_embedding[:384], mock_embedding[:384]]

            result = await service.calculate_context_embedding(messages, strategy="mean")

            assert isinstance(result, list)
            assert len(result) == 384
            assert all(isinstance(x, float) for x in result)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_context_embedding_weighted_strategy(self, service, mock_embedding):
        """Test context embedding calculation with weighted strategy."""
        messages = ["Message 1", "Message 2", "Message 3"]

        with patch.object(service, 'generate_batch_embeddings') as mock_generate:
            embeddings = [mock_embedding[:384], mock_embedding[:384], mock_embedding[:384]]
            mock_generate.return_value = embeddings

            result = await service.calculate_context_embedding(messages, strategy="weighted")

            assert isinstance(result, list)
            assert len(result) == 384

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_context_embedding_sliding_window_strategy(self, service, mock_embedding):
        """Test context embedding calculation with sliding window strategy."""
        messages = ["Message 1", "Message 2", "Message 3", "Message 4", "Message 5"]

        with patch.object(service, 'generate_batch_embeddings') as mock_generate:
            embeddings = [mock_embedding[:384]] * 5
            mock_generate.return_value = embeddings

            result = await service.calculate_context_embedding(messages, strategy="sliding_window")

            assert isinstance(result, list)
            assert len(result) == 384

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_context_embedding_empty_messages(self, service):
        """Test context embedding calculation with empty messages list."""
        with pytest.raises(ValueError, match="Messages list cannot be empty"):
            await service.calculate_context_embedding([])

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_context_embedding_invalid_strategy(self, service):
        """Test context embedding calculation with invalid strategy."""
        messages = ["Test message"]

        with pytest.raises(ValueError, match="Unknown strategy"):
            await service.calculate_context_embedding(messages, strategy="invalid")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_find_similar_messages_success(self, service, mock_embedding):
        """Test finding similar messages."""
        query_embedding = mock_embedding[:384]
        message_embeddings = [
            {
                "embedding": mock_embedding[:384],
                "metadata": {"text": "Similar message"},
                "message_id": "msg_001"
            },
            {
                "embedding": [0.0] * 384,  # Different embedding
                "metadata": {"text": "Different message"},
                "message_id": "msg_002"
            }
        ]

        result = await service.find_similar_messages(
            query_embedding,
            message_embeddings,
            threshold=0.7
        )

        assert isinstance(result, list)
        # First message should be similar (same embedding), second should not
        assert len(result) >= 1
        assert result[0]["message_id"] == "msg_001"
        assert result[0]["similarity"] >= 0.7

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_find_similar_messages_no_results(self, service, mock_embedding):
        """Test finding similar messages with no results."""
        query_embedding = mock_embedding[:384]
        message_embeddings = [
            {
                "embedding": [0.0] * 384,  # Different embedding
                "metadata": {"text": "Different message"},
                "message_id": "msg_001"
            }
        ]

        result = await service.find_similar_messages(
            query_embedding,
            message_embeddings,
            threshold=0.7
        )

        assert isinstance(result, list)
        # Zero vector should have low similarity with random embedding
        assert len(result) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_find_similar_messages_empty_inputs(self, service):
        """Test finding similar messages with empty inputs."""
        result1 = await service.find_similar_messages([], [])
        result2 = await service.find_similar_messages([1.0], [])

        assert result1 == []
        assert result2 == []

    @pytest.mark.unit
    def test_get_model_info(self, service):
        """Test getting model information."""
        info = service.get_model_info()

        assert isinstance(info, dict)
        assert "model_name" in info
        assert "is_loaded" in info
        assert "embedding_dimension" in info
        assert "max_sequence_length" in info
        assert "supported_strategies" in info

        assert info["model_name"] == "all-MiniLM-L6-v2"
        assert info["is_loaded"] is False
        assert info["embedding_dimension"] == 384
        assert "mean" in info["supported_strategies"]
        assert "weighted" in info["supported_strategies"]
        assert "sliding_window" in info["supported_strategies"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_check_success(self, service, mock_embedding):
        """Test successful health check."""
        with patch.object(service, 'generate_embedding') as mock_generate:
            mock_generate.return_value = mock_embedding[:384]

            result = await service.health_check()

            assert result["status"] == "healthy"
            assert "model_loaded" in result
            assert "model_name" in result
            assert "embedding_dimension" in result
            assert "test_embedding_sample" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_check_failure(self, service):
        """
        Verifies that health_check reports an unhealthy status when embedding generation fails.
        
        Patches the service's generate_embedding to raise an exception and asserts the returned health report has status "unhealthy" and includes the keys "error", "model_loaded", and "model_name".
        
        Parameters:
            service (EmbeddingService): Test fixture providing an EmbeddingService instance.
        """
        with patch.object(service, 'generate_embedding') as mock_generate:
            mock_generate.side_effect = Exception("Health check failed")

            result = await service.health_check()

            assert result["status"] == "unhealthy"
            assert "error" in result
            assert "model_loaded" in result
            assert "model_name" in result