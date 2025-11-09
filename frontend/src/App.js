import React, { useState, useEffect } from 'react';
import ModerationInterface from './components/ModerationInterface';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import FeedbackForm from './components/FeedbackForm';
import { moderationService } from './services/api';
import { Shield, BarChart3, MessageSquare, Activity, Settings, Info, Moon, Sun } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('moderation');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [userId] = useState('user_' + Math.random().toString(36).substr(2, 9));
  const [apiStatus, setApiStatus] = useState('unknown');
  const [showInfo, setShowInfo] = useState(false);
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : true; // Default to dark mode
  });

  // Dark mode persistence
  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

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
    // Keep user on current tab to view results
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
      name: 'Text Analysis',
      icon: Shield,
      component: <ModerationInterface onAnalysisComplete={handleAnalysisComplete} darkMode={darkMode} />
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
          darkMode={darkMode}
        />
      )
    },
    {
      id: 'analytics',
      name: 'Analytics',
      icon: BarChart3,
      component: <AnalyticsDashboard darkMode={darkMode} />
    }
  ];

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      darkMode 
        ? 'bg-gray-900' 
        : 'bg-gray-50'
    }`}>
      {/* Header */}
      <header className={`border-b transition-colors duration-300 ${
        darkMode 
          ? 'bg-black border-gray-800' 
          : 'bg-white border-gray-200'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo and Title */}
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className={`text-xl font-bold transition-colors duration-200 ${
                  darkMode ? 'text-white' : 'text-gray-900'
                }`}>Hate Speech Moderation</h1>
                <p className={`text-xs transition-colors duration-200 ${
                  darkMode ? 'text-gray-400' : 'text-gray-500'
                }`}>Industry-Grade Content Analysis</p>
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
                className={`p-2 transition-colors ${
                  darkMode 
                    ? 'text-gray-400 hover:text-gray-200' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Info className="w-5 h-5" />
              </button>

              <button
                onClick={toggleDarkMode}
                className={`p-2 transition-colors ${
                  darkMode 
                    ? 'text-gray-400 hover:text-gray-200' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
                title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              >
                {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Info Banner */}
      {showInfo && (
        <div className={`border-b transition-colors duration-300 ${
          darkMode 
            ? 'bg-gray-800 border-gray-700' 
            : 'bg-gray-100 border-gray-200'
        }`}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <div className="flex items-center justify-between">
              <div className={`text-sm ${
                darkMode ? 'text-gray-300' : 'text-gray-700'
              }`}>
                <strong>🛡️ Detection Method:</strong> Ensemble ML Models (Detoxify + Semantic Analysis) • 
                <strong>🌐 Browser Extension:</strong> Available for universal platform analysis (Instagram, Twitter, YouTube, etc.)
              </div>
              <button
                onClick={() => setShowInfo(false)}
                className={`text-sm font-medium transition-colors ${
                  darkMode 
                    ? 'text-gray-400 hover:text-gray-200' 
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className={`transition-colors duration-300 ${
        darkMode ? 'bg-black' : 'bg-white'
      }`}>
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
                      ? darkMode 
                        ? 'border-blue-400 text-blue-400'
                        : 'border-blue-600 text-blue-600'
                      : darkMode
                        ? 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-600'
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
      <footer className={`border-t mt-auto transition-colors duration-300 ${
        darkMode 
          ? 'bg-black border-gray-800' 
          : 'bg-white border-gray-200'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className={`flex items-center justify-between text-sm ${
            darkMode ? 'text-gray-400' : 'text-gray-500'
          }`}>
            <div>
              🛡️ Hate Speech Moderation v2.0 | 
              <span className={darkMode ? 'text-gray-300' : 'text-gray-600'}>
                Enhanced Rule-based Detection
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className={`transition-colors ${
                  darkMode 
                    ? 'text-blue-400 hover:text-blue-300' 
                    : 'text-blue-600 hover:text-blue-800'
                }`}
              >
                API Docs
              </a>
              <span>•</span>
              <span className="text-xs">
                Key: industry-demo-key-12345
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;