// Background Service Worker for Browser Extension
class BackgroundService {
    constructor() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Handle extension installation
        chrome.runtime.onInstalled.addListener((details) => {
            this.handleInstallation(details);
        });

        // Handle messages from content scripts and popup
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            this.handleMessage(request, sender, sendResponse);
            return true; // Keep message channel open for async responses
        });

        // Handle tab updates to inject content scripts
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            this.handleTabUpdate(tabId, changeInfo, tab);
        });
    }

    handleInstallation(details) {
        if (details.reason === 'install') {
            console.log('Hate Speech Detector extension installed');
            
            // Set default settings
            chrome.storage.sync.set({
                apiUrl: 'http://localhost:8000',
                apiKey: 'industry-demo-key-12345',
                autoAnalyze: false,
                toxicityThreshold: 0.5,
                enabledPlatforms: {
                    instagram: true,
                    twitter: true,
                    youtube: true,
                    facebook: true,
                    reddit: true,
                    tiktok: true,
                    discord: true,
                    linkedin: true
                }
            });

            // Open welcome page
            chrome.tabs.create({
                url: chrome.runtime.getURL('welcome.html')
            });
        }
    }

    async handleMessage(request, sender, sendResponse) {
        try {
            switch (request.action) {
                case 'analyzeText':
                    const result = await this.analyzeText(request.text);
                    sendResponse({ success: true, result });
                    break;

                case 'getSettings':
                    const settings = await this.getSettings();
                    sendResponse({ success: true, settings });
                    break;

                case 'saveSettings':
                    await this.saveSettings(request.settings);
                    sendResponse({ success: true });
                    break;

                case 'checkApiHealth':
                    const health = await this.checkApiHealth();
                    sendResponse({ success: true, health });
                    break;

                default:
                    sendResponse({ success: false, error: 'Unknown action' });
            }
        } catch (error) {
            console.error('Background script error:', error);
            sendResponse({ success: false, error: error.message });
        }
    }

    handleTabUpdate(tabId, changeInfo, tab) {
        // Inject content script when page is loaded
        if (changeInfo.status === 'complete' && tab.url) {
            const supportedSites = [
                'instagram.com',
                'twitter.com',
                'x.com',
                'youtube.com',
                'facebook.com',
                'reddit.com',
                'tiktok.com',
                'discord.com',
                'linkedin.com'
            ];

            const isSupported = supportedSites.some(site => tab.url.includes(site));
            
            if (isSupported) {
                chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    files: ['content.js']
                }).catch(error => {
                    // Ignore errors for tabs we can't access
                    console.log('Could not inject content script:', error);
                });
            }
        }
    }

    async analyzeText(text) {
        const settings = await this.getSettings();
        
        const response = await fetch(`${settings.apiUrl}/api/v1/moderation/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': settings.apiKey
            },
            body: JSON.stringify({
                text: text,
                user_id: 'browser_extension_user'
            })
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        return await response.json();
    }

    async getSettings() {
        return new Promise((resolve) => {
            chrome.storage.sync.get([
                'apiUrl',
                'apiKey',
                'autoAnalyze',
                'toxicityThreshold',
                'enabledPlatforms'
            ], (result) => {
                resolve({
                    apiUrl: result.apiUrl || 'http://localhost:8000',
                    apiKey: result.apiKey || 'industry-demo-key-12345',
                    autoAnalyze: result.autoAnalyze || false,
                    toxicityThreshold: result.toxicityThreshold || 0.5,
                    enabledPlatforms: result.enabledPlatforms || {
                        instagram: true,
                        twitter: true,
                        youtube: true,
                        facebook: true,
                        reddit: true,
                        tiktok: true,
                        discord: true,
                        linkedin: true
                    }
                });
            });
        });
    }

    async saveSettings(settings) {
        return new Promise((resolve) => {
            chrome.storage.sync.set(settings, () => {
                resolve();
            });
        });
    }

    async checkApiHealth() {
        try {
            const settings = await this.getSettings();
            
            const response = await fetch(`${settings.apiUrl}/api/v1/health`, {
                headers: {
                    'X-API-Key': settings.apiKey
                }
            });

            return {
                online: response.ok,
                status: response.status,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            return {
                online: false,
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }
}

// Initialize background service
new BackgroundService();
