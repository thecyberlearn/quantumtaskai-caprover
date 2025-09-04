/**
 * Agent Template Starter - Template JavaScript File
 * Copy this file and customize for new agents
 * 
 * REPLACE THE FOLLOWING:
 * 1. "AgentTemplateProcessor" -> YourAgentProcessor
 * 2. "agent-template-starter" -> your-agent-slug
 * 3. webhook URL and price to match your agent config
 * 4. Form validation logic for your specific fields
 * 5. Results formatting for your agent's output
 * 
 * KEEP THE FOLLOWING:
 * - Class-based architecture extending WorkflowsCore
 * - Standard initialization and validation patterns
 * - File upload handling (if needed)
 * - Error handling and user feedback
 */

class AgentTemplateProcessor extends WorkflowsCore {
    constructor() {
        super();
        this.agentSlug = 'agent-template-starter'; // CUSTOMIZE: Change to your agent slug
        this.webhookUrl = 'http://localhost:5678/webhook/your-webhook-id'; // CUSTOMIZE: Set your N8N webhook URL
        this.price = 10.0; // CUSTOMIZE: Set your agent price (will be overridden by template data)
        this.sessionId = this.constructor.generateSessionId();
        
        // Initialize on page load
        this.initialize();
    }
    
    initialize() {
        // Set data attributes from page
        const priceElement = document.body.getAttribute('data-agent-price');
        if (priceElement) {
            this.price = parseFloat(priceElement);
        }
        
        // Initialize form submission
        const form = document.getElementById('agentForm');
        if (form) {
            form.addEventListener('submit', this.handleFormSubmission.bind(this));
        }
        
        // Initialize file upload functionality if present
        this.initializeFileUpload();
        
        // Initialize form validation
        this.initializeFormValidation();
        
        // Setup real-time validation
        this.setupRealTimeValidation();
    }
    
    /**
     * Initialize file upload functionality if file input exists
     */
    initializeFileUpload() {
        const fileInput = document.getElementById('example_file');
        if (fileInput) {
            fileInput.addEventListener('change', this.handleFileChange.bind(this));
            
            // Setup drag and drop
            const uploadArea = document.getElementById('fileUploadArea');
            if (uploadArea) {
                this.setupDragAndDrop(uploadArea, fileInput);
            }
        }
    }
    
    /**
     * Handle form submission with validation and processing
     * CUSTOMIZE: Modify validation logic for your specific fields
     */
    async handleFormSubmission(e) {
        e.preventDefault();
        
        if (!this.isFormValid()) {
            this.constructor.showToast('Please fix the errors in the form', 'error');
            return;
        }
        
        // Check authentication and balance
        if (!this.constructor.checkAuthentication()) return;
        if (!this.constructor.checkBalance(this.price)) return;
        
        // Show processing status and disable submit button
        this.constructor.showProcessing('Processing your request...');
        
        const submitBtn = document.getElementById('generateBtn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = '⏳ Processing...';
        }
        
        try {
            // CUSTOMIZE: Choose processing method based on your agent needs
            // For simple text-based agents, use processViaDjango
            // For file uploads or complex processing, use processViaDjangoImmediate
            await this.processViaDjango(e.target);
        } catch (error) {
            console.error('Form submission error:', error);
            this.constructor.hideProcessing();
            this.constructor.showToast('❌ Connection error. Please try again.', 'error');
            this.resetSubmitButton();
        }
    }
    
    /**
     * Standard Django processing with polling for results
     * CUSTOMIZE: Use this for agents that process via N8N webhooks
     */
    async processViaDjango(form) {
        const formData = new FormData(form);
        
        const response = await fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        
        const result = await response.json();
        
        if (result.success && result.workflow_request_id) {
            // Start polling for results
            this.startPolling(result.workflow_request_id);
            
            // Update wallet balance if provided
            if (result.wallet_balance !== undefined) {
                this.constructor.updateWalletBalance(result.wallet_balance);
            }
        } else {
            this.constructor.hideProcessing();
            this.constructor.showToast(`❌ ${result.error || 'Processing failed'}`, 'error');
            this.resetSubmitButton();
        }
    }
    
