"""Toxicity detection service using Detoxify library."""

import time
from typing import Dict, List, Optional, Tuple

try:
    import numpy as np
    from detoxify import Detoxify
    DETOXIFY_AVAILABLE = True
except ImportError:
    DETOXIFY_AVAILABLE = False
    # Create a mock numpy for basic functionality
    try:
        import numpy as np
    except ImportError:
        np = None

from src.config.settings import settings, TOXICITY_WEIGHTS
from src.models.message import ToxicityAnalysis, ToxicityPredictions


class ToxicityDetector:
    """Service for detecting toxicity in text using Detoxify models."""

    def __init__(self, model_name: Optional[str] = None, use_ensemble: bool = True):
        """
        Initialize the toxicity detector.

        Args:
            model_name: Name of the Detoxify model to use
            use_ensemble: Whether to use multiple models in ensemble mode
        """
        self.model_name = model_name or settings.detoxify_model
        self.use_ensemble = use_ensemble
        self.model = None
        self.models = {}  # For ensemble mode
        self._model_loaded = False

    def _load_model(self) -> None:
        """Load the Detoxify model(s) if not already loaded."""
        if not DETOXIFY_AVAILABLE:
            raise RuntimeError("Detoxify library is not installed. Install it with: pip install detoxify")
        if not self._model_loaded:
            try:
                if self.use_ensemble:
                    # Load multiple models for ensemble
                    model_variants = ['original', 'multilingual', 'unbiased']
                    for variant in model_variants:
                        try:
                            self.models[variant] = Detoxify(variant)
                            print(f"Loaded Detoxify model: {variant}")
                        except Exception as e:
                            print(f"Warning: Failed to load {variant} model: {e}")
                    
                    if not self.models:
                        # Fallback to single model if ensemble fails
                        print("Ensemble loading failed, falling back to single model")
                        self.model = Detoxify(self.model_name)
                        self.use_ensemble = False
                    else:
                        print(f"Successfully loaded {len(self.models)} models for ensemble")
                else:
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
            if self.use_ensemble and self.models:
                # Ensemble prediction: average predictions from multiple models
                all_predictions = []
                for model_name, model in self.models.items():
                    try:
                        preds = model.predict(text)
                        all_predictions.append(preds)
                    except Exception as e:
                        print(f"Warning: Prediction failed for {model_name}: {e}")
                
                # Average the predictions
                if all_predictions:
                    averaged_predictions = {}
                    for key in all_predictions[0].keys():
                        values = [p[key] for p in all_predictions if key in p]
                        averaged_predictions[key] = sum(values) / len(values) if values else 0.0
                    predictions = averaged_predictions
                else:
                    # Fallback to single model
                    predictions = self.model.predict(text) if self.model else {}
            else:
                # Single model prediction
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
        Calculate overall toxicity score using hybrid approach.
        
        Uses a combination of:
        1. Weighted average of significant categories
        2. Maximum score as a floor (don't underestimate clear toxicity)

        Args:
            predictions: Individual toxicity category predictions

        Returns:
            Overall toxicity score between 0 and 1
        """
        scores_with_weights = []
        max_score = 0.0
        
        for category, weight in TOXICITY_WEIGHTS.items():
            score = getattr(predictions, category)
            max_score = max(max_score, score)
            
            # Only include categories with meaningful scores (>5%) in weighted average
            # This prevents zero-weight categories from diluting the result
            if score > 0.05:
                scores_with_weights.append((score, weight))
        
        # Calculate weighted average of significant categories
        if scores_with_weights:
            weighted_sum = sum(score * weight for score, weight in scores_with_weights)
            total_weight = sum(weight for _, weight in scores_with_weights)
            weighted_avg = weighted_sum / total_weight
        else:
            weighted_avg = 0.0
        
        # Hybrid score: use the higher of weighted average or 80% of max score
        # This ensures that if ANY category is very high, the overall reflects it
        # But still respects the weighted average for balanced cases
        max_based_score = max_score * 0.8
        
        # Take the maximum to ensure we don't underestimate clear toxicity
        overall_score = max(weighted_avg, max_based_score)
        
        return min(1.0, overall_score)

    def _calculate_confidence(self, predictions: ToxicityPredictions) -> float:
        """
        Calculate confidence score based on prediction clarity.

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

        # Check if any major category is very high (clear toxicity)
        max_score = max(scores)
        high_confidence_categories = sum(1 for s in scores if s > 0.85)
        
        if np is not None:
            variance = np.var(scores)
            mean_score = np.mean(scores)
        else:
            # Fallback calculation without numpy
            mean_score = sum(scores) / len(scores)
            variance = sum((x - mean_score) ** 2 for x in scores) / len(scores)

        # HIGH CONFIDENCE CASES
        # If multiple categories are very high, it's clearly toxic regardless of variance
        if high_confidence_categories >= 2:
            return 0.9
        
        # If any single category is extremely high (>95%), high confidence
        if max_score > 0.95:
            return 0.85
        
        # If all scores are very low, high confidence in non-toxicity
        if mean_score < 0.1 and max_score < 0.15:
            return 0.9
        
        # If mean is very high with low variance, high confidence
        if mean_score > 0.8:
            return 0.8 + (0.2 * (1 - min(variance, 1.0)))
        
        # MODERATE CONFIDENCE CASES
        # If mean is low but one category is somewhat high, moderate confidence
        if mean_score < 0.4 and max_score > 0.6:
            return 0.7
        
        # Mid-range scores with high variance = lower confidence
        if variance > 0.1:
            return max(0.5, 0.7 - variance)
        
        # Default: moderate confidence
        return 0.6

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