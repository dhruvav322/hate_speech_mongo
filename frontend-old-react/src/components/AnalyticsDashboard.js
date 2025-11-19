import React, { useState, useEffect } from 'react';
import { moderationService } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, Users, AlertTriangle, Shield, Loader2, RefreshCw, RotateCcw } from 'lucide-react';

const AnalyticsDashboard = ({ darkMode }) => {
  const [analytics, setAnalytics] = useState(null);
  const [modelPerformance, setModelPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const fetchAnalytics = async () => {
    try {
      setRefreshing(true);
      const [analyticsData, performanceData] = await Promise.all([
        moderationService.getAnalytics(),
        moderationService.getModelPerformance()
      ]);

      setAnalytics(analyticsData);
      setModelPerformance(performanceData);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const resetAnalytics = async () => {
    if (!window.confirm('Are you sure you want to reset all analytics data? This action cannot be undone.')) {
      return;
    }

    try {
      setRefreshing(true);
      await moderationService.resetAnalytics();
      await fetchAnalytics(); // Refresh data after reset
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const pieData = analytics ? [
    { name: 'Allowed', value: analytics.data.total_messages - analytics.data.toxic_messages, color: '#10b981' },
    { name: 'Toxic', value: analytics.data.toxic_messages, color: '#ef4444' }
  ] : [];

  const barData = analytics ? [
    { name: 'Total', value: analytics.data.total_messages, color: '#3b82f6' },
    { name: 'Flagged', value: analytics.data.flagged_messages, color: '#f59e0b' },
    { name: 'Blocked', value: analytics.data.blocked_messages, color: '#ef4444' }
  ] : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading analytics...</span>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Activity className="w-6 h-6 text-blue-600" />
          <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Analytics Dashboard</h2>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={resetAnalytics}
            disabled={refreshing}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
              darkMode
                ? 'bg-red-600 hover:bg-red-700 disabled:bg-gray-700 text-white'
                : 'bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white'
            }`}
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset</span>
          </button>
          <button
            onClick={fetchAnalytics}
            disabled={refreshing}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
              darkMode
                ? 'bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white'
                : 'bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white'
            }`}
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      {analytics && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow-md p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-gray-600">Total Messages</div>
                  <div className="text-2xl font-bold text-gray-900">{analytics.data.total_messages}</div>
                </div>
                <Users className="w-8 h-8 text-blue-600" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-gray-600">Toxic Messages</div>
                  <div className="text-2xl font-bold text-red-600">{analytics.data.toxic_messages}</div>
                </div>
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-gray-600">Flagged</div>
                  <div className="text-2xl font-bold text-yellow-600">{analytics.data.flagged_messages}</div>
                </div>
                <Shield className="w-8 h-8 text-yellow-600" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-gray-600">Blocked</div>
                  <div className="text-2xl font-bold text-red-700">{analytics.data.blocked_messages}</div>
                </div>
                <AlertTriangle className="w-8 h-8 text-red-700" />
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Pie Chart */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Message Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Bar Chart */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Action Summary</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6">
                    {barData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Model Performance */}
          {modelPerformance && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Performance</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">Model Name</div>
                  <div className="text-lg font-semibold text-gray-900">{modelPerformance.model_name}</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">Total Predictions</div>
                  <div className="text-lg font-semibold text-blue-600">{modelPerformance.total_predictions}</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">Avg Response Time</div>
                  <div className="text-lg font-semibold text-green-600">{modelPerformance.average_response_time_ms}ms</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">Cache Hit Rate</div>
                  <div className="text-lg font-semibold text-purple-600">{modelPerformance.cache_hit_rate_percent}%</div>
                </div>
              </div>
              <div className="mt-4 flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  modelPerformance.model_status === 'active' ? 'bg-green-500' : 'bg-yellow-500'
                }`} />
                <span className="text-sm text-gray-600">
                  Status: {modelPerformance.model_status} | Type: {modelPerformance.model_type}
                </span>
              </div>
            </div>
          )}

          {/* Last Updated */}
          <div className="text-center text-sm text-gray-500">
            Last updated: {new Date(analytics.generated_at).toLocaleString()}
          </div>
        </>
      )}
    </div>
  );
};

export default AnalyticsDashboard;