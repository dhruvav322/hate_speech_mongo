"""Toxicity detection service using Detoxify library."""

import time
from typing import Dict, List, Optional, Tuple

import numpy as np
from detoxify import Detoxify

from src.config.settings import settings, TOXICITY_WEIGHTS
from src.models.message import ToxicityAnalysis, ToxicityPredictions


class ToxicityDetector:
    """Service for detecting toxicity in text using Detoxify models."""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the toxicity detector.

        Args:
            model_name: Name of the Detoxify model to use
        """
        self.model_name = model_name or settings.detoxify_model
        self.model = None
        self._model_loaded = False

    def _load_model(self) -> None:
        """Load the Detoxify model if not already loaded."""
        if not self._model_loaded:
            try:
                self.model = Detoxify(self.model_name)
                self._model_loaded = True
            except Exception as e:
                raise RuntimeError(f"Failed to load Detoxify model '{self.model_name}': {e}")

    async def analyze_toxicity(self, text: str) -> ToxicityAnalysis:
        """
        Analyze text for toxicity.

        Args:
            text: Text to analyze

        Returns:
            ToxicityAnalysis object with detailed results
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        start_time = time.time()

        # Load model if needed
        if not self._model_loaded:
            self._load_model()

        try:
            # Get predictions from Detoxify
            predictions = self.model.predict(text)

            # Convert to our format and ensure all required categories exist
            toxicity_predictions = self._normalize_predictions(predictions)

            # Calculate weighted overall score
            overall_score = self._calculate_overall_score(toxicity_predictions)

            # Calculate confidence based on prediction variance
            confidence = self._calculate_confidence(toxicity_predictions)

            processing_time = int((time.time() - start_time) * 1000)

            return ToxicityAnalysis(
                overall_score=overall_score,
                predictions=toxicity_predictions,
                confidence=confidence,
                processing_time_ms=processing_time
            )

        except Exception as e:
            raise RuntimeError(f"Error during toxicity analysis: {e}")

    async def analyze_batch(self, texts: List[str]) -> List[ToxicityAnalysis]:
        """
        Analyze multiple texts for toxicity.

        Args:
            texts: List of texts to analyze

        Returns:
            List of ToxicityAnalysis objects
        """
        if not texts:
            return []

        # Load model if needed
        if not self._model_loaded:
            self._load_model()

        results = []
        start_time = time.time()

        try:
            # Process in batches for efficiency
            batch_size = settings.batch_size
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]

                # Get predictions for batch
                batch_predictions = self.model.predict(batch_texts)

                # Process each text in the batch
                for j, text in enumerate(batch_texts):
                    if not text or not text.strip():
                        # Skip empty texts but maintain order
                        results.append(None)
                        continue

                    # Extract predictions for this text
                    predictions = {
                        key: batch_predictions[key][j]
                        for key in batch_predictions
                    }

                    toxicity_predictions = self._normalize_predictions(predictions)
                    overall_score = self._calculate_overall_score(toxicity_predictions)
                    confidence = self._calculate_confidence(toxicity_predictions)

                    results.append(ToxicityAnalysis(
                        overall_score=overall_score,
                        predictions=toxicity_predictions,
                        confidence=confidence,
                        processing_time_ms=0  # Will be calculated for the whole batch
                    ))

            # Calculate average processing time
            total_time = int((time.time() - start_time) * 1000)
            avg_time = total_time // len(texts)

            # Update processing times
            for result in results:
                if result is not None:
                    result.processing_time_ms = avg_time

            return results

        except Exception as e:
            raise RuntimeError(f"Error during batch toxicity analysis: {e}")

    def _normalize_predictions(self, predictions: Dict[str, float]) -> ToxicityPredictions:
        """
        Normalize Detoxify predictions to our expected format.

        Args:
            predictions: Raw predictions from Detoxify

        Returns:
            Normalized ToxicityPredictions object
        """
        # Ensure all required categories exist, defaulting to 0.0 if missing
        normalized = {}
        required_categories = [
            'toxic', 'severe_toxic', 'obscene',
            'threat', 'insult', 'identity_hate'
        ]

        for category in required_categories:
            # Detoxify might use different naming conventions
            value = 0.0
            for key in predictions:
                if category.lower() in key.lower():
                    value = float(predictions[key])
                    break
            normalized[category] = max(0.0, min(1.0, value))  # Clamp between 0 and 1

        return ToxicityPredictions(**normalized)

    def _calculate_overall_score(self, predictions: ToxicityPredictions) -> float:
        """
        Calculate weighted overall toxicity score.

        Args:
            predictions: Individual toxicity category predictions

        Returns:
            Weighted overall score
        """
        overall = 0.0
        total_weight = 0.0

        for category, weight in TOXICITY_WEIGHTS.items():
            score = getattr(predictions, category)
            overall += score * weight
            total_weight += weight

        return min(1.0, overall / total_weight) if total_weight > 0 else 0.0

    def _calculate_confidence(self, predictions: ToxicityPredictions) -> float:
        """
        Calculate confidence score based on prediction variance.

        Args:
            predictions: Individual toxicity category predictions

        Returns:
            Confidence score between 0 and 1
        """
        scores = [
            predictions.toxic,
            predictions.severe_toxic,
            predictions.obscene,
            predictions.threat,
            predictions.insult,
            predictions.identity_hate
        ]

        # Higher confidence when predictions are more decisive (either high or low)
        variance = np.var(scores)
        mean_score = np.mean(scores)

        # Adjust confidence based on how clear-cut the predictions are
        if mean_score < 0.1:
            # Very low scores - high confidence in non-toxicity
            return 0.9
        elif mean_score > 0.8:
            # Very high scores - high confidence in toxicity
            return 0.8 + (0.2 * (1 - variance))
        else:
            # Mid-range scores - lower confidence
            return max(0.3, 0.7 - variance)

    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "is_loaded": self._model_loaded,
            "supported_languages": ["en"],  # Detoxify is primarily trained on English
            "categories": [
                "toxic", "severe_toxic", "obscene",
                "threat", "insult", "identity_hate"
            ],
            "weights": TOXICITY_WEIGHTS
        }

    async def health_check(self) -> Dict[str, any]:
        """
        Perform health check on the toxicity detector.

        Returns:
            Health status information
        """
        try:
            # Test with a simple example
            test_text = "This is a friendly test message."
            result = await self.analyze_toxicity(test_text)

            return {
                "status": "healthy",
                "model_loaded": self._model_loaded,
                "model_name": self.model_name,
                "test_result": {
                    "overall_score": result.overall_score,
                    "processing_time_ms": result.processing_time_ms
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model_loaded": self._model_loaded,
                "model_name": self.model_name
            }


# Global toxicity detector instance
toxicity_detector = ToxicityDetector()