    /**
     * Immediate Django processing without polling
     * CUSTOMIZE: Use this for agents that return results immediately
     */
    async processViaDjangoImmediate(form) {
        const formData = new FormData(form);
        
        const response = await fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        
        const result = await response.json();
        
        if (result.success && result.results) {
            this.constructor.hideProcessing();
            
            if (result.wallet_balance !== undefined) {
                this.constructor.updateWalletBalance(result.wallet_balance);
            }
            
            // CUSTOMIZE: Format results for your agent
            const formattedHtml = this.formatResults(result.results);
            WorkflowsCore.showResults(formattedHtml, 'Generated Results');
            this.constructor.showToast('✅ Processing completed successfully!', 'success');
            
            this.resetSubmitButton();
        } else {
            this.constructor.hideProcessing();
            this.constructor.showToast(`❌ ${result.error || 'Processing failed'}`, 'error');
            this.resetSubmitButton();
        }
    }
    
    /**
     * Form validation specific to this agent
     * CUSTOMIZE: Add validation for your specific form fields
     */
    initializeFormValidation() {
        // Add validation for standard fields
        const exampleInput = document.getElementById('example_input');
        const exampleTextarea = document.getElementById('example_textarea');
        const exampleSelect = document.getElementById('example_select');
        const fileInput = document.getElementById('example_file');
        
        if (exampleInput) {
            exampleInput.addEventListener('blur', () => this.validateField('example_input'));
        }
        
        if (exampleTextarea) {
            exampleTextarea.addEventListener('blur', () => this.validateField('example_textarea'));
        }
        
        if (exampleSelect) {
            exampleSelect.addEventListener('change', () => this.validateField('example_select'));
        }
        
        if (fileInput) {
            fileInput.addEventListener('change', () => this.validateField('example_file'));
        }
    }
    
    /**
     * Validate individual form fields
     * CUSTOMIZE: Add validation rules for your specific fields
     */
    validateField(fieldName) {
        switch (fieldName) {
            case 'example_input':
                const inputField = document.getElementById('example_input');
                if (!inputField.value.trim()) {
                    this.constructor.showFieldError('example_input', 'This field is required');
                    return false;
                }
                // CUSTOMIZE: Add specific validation rules
                if (inputField.value.length < 3) {
                    this.constructor.showFieldError('example_input', 'Please enter at least 3 characters');
                    return false;
                }
                break;
                
            case 'example_textarea':
                const textareaField = document.getElementById('example_textarea');
                if (!textareaField.value.trim()) {
                    this.constructor.showFieldError('example_textarea', 'This field is required');
                    return false;
                }
                // CUSTOMIZE: Add specific validation rules
                if (textareaField.value.length < 10) {
                    this.constructor.showFieldError('example_textarea', 'Please provide more detailed information');
                    return false;
                }
                break;
                
            case 'example_select':
                const selectField = document.getElementById('example_select');
                if (!selectField.value) {
                    this.constructor.showFieldError('example_select', 'Please select an option');
                    return false;
                }
                break;
                
            case 'example_file':
                const fileField = document.getElementById('example_file');
                if (fileField.files && fileField.files.length > 0) {
                    const file = fileField.files[0];
                    const maxSize = 10 * 1024 * 1024; // 10MB
                    
                    if (file.size > maxSize) {
                        this.constructor.showFieldError('example_file', 'File size must be less than 10MB');
                        return false;
                    }
                    
                    // CUSTOMIZE: Add file type validation
                    const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
                    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
                    if (!allowedTypes.includes(fileExtension)) {
                        this.constructor.showFieldError('example_file', 'Unsupported file type');
                        return false;
                    }
                }
                break;
        }
        
        this.constructor.clearFieldError(fieldName);
        return true;
    }
    
    /**
     * Check if entire form is valid
     * CUSTOMIZE: Add all your required fields here
     */
    isFormValid() {
        const inputValid = this.validateField('example_input');
        const textareaValid = this.validateField('example_textarea');
        const selectValid = this.validateField('example_select');
        const fileValid = this.validateField('example_file');
        
        return inputValid && textareaValid && selectValid && fileValid;
    }
    
