#!/usr/bin/env python3
"""
Advanced ML Models for Hate Speech Detection
Industry-grade models with ensemble predictions and real-time performance monitoring
"""

import os
import logging
import time
import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

# ML Imports
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    from detoxify import Detoxify
    from sentence_transformers import SentenceTransformer
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    logging.warning(f"ML libraries not available: {e}")

logger = logging.getLogger(__name__)

@dataclass
class ModelPrediction:
    model_name: str
    toxicity_score: float
    confidence: float
    prediction_time_ms: float
    raw_scores: Dict[str, float]
    model_type: str
    version: str

@dataclass
class EnsembleResult:
    final_score: float
    confidence: float
    individual_predictions: List[ModelPrediction]
    consensus: float
    processing_time_ms: float
    model_count: int

class AdvancedToxicityModels:
    def __init__(self):
        self.models = {}
        self.model_load_times = {}
        self.prediction_cache = {}
        self.performance_metrics = {
            "total_predictions": 0,
            "average_prediction_time": 0.0,
            "model_usage": {},
            "cache_hits": 0,
            "cache_misses": 0
        }
        self.start_time = time.time()

    async def load_all_models(self):
        """Load all available models with fallback support"""
        if not ML_AVAILABLE:
            logger.error("ML libraries not available")
            return

        logger.info("Loading advanced ML models...")

        # Load Detoxify models
        await self._load_detoxify_models()

        # Load Hugging Face models
        await self._load_huggingface_models()

        # Load sentence embeddings model
        await self._load_sentence_transformer()

        # Initialize rule-based model as fallback
        self._load_rule_based_model()

        logger.info(f"Loaded {len(self.models)} models successfully")

    async def _load_detoxify_models(self):
        """Load multiple Detoxify models"""
        try:
            models_to_load = [
                ("detoxify_original", "original"),
                ("detoxify_multilingual", "multilingual"),
                ("detoxify_unbiased", "unbiased-small")
            ]

            for name, model_type in models_to_load:
                try:
                    start_time = time.time()
                    model = Detoxify(model_type)
                    load_time = (time.time() - start_time) * 1000
                    self.models[name] = {
                        "model": model,
                        "type": "detoxify",
                        "version": model_type,
                        "load_time_ms": load_time
                    }
                    logger.info(f"Loaded {name} in {load_time:.2f}ms")
                except Exception as e:
                    logger.warning(f"Failed to load {name}: {e}")
        except Exception as e:
            logger.error(f"Detoxify loading failed: {e}")

    async def _load_huggingface_models(self):
        """Load Hugging Face toxicity models"""
        try:
            huggingface_models = [
                ("toxicbert", "unitary/toxic-bert"),
                ("hatespeech_offensive", "Hate-speech-CNERG/dehate-finetuned-hatespeech-offensive"),
                ("roberta_toxicity", "FacebookAI/roberta-base")
            ]

            for name, model_path in huggingface_models:
                try:
                    start_time = time.time()

                    # Load tokenizer and model
                    tokenizer = AutoTokenizer.from_pretrained(model_path)
                    model = AutoModelForSequenceClassification.from_pretrained(model_path)

                    # Create pipeline
                    pipe = pipeline(
                        "text-classification",
                        model=model,
                        tokenizer=tokenizer,
                        return_all_scores=True
                    )

                    load_time = (time.time() - start_time) * 1000
                    self.models[name] = {
                        "pipeline": pipe,
                        "type": "huggingface",
                        "version": model_path,
                        "load_time_ms": load_time
                    }
                    logger.info(f"Loaded {name} in {load_time:.2f}ms")
                except Exception as e:
                    logger.warning(f"Failed to load {name}: {e}")
        except Exception as e:
            logger.error(f"HuggingFace loading failed: {e}")

    async def _load_sentence_transformer(self):
        """Load sentence transformer for semantic analysis"""
        try:
            start_time = time.time()
            model = SentenceTransformer('all-MiniLM-L6-v2')
            load_time = (time.time() - start_time) * 1000
            self.models["sentence_transformer"] = {
                "model": model,
                "type": "sentence_transformer",
                "version": "all-MiniLM-L6-v2",
                "load_time_ms": load_time
            }
            logger.info(f"Loaded sentence transformer in {load_time:.2f}ms")
        except Exception as e:
            logger.warning(f"Sentence transformer loading failed: {e}")

    def _load_rule_based_model(self):
        """Load rule-based model as fallback"""
        toxic_keywords = {
            'severe': ['kill', 'die', 'murder', 'violence', 'harm', 'hurt', 'destroy'],
            'insult': ['stupid', 'idiot', 'dumb', 'moron', 'fool', 'loser', 'jerk'],
            'hate': ['hate', 'despise', 'loathe', 'disgusting', 'pathetic'],
            'discrimination': ['race', 'gender', 'religion', 'sexual', 'orientation'],
            'threat': ['threat', 'kill', 'hurt', 'harm', 'attack', 'violence']
        }

        self.models["rule_based"] = {
            "keywords": toxic_keywords,
            "type": "rule_based",
            "version": "1.0",
            "load_time_ms": 0
        }
        logger.info("Loaded rule-based model")

    async def predict_toxicity_ensemble(self, text: str, use_cache: bool = True) -> EnsembleResult:
        """Make ensemble prediction using all available models"""
        if not ML_AVAILABLE:
            return self._fallback_prediction(text)

        start_time = time.time()

        # Check cache
        if use_cache:
            cached_result = self._get_cached_prediction(text)
            if cached_result:
                self.performance_metrics["cache_hits"] += 1
                return cached_result

        self.performance_metrics["cache_misses"] += 1

        # Collect predictions from all models
        predictions = []

        # Detoxify predictions
        for name, model_info in self.models.items():
            if model_info["type"] == "detoxify":
                try:
                    pred = await self._predict_detoxify(name, text, model_info)
                    if pred:
                        predictions.append(pred)
                except Exception as e:
                    logger.warning(f"Detoxify prediction failed for {name}: {e}")

        # HuggingFace predictions
        for name, model_info in self.models.items():
            if model_info["type"] == "huggingface":
                try:
                    pred = await self._predict_huggingface(name, text, model_info)
                    if pred:
                        predictions.append(pred)
                except Exception as e:
                    logger.warning(f"HuggingFace prediction failed for {name}: {e}")

        # Sentence transformer prediction
        if "sentence_transformer" in self.models:
            try:
                pred = await self._predict_sentence_transformer(text, self.models["sentence_transformer"])
                if pred:
                    predictions.append(pred)
            except Exception as e:
                logger.warning(f"Sentence transformer prediction failed: {e}")

        # Rule-based prediction (always included as fallback)
        try:
            pred = self._predict_rule_based(text, self.models["rule_based"])
            predictions.append(pred)
        except Exception as e:
            logger.warning(f"Rule-based prediction failed: {e}")

        # If no models loaded, use fallback
        if not predictions:
            result = self._fallback_prediction(text)
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = processing_time
            return result

        # Calculate ensemble result
        ensemble_result = self._calculate_ensemble(predictions, text, start_time)

        # Update metrics
        self._update_performance_metrics(predictions)

        # Cache result
        if use_cache:
            self._cache_prediction(text, ensemble_result)

        return ensemble_result

    async def _predict_detoxify(self, name: str, text: str, model_info: Dict) -> Optional[ModelPrediction]:
        """Predict using Detoxify model"""
        start_time = time.time()
        model = model_info["model"]
        results = model.predict(text)

        prediction_time = (time.time() - start_time) * 1000

        # Calculate overall toxicity score
        toxicity_score = max(results.values())

        return ModelPrediction(
            model_name=name,
            toxicity_score=toxicity_score,
            confidence=max(0.1, 1.0 - toxicity_score),
            prediction_time_ms=prediction_time,
            raw_scores=results,
            model_type="detoxify",
            version=model_info["version"]
        )

    async def _predict_huggingface(self, name: str, text: str, model_info: Dict) -> Optional[ModelPrediction]:
        """Predict using HuggingFace model"""
        start_time = time.time()
        pipe = model_info["pipeline"]

        # Run prediction
        results = pipe(text)
        prediction_time = (time.time() - start_time) * 1000

        # Process results
        raw_scores = {}
        toxicity_score = 0.0

        for result in results[0]:
            label = result['label'].lower()
            score = result['score']
            raw_scores[label] = score

            # Check if this is a toxicity-related label
            if any(keyword in label for keyword in ['toxic', 'hate', 'offensive', 'negative']):
                toxicity_score = max(toxicity_score, score)

        # If no toxicity labels found, use the highest score as toxicity
        if toxicity_score == 0.0:
            toxicity_score = max(r['score'] for r in results[0])

        return ModelPrediction(
            model_name=name,
            toxicity_score=toxicity_score,
            confidence=max(0.1, 1.0 - toxicity_score),
            prediction_time_ms=prediction_time,
            raw_scores=raw_scores,
            model_type="huggingface",
            version=model_info["version"]
        )

    async def _predict_sentence_transformer(self, text: str, model_info: Dict) -> Optional[ModelPrediction]:
        """Predict using semantic similarity to known toxic patterns"""
        start_time = time.time()
        model = model_info["model"]

        # Known toxic and non-toxic examples
        toxic_examples = [
            "You are stupid and ugly",
            "I hate you",
            "Kill yourself",
            "You are worthless"
        ]

        non_toxic_examples = [
            "Hello, how are you?",
            "I love this weather",
            "Thank you for your help",
            "Have a great day"
        ]

        # Get embeddings
        text_embedding = model.encode([text])
        toxic_embeddings = model.encode(toxic_examples)
        non_toxic_embeddings = model.encode(non_toxic_examples)

        # Calculate similarities
        from sklearn.metrics.pairwise import cosine_similarity
        toxic_similarities = cosine_similarity(text_embedding, toxic_embeddings)[0]
        non_toxic_similarities = cosine_similarity(text_embedding, non_toxic_embeddings)[0]

        # Calculate toxicity score based on similarities
        avg_toxic_sim = np.mean(toxic_similarities)
        avg_non_toxic_sim = np.mean(non_toxic_similarities)

        # Normalize to 0-1 range
        toxicity_score = max(0, min(1, avg_toxic_sim - avg_non_toxic_sim + 0.5))

        prediction_time = (time.time() - start_time) * 1000

        return ModelPrediction(
            model_name="sentence_transformer",
            toxicity_score=toxicity_score,
            confidence=max(0.1, 1.0 - toxicity_score),
            prediction_time_ms=prediction_time,
            raw_scores={
                "toxic_similarity": float(avg_toxic_sim),
                "non_toxic_similarity": float(avg_non_toxic_sim)
            },
            model_type="sentence_transformer",
            version=model_info["version"]
        )

    def _predict_rule_based(self, text: str, model_info: Dict) -> ModelPrediction:
        """Predict using rule-based approach"""
        start_time = time.time()
        keywords = model_info["keywords"]
        text_lower = text.lower()

        # Calculate scores for each category
        category_scores = {}
        total_toxicity = 0.0

        for category, words in keywords.items():
            score = 0.0
            for word in words:
                if word in text_lower:
                    score += 0.3  # Add 0.3 for each keyword match
            category_scores[category] = min(1.0, score)
            total_toxicity = max(total_toxicity, score)

        # Apply category weights
        weights = {
            'severe': 1.0,
            'threat': 0.9,
            'hate': 0.8,
            'insult': 0.6,
            'discrimination': 0.7
        }

        weighted_score = 0.0
        for category, score in category_scores.items():
            weight = weights.get(category, 0.5)
            weighted_score += score * weight

        toxicity_score = min(1.0, weighted_score)
        prediction_time = (time.time() - start_time) * 1000

        return ModelPrediction(
            model_name="rule_based",
            toxicity_score=toxicity_score,
            confidence=max(0.1, 1.0 - toxicity_score),
            prediction_time_ms=prediction_time,
            raw_scores=category_scores,
            model_type="rule_based",
            version=model_info["version"]
        )

    def _calculate_ensemble(self, predictions: List[ModelPrediction], text: str, start_time: float) -> EnsembleResult:
        """Calculate ensemble result from individual predictions"""
        if not predictions:
            return self._fallback_prediction(text)

        # Weight models by their type and confidence
        weights = {
            "detoxify": 0.3,
            "huggingface": 0.35,
            "sentence_transformer": 0.25,
            "rule_based": 0.1
        }

        weighted_score = 0.0
        total_weight = 0.0
        confidences = []

        for pred in predictions:
            weight = weights.get(pred.model_type, 0.1)
            weighted_score += pred.toxicity_score * weight * pred.confidence
            total_weight += weight * pred.confidence
            confidences.append(pred.confidence)

        # Calculate final score
        final_score = weighted_score / total_weight if total_weight > 0 else np.mean([p.toxicity_score for p in predictions])
        final_score = max(0.0, min(1.0, final_score))

        # Calculate consensus (how much models agree)
        scores = [p.toxicity_score for p in predictions]
        consensus = 1.0 - np.std(scores)  # Lower standard deviation = higher consensus

        # Calculate overall confidence
        avg_confidence = np.mean(confidences)
        confidence = avg_confidence * consensus

        processing_time = (time.time() - start_time) * 1000

        return EnsembleResult(
            final_score=final_score,
            confidence=confidence,
            individual_predictions=predictions,
            consensus=consensus,
            processing_time_ms=processing_time,
            model_count=len(predictions)
        )

    def _fallback_prediction(self, text: str) -> EnsembleResult:
        """Fallback prediction when no models are available"""
        # Simple keyword-based fallback
        toxic_keywords = ['hate', 'stupid', 'ugly', 'kill', 'die', 'idiot']
        toxicity_score = 0.7 if any(word in text.lower() for word in toxic_keywords) else 0.0

        fallback_pred = ModelPrediction(
            model_name="fallback",
            toxicity_score=toxicity_score,
            confidence=0.5,
            prediction_time_ms=1.0,
            raw_scores={"fallback": toxicity_score},
            model_type="fallback",
            version="1.0"
        )

        return EnsembleResult(
            final_score=toxicity_score,
            confidence=0.5,
            individual_predictions=[fallback_pred],
            consensus=1.0,
            processing_time_ms=1.0,
            model_count=1
        )

    def _get_cached_prediction(self, text: str) -> Optional[EnsembleResult]:
        """Get cached prediction if available"""
        text_hash = hash(text)
        if text_hash in self.prediction_cache:
            cached = self.prediction_cache[text_hash]
            # Cache is valid for 1 hour
            if time.time() - cached["timestamp"] < 3600:
                return cached["result"]
            else:
                del self.prediction_cache[text_hash]
        return None

    def _cache_prediction(self, text: str, result: EnsembleResult):
        """Cache prediction result"""
        text_hash = hash(text)
        self.prediction_cache[text_hash] = {
            "result": result,
            "timestamp": time.time()
        }

        # Limit cache size
        if len(self.prediction_cache) > 1000:
            oldest_key = min(self.prediction_cache.keys(),
                           key=lambda k: self.prediction_cache[k]["timestamp"])
            del self.prediction_cache[oldest_key]

    def _update_performance_metrics(self, predictions: List[ModelPrediction]):
        """Update performance metrics"""
        self.performance_metrics["total_predictions"] += 1

        # Update average prediction time
        pred_times = [p.prediction_time_ms for p in predictions]
        avg_time = np.mean(pred_times)
        total_pred = self.performance_metrics["total_predictions"]
        current_avg = self.performance_metrics["average_prediction_time"]
        self.performance_metrics["average_prediction_time"] = (
            (current_avg * (total_pred - 1) + avg_time) / total_pred
        )

        # Update model usage
        for pred in predictions:
            model_type = pred.model_type
            self.performance_metrics["model_usage"][model_type] = (
                self.performance_metrics["model_usage"].get(model_type, 0) + 1
            )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        uptime = time.time() - self.start_time
        cache_total = self.performance_metrics["cache_hits"] + self.performance_metrics["cache_misses"]
        cache_hit_rate = (self.performance_metrics["cache_hits"] / cache_total * 100) if cache_total > 0 else 0

        return {
            "models_loaded": len(self.models),
            "total_predictions": self.performance_metrics["total_predictions"],
            "average_prediction_time_ms": self.performance_metrics["average_prediction_time"],
            "uptime_hours": uptime / 3600,
            "cache_hit_rate_percent": cache_hit_rate,
            "cache_size": len(self.prediction_cache),
            "model_usage": self.performance_metrics["model_usage"],
            "available_models": list(self.models.keys()),
            "ml_libraries_available": ML_AVAILABLE
        }

# Global model instance
advanced_models = AdvancedToxicityModels()