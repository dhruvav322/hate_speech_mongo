import React, { useState } from 'react';
import ModerationInterface from './components/ModerationInterface';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import FeedbackForm from './components/FeedbackForm';
import { moderationService } from './services/api';
import { Shield, BarChart3, MessageSquare, Activity, Settings, Info } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('moderation');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [userId] = useState('user_' + Math.random().toString(36).substr(2, 9));
  const [apiStatus, setApiStatus] = useState('unknown');
  const [showInfo, setShowInfo] = useState(false);

  // Check API status on mount
  React.useEffect(() => {
    const checkApiHealth = async () => {
      try {
        await moderationService.healthCheck();
        setApiStatus('healthy');
      } catch (error) {
        setApiStatus('error');
      }
    };

    checkApiHealth();
    // Check health every 30 seconds
    const interval = setInterval(checkApiHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleAnalysisComplete = (result) => {
    setAnalysisResult(result);
    // Auto-switch to feedback tab after successful analysis
    if (result) {
      setTimeout(() => {
        setActiveTab('feedback');
      }, 1000);
    }
  };

  const handleFeedbackSubmitted = () => {
    // Clear analysis result after feedback submission
    setTimeout(() => {
      setAnalysisResult(null);
      setActiveTab('moderation');
    }, 2000);
  };

  const tabs = [
    {
      id: 'moderation',
      name: 'Moderation',
      icon: Shield,
      component: <ModerationInterface onAnalysisComplete={handleAnalysisComplete} />
    },
    {
      id: 'feedback',
      name: 'Feedback',
      icon: MessageSquare,
      component: (
        <FeedbackForm
          analysisResult={analysisResult}
          userId={userId}
          onFeedbackSubmitted={handleFeedbackSubmitted}
        />
      )
    },
    {
      id: 'analytics',
      name: 'Analytics',
      icon: BarChart3,
      component: <AnalyticsDashboard />
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo and Title */}
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Hate Speech Moderation</h1>
                <p className="text-xs text-gray-500">Industry-Grade Content Analysis</p>
              </div>
            </div>

            {/* API Status */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Activity className={`w-4 h-4 ${
                  apiStatus === 'healthy' ? 'text-green-500' :
                  apiStatus === 'error' ? 'text-red-500' : 'text-gray-400'
                }`} />
                <span className={`text-sm font-medium ${
                  apiStatus === 'healthy' ? 'text-green-700' :
                  apiStatus === 'error' ? 'text-red-700' : 'text-gray-500'
                }`}>
                  {apiStatus === 'healthy' ? 'API Online' :
                   apiStatus === 'error' ? 'API Offline' : 'Checking...'}
                </span>
              </div>

              <button
                onClick={() => setShowInfo(!showInfo)}
                className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
              >
                <Info className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Info Banner */}
      {showInfo && (
        <div className="bg-blue-50 border-b border-blue-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <div className="flex items-center justify-between">
              <div className="text-sm text-blue-800">
                <strong>🛡️ Industry-Ready Features:</strong> API Key Authentication • MLOps Feedback Loop •
                Background Processing • Real-time Analytics • Production Performance
              </div>
              <button
                onClick={() => setShowInfo(false)}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {tabs.find(tab => tab.id === activeTab)?.component}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div>
              🛡️ Industry-Ready Hate Speech Moderation v2.0 |
              Model: Rule-based with optional ML support
            </div>
            <div className="flex items-center space-x-4">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800"
              >
                API Documentation
              </a>
              <span>•</span>
              <span className="text-xs">
                API Key: industry-demo-key-12345
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;