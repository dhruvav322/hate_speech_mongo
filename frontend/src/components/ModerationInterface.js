import React, { useState } from 'react';
import { moderationService } from '../services/api';
import { Shield, AlertTriangle, CheckCircle, XCircle, Send, Loader2 } from 'lucide-react';

const ModerationInterface = () => {
  const [text, setText] = useState('');
  const [userId, setUserId] = useState('user_' + Math.random().toString(36).substr(2, 9));
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const analyzeText = async () => {
    if (!text.trim()) {
      setError('Please enter text to analyze');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const analysisResult = await moderationService.analyzeText(text, userId);
      setResult(analysisResult);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getActionIcon = (action) => {
    switch (action) {
      case 'allow':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'flag':
        return <AlertTriangle className="w-6 h-6 text-yellow-500" />;
      case 'block':
        return <XCircle className="w-6 h-6 text-red-500" />;
      default:
        return null;
    }
  };

  const getActionColor = (action) => {
    switch (action) {
      case 'allow':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'flag':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'block':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getToxicityColor = (score) => {
    if (score < 0.3) return 'text-green-600';
    if (score < 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center space-x-2">
          <Shield className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Hate Speech Moderation</h1>
        </div>
        <p className="text-gray-600">AI-powered content moderation with industry-grade accuracy</p>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
        <div>
          <label htmlFor="userId" className="block text-sm font-medium text-gray-700 mb-1">
            User ID (optional)
          </label>
          <input
            type="text"
            id="userId"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter user ID"
          />
        </div>

        <div>
          <label htmlFor="text" className="block text-sm font-medium text-gray-700 mb-1">
            Text to Analyze
          </label>
          <textarea
            id="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 h-32 resize-none"
            placeholder="Enter text to analyze for hate speech..."
          />
          <div className="text-right text-sm text-gray-500 mt-1">
            {text.length} / 10,000 characters
          </div>
        </div>

        <button
          onClick={analyzeText}
          disabled={loading || !text.trim()}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              <span>Analyze Text</span>
            </>
          )}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 flex items-center space-x-2">
          <XCircle className="w-5 h-5 text-red-600" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Analysis Results</h2>
            <div className="flex items-center space-x-2">
              {getActionIcon(result.recommended_action)}
              <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getActionColor(result.recommended_action)}`}>
                {result.recommended_action.toUpperCase()}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm font-medium text-gray-600 mb-1">Toxicity Score</div>
              <div className={`text-2xl font-bold ${getToxicityColor(result.analysis.toxicity_score)}`}>
                {(result.analysis.toxicity_score * 100).toFixed(1)}%
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${
                    result.analysis.toxicity_score < 0.3
                      ? 'bg-green-500'
                      : result.analysis.toxicity_score < 0.7
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                  style={{ width: `${result.analysis.toxicity_score * 100}%` }}
                />
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm font-medium text-gray-600 mb-1">Confidence</div>
              <div className="text-2xl font-bold text-blue-600">
                {(result.analysis.confidence * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Model: {result.analysis.model_used}
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="text-sm font-medium text-blue-800 mb-1">Reasoning</div>
            <div className="text-blue-700">{result.reasoning}</div>
          </div>

          {/* Category Breakdown */}
          {Object.keys(result.analysis.categories).length > 0 && (
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm font-medium text-gray-700 mb-3">Toxicity Categories</div>
              <div className="space-y-2">
                {Object.entries(result.analysis.categories).map(([category, score]) => (
                  <div key={category} className="flex items-center justify-between">
                    <div className="text-sm text-gray-600 capitalize">
                      {category.replace(/_/g, ' ')}
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            score < 0.3 ? 'bg-green-500' : score < 0.7 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${score * 100}%` }}
                        />
                      </div>
                      <div className="text-sm font-medium text-gray-700 w-12 text-right">
                        {(score * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="text-xs text-gray-500 border-t pt-3">
            Message ID: {result.message_id} | Analyzed at: {new Date(result.timestamp).toLocaleString()}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModerationInterface;