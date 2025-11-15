"""Unit tests for toxicity detection service."""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.services.toxicity_detector import ToxicityDetector
from src.models.message import ToxicityAnalysis, ToxicityPredictions


class TestToxicityDetector:
    """Test cases for ToxicityDetector class."""

    @pytest.fixture
    def detector(self):
        """Create a toxicity detector instance."""
        return ToxicityDetector()

    @pytest.fixture
    def mock_detoxify_predictions(self):
        """Mock detoxify predictions."""
        return {
            'toxic': 0.1,
            'severe_toxic': 0.0,
            'obscene': 0.0,
            'threat': 0.0,
            'insult': 0.05,
            'identity_hate': 0.0
        }

    @pytest.mark.unit
    def test_initialization(self, detector):
        """Test detector initialization."""
        assert detector.model_name == "original"
        assert detector.model is None
        assert detector._model_loaded is False

    @pytest.mark.unit
    def test_initialization_with_custom_model(self):
        """Test detector initialization with custom model."""
        detector = ToxicityDetector(model_name="unbiased")
        assert detector.model_name == "unbiased"

    @pytest.mark.unit
    @patch('src.services.toxicity_detector.Detoxify')
    async def test_load_model(self, mock_detoxify_class, detector):
        """Test model loading."""
        mock_model = Mock()
        mock_detoxify_class.return_value = mock_model

        detector._load_model()

        mock_detoxify_class.assert_called_once_with("original")
        assert detector.model is mock_model
        assert detector._model_loaded is True

    @pytest.mark.unit
    @patch('src.services.toxicity_detector.Detoxify')
    async def test_load_model_error(self, mock_detoxify_class, detector):
        """Test model loading error handling."""
        mock_detoxify_class.side_effect = Exception("Model loading failed")

        with pytest.raises(RuntimeError, match="Failed to load Detoxify model"):
            detector._load_model()

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.toxicity_detector.Detoxify')
    async def test_analyze_toxicity_empty_text(self, mock_detoxify_class, detector):
        """Test toxicity analysis with empty text."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await detector.analyze_toxicity("")

        with pytest.raises(ValueError, match="Text cannot be empty"):
            await detector.analyze_toxicity("   ")

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.toxicity_detector.Detoxify')
    async def test_analyze_toxicity_success(self, mock_detoxify_class, detector, mock_detoxify_predictions):
        """Test successful toxicity analysis."""
        mock_model = Mock()
        mock_model.predict.return_value = mock_detoxify_predictions
        mock_detoxify_class.return_value = mock_model

        result = await detector.analyze_toxicity("Hello world")

        assert isinstance(result, ToxicityAnalysis)
        assert result.overall_score >= 0.0 and result.overall_score <= 1.0
        assert result.confidence >= 0.0 and result.confidence <= 1.0
        assert result.processing_time_ms > 0
        assert isinstance(result.predictions, ToxicityPredictions)
        assert result.predictions.toxic == 0.1
        assert result.predictions.severe_toxic == 0.0

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.toxicity_detector.Detoxify')
    async def test_analyze_toxicity_with_missing_categories(self, mock_detoxify_class, detector):
        """Test toxicity analysis with missing prediction categories."""
        mock_model = Mock()
        # Return only some categories
        mock_model.predict.return_value = {
            'toxic': 0.2,
            'insult': 0.1
        }
        mock_detoxify_class.return_value = mock_model

        result = await detector.analyze_toxicity("Test message")

        assert isinstance(result, ToxicityAnalysis)
        # Missing categories should default to 0.0
        assert result.predictions.severe_toxic == 0.0
        assert result.predictions.obscene == 0.0
        assert result.predictions.threat == 0.0
        assert result.predictions.identity_hate == 0.0

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.toxicity_detector.Detoxify')
    async def test_analyze_toxicity_error(self, mock_detoxify_class, detector):
        """Test toxicity analysis error handling."""
        mock_model = Mock()
        mock_model.predict.side_effect = Exception("Prediction failed")
        mock_detoxify_class.return_value = mock_model

        with pytest.raises(RuntimeError, match="Error during toxicity analysis"):
            await detector.analyze_toxicity("Test message")

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.toxicity_detector.Detoxify')
    async def test_analyze_batch_empty_list(self, mock_detoxify_class, detector):
        """Test batch analysis with empty list."""
        result = await detector.analyze_batch([])
        assert result == []

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.toxicity_detector.Detoxify')
    async def test_analyze_batch_success(self, mock_detoxify_class, detector, mock_detoxify_predictions):
        """Test successful batch analysis."""
        mock_model = Mock()
        # Return predictions for batch
        mock_model.predict.return_value = {
            'toxic': [0.1, 0.3],
            'severe_toxic': [0.0, 0.0],
            'obscene': [0.0, 0.0],
            'threat': [0.0, 0.0],
            'insult': [0.05, 0.1],
            'identity_hate': [0.0, 0.0]
        }
        mock_detoxify_class.return_value = mock_model

        texts = ["Hello world", "You are stupid"]
        results = await detector.analyze_batch(texts)

        assert len(results) == 2
        for result in results:
            assert isinstance(result, ToxicityAnalysis)
            assert result.processing_time_ms >= 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.toxicity_detector.Detoxify')
    async def test_analyze_batch_with_empty_texts(self, mock_detoxify_class, detector, mock_detoxify_predictions):
        """Test batch analysis with empty texts mixed in."""
        mock_model = Mock()
        mock_model.predict.return_value = {
            'toxic': [0.1],
            'severe_toxic': [0.0],
            'obscene': [0.0],
            'threat': [0.0],
            'insult': [0.05],
            'identity_hate': [0.0]
        }
        mock_detoxify_class.return_value = mock_model

        texts = ["Hello world", "", "Test message"]
        results = await detector.analyze_batch(texts)

        assert len(results) == 3
        # Empty text should result in None
        assert results[1] is None
        # Valid texts should have results
        assert results[0] is not None
        assert results[2] is not None

    @pytest.mark.unit
    def test_normalize_predictions(self, detector, mock_detoxify_predictions):
        """Test prediction normalization."""
        result = detector._normalize_predictions(mock_detoxify_predictions)

        assert isinstance(result, ToxicityPredictions)
        assert result.toxic == 0.1
        assert result.severe_toxic == 0.0
        assert result.obscene == 0.0
        assert result.threat == 0.0
        assert result.insult == 0.05
        assert result.identity_hate == 0.0

    @pytest.mark.unit
    def test_normalize_predictions_missing_categories(self, detector):
        """Test prediction normalization with missing categories."""
        predictions = {
            'toxic': 0.2,
            'insult': 0.1
        }

        result = detector._normalize_predictions(predictions)

        assert isinstance(result, ToxicityPredictions)
        assert result.toxic == 0.2
        assert result.insult == 0.1
        # Missing categories should default to 0.0
        assert result.severe_toxic == 0.0
        assert result.obscene == 0.0
        assert result.threat == 0.0
        assert result.identity_hate == 0.0

    @pytest.mark.unit
    def test_normalize_predictions_with_different_naming(self, detector):
        """Test prediction normalization with different naming conventions."""
        predictions = {
            'toxicity': 0.3,  # Different naming
            'severe_toxicity': 0.1,
            'insults': 0.2  # Plural form
        }

        result = detector._normalize_predictions(predictions)

        assert isinstance(result, ToxicityPredictions)
        assert result.toxic == 0.3
        assert result.severe_toxic == 0.1
        assert result.insult == 0.2

    @pytest.mark.unit
    def test_normalize_predictions_clamping(self, detector):
        """Test prediction value clamping."""
        predictions = {
            'toxic': 1.5,  # Above 1.0
            'severe_toxic': -0.5,  # Below 0.0
            'obscene': 0.5
        }

        result = detector._normalize_predictions(predictions)

        assert isinstance(result, ToxicityPredictions)
        # Values should be clamped between 0 and 1
        assert result.toxic == 1.0
        assert result.severe_toxic == 0.0
        assert result.obscene == 0.5

    @pytest.mark.unit
    def test_calculate_overall_score(self, detector):
        """Test overall score calculation."""
        predictions = ToxicityPredictions(
            toxic=0.5,
            severe_toxic=0.1,
            obscene=0.2,
            threat=0.0,
            insult=0.3,
            identity_hate=0.0
        )

        result = detector._calculate_overall_score(predictions)

        assert isinstance(result, float)
        assert result >= 0.0 and result <= 1.0
        # Severe toxic should have higher weight
        assert result > 0.3  # Should be higher than simple average

    @pytest.mark.unit
    def test_calculate_confidence_low_scores(self, detector):
        """Test confidence calculation for low toxicity scores."""
        predictions = ToxicityPredictions(
            toxic=0.01,
            severe_toxic=0.0,
            obscene=0.0,
            threat=0.0,
            insult=0.02,
            identity_hate=0.0
        )

        result = detector._calculate_confidence(predictions)

        assert isinstance(result, float)
        assert result >= 0.0 and result <= 1.0
        # Low scores should have high confidence
        assert result > 0.7

    @pytest.mark.unit
    def test_calculate_confidence_high_scores(self, detector):
        """Test confidence calculation for high toxicity scores."""
        predictions = ToxicityPredictions(
            toxic=0.9,
            severe_toxic=0.5,
            obscene=0.7,
            threat=0.3,
            insult=0.8,
            identity_hate=0.6
        )

        result = detector._calculate_confidence(predictions)

        assert isinstance(result, float)
        assert result >= 0.0 and result <= 1.0
        # High scores should have good confidence
        assert result > 0.7

    @pytest.mark.unit
    def test_calculate_confidence_mixed_scores(self, detector):
        """Test confidence calculation for mixed toxicity scores."""
        predictions = ToxicityPredictions(
            toxic=0.5,
            severe_toxic=0.1,
            obscene=0.3,
            threat=0.2,
            insult=0.4,
            identity_hate=0.1
        )

        result = detector._calculate_confidence(predictions)

        assert isinstance(result, float)
        assert result >= 0.0 and result <= 1.0
        # Mixed scores should have lower confidence
        assert result < 0.7

    @pytest.mark.unit
    def test_get_model_info(self, detector):
        """Test getting model information."""
        info = detector.get_model_info()

        assert isinstance(info, dict)
        assert "model_name" in info
        assert "is_loaded" in info
        assert "supported_languages" in info
        assert "categories" in info
        assert "weights" in info

        assert info["model_name"] == "original"
        assert info["is_loaded"] is False
        assert "en" in info["supported_languages"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_check_success(self, detector, mock_detoxify_predictions):
        """Test successful health check."""
        with patch.object(detector, 'analyze_toxicity') as mock_analyze:
            mock_analyze.return_value = ToxicityAnalysis(
                overall_score=0.1,
                predictions=ToxicityPredictions(
                    toxic=0.1, severe_toxic=0.0, obscene=0.0,
                    threat=0.0, insult=0.0, identity_hate=0.0
                ),
                confidence=0.9,
                processing_time_ms=50
            )

            result = await detector.health_check()

            assert result["status"] == "healthy"
            assert "model_loaded" in result
            assert "model_name" in result
            assert "test_result" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_check_failure(self, detector):
        """Test health check failure."""
        with patch.object(detector, 'analyze_toxicity') as mock_analyze:
            mock_analyze.side_effect = Exception("Health check failed")

            result = await detector.health_check()

            assert result["status"] == "unhealthy"
            assert "error" in result
            assert "model_loaded" in result
            assert "model_name" in result