    /**
     * Setup real-time validation on user input
     */
    setupRealTimeValidation() {
        const inputs = document.querySelectorAll('#agentForm input, #agentForm textarea, #agentForm select');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                if (input.value.trim()) {
                    this.constructor.clearFieldError(input.name);
                }
            });
        });
    }
    
    /**
     * Handle file change events with enhanced UX
     */
    handleFileChange(event) {
        const file = event.target.files[0];
        const uploadArea = document.getElementById('fileUploadArea');
        const filePreview = document.getElementById('filePreview');
        const validationMessage = document.getElementById('validationMessage');
        
        if (file) {
            // Validate file first
            const validation = this.validateFileUpload(file);
            
            if (!validation.valid) {
                this.showValidationMessage(validation.message, 'error');
                if (uploadArea) {
                    uploadArea.classList.add('upload-error');
                    uploadArea.classList.remove('file-selected');
                }
                this.hideFilePreview();
                return;
            }
            
            // Show success validation
            this.showValidationMessage(validation.message, 'success');
            
            // Update upload area
            if (uploadArea) {
                uploadArea.classList.remove('upload-error');
                uploadArea.classList.add('file-selected');
            }
            
            // Show file preview
            this.showFilePreview(file);
            
            // Clear any previous errors
            this.constructor.clearFieldError('example_file');
        } else {
            this.resetFileUploadState();
        }
    }
    
    /**
     * Validate file upload with detailed feedback
     * CUSTOMIZE: Modify file validation rules for your agent
     */
    validateFileUpload(file) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = ['application/pdf', 'application/msword', 'text/plain'];
        const allowedExtensions = ['.pdf', '.doc', '.docx', '.txt'];
        
        // Check file type
        if (!allowedTypes.includes(file.type) && !allowedExtensions.includes('.' + file.name.split('.').pop().toLowerCase())) {
            return {
                valid: false,
                message: 'Invalid file type. Please upload PDF, DOC, or TXT files only.'
            };
        }
        
        // Check file size
        if (file.size > maxSize) {
            return {
                valid: false,
                message: `File too large (${this.formatFileSize(file.size)}). Maximum size is 10MB.`
            };
        }
        
        // Check for empty file
        if (file.size === 0) {
            return {
                valid: false,
                message: 'File appears to be empty. Please select a valid file.'
            };
        }
        
        return {
            valid: true,
            message: `✅ File validated successfully (${this.formatFileSize(file.size)})`
        };
    }
    
    /**
     * Show file preview with enhanced information
     */
    showFilePreview(file) {
        const filePreview = document.getElementById('filePreview');
        const previewFileName = document.getElementById('previewFileName');
        const previewFileSize = document.getElementById('previewFileSize');
        const previewTimestamp = document.getElementById('previewTimestamp');
        
        if (filePreview && previewFileName && previewFileSize && previewTimestamp) {
            previewFileName.textContent = file.name;
            previewFileSize.textContent = this.formatFileSize(file.size);
            previewTimestamp.textContent = `Added ${new Date().toLocaleTimeString()}`;
            
            filePreview.classList.add('show');
        }
    }
    
    /**
     * Hide file preview
     */
    hideFilePreview() {
        const filePreview = document.getElementById('filePreview');
        if (filePreview) {
            filePreview.classList.remove('show');
        }
    }
    
    /**
     * Show validation message with type
     */
    showValidationMessage(message, type = 'info') {
        const validationMessage = document.getElementById('validationMessage');
        if (validationMessage) {
            validationMessage.textContent = message;
            validationMessage.className = `validation-message show ${type}`;
        }
    }
    
    /**
     * Hide validation message
     */
    hideValidationMessage() {
        const validationMessage = document.getElementById('validationMessage');
        if (validationMessage) {
            validationMessage.classList.remove('show');
        }
    }
    
    /**
     * Reset file upload state
     */
    resetFileUploadState() {
        const uploadArea = document.getElementById('fileUploadArea');
        
        if (uploadArea) {
            uploadArea.classList.remove('file-selected', 'upload-error', 'uploading');
        }
        
        this.hideFilePreview();
        this.hideValidationMessage();
    }
    
    /**
     * Setup drag and drop functionality
     */
    setupDragAndDrop(uploadArea, fileInput) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });
        
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('dragover');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('dragover');
            }, false);
        });
        
        // Handle dropped files
        uploadArea.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }, false);
    }
    
    /**
     * Prevent default drag behaviors
     */
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    /**
     * Format file size for display
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    /**
     * Format results for HTML display
     * CUSTOMIZE: Modify this to format your agent's specific output
     */
    formatResults(resultsData) {
        let resultsHtml = '<h3>✅ Processing Complete</h3>';
        
        // CUSTOMIZE: Handle your agent's specific result format
        if (typeof resultsData === 'object' && resultsData.sections) {
            // Handle structured sections
            resultsHtml += '<div class="results-sections">';
            
            resultsData.sections.forEach(section => {
                if (section.heading && section.content) {
                    resultsHtml += `
                        <div style="background: var(--surface-variant); border-radius: var(--radius-md); padding: var(--spacing-lg); margin-bottom: var(--spacing-md); border-left: 4px solid var(--primary);">
                            <h4 style="color: var(--primary); font-weight: 600; margin: 0 0 var(--spacing-md) 0; font-size: 16px;">📋 ${this.escapeHtml(section.heading)}</h4>
                            <div style="color: var(--on-surface); line-height: 1.6; font-size: 14px;">${this.escapeHtml(section.content).replace(/\n/g, '<br>')}</div>
                        </div>
                    `;
                }
            });
            
            resultsHtml += '</div>';
        } else {
            // Handle simple text response
            const content = typeof resultsData === 'string' ? resultsData : JSON.stringify(resultsData, null, 2);
            resultsHtml += `
                <div style="background: var(--surface-variant); border-radius: var(--radius-md); padding: var(--spacing-lg); margin-bottom: var(--spacing-md); border-left: 4px solid var(--primary);">
                    <h4 style="color: var(--primary); font-weight: 600; margin: 0 0 var(--spacing-md) 0; font-size: 16px;">📊 Results</h4>
                    <div style="color: var(--on-surface); line-height: 1.6; font-size: 14px; white-space: pre-wrap;">${this.escapeHtml(content)}</div>
                </div>
            `;
        }
        
        // Add timestamp
        resultsHtml += `<p style="margin-top: var(--spacing-lg); text-align: center; color: var(--on-surface-variant);"><small>Completed: ${new Date().toLocaleString()}</small></p>`;
        
        return resultsHtml;
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Reset submit button to original state
     */
    resetSubmitButton() {
        const submitBtn = document.getElementById('generateBtn');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = `🚀 Generate (${this.price} AED)`; // CUSTOMIZE: Change action verb
        }
    }
}

