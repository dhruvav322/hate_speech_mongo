// Browser Extension Popup JavaScript
class HateSpeechDetector {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
        this.apiKey = 'industry-demo-key-12345';
        this.currentTab = null;
        this.init();
    }

    async init() {
        await this.getCurrentTab();
        this.setupEventListeners();
        this.detectPlatform();
        this.checkApiStatus();
    }

    async getCurrentTab() {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        this.currentTab = tab;
    }

    setupEventListeners() {
        document.getElementById('analyzeBtn').addEventListener('click', () => this.analyzePage());
        document.getElementById('selectBtn').addEventListener('click', () => this.selectText());
        document.getElementById('settingsBtn').addEventListener('click', () => this.openSettings());
    }

    detectPlatform() {
        if (!this.currentTab) return;

        const url = this.currentTab.url || '';

        if (!url) {
            document.getElementById('platformIcon').textContent = '🌐';
            document.getElementById('platformName').textContent = 'Unknown Platform';
            document.getElementById('platformUrl').textContent = 'Unsupported page';
            return;
        }

        const platformInfo = this.getPlatformInfo(url);

        document.getElementById('platformIcon').textContent = platformInfo.icon;
        document.getElementById('platformName').textContent = platformInfo.name;
        document.getElementById('platformUrl').textContent = this.truncateUrl(url);
    }

    getPlatformInfo(url) {
        if (!url || typeof url !== 'string') {
            return { name: 'Unknown Platform', icon: '🌐' };
        }

        const platforms = {
            'instagram.com': { name: 'Instagram', icon: '📷' },
            'twitter.com': { name: 'Twitter', icon: '🐦' },
            'x.com': { name: 'X (Twitter)', icon: '❌' },
            'youtube.com': { name: 'YouTube', icon: '📺' },
            'facebook.com': { name: 'Facebook', icon: '📘' },
            'reddit.com': { name: 'Reddit', icon: '🤖' },
            'tiktok.com': { name: 'TikTok', icon: '🎵' },
            'discord.com': { name: 'Discord', icon: '💬' },
            'linkedin.com': { name: 'LinkedIn', icon: '💼' }
        };

        for (const [domain, info] of Object.entries(platforms)) {
            if (url.includes(domain)) {
                return info;
            }
        }

        return { name: 'Unknown Platform', icon: '🌐' };
    }

    truncateUrl(url) {
        if (url.length > 40) {
            return url.substring(0, 37) + '...';
        }
        return url;
    }

    async checkApiStatus() {
        try {
            const response = await fetch(`${this.apiUrl}/api/v1/health`, {
                headers: {
                    'X-API-Key': this.apiKey
                }
            });

            if (response.ok) {
                this.updateApiStatus('healthy', 'API Online');
            } else {
                this.updateApiStatus('error', 'API Error');
            }
        } catch (error) {
            this.updateApiStatus('error', 'API Offline');
        }
    }

    updateApiStatus(status, text) {
        const statusElement = document.getElementById('apiStatus');
        const dot = statusElement.querySelector('.status-dot');
        const span = statusElement.querySelector('span');

        dot.style.background = status === 'healthy' ? '#10b981' : '#ef4444';
        span.textContent = text;
    }

    async analyzePage() {
        this.showLoading();

        try {
            // Extract text from the current page
            const texts = await this.extractPageText();
            
            if (texts.length === 0) {
                throw new Error('No text content found on this page');
            }

            // Analyze each text with our API
            const results = await this.analyzeTexts(texts);
            
            // Display results
            this.displayResults(results);

        } catch (error) {
            this.showError(error.message);
        }
    }

    async extractPageText() {
        return new Promise((resolve) => {
            chrome.tabs.sendMessage(this.currentTab.id, { action: 'extractText' }, (response) => {
                if (chrome.runtime.lastError) {
                    // If content script not injected, inject it
                    chrome.scripting.executeScript({
                        target: { tabId: this.currentTab.id },
                        files: ['content.js']
                    }, () => {
                        // Try again after injection
                        chrome.tabs.sendMessage(this.currentTab.id, { action: 'extractText' }, (response) => {
                            resolve(response?.texts || []);
                        });
                    });
                } else {
                    resolve(response?.texts || []);
                }
            });
        });
    }

    async analyzeTexts(texts) {
        const results = [];
        const batchSize = 10; // Analyze in batches to avoid overwhelming the API

        for (let i = 0; i < texts.length; i += batchSize) {
            const batch = texts.slice(i, i + batchSize);
            const batchPromises = batch.map(text => this.analyzeText(text));
            const batchResults = await Promise.allSettled(batchPromises);
            
            batchResults.forEach((result, index) => {
                if (result.status === 'fulfilled') {
                    results.push({
                        text: batch[index],
                        analysis: result.value
                    });
                }
            });
        }

        return results;
    }

    async analyzeText(text) {
        const response = await fetch(`${this.apiUrl}/api/v1/moderation/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.apiKey
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

    displayResults(results) {
        if (results.length === 0) {
            this.showError('No valid analysis results');
            return;
        }

        // Calculate statistics
        const stats = this.calculateStats(results);
        
        // Update UI
        document.getElementById('totalTexts').textContent = results.length;
        document.getElementById('toxicRatio').textContent = `${stats.toxicRatio.toFixed(1)}%`;
        document.getElementById('avgToxicity').textContent = `${(stats.avgToxicity * 100).toFixed(1)}%`;
        document.getElementById('confidence').textContent = `${(stats.avgConfidence * 100).toFixed(0)}% confidence`;

        // Update action breakdown
        document.getElementById('allowCount').textContent = stats.breakdown.allow;
        document.getElementById('flagCount').textContent = stats.breakdown.flag;
        document.getElementById('blockCount').textContent = stats.breakdown.block;

        // Show toxic samples
        this.displayToxicSamples(stats.toxicSamples);

        // Show results section
        this.hideLoading();
        document.getElementById('results').classList.remove('hidden');
    }

    calculateStats(results) {
        let totalToxicity = 0;
        let totalConfidence = 0;
        const breakdown = { allow: 0, flag: 0, block: 0 };
        const toxicSamples = [];

        results.forEach(result => {
            const analysis = result.analysis;
            const toxicityScore = analysis.analysis.toxicity_score;
            
            totalToxicity += toxicityScore;
            totalConfidence += analysis.analysis.confidence;

            // Count actions
            breakdown[analysis.recommended_action]++;

            // Collect toxic samples
            if (toxicityScore >= 0.4) {
                toxicSamples.push({
                    text: result.text,
                    score: toxicityScore,
                    action: analysis.recommended_action
                });
            }
        });

        // Sort toxic samples by score
        toxicSamples.sort((a, b) => b.score - a.score);

        return {
            avgToxicity: totalToxicity / results.length,
            avgConfidence: totalConfidence / results.length,
            toxicRatio: (toxicSamples.length / results.length) * 100,
            breakdown,
            toxicSamples: toxicSamples.slice(0, 5) // Top 5
        };
    }

    displayToxicSamples(samples) {
        const container = document.getElementById('samplesList');
        container.innerHTML = '';

        if (samples.length === 0) {
            container.innerHTML = '<div class="no-samples">No toxic content detected</div>';
            return;
        }

        samples.forEach(sample => {
            const sampleDiv = document.createElement('div');
            sampleDiv.className = 'sample-item';
            
            const truncatedText = sample.text.length > 100 
                ? sample.text.substring(0, 97) + '...' 
                : sample.text;

            sampleDiv.innerHTML = `
                <div class="sample-text">"${truncatedText}"</div>
                <div class="sample-score">${(sample.score * 100).toFixed(1)}% toxic • ${sample.action.toUpperCase()}</div>
            `;
            
            container.appendChild(sampleDiv);
        });
    }

    async selectText() {
        try {
            // Enable text selection mode
            chrome.tabs.sendMessage(this.currentTab.id, { action: 'enableSelection' });
            
            // Close popup to let user select text
            window.close();
        } catch (error) {
            this.showError('Failed to enable text selection mode');
        }
    }

    openSettings() {
        // Open options page or settings
        chrome.runtime.openOptionsPage();
    }

    showLoading() {
        document.getElementById('results').classList.add('hidden');
        document.getElementById('error').classList.add('hidden');
        document.getElementById('loading').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }

    showError(message) {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('results').classList.add('hidden');
        document.getElementById('errorMessage').textContent = message;
        document.getElementById('error').classList.remove('hidden');
    }
}

// Initialize the extension when popup loads
document.addEventListener('DOMContentLoaded', () => {
    new HateSpeechDetector();
});
