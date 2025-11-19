import React, { useState } from 'react';
import { moderationService } from '../services/api';
import { Instagram, AlertTriangle, CheckCircle, XCircle, Send, Loader2, BarChart3, Users, MessageSquare } from 'lucide-react';

const InstagramAnalysis = ({ darkMode }) => {
  const [instagramUrl, setInstagramUrl] = useState('');
  const [maxComments, setMaxComments] = useState(50);
  const [includeReplies, setIncludeReplies] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const analyzeInstagramPost = async () => {
    if (!instagramUrl.trim()) {
      setError('Please enter an Instagram URL');
      return;
    }

    // Validate Instagram URL format
    const instagramRegex = /instagram\.com\/(p|reel|tv)\/[A-Za-z0-9_-]+/;
    if (!instagramRegex.test(instagramUrl)) {
      setError('Please enter a valid Instagram post or reel URL');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const analysisResult = await moderationService.analyzeInstagramPost(
        instagramUrl, 
        maxComments, 
        includeReplies
      );
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
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'flag':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'block':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getActionColor = (action) => {
    if (darkMode) {
      switch (action) {
        case 'allow':
          return 'bg-green-900 border-green-700 text-green-300';
        case 'flag':
          return 'bg-yellow-900 border-yellow-700 text-yellow-300';
        case 'block':
          return 'bg-red-900 border-red-700 text-red-300';
        default:
          return 'bg-gray-800 border-gray-600 text-gray-300';
      }
    } else {
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
    }
  };

  const getRatioColor = (ratio) => {
    if (ratio < 10) return darkMode ? 'text-green-400' : 'text-green-600';
    if (ratio < 30) return darkMode ? 'text-yellow-400' : 'text-yellow-600';
    return darkMode ? 'text-red-400' : 'text-red-600';
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center space-x-2">
          <Instagram className="w-8 h-8 text-pink-500" />
          <h1 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            Instagram Analysis
          </h1>
        </div>
        <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
          Analyze Instagram posts and reels for hate speech in comments
        </p>
        <div className={`text-sm p-3 rounded-lg ${
          darkMode 
            ? 'bg-blue-900 border border-blue-700 text-blue-300' 
            : 'bg-blue-50 border border-blue-200 text-blue-800'
        }`}>
          <strong>📝 Note:</strong> Due to Instagram's restrictions, real posts may fallback to demo mode with realistic sample data analyzed by our ML models.
          <br />
          <strong>🎯 Try:</strong> Use "demo" in the URL or any Instagram URL to see the analysis in action!
        </div>
      </div>

      {/* Input Section */}
      <div className={`rounded-lg p-6 space-y-4 transition-colors duration-300 ${
        darkMode 
          ? 'bg-gray-800 border border-gray-700' 
          : 'bg-white shadow-md'
      }`}>
        <div>
          <label htmlFor="instagramUrl" className={`block text-sm font-medium mb-1 ${
            darkMode ? 'text-gray-300' : 'text-gray-700'
          }`}>
            Instagram Post/Reel URL
          </label>
          <input
            type="url"
            id="instagramUrl"
            value={instagramUrl}
            onChange={(e) => setInstagramUrl(e.target.value)}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${
              darkMode 
                ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
            }`}
            placeholder="Try: 'demo' or any Instagram URL like https://www.instagram.com/p/ABC123/"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="maxComments" className={`block text-sm font-medium mb-1 ${
              darkMode ? 'text-gray-300' : 'text-gray-700'
            }`}>
              Max Comments to Analyze
            </label>
            <select
              id="maxComments"
              value={maxComments}
              onChange={(e) => setMaxComments(parseInt(e.target.value))}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${
                darkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              }`}
            >
              <option value={25}>25 comments</option>
              <option value={50}>50 comments</option>
              <option value={100}>100 comments</option>
              <option value={200}>200 comments</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="includeReplies"
              checked={includeReplies}
              onChange={(e) => setIncludeReplies(e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="includeReplies" className={`text-sm ${
              darkMode ? 'text-gray-300' : 'text-gray-700'
            }`}>
              Include comment replies
            </label>
          </div>
        </div>

        <button
          onClick={analyzeInstagramPost}
          disabled={loading || !instagramUrl.trim()}
          className={`w-full py-3 px-4 rounded-md font-medium transition-colors flex items-center justify-center space-x-2 ${
            darkMode
              ? 'bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white'
              : 'bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white'
          } disabled:cursor-not-allowed`}
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Analyzing Comments...</span>
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              <span>Analyze Instagram Post</span>
            </>
          )}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className={`border rounded-md p-4 flex items-center space-x-2 ${
          darkMode 
            ? 'bg-red-900 border-red-700 text-red-300' 
            : 'bg-red-50 border-red-200 text-red-800'
        }`}>
          <XCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          {/* Overview Stats */}
          <div className={`rounded-lg p-6 transition-colors duration-300 ${
            darkMode 
              ? 'bg-gray-800 border border-gray-700' 
              : 'bg-white shadow-md'
          }`}>
            <h2 className={`text-xl font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              Analysis Overview
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className={`rounded-lg p-4 ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
                <div className="flex items-center space-x-2">
                  <MessageSquare className={`w-5 h-5 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`} />
                  <div className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Comments Analyzed
                  </div>
                </div>
                <div className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                  {result.total_comments_analyzed}
                </div>
              </div>

              <div className={`rounded-lg p-4 ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
                <div className="flex items-center space-x-2">
                  <AlertTriangle className={`w-5 h-5 ${getRatioColor(result.hate_speech_ratio)}`} />
                  <div className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Hate Speech Ratio
                  </div>
                </div>
                <div className={`text-2xl font-bold ${getRatioColor(result.hate_speech_ratio)}`}>
                  {result.hate_speech_ratio.toFixed(1)}%
                </div>
              </div>

              <div className={`rounded-lg p-4 ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
                <div className="flex items-center space-x-2">
                  <BarChart3 className={`w-5 h-5 ${darkMode ? 'text-purple-400' : 'text-purple-600'}`} />
                  <div className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Avg Toxicity
                  </div>
                </div>
                <div className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                  {(result.overall_toxicity_score * 100).toFixed(1)}%
                </div>
              </div>

              <div className={`rounded-lg p-4 ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
                <div className="flex items-center space-x-2">
                  <Users className={`w-5 h-5 ${darkMode ? 'text-green-400' : 'text-green-600'}`} />
                  <div className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Confidence
                  </div>
                </div>
                <div className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                  {(result.confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          </div>

          {/* Action Breakdown */}
          <div className={`rounded-lg p-6 transition-colors duration-300 ${
            darkMode 
              ? 'bg-gray-800 border border-gray-700' 
              : 'bg-white shadow-md'
          }`}>
            <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              Moderation Actions Breakdown
            </h3>
            
            <div className="grid grid-cols-3 gap-4">
              {Object.entries(result.comments_breakdown).map(([action, count]) => (
                <div key={action} className={`rounded-lg p-4 border ${getActionColor(action)}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getActionIcon(action)}
                      <span className="font-medium capitalize">{action}</span>
                    </div>
                    <span className="text-2xl font-bold">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Toxic Comments */}
          {result.toxic_comments && result.toxic_comments.length > 0 && (
            <div className={`rounded-lg p-6 transition-colors duration-300 ${
              darkMode 
                ? 'bg-gray-800 border border-gray-700' 
                : 'bg-white shadow-md'
            }`}>
              <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                Most Toxic Comments
              </h3>
              
              <div className="space-y-3">
                {result.toxic_comments.slice(0, 5).map((comment, index) => (
                  <div key={index} className={`rounded-lg p-4 border ${
                    darkMode 
                      ? 'bg-gray-700 border-gray-600' 
                      : 'bg-gray-50 border-gray-200'
                  }`}>
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        {getActionIcon(comment.recommended_action)}
                        <span className={`font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                          @{comment.username}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                          {(comment.toxicity_score * 100).toFixed(1)}% toxic
                        </span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getActionColor(comment.recommended_action)}`}>
                          {comment.recommended_action.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      "{comment.comment_text}"
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Analysis Info */}
          <div className={`text-xs border-t pt-3 ${
            darkMode 
              ? 'text-gray-500 border-gray-700' 
              : 'text-gray-500 border-gray-200'
          }`}>
            Post URL: {result.post_url} | 
            Analyzed at: {new Date(result.analysis_timestamp).toLocaleString()} |
            Model: Ensemble ML (Detoxify + Semantic Analysis)
          </div>
        </div>
      )}
    </div>
  );
};

export default InstagramAnalysis;