// Global functions for template onclick handlers
// CUSTOMIZE: Add any additional global functions your agent needs

function triggerFileSelect() {
    const fileInput = document.getElementById('example_file');
    if (fileInput) {
        fileInput.click();
    }
}

function replaceFile() {
    const fileInput = document.getElementById('example_file');
    if (fileInput) {
        fileInput.value = '';
        fileInput.click();
    }
}

function removeFile() {
    const fileInput = document.getElementById('example_file');
    
    if (fileInput) {
        fileInput.value = '';
        
        // Reset all file upload states
        if (window.agentTemplateProcessor) {
            window.agentTemplateProcessor.resetFileUploadState();
        }
        
        // Clear form errors
        if (window.agentTemplateProcessor) {
            window.agentTemplateProcessor.constructor.clearFieldError('example_file');
        }
    }
}

// Result action functions (global for button onclick handlers)
function copyResults() {
    const content = document.getElementById('resultsContent');
    if (content) {
        const text = content.textContent || '';
        WorkflowsCore.copyToClipboard(text, 'Results copied to clipboard!');
    }
}

function downloadResults() {
    const content = document.getElementById('resultsContent');
    if (content) {
        const text = content.textContent || '';
        WorkflowsCore.downloadAsFile(text, 'agent-results.txt', 'Results downloaded!'); // CUSTOMIZE: Change filename
    }
}

function resetForm() {
    const form = document.getElementById('agentForm');
    if (form) {
        form.reset();
    }
    
    const resultsContainer = document.getElementById('resultsContainer');
    const processingStatus = document.getElementById('processingStatus');
    
    if (resultsContainer) resultsContainer.style.display = 'none';
    if (processingStatus) processingStatus.style.display = 'none';
    
    // Reset file upload state
    if (window.agentTemplateProcessor) {
        window.agentTemplateProcessor.resetFileUploadState();
    }
    
    // Clear validation errors
    WorkflowsCore.clearFieldError('example_input');
    WorkflowsCore.clearFieldError('example_textarea');
    WorkflowsCore.clearFieldError('example_select');
    WorkflowsCore.clearFieldError('example_file');
    
    // Scroll back to form
    const formSection = document.getElementById('agentForm');
    if (formSection) {
        formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Initialize Agent Template Processor when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize processor (data attributes set by template)
    window.agentTemplateProcessor = new AgentTemplateProcessor();
});