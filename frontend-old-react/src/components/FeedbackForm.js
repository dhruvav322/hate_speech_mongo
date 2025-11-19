import React, { useState } from 'react';
import { moderationService } from '../services/api';
import { MessageSquare, ThumbsUp, ThumbsDown, Flag, Send, CheckCircle } from 'lucide-react';

const FeedbackForm = ({ analysisResult, userId, onFeedbackSubmitted }) => {
  const [correctAction, setCorrectAction] = useState('');
  const [feedbackText, setFeedbackText] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const submitFeedback = async () => {
    if (!correctAction) {
      setError('Please select the correct action');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await moderationService.submitFeedback(
        analysisResult.message_id,
        correctAction,
        feedbackText,
        userId
      );

      setSubmitted(true);
      setError('');
      setFeedbackText('');
      setCorrectAction('');

      if (onFeedbackSubmitted) {
        onFeedbackSubmitted();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!analysisResult) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 text-center">
        <MessageSquare className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-500">Analyze a message first to provide feedback</p>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
        <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
        <h3 className="text-lg font-semibold text-green-800 mb-1">Feedback Submitted!</h3>
        <p className="text-green-700 mb-4">
          Thank you for helping improve our moderation system. Your feedback has been recorded.
        </p>
        <button
          onClick={() => setSubmitted(false)}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
        >
          Submit More Feedback
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center space-x-2 mb-4">
        <MessageSquare className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">MLOps Feedback</h3>
      </div>

      <div className="bg-gray-50 rounded-lg p-4 mb-4">
        <div className="text-sm font-medium text-gray-600 mb-1">Original Analysis</div>
        <div className="flex items-center justify-between">
          <span className="text-gray-800">Message ID: {analysisResult.message_id}</span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            analysisResult.recommended_action === 'allow' ? 'bg-green-100 text-green-800' :
            analysisResult.recommended_action === 'flag' ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            {analysisResult.recommended_action.toUpperCase()}
          </span>
        </div>
        <div className="text-sm text-gray-600 mt-1">
          Toxicity: {(analysisResult.analysis.toxicity_score * 100).toFixed(1)}%
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            What should the correct action have been?
          </label>
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => setCorrectAction('allow')}
              className={`flex items-center justify-center space-x-2 py-2 px-3 rounded-md border transition-colors ${
                correctAction === 'allow'
                  ? 'bg-green-50 border-green-500 text-green-700'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <ThumbsUp className="w-4 h-4" />
              <span>Allow</span>
            </button>
            <button
              onClick={() => setCorrectAction('flag')}
              className={`flex items-center justify-center space-x-2 py-2 px-3 rounded-md border transition-colors ${
                correctAction === 'flag'
                  ? 'bg-yellow-50 border-yellow-500 text-yellow-700'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Flag className="w-4 h-4" />
              <span>Flag</span>
            </button>
            <button
              onClick={() => setCorrectAction('block')}
              className={`flex items-center justify-center space-x-2 py-2 px-3 rounded-md border transition-colors ${
                correctAction === 'block'
                  ? 'bg-red-50 border-red-500 text-red-700'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <ThumbsDown className="w-4 h-4" />
              <span>Block</span>
            </button>
          </div>
        </div>

        <div>
          <label htmlFor="feedbackText" className="block text-sm font-medium text-gray-700 mb-1">
            Additional Feedback (optional)
          </label>
          <textarea
            id="feedbackText"
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 h-20 resize-none"
            placeholder="Provide any additional context about why this action should be corrected..."
          />
          <div className="text-right text-sm text-gray-500 mt-1">
            {feedbackText.length} / 1000 characters
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-800">
            {error}
          </div>
        )}

        <button
          onClick={submitFeedback}
          disabled={loading || !correctAction}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
        >
          {loading ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              <Send className="w-5 h-5" />
              <span>Submit Feedback</span>
            </>
          )}
        </button>
      </div>

      <div className="mt-4 text-xs text-gray-500 bg-blue-50 rounded-lg p-3">
        <strong>🤖 MLOps Feedback Loop:</strong> Your feedback helps improve our moderation models and will be used for future training and model refinement.
      </div>
    </div>
  );
};

export default FeedbackForm;