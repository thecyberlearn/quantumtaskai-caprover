/**
 * Workflows Core - Base functionality for all agents and workflows
 * Provides common utilities, toast notifications, and form handling
 */

class WorkflowsCore {
    constructor() {
        // Base initialization
    }
    
    /**
     * Generate unique session ID
     */
    static generateSessionId() {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(2, 8);
        return `session_${timestamp}_${random}`;
    }
    
    /**
     * Show toast notification
     */
    static showToast(message, type = 'info') {
        console.log('Showing toast:', message, type);
        
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 99999;
                max-width: 400px;
                pointer-events: none;
            `;
            
            // Safely append to body
            const targetElement = document.body || document.documentElement;
            if (targetElement) {
                targetElement.appendChild(toastContainer);
                console.log('Created toast container');
            } else {
                console.error('Cannot create toast container - no body or documentElement');
                return;
            }
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            background: ${type === 'error' ? '#fee2e2' : type === 'success' ? '#d1fae5' : '#dbeafe'};
            color: ${type === 'error' ? '#dc2626' : type === 'success' ? '#059669' : '#2563eb'};
            border: 1px solid ${type === 'error' ? '#fecaca' : type === 'success' ? '#a7f3d0' : '#93c5fd'};
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            animation: slideIn 0.3s ease-out;
            pointer-events: auto;
            position: relative;
            z-index: 100000;
        `;
        
        // Add icon and message
        const icon = type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️';
        toast.innerHTML = `
            <span style="margin-right: 8px; font-size: 14px;">${icon}</span>
            <span style="flex: 1; font-size: 14px; font-weight: 500;">${message}</span>
            <button onclick="this.parentElement.remove()" style="
                background: none;
                border: none;
                color: inherit;
                cursor: pointer;
                margin-left: 8px;
                padding: 0;
                font-size: 16px;
            ">×</button>
        `;
        
        // Add animation styles if not already added
        if (!document.getElementById('toast-styles')) {
            const style = document.createElement('style');
            style.id = 'toast-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
        
        toastContainer.appendChild(toast);
        
        // Auto-remove after longer time for errors
        const timeout = type === 'error' ? 8000 : 5000; // 8 seconds for errors, 5 for others
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, timeout);
    }
    
    /**
     * Check if user is authenticated
     */
    static checkAuthentication() {
        const isAuthenticated = document.body.getAttribute('data-user-authenticated') === 'true';
        if (!isAuthenticated) {
            this.showToast('Please login to use this agent', 'error');
            setTimeout(() => {
                window.location.href = '/auth/login/';
            }, 2000);
            return false;
        }
        return true;
    }
    
    /**
     * Check if user has sufficient balance
     */
    static checkBalance(requiredAmount) {
        const userBalance = parseFloat(document.body.getAttribute('data-user-balance') || '0');
        
        if (userBalance < requiredAmount) {
            this.showToast(`Insufficient balance! You need ${requiredAmount} AED.`, 'error');
            setTimeout(() => {
                window.location.href = '/wallet/';
            }, 2000);
            return false;
        }
        return true;
    }
    
    /**
     * Show processing status
     */
    static showProcessing(message = 'Processing...') {
        const processingStatus = document.getElementById('processingStatus');
        if (processingStatus) {
            const statusText = processingStatus.querySelector('.status-text');
            if (statusText) {
                statusText.textContent = message;
            }
            processingStatus.style.display = 'block';
        }
    }
    
    /**
     * Hide processing status
     */
    static hideProcessing() {
        const processingStatus = document.getElementById('processingStatus');
        if (processingStatus) {
            processingStatus.style.display = 'none';
        }
    }
    
    /**
     * Show field error
     */
    static showFieldError(fieldName, message) {
        const errorElement = document.getElementById(`${fieldName}-error`);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
        
        const field = document.getElementById(fieldName);
        if (field) {
            field.classList.add('error');
        }
    }
    
    /**
     * Clear field error
     */
    static clearFieldError(fieldName) {
        const errorElement = document.getElementById(`${fieldName}-error`);
        if (errorElement) {
            errorElement.style.display = 'none';
        }
        
        const field = document.getElementById(fieldName);
        if (field) {
            field.classList.remove('error');
        }
    }
    
