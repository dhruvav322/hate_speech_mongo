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
      return response.data;
    } catch (error) {
      console.error('Analysis failed:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Analysis failed');
    }
  },

  // Submit feedback for incorrect moderation
  async submitFeedback(messageId, correctAction, feedbackText, userId) {
    try {
      const response = await api.post('/api/v1/feedback', {
        message_id: messageId,
        correct_action: correctAction,
        feedback_text: feedbackText,
        user_id: userId,
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
      const params = {};
      if (startDate) params.start_date = startDate.toISOString();
      if (endDate) params.end_date = endDate.toISOString();
      if (userId) params.user_id = userId;

      const response = await api.get('/api/v1/analytics', { params });
      return response.data;
    } catch (error) {
      console.error('Analytics fetch failed:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Analytics fetch failed');
    }
  },

  // Get model performance stats
  async getModelPerformance() {
    try {
      const response = await api.get('/api/v1/model-performance');
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
};

export default api;