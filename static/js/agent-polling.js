/**
 * Reusable polling system for NetCop AI agents
 * Handles async request polling with proper cleanup and error handling
 */

class AgentPoller {
    constructor(config) {
        this.requestId = config.requestId;
        this.statusUrl = config.statusUrl;
        this.maxPolls = config.maxPolls || 30;
        this.pollInterval = config.pollInterval || 1000;
        this.onComplete = config.onComplete;
        this.onError = config.onError;
        this.onTimeout = config.onTimeout;
        
        // Internal state
        this.pollCount = 0;
        this.currentInterval = null;
        this.isPolling = false;
        this.resultsDisplayed = false;
    }

    start() {
        if (this.isPolling) {
            console.warn('Poller is already running');
            return;
        }

        this.isPolling = true;
        this.pollCount = 0;
        this.resultsDisplayed = false;

        // Clear any existing interval
        this.stop();

        this.currentInterval = setInterval(() => {
            this.pollCount++;
            
            fetch(this.statusUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    return response.json();
                })
                .then(result => {
                    if (result.status === 'completed' || result.status === 'failed') {
                        this.stop();
                        
                        // Display results only once
                        if (!this.resultsDisplayed) {
                            this.resultsDisplayed = true;
                            if (this.onComplete) {
                                this.onComplete(result);
                            }
                        }
                    } else if (this.pollCount >= this.maxPolls) {
                        this.stop();
                        if (this.onTimeout) {
                            this.onTimeout();
                        }
                    }
                })
                .catch(error => {
                    console.error('Error polling results:', error);
                    this.stop();
                    if (this.onError) {
                        this.onError(error);
                    }
                });
        }, this.pollInterval);
    }

    stop() {
        if (this.currentInterval) {
            clearInterval(this.currentInterval);
            this.currentInterval = null;
        }
        this.isPolling = false;
    }

    isRunning() {
        return this.isPolling;
    }
}

/**
 * Global polling manager to handle multiple pollers
 */
class PollingManager {
    constructor() {
        this.pollers = new Map();
    }

    createPoller(id, config) {
        // Stop existing poller if any
        this.stopPoller(id);
        
        const poller = new AgentPoller(config);
        this.pollers.set(id, poller);
        return poller;
    }

    stopPoller(id) {
        const poller = this.pollers.get(id);
        if (poller) {
            poller.stop();
            this.pollers.delete(id);
        }
    }

    stopAll() {
        this.pollers.forEach(poller => poller.stop());
        this.pollers.clear();
    }
}

// Global instance
window.pollingManager = new PollingManager();

/**
 * Utility functions for common agent UI operations
 */
window.AgentUtils = {
    // Update wallet balance display
    updateWalletBalance(newBalance) {
        const balanceElement = document.querySelector('[data-wallet-balance]') || 
                              document.getElementById('walletBalance');
        if (balanceElement) {
            balanceElement.textContent = `${newBalance.toFixed(2)} AED`;
        }
        window.currentWalletBalance = newBalance;
    },

    // Reset UI to initial state
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
        }

        if (elements.results) {
            elements.results.style.display = 'none';
        }
    },

    // Show processing status
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
            elements.processButton.innerHTML = config.processingText || '⏳ Processing...';
        }

        if (elements.results) {
            elements.results.style.display = 'none';
        }
    },

    // Show toast notification
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