    /**
     * Update wallet balance display - TARGET CORRECT ELEMENT
     */
    static updateWalletBalance(newBalance) {
        console.log('Updating wallet balance to:', newBalance);
        
        // Target the specific walletBalance span element
        const walletElement = document.getElementById('walletBalance');
        
        if (walletElement) {
            const oldText = walletElement.textContent;
            walletElement.textContent = newBalance.toFixed(2);  // Just the number, no symbols
            console.log(`✅ Updated walletBalance from "${oldText}" to "${walletElement.textContent}"`);
        } else {
            console.warn('❌ walletBalance element not found, trying fallback approaches');
            
            // Fallback 1: Try other common selectors
            const fallbackElement = document.querySelector('.balance') || 
                                   document.querySelector('[data-wallet-balance]') ||
                                   document.querySelector('a[href*="wallet"]');
            
            if (fallbackElement) {
                const oldText = fallbackElement.textContent;
                fallbackElement.textContent = `💰 ${newBalance.toFixed(2)} AED`;
                console.log(`✅ Updated fallback element from "${oldText}" to "${fallbackElement.textContent}"`);
            } else {
                // Fallback 2: Find any element with AED in text
                console.log('Trying manual search for wallet elements...');
                let found = false;
                document.querySelectorAll('*').forEach(el => {
                    if (!found && el.textContent && el.textContent.includes('AED') && el.textContent.match(/\d+\.\d+/)) {
                        const oldText = el.textContent;
                        el.textContent = `💰 ${newBalance.toFixed(2)} AED`;
                        console.log(`✅ Updated manual element: ${oldText} -> ${el.textContent}`);
                        found = true;
                    }
                });
                
                if (!found) {
                    console.error('❌ No wallet balance elements found to update');
                }
            }
        }
        
        // Update data attribute for future calculations
        document.body.setAttribute('data-user-balance', newBalance.toString());
        console.log(`Updated data-user-balance to: ${newBalance.toString()}`);
    }
    
    /**
     * Debug function to show wallet elements
     */
    static debugWalletElements() {
        console.log('=== WALLET DEBUG INFO ===');
        document.querySelectorAll('*').forEach(el => {
            const text = el.textContent?.trim();
            if (text && text.includes('AED')) {
                console.log('AED Element:', {
                    tag: el.tagName,
                    class: el.className,
                    id: el.id,
                    text: text,
                    hasDataAttr: el.hasAttribute('data-wallet-balance'),
                    href: el.href || 'none'
                });
            }
        });
        console.log('========================');
    }
    
    /**
     * Copy text to clipboard
     */
    static copyToClipboard(text, successMessage = 'Copied to clipboard!') {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast(successMessage, 'success');
            }).catch(() => {
                this.fallbackCopyToClipboard(text, successMessage);
            });
        } else {
            this.fallbackCopyToClipboard(text, successMessage);
        }
    }
    
    /**
     * Fallback copy method for older browsers
     */
    static fallbackCopyToClipboard(text, successMessage) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showToast(successMessage, 'success');
        } catch (err) {
            this.showToast('Failed to copy to clipboard', 'error');
        } finally {
            textArea.remove();
        }
    }
    
    /**
     * Download text as file
     */
    static downloadAsFile(content, filename, successMessage = 'File downloaded!') {
        try {
            const blob = new Blob([content], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            this.showToast(successMessage, 'success');
        } catch (err) {
            this.showToast('Failed to download file', 'error');
        }
    }
    
    /**
     * Deduct balance via Django API (for direct N8N integrations)
     */
    static async deductBalance(amount, description, agentSlug) {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            
            const response = await fetch('/wallet/api/deduct/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    amount: amount,
                    description: description,
                    agent_slug: agentSlug
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateWalletBalance(data.new_balance);
                document.body.setAttribute('data-user-balance', data.new_balance.toString());
                return true;
            } else {
                console.warn('Failed to deduct balance:', response.status);
                return false;
            }
        } catch (error) {
            console.warn('Balance deduction error:', error);
            return false;
        }
    }
}

// Make available globally
window.WorkflowsCore = WorkflowsCore;