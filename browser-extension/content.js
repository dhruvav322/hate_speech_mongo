// Content Script for Text Extraction
class TextExtractor {
    constructor() {
        this.selectionMode = false;
        this.setupMessageListener();
    }

    setupMessageListener() {
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            if (request.action === 'extractText') {
                const texts = this.extractPageText();
                sendResponse({ texts });
            } else if (request.action === 'enableSelection') {
                this.enableSelectionMode();
                sendResponse({ success: true });
            }
        });
    }

    extractPageText() {
        const texts = [];
        const platform = this.detectPlatform();
        
        // Platform-specific text extraction
        switch (platform) {
            case 'instagram':
                texts.push(...this.extractInstagramText());
                break;
            case 'twitter':
            case 'x':
                texts.push(...this.extractTwitterText());
                break;
            case 'youtube':
                texts.push(...this.extractYouTubeText());
                break;
            case 'facebook':
                texts.push(...this.extractFacebookText());
                break;
            case 'reddit':
                texts.push(...this.extractRedditText());
                break;
            case 'tiktok':
                texts.push(...this.extractTikTokText());
                break;
            case 'discord':
                texts.push(...this.extractDiscordText());
                break;
            case 'linkedin':
                texts.push(...this.extractLinkedInText());
                break;
            default:
                texts.push(...this.extractGenericText());
        }

        // Filter and clean texts
        return this.filterTexts(texts);
    }

    detectPlatform() {
        const hostname = window.location.hostname.toLowerCase();
        
        if (hostname.includes('instagram.com')) return 'instagram';
        if (hostname.includes('twitter.com') || hostname.includes('x.com')) return 'twitter';
        if (hostname.includes('youtube.com')) return 'youtube';
        if (hostname.includes('facebook.com')) return 'facebook';
        if (hostname.includes('reddit.com')) return 'reddit';
        if (hostname.includes('tiktok.com')) return 'tiktok';
        if (hostname.includes('discord.com')) return 'discord';
        if (hostname.includes('linkedin.com')) return 'linkedin';
        
        return 'generic';
    }

    extractInstagramText() {
        const texts = [];
        
        // Instagram comments
        const commentSelectors = [
            'article span[dir="auto"]', // Comments
            'div[data-testid="comment"] span', // Comment text
            'span._aacl._aaco._aacu._aacx._aad7._aade', // Comment spans
            'div[role="button"] span', // Interactive text
        ];
        
        commentSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                const text = this.getCleanText(el);
                if (text && text.length > 3) {
                    texts.push(text);
                }
            });
        });

        return texts;
    }

    extractTwitterText() {
        const texts = [];
        
        // Twitter/X tweets and replies
        const tweetSelectors = [
            '[data-testid="tweetText"]', // Tweet content
            '[data-testid="reply"] span', // Reply text
            'div[lang] span', // Text with language attribute
            '[role="group"] span', // Interactive text groups
        ];
        
        tweetSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                const text = this.getCleanText(el);
                if (text && text.length > 3) {
                    texts.push(text);
                }
            });
        });

        return texts;
    }

    extractYouTubeText() {
        const texts = [];
        
        // YouTube comments
        const commentSelectors = [
            '#content-text', // Comment content
            '#comment-content span', // Comment spans
            'yt-formatted-string#content-text', // Formatted comment text
            '.ytd-comment-renderer #content-text', // Comment renderer text
        ];
        
        commentSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                const text = this.getCleanText(el);
                if (text && text.length > 3) {
                    texts.push(text);
                }
            });
        });

        return texts;
    }

    extractFacebookText() {
        const texts = [];
        
        // Facebook posts and comments
        const postSelectors = [
            '[data-ad-preview="message"] span', // Post content
            'div[dir="auto"] span', // Auto-direction text
            '[role="article"] span', // Article content
            '.userContent span', // User content
        ];
        
        postSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                const text = this.getCleanText(el);
                if (text && text.length > 3) {
                    texts.push(text);
                }
            });
        });

        return texts;
    }

    extractRedditText() {
        const texts = [];
        
        // Reddit posts and comments
        const redditSelectors = [
            '[data-testid="comment"] p', // Comment paragraphs
            '.usertext-body p', // User text body
            '[data-click-id="text"] p', // Text content
            'div[data-testid="post-content"] p', // Post content
        ];
        
        redditSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                const text = this.getCleanText(el);
                if (text && text.length > 3) {
                    texts.push(text);
                }
            });
        });

        return texts;
    }

    extractTikTokText() {
        const texts = [];
        
        // TikTok comments
        const tikTokSelectors = [
            '[data-e2e="comment-item"] span', // Comment items
            '.comment-text span', // Comment text
            '[data-testid="browse-comment"] span', // Browse comments
        ];
        
        tikTokSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                const text = this.getCleanText(el);
                if (text && text.length > 3) {
                    texts.push(text);
                }
            });
        });

        return texts;
    }

    extractDiscordText() {
        const texts = [];
        
        // Discord messages
        const discordSelectors = [
            '[class*="messageContent"]', // Message content
            '[class*="markup"] span', // Markup spans
            'div[id^="message-content"] span', // Message content divs
        ];
        
        discordSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                const text = this.getCleanText(el);
                if (text && text.length > 3) {
                    texts.push(text);
                }
            });
        });

        return texts;
    }

    extractLinkedInText() {
        const texts = [];
        
        // LinkedIn posts and comments
        const linkedInSelectors = [
            '.feed-shared-text span', // Feed text
            '[data-test-id="comment"] span', // Comments
            '.update-components-text span', // Update text
        ];
        
        linkedInSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                const text = this.getCleanText(el);
                if (text && text.length > 3) {
                    texts.push(text);
                }
            });
        });

        return texts;
    }

    extractGenericText() {
        const texts = [];
        
        // Generic text extraction for any website
        const genericSelectors = [
            'p', // Paragraphs
            'span', // Spans
            'div[class*="comment"]', // Comment divs
            'div[class*="message"]', // Message divs
            'div[class*="post"]', // Post divs
            'div[class*="text"]', // Text divs
        ];
        
        genericSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                const text = this.getCleanText(el);
                if (text && text.length > 10 && text.length < 500) {
                    texts.push(text);
                }
            });
        });

        return texts;
    }

    getCleanText(element) {
        if (!element) return '';
        
        // Get text content and clean it
        let text = element.textContent || element.innerText || '';
        
        // Remove extra whitespace
        text = text.trim().replace(/\s+/g, ' ');
        
        // Remove URLs
        text = text.replace(/https?:\/\/[^\s]+/g, '');
        
        // Remove mentions and hashtags for cleaner analysis
        text = text.replace(/@\w+/g, '').replace(/#\w+/g, '');
        
        // Remove emojis (optional - they might be relevant for sentiment)
        // text = text.replace(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]/gu, '');
        
        return text.trim();
    }

    filterTexts(texts) {
        // Remove duplicates and filter by quality
        const uniqueTexts = [...new Set(texts)];
        
        return uniqueTexts.filter(text => {
            // Filter criteria
            if (!text || text.length < 5) return false; // Too short
            if (text.length > 1000) return false; // Too long
            if (/^[0-9\s\.\,\!\?\-]+$/.test(text)) return false; // Only numbers/punctuation
            if (text.split(' ').length < 2) return false; // Single word
            
            return true;
        }).slice(0, 50); // Limit to 50 texts for performance
    }

    enableSelectionMode() {
        this.selectionMode = true;
        
        // Add visual indicator
        const indicator = document.createElement('div');
        indicator.id = 'hate-speech-detector-indicator';
        indicator.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: #3b82f6;
                color: white;
                padding: 12px 16px;
                border-radius: 8px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
                font-weight: 500;
                z-index: 10000;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                cursor: pointer;
            ">
                🛡️ Select text to analyze • Click to cancel
            </div>
        `;
        
        document.body.appendChild(indicator);
        
        // Add click handler to cancel
        indicator.addEventListener('click', () => {
            this.disableSelectionMode();
        });
        
        // Add selection handler
        document.addEventListener('mouseup', this.handleTextSelection.bind(this));
    }

    disableSelectionMode() {
        this.selectionMode = false;
        
        // Remove indicator
        const indicator = document.getElementById('hate-speech-detector-indicator');
        if (indicator) {
            indicator.remove();
        }
        
        // Remove selection handler
        document.removeEventListener('mouseup', this.handleTextSelection.bind(this));
    }

    async handleTextSelection() {
        if (!this.selectionMode) return;
        
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();
        
        if (selectedText && selectedText.length > 5) {
            // Analyze selected text
            try {
                const response = await fetch('http://localhost:8000/api/v1/moderation/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': 'industry-demo-key-12345'
                    },
                    body: JSON.stringify({
                        text: selectedText,
                        user_id: 'browser_extension_selection'
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    this.showSelectionResult(result, selectedText);
                }
            } catch (error) {
                console.error('Analysis failed:', error);
            }
        }
        
        this.disableSelectionMode();
    }

    showSelectionResult(result, text) {
        // Create result popup
        const popup = document.createElement('div');
        popup.id = 'hate-speech-result-popup';
        
        const toxicityScore = (result.analysis.toxicity_score * 100).toFixed(1);
        const action = result.recommended_action;
        const actionColor = action === 'allow' ? '#10b981' : action === 'flag' ? '#f59e0b' : '#ef4444';
        
        popup.innerHTML = `
            <div style="
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                border-radius: 12px;
                padding: 24px;
                max-width: 400px;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                z-index: 10001;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 16px;">
                    <div style="
                        width: 40px;
                        height: 40px;
                        background: ${actionColor};
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 12px;
                        color: white;
                        font-size: 18px;
                    ">🛡️</div>
                    <div>
                        <h3 style="margin: 0; font-size: 18px; font-weight: 600;">Analysis Result</h3>
                        <p style="margin: 4px 0 0 0; color: #64748b; font-size: 14px;">AI-powered toxicity detection</p>
                    </div>
                </div>
                
                <div style="
                    background: #f8fafc;
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 16px;
                    border-left: 4px solid ${actionColor};
                ">
                    <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">Selected Text:</div>
                    <div style="font-size: 14px; color: #1e293b;">"${text.length > 100 ? text.substring(0, 97) + '...' : text}"</div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: 700; color: ${actionColor};">${toxicityScore}%</div>
                        <div style="font-size: 12px; color: #64748b;">Toxicity Score</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="
                            font-size: 14px; 
                            font-weight: 600; 
                            color: ${actionColor};
                            text-transform: uppercase;
                            background: ${actionColor}20;
                            padding: 4px 8px;
                            border-radius: 4px;
                        ">${action}</div>
                        <div style="font-size: 12px; color: #64748b; margin-top: 4px;">Recommendation</div>
                    </div>
                </div>
                
                <button onclick="document.getElementById('hate-speech-result-popup').remove()" style="
                    width: 100%;
                    background: #3b82f6;
                    color: white;
                    border: none;
                    padding: 12px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                ">Close</button>
            </div>
        `;
        
        document.body.appendChild(popup);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (document.getElementById('hate-speech-result-popup')) {
                popup.remove();
            }
        }, 10000);
    }
}

// Initialize content script
new TextExtractor();
