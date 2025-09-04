/**
 * NetCop AI Agents - Shared Utilities
 * Contains common functions used across all agent templates
 */

window.AgentUtils = {
    /**
     * Enhanced Markdown Parser
     * Converts markdown syntax to styled HTML with proper formatting
     */
    parseMarkdown(text) {
        // Handle null, undefined, or non-string inputs
        if (!text || typeof text !== 'string') {
            return '';
        }
        
        let html = text;
        
        // Convert headers with proper styling
        html = html.replace(/^### (.*$)/gm, '<h3 style="font-size: 1.1em; font-weight: 600; margin: 12px 0 8px 0; color: #374151;">$1</h3>');
        html = html.replace(/^## (.*$)/gm, '<h2 style="font-size: 1.2em; font-weight: 600; margin: 14px 0 8px 0; color: #374151;">$1</h2>');
        html = html.replace(/^# (.*$)/gm, '<h1 style="font-size: 1.3em; font-weight: 600; margin: 16px 0 10px 0; color: #374151;">$1</h1>');
        
        // Convert bold text
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight: 500; color: #1f2937;">$1</strong>');
        
        // Convert bullet points to proper lists
        const lines = html.split('\n');
        let inList = false;
        let processedLines = [];
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            if (line.startsWith('- ')) {
                if (!inList) {
                    processedLines.push('<ul style="margin: 8px 0; padding-left: 20px;">');
                    inList = true;
                }
                processedLines.push(`<li style="margin: 3px 0; color: #4b5563;">${line.substring(2).trim()}</li>`);
            } else {
                if (inList) {
                    processedLines.push('</ul>');
                    inList = false;
                }
                processedLines.push(line);
            }
        }
        
        if (inList) {
            processedLines.push('</ul>');
        }
        
        html = processedLines.join('\n');
        
        // Reduce excessive line breaks and convert to paragraphs
        html = html.replace(/\n{3,}/g, '\n\n');
        
        // Convert double line breaks to paragraph breaks
        const paragraphs = html.split('\n\n');
        html = paragraphs
            .filter(p => p.trim() !== '')
            .map(p => {
                const trimmed = p.trim();
                // Don't wrap headers or lists in paragraphs
                if (trimmed.startsWith('<h') || trimmed.startsWith('<ul') || trimmed.startsWith('</ul>') || trimmed.includes('<li')) {
                    return trimmed;
                }
                return `<p style="margin: 8px 0; line-height: 1.4; color: #4b5563;">${trimmed}</p>`;
            })
            .join('');
        
        // Convert remaining single line breaks to <br> tags
        html = html.replace(/\n/g, '<br>');
        
        return html.trim();
    },

    /**
     * Update wallet balance display across all agents
     */
    updateWalletBalance(newBalance) {
        // Update all wallet balance elements
        document.querySelectorAll('[data-wallet-balance]').forEach(element => {
            if (element.tagName === 'A') {
                // Header balance with emoji (anchor tag)
                element.textContent = `💰 ${newBalance.toFixed(2)} AED`;
            } else {
                // Page balance without emoji (div or other elements)
                element.textContent = `${newBalance.toFixed(2)} AED`;
            }
        });
        
        // Fallback for old ID-based elements
        const legacyElement = document.getElementById('walletBalance');
        if (legacyElement) {
            legacyElement.textContent = `${newBalance.toFixed(2)} AED`;
        }
        
        window.currentWalletBalance = newBalance;
    },

    /**
     * Reset UI to initial state
     */
    resetUI(config) {
        const elements = {
            processingStatus: document.getElementById(config.processingStatusId || 'processingStatus'),
            processButton: document.getElementById(config.processButtonId || 'processButton'),
            results: document.getElementById(config.resultsId)
        };

        if (elements.processingStatus) {
            elements.processingStatus.style.display = 'none';
        }
        
        if (elements.processButton) {
            elements.processButton.disabled = false;
            elements.processButton.innerHTML = config.buttonText || 'Process';
            elements.processButton.classList.remove('loading');
        }

        if (elements.results) {
            elements.results.style.display = 'none';
        }
    },

    /**
     * Show processing status
     */
    showProcessing(config) {
        const elements = {
            processingStatus: document.getElementById(config.processingStatusId || 'processingStatus'),
            processButton: document.getElementById(config.processButtonId || 'processButton'),
            results: document.getElementById(config.resultsId)
        };

        if (elements.processingStatus) {
            elements.processingStatus.style.display = 'block';
        }
        
        if (elements.processButton) {
            elements.processButton.disabled = true;
            elements.processButton.classList.add('loading');
            elements.processButton.innerHTML = config.processingText || '⏳ Processing...';
        }

        if (elements.results) {
            elements.results.style.display = 'none';
        }
    },

    /**
     * Show toast notification with duplicate prevention
     */
    showToast(message, type = 'info') {
        // Prevent duplicate toasts
        const existingToast = document.querySelector('.agent-toast');
        if (existingToast) {
            existingToast.remove();
        }

        const toast = document.createElement('div');
        toast.className = 'agent-toast';
        toast.style.cssText = `
            position: fixed;
            top: 16px;
            right: 16px;
            padding: 8px 12px;
            border-radius: 4px;
            color: white;
            font-size: 13px;
            z-index: 1000;
            max-width: 300px;
            font-weight: 500;
            ${type === 'success' ? 'background: #10b981;' : 'background: #ef4444;'}
        `;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 2000);
    },

    // NOTE: displayResults() function removed - each agent now has its own custom display logic

    /**
     * Generate text for copy/download functionality
     */
    generateTextForExport(contentElementId) {
        const content = document.getElementById(contentElementId);
        if (content) {
            return content.innerText || content.textContent || '';
        }
        return 'No content available';
    },

    /**
     * Copy content to clipboard
     */
    copyToClipboard(text, successMessage = 'Content copied to clipboard!') {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast(`📋 ${successMessage}`, 'success');
        }).catch(() => {
            this.showToast('Failed to copy content', 'error');
        });
    },

    /**
     * Download content as text file
     */
    downloadAsFile(text, filename, successMessage = 'File downloaded!') {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename || `content-${Date.now()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        this.showToast(`💾 ${successMessage}`, 'success');
    }
};

/**
 * Progressive status steps for better UX
 */
window.StatusStepper = class {
    constructor(steps, statusTextElementId, interval = 800) {
        this.steps = steps;
        this.statusTextElement = document.getElementById(statusTextElementId);
        this.interval = interval;
        this.currentStep = 0;
        this.stepInterval = null;
    }

    start() {
        this.currentStep = 0;
        this.stepInterval = setInterval(() => {
            if (this.currentStep < this.steps.length && this.statusTextElement) {
                this.statusTextElement.textContent = this.steps[this.currentStep];
                this.currentStep++;
            } else {
                this.stop();
            }
        }, this.interval);
    }

    stop() {
        if (this.stepInterval) {
            clearInterval(this.stepInterval);
            this.stepInterval = null;
        }
    }
};