import axios from 'axios';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_KEY = process.env.REACT_APP_API_KEY || 'industry-demo-key-12345';

// Create axios instance with default headers
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  },
});

// API Service Functions
export const moderationService = {
  // Analyze text for hate speech
  async analyzeText(text, userId) {
    try {
      const response = await api.post('/api/v1/moderation/analyze', {
        text,
        user_id: userId,
      });
      const raw = response.data || {};

      // Map backend response to UI-expected shape
      const recommendedAction = raw?.moderation_action?.recommended_action || 'allow';
      const confidence = raw?.moderation_action?.confidence ?? 0;
      const toxicityScore = raw?.analysis?.toxicity_score ?? 0;
      const categories = raw?.analysis?.toxicity_scores || {};
      const modelUsed = raw?.model_info?.model_type || 'ensemble';
      const processingTime = raw?.analysis?.processing_time_ms || 0;

      return {
        message_id: raw.message_id || '',
        recommended_action: recommendedAction,
        analysis: {
          toxicity_score: toxicityScore,
          confidence: confidence,
          model_used: modelUsed,
          categories: categories,
          text: text,
          processing_time_ms: processingTime,
        },
        reasoning: `Analysis complete using ${modelUsed} model (${processingTime.toFixed(0)}ms)`,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Analysis failed:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Analysis failed');
    }
  },

  // Submit feedback for incorrect moderation
  async submitFeedback(messageId, correctAction, feedbackText, userId) {
    try {
      const response = await api.post('/api/v1/feedback/report', {
        message_id: messageId,
        reporter_id: userId || 'anonymous',
        reason: `Incorrect moderation - should be: ${correctAction}`,
        description: feedbackText || `User believes the correct action should be "${correctAction}" instead.`,
      });
      return response.data;
    } catch (error) {
      console.error('Feedback submission failed:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Feedback submission failed');
    }
  },

  // Get analytics data
  async getAnalytics(startDate, endDate, userId) {
    try {
      const params = { days: 7 };
      if (userId) params.user_id = userId;

      // Get overview and statistics
      const [overview, statistics] = await Promise.all([
        api.get('/api/v1/analytics/overview', { params }),
        api.get('/api/v1/moderation/statistics', { params })
      ]);

      // Map to expected dashboard format
      const ovData = overview.data;
      const statData = statistics.data;
      
      // Calculate toxic messages (flagged messages that aren't false positives)
      const totalMessages = ovData.total_messages || 0;
      const flaggedRate = ovData.flagged_rate || 0;
      const flaggedMessages = Math.round(totalMessages * (flaggedRate / 100));
      const toxicMessages = flaggedMessages;

      return {
        data: {
          total_messages: totalMessages,
          flagged_messages: flaggedMessages,
          toxic_messages: toxicMessages,
          active_users: ovData.active_users || 0,
          active_conversations: ovData.active_conversations || 0,
          messages_last_24h: ovData.messages_last_24h || 0,
          messages_last_7d: ovData.messages_last_7d || 0,
          flagged_rate: flaggedRate,
          false_positive_rate: ovData.false_positive_rate || 0
        },
        action_breakdown: statData.action_breakdown || {},
        period_days: statData.period_days || 7
      };
    } catch (error) {
      console.error('Analytics fetch failed:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Analytics fetch failed');
    }
  },

  // Get model performance stats
  async getModelPerformance() {
    try {
      const response = await api.get('/api/v1/moderation/statistics');
      return response.data;
    } catch (error) {
      console.error('Model performance fetch failed:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Model performance fetch failed');
    }
  },

  // Health check
  async healthCheck() {
    try {
      const response = await api.get('/api/v1/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Health check failed');
    }
  },

  // Instagram Analysis
  async analyzeInstagramPost(instagramUrl, maxComments = 50, includeReplies = false) {
    try {
      const response = await api.post('/api/v1/instagram/analyze', {
        instagram_url: instagramUrl,
        max_comments: maxComments,
        include_replies: includeReplies
      });
      return response.data;
    } catch (error) {
      console.error('Instagram analysis failed:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Instagram analysis failed');
    }
  },

  // Reset Analytics
  async resetAnalytics() {
    try {
      const response = await api.post('/api/v1/analytics/reset');
      return response.data;
    } catch (error) {
      console.error('Analytics reset failed:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Analytics reset failed');
    }
  },
};

export default api;