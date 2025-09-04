/**
 * Agents Core - Dynamic Agent Execution System
 * Handles form submission and N8N integration for any agent
 */

class AgentsCore extends WorkflowsCore {
    constructor() {
        super();
        this.agentId = document.body.getAttribute('data-agent-id');
        this.agentSlug = document.body.getAttribute('data-agent-slug');
        this.webhookUrl = document.body.getAttribute('data-webhook-url');
        this.price = parseFloat(document.body.getAttribute('data-agent-price') || '0');
        this.sessionId = this.constructor.generateSessionId();
        
        // Initialize on page load
        this.initialize();
    }
    
    initialize() {
        // Initialize form submission
        const form = document.getElementById('agentForm');
        if (form) {
            form.addEventListener('submit', this.handleFormSubmission.bind(this));
        }
        
        // Initialize form validation
        this.initializeDynamicFormValidation();
    }
    
    /**
     * Handle form submission with agents API integration
     */
    async handleFormSubmission(e) {
        e.preventDefault();
        
        if (!this.isFormValid()) {
            this.constructor.showToast('Please fill in all required fields correctly', 'error');
            return;
        }
        
        // Check authentication and balance
        if (!this.constructor.checkAuthentication()) return;
        if (!this.constructor.checkBalance(this.price)) return;
        
        // Show processing status and disable submit button
        this.constructor.showProcessing('Executing agent...');
        
        const submitBtn = document.getElementById('generateBtn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = '⏳ Processing...';
        }
        
        try {
            // Use agents API for execution
            await this.executeViaAgentsAPI(e.target);
        } catch (error) {
            console.error('Form submission error:', error);
            this.constructor.hideProcessing();
            this.showErrorMessage('❌ Agent is temporarily unavailable. Please try again later.');
            this.resetSubmitButton();
        }
    }
    
    /**
     * Execute agent via the agents API
     */
    async executeViaAgentsAPI(form) {
        try {
            const formData = new FormData(form);
            
            // Check if form contains file uploads
            const hasFiles = Array.from(formData.entries()).some(([key, value]) => 
                value instanceof File && key !== 'csrfmiddlewaretoken'
            );
            
            if (hasFiles) {
                // Handle file upload via multipart form data
                await this.executeWithFileUpload(formData);
            } else {
                // Handle regular form data via JSON API
                await this.executeWithJsonAPI(formData);
            }
        } catch (error) {
            console.error('Agent execution error:', error);
            this.constructor.hideProcessing();
            this.showErrorMessage('❌ Agent is temporarily unavailable. Please try again later.');
            this.resetSubmitButton();
        }
    }
    
    /**
     * Execute agent with file upload using multipart form data
     */
    async executeWithFileUpload(formData) {
        // Get CSRF token
        const csrfToken = formData.get('csrfmiddlewaretoken');
        
        // Prepare multipart form data for direct webhook call (similar to workflows)
        const webhookFormData = new FormData();
        
        // Add files and regular form fields
        for (let [key, value] of formData.entries()) {
            if (key !== 'csrfmiddlewaretoken') {
                if (value instanceof File) {
                    webhookFormData.append('file', value);
                } else {
                    // Map form fields to webhook expected format
                    if (key === 'analysis_type') {
                        webhookFormData.append('analysisType', value);
                    } else {
                        webhookFormData.append(key, value);
                    }
                }
            }
        }
        
        // Call webhook directly for file uploads (similar to workflows approach)
        const response = await fetch(this.webhookUrl, {
            method: 'POST',
            body: webhookFormData,
            signal: AbortSignal.timeout(120000) // 2 minute timeout for file processing
        });
        
        if (!response.ok) {
            throw new Error(`File processing failed: ${response.status}`);
        }
        
        // Parse response
        const data = await response.json();
        
        // Deduct wallet balance manually since we bypassed the API
        await this.deductBalanceForFileUpload();
        
        // Process successful execution
        this.constructor.hideProcessing();
        
        // Display results
        this.displayFileProcessingResults(data);
        
        this.constructor.showToast('✅ File processed successfully!', 'success');
    }
    
    /**
     * Execute agent with JSON API (for non-file uploads)
     */
    async executeWithJsonAPI(formData) {
        // Extract all form data dynamically
        const inputData = {};
        for (let [key, value] of formData.entries()) {
            if (key !== 'csrfmiddlewaretoken') {
                inputData[key] = value;
            }
        }
        
        // Get CSRF token
        const csrfToken = formData.get('csrfmiddlewaretoken');
        
        // Form validation passed, proceeding with execution
        
        // Call agents API
        const response = await fetch('/agents/api/execute/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                agent_slug: this.agentSlug,
                input_data: inputData
            }),
            signal: AbortSignal.timeout(90000) // 90 second timeout
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || `API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Process successful execution
        this.constructor.hideProcessing();
        
        // Update wallet balance ONLY after successful AI execution
        if (data.fee_charged) {
            const currentBalance = parseFloat(document.body.getAttribute('data-user-balance') || '0');
            const newBalance = currentBalance - parseFloat(data.fee_charged);
            
            console.log('Charging wallet after successful execution:', {
                currentBalance,
                feeCharged: data.fee_charged,
                newBalance,
                executionStatus: data.status
            });
            
            // Update the wallet balance display
            this.constructor.updateWalletBalance(newBalance);
            
            // Show notification about successful charge
            this.constructor.showToast(`💰 Charged ${data.fee_charged} AED - Service completed!`, 'success');
        }
        
        // Display results
        this.displayExecutionResults(data);
        
        this.constructor.showToast('✅ Agent executed successfully!', 'success');
    }
    
    /**
     * Deduct wallet balance for file upload (manual deduction)
     */
    async deductBalanceForFileUpload() {
        try {
            // Call the wallet deduction API
            const response = await fetch('/wallet/api/deduct/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    amount: this.price,
                    description: `${this.agentSlug.replace('-', ' ')} execution`,
                    agent_slug: this.agentSlug
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.new_balance !== undefined) {
                    // Update wallet balance display
                    this.constructor.updateWalletBalance(data.new_balance);
                }
            }
        } catch (error) {
            console.error('Wallet deduction error:', error);
        }
    }
    
    /**
     * Display execution results
     */
    displayExecutionResults(data) {
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsContent = document.getElementById('resultsContent');
        
        if (!resultsContainer || !resultsContent) {
            console.log('Results containers not found');
            return;
        }
        
        // Clear previous results
        resultsContent.innerHTML = '';
        
        // Extract output content with better format handling and debugging
        let content = '';
        
        // Add debugging to see what we're getting
        console.log('=== DEBUGGING EXECUTION RESULTS ===');
        console.log('Full data object:', data);
        console.log('output_data type:', typeof data.output_data);
        console.log('output_data content:', data.output_data);
        console.log('Agent slug:', this.agentSlug);
        
        // Check for PDF analyzer direct response format FIRST
        if (data.sections && Array.isArray(data.sections)) {
            console.log('Using PDF direct response format');
            content = this.formatPDFAnalysisResults(data.sections);
        }
        // Check for PDF analyzer array response format
        else if (Array.isArray(data) && data[0] && data[0].sections) {
            console.log('Using PDF array response format');
            content = this.formatPDFAnalysisResults(data[0].sections);
        }
        // Then check for standard output_data format
        else if (data.output_data && typeof data.output_data === 'object') {
            // Handle PDF analyzer nested response format
            if (Array.isArray(data.output_data) && data.output_data[0] && data.output_data[0].sections) {
                console.log('Using PDF nested analysis format');
                content = this.formatPDFAnalysisResults(data.output_data[0].sections);
            }
            // Handle standard webhook response format  
            else if (data.output_data.output) {
                console.log('Using standard output format');
                // Check if this is a job posting and format it specially
                if (this.agentSlug === 'job-posting-generator') {
                    content = this.formatJobPostingResults(data.output_data.output);
                } else {
                    content = data.output_data.output;
                }
            }
            // Handle brand presence finder results (regular version)
            else if (this.agentSlug === 'brand-digital-presence-finder' && data.output_data.data) {
                console.log('Using brand presence analysis format v2');
                content = this.formatBrandPresenceResults_v2(data.output_data.data, data.output_data);
            }
            // Handle brand presence finder PRO results (enhanced version)
            else if (this.agentSlug === 'brand-digital-presence-finder-pro' && data.output_data.data) {
                console.log('Using brand presence PRO enhanced format with follower tracking');
                content = this.formatBrandPresenceResults_v2(data.output_data.data, data.output_data);
            }
            // Handle other response formats
            else if (data.output_data.result || data.output_data.content) {
                console.log('Using result/content format');
                content = data.output_data.result || data.output_data.content;
            }
            // Show the actual data structure instead of generic message
            else {
                console.log('Using JSON fallback format');
                content = `<div style="background: #f5f5f5; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap;">${JSON.stringify(data.output_data, null, 2)}</div>`;
            }
        } else if (data.output_data) {
            console.log('Using string format');
            content = data.output_data.toString();
        } else {
            console.log('No output_data found - using fallback');
            // Show the full response to debug what's missing
            content = `<div style="background: #fff3cd; padding: 15px; border: 1px solid #ffeaa7; border-radius: 5px;">
                <h4>Execution Details:</h4>
                <p><strong>Status:</strong> ${data.status || 'unknown'}</p>
                <p><strong>Agent:</strong> ${this.agentSlug}</p>
                <p><strong>Execution ID:</strong> ${data.id || 'unknown'}</p>
                <p><strong>Error:</strong> ${data.error_message || 'No error message'}</p>
                <details>
                    <summary>Full Response Data</summary>
                    <pre style="background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto;">${JSON.stringify(data, null, 2)}</pre>
                </details>
            </div>`;
        }
        console.log('Final content length:', content.length);
        console.log('=====================================');
        
        // Create content element
        const contentDiv = document.createElement('div');
        contentDiv.className = 'results-content';
        
        // Use innerHTML for formatted PDF results, textContent for others
        if (content.includes('<h') || content.includes('<div')) {
            contentDiv.innerHTML = content;
        } else {
            contentDiv.textContent = content;
        }
        
        resultsContent.appendChild(contentDiv);
        
        // Show results container
        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        this.resetSubmitButton();
    }
    
    /**
     * Format PDF analysis results - simple and clean
     */
    formatPDFAnalysisResults(sections) {
        let html = '<div class="simple-results">';
        
        sections.forEach(section => {
            let content = section.content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            content = content.replace(/\n/g, '<br>');
            
            html += `
                <div class="result-section">
                    <h3>${section.heading}</h3>
                    <div>${content}</div>
                </div>
            `;
        });
        
        html += '</div>';
        
        // Simple, clean styling
        html += `
            <style>
                .simple-results {
                    font-family: system-ui, sans-serif;
                    line-height: 1.5;
                }
                .result-section {
                    margin-bottom: 20px;
                    padding-bottom: 15px;
                    border-bottom: 1px solid #eee;
                }
                .result-section:last-child {
                    border-bottom: none;
                }
                .result-section h3 {
                    color: #333;
                    margin: 0 0 10px 0;
                    font-size: 16px;
                    font-weight: 600;
                }
                .result-section div {
                    color: #555;
                    font-size: 14px;
                }
                .result-section strong {
                    color: #222;
                }
            </style>
        `;
        
        return html;
    }
    
    /**
     * Process markdown-like content and convert to HTML
     */
    processMarkdownContent(content) {
        // Handle numbered lists (1. **Title**: Description)
        content = content.replace(/(\d+)\.\s\*\*(.*?)\*\*:\s*(.*?)(?=\n\d+\.|\n-|$)/g, 
            '<ol><li><strong>$2</strong>: $3</li></ol>');
        
        // Fix multiple consecutive ol tags
        content = content.replace(/<\/ol>\s*<ol>/g, '');
        
        // Handle bullet points (- **Title**: Description)
        content = content.replace(/(?:^|\n)-\s\*\*(.*?)\*\*:\s*(.*?)(?=\n-|$)/g, 
            '<ul><li><strong>$1</strong>: $2</li></ul>');
        
        // Fix multiple consecutive ul tags  
        content = content.replace(/<\/ul>\s*<ul>/g, '');
        
        // Handle standalone numbered items without the list wrapper
        content = content.replace(/(\d+)\.\s\*\*(.*?)\*\*:\s*(.*?)(?=\n|$)/g, 
            '<div class="numbered-item"><strong>$1. $2</strong>: $3</div>');
        
        // Handle standalone bold items
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Handle line breaks
        content = content.replace(/\n/g, '<br>');
        
        // Clean up extra breaks around lists
        content = content.replace(/<br>\s*<(ol|ul|div class="numbered-item")>/g, '<$1>');
        content = content.replace(/<\/(ol|ul)>\s*<br>/g, '</$1>');
        
        return content;
    }
    
    /**
     * Format job posting results - simple and clean
     */
    formatJobPostingResults(jobPostingText) {
        // Just convert markdown bold to HTML and preserve line breaks
        let content = jobPostingText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        content = content.replace(/\n\n/g, '<br><br>');
        content = content.replace(/\n/g, '<br>');
        
        let html = `
            <div class="simple-job-posting">
                ${content}
            </div>
            <style>
                .simple-job-posting {
                    font-family: system-ui, sans-serif;
                    line-height: 1.5;
                    color: #333;
                    font-size: 14px;
                }
                .simple-job-posting strong {
                    color: #222;
                    font-weight: 600;
                }
            </style>
        `;
        
        return html;
    }
    
    /**
     * Get platform logo for display
     */
    getPlatformLogo(platformName) {
        const logos = {
            'Google Business': 'https://upload.wikimedia.org/wikipedia/commons/c/c7/Google_My_Business_logo.png',
            'LinkedIn': 'https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png',
            'YouTube': 'https://upload.wikimedia.org/wikipedia/commons/4/42/YouTube_icon_%282013-2017%29.png',
            'TikTok': 'https://upload.wikimedia.org/wikipedia/en/a/a9/TikTok_logo.png',
            'Instagram': 'https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png',
            'Pinterest': 'https://upload.wikimedia.org/wikipedia/commons/0/08/Pinterest-logo.png',
            'Twitter': 'https://upload.wikimedia.org/wikipedia/commons/6/6f/Logo_of_Twitter.svg',
            'X (Twitter)': 'https://upload.wikimedia.org/wikipedia/commons/5/5a/X_icon_2.svg',
            'X': 'https://upload.wikimedia.org/wikipedia/commons/5/5a/X_icon_2.svg',
            'Facebook': 'https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg',
            'Medium': 'https://upload.wikimedia.org/wikipedia/commons/e/ec/Medium_logo_Monogram.svg',
            'Tumblr': 'https://upload.wikimedia.org/wikipedia/commons/4/43/Tumblr_Logo.svg',
            'Threads': 'https://upload.wikimedia.org/wikipedia/commons/9/9d/Threads_%28app%29_logo.svg',
            'Quora': 'https://upload.wikimedia.org/wikipedia/commons/9/91/Quora_logo_2015.svg',
            'Reddit': 'https://upload.wikimedia.org/wikipedia/commons/5/58/Reddit_logo_new.svg',
            'Blue Sky': 'https://upload.wikimedia.org/wikipedia/commons/7/7a/Bluesky_Logo.svg'
        };
        
        const logoUrl = logos[platformName];
        if (logoUrl) {
            return `<img src="${logoUrl}" alt="${platformName}" style="width: 24px; height: 24px; object-fit: contain;" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
                    <span style="display: none; font-size: 24px;">${this.getPlatformIcon(platformName)}</span>`;
        }
        return `<span style="font-size: 24px;">${this.getPlatformIcon(platformName)}</span>`;
    }
    
    /**
     * Get brand logo for display
     */
    getBrandLogo(brandName, websiteUrl) {
        if (!brandName) return '';
        
        // Try to get logo from various sources
        const logoSources = [
            `https://logo.clearbit.com/${this.extractDomain(websiteUrl)}`,
            `https://www.google.com/s2/favicons?domain=${this.extractDomain(websiteUrl)}&sz=64`,
            `https://favicon.yandex.net/favicon/v2/${this.extractDomain(websiteUrl)}?size=64`
        ];
        
        return `
            <img src="${logoSources[0]}" 
                 alt="${brandName} logo" 
                 style="width: 32px; height: 32px; object-fit: contain; border-radius: 4px; margin-right: 8px;" 
                 onerror="
                     if (this.src !== '${logoSources[1]}') {
                         this.src = '${logoSources[1]}';
                     } else if (this.src !== '${logoSources[2]}') {
                         this.src = '${logoSources[2]}';
                     } else {
                         this.style.display = 'none';
                     }
                 ">
        `;
    }
    
    /**
     * Extract domain from URL
     */
    extractDomain(url) {
        if (!url) return '';
        try {
            const domain = url.replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0];
            return domain;
        } catch {
            return '';
        }
    }
    
    /**
     * Get platform icon fallback for display
     */
    getPlatformIcon(platformName) {
        const icons = {
            'Google Business': '🏢',
            'LinkedIn': '💼', 
            'YouTube': '📺',
            'TikTok': '🎵',
            'Instagram': '📷',
            'Pinterest': '📌',
            'Twitter': '🐦',
            'X (Twitter)': '❌',
            'X': '❌',
            'Facebook': '📘',
            'Medium': '📝',
            'Tumblr': '🎨',
            'Threads': '🧵',
            'Quora': '❓',
            'Reddit': '🤖',
            'Blue Sky': '☁️'
        };
        return icons[platformName] || '🌐';
    }
    
    /**
     * Format brand presence analysis results into beautiful HTML
     */
    formatBrandPresenceResults_v2(data, fullData = null) {
        const platforms = data.platforms || [];
        const summary = data.summary || {};
        const recommendations = data.recommendations || [];
        
        // Try to get brand analysis from parent data or current data
        const brandAnalysis = fullData?.brand_analysis || data.brand_analysis || {};
        
        // Check if this is Pro version with enhanced features
        const isProVersion = fullData?.meta?.is_pro_version || false;
        const proFeatures = data.pro_features || {};
        const insights = fullData?.insights || {};
        
        // Calculate key metrics
        const foundPlatforms = platforms.filter(p => p.found);
        const notFoundPlatforms = platforms.filter(p => !p.found);
        const completionPercentage = Math.round(summary.completion_percentage || 0);
        
        // Pro version: Format follower count
        const formatFollowers = (count) => {
            if (!count) return 'N/A';
            if (count >= 1000000) return `${(count/1000000).toFixed(1)}M`;
            if (count >= 1000) return `${(count/1000).toFixed(1)}K`;
            return count.toString();
        };
        
        // Professional card layout with hardcoded styling
        const html = `

            <!-- Brand Information -->
            <div style="
                background: white;
                border: 1px solid #e1e4e7;
                border-radius: 12px;
                padding: 32px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                margin-bottom: 32px;
                font-family: 'Inter', Arial, sans-serif;
            ">
                <h3 style="
                    font-size: 20px; 
                    font-weight: 700; 
                    color: #3b82f6; 
                    margin: 0 0 24px 0; 
                    display: flex; 
                    align-items: center; 
                    gap: 8px;
                    border-bottom: 3px solid #3b82f6;
                    padding-bottom: 8px;
                ">
                    📌 Brand Information
                </h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                    <div style="grid-column: 1 / -1; display: flex; align-items: center; margin-bottom: 8px;">
                        ${this.getBrandLogo(brandAnalysis.brand_name, brandAnalysis.website)}
                        <div>
                            <strong style="color: #4b5563;">Brand Name:</strong>
                            <span style="color: #1a1a1a; margin-left: 8px; font-size: 18px; font-weight: 600;">${brandAnalysis.brand_name || 'Unknown'}</span>
                        </div>
                    </div>
                    <div>
                        <strong style="color: #4b5563;">Website:</strong>
                        <a href="${brandAnalysis.website || '#'}" target="_blank" style="color: #3b82f6; text-decoration: none; margin-left: 8px;">
                            ${brandAnalysis.website?.replace('https://', '').replace('http://', '') || 'N/A'}
                        </a>
                    </div>
                    <div>
                        <strong style="color: #4b5563;">Analysis Date:</strong>
                        <span style="color: #1a1a1a; margin-left: 8px;">${brandAnalysis.analysis_date ? new Date(brandAnalysis.analysis_date).toLocaleDateString() : new Date().toLocaleDateString()}</span>
                    </div>
                    <div>
                        <strong style="color: #4b5563;">Processing:</strong>
                        <span style="color: #1a1a1a; margin-left: 8px;">${brandAnalysis.processing_time || 'AI-powered analysis'}</span>
                    </div>
                </div>
            </div>

            <!-- Quick Stats -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 16px; margin-bottom: 32px; font-family: 'Inter', Arial, sans-serif;">
                <div style="
                    background: white;
                    border: 1px solid #e1e4e7;
                    border-radius: 12px;
                    padding: 24px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    border-left: 4px solid #10b981;
                    transition: all 0.2s ease;
                ">
                    <div style="font-size: 36px; font-weight: 700; color: #10b981; margin-bottom: 4px;">${foundPlatforms.length}</div>
                    <div style="font-size: 12px; color: #6b7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Platforms Found</div>
                </div>
                <div style="
                    background: white;
                    border: 1px solid #e1e4e7;
                    border-radius: 12px;
                    padding: 24px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    border-left: 4px solid #ef4444;
                    transition: all 0.2s ease;
                ">
                    <div style="font-size: 36px; font-weight: 700; color: #ef4444; margin-bottom: 4px;">${notFoundPlatforms.length}</div>
                    <div style="font-size: 12px; color: #6b7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Platforms Missing</div>
                </div>
                <div style="
                    background: white;
                    border: 1px solid #e1e4e7;
                    border-radius: 12px;
                    padding: 24px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    border-left: 4px solid #3b82f6;
                    transition: all 0.2s ease;
                ">
                    <div style="font-size: 36px; font-weight: 700; color: #3b82f6; margin-bottom: 4px;">${completionPercentage}%</div>
                    <div style="font-size: 12px; color: #6b7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Coverage</div>
                </div>
                ${isProVersion ? `
                <div style="
                    background: white;
                    border: 1px solid #e1e4e7;
                    border-radius: 12px;
                    padding: 24px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    border-left: 4px solid #8b5cf6;
                    transition: all 0.2s ease;
                ">
                    <div style="font-size: 24px; font-weight: 700; color: #8b5cf6; margin-bottom: 4px;">${formatFollowers(proFeatures.total_followers || summary.total_followers || 0)}</div>
                    <div style="font-size: 12px; color: #6b7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Total Followers</div>
                </div>
                <div style="
                    background: white;
                    border: 1px solid #e1e4e7;
                    border-radius: 12px;
                    padding: 24px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    border-left: 4px solid #f59e0b;
                    transition: all 0.2s ease;
                ">
                    <div style="font-size: 24px; font-weight: 700; color: #f59e0b; margin-bottom: 4px;">${insights.digital_presence_score || 'N/A'}</div>
                    <div style="font-size: 12px; color: #6b7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Presence Score</div>
                </div>
                ` : ''}
            </div>

            ${isProVersion ? `
            <!-- Pro Insights -->
            <div style="
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                border-radius: 12px;
                padding: 32px;
                margin-bottom: 32px;
                color: white;
                font-family: 'Inter', Arial, sans-serif;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            ">
                <h3 style="
                    font-size: 20px; 
                    font-weight: 700; 
                    margin: 0 0 24px 0; 
                    display: flex; 
                    align-items: center; 
                    gap: 8px;
                ">
                    🚀 Pro Insights
                </h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                    <div>
                        <strong style="font-weight: 600;">Strongest Presence:</strong>
                        <div style="font-size: 18px; margin-top: 4px; font-weight: 500;">${insights.strongest_presence || 'None'}</div>
                    </div>
                    <div>
                        <strong style="font-weight: 600;">Biggest Opportunity:</strong>
                        <div style="font-size: 18px; margin-top: 4px; font-weight: 500;">${insights.biggest_opportunity || 'None'}</div>
                    </div>
                    <div>
                        <strong style="font-weight: 600;">Industry Benchmark:</strong>
                        <div style="font-size: 14px; margin-top: 4px; opacity: 0.9;">${insights.industry_benchmark || 'N/A'}</div>
                    </div>
                    <div>
                        <strong style="font-weight: 600;">Verification Gaps:</strong>
                        <div style="font-size: 18px; margin-top: 4px; font-weight: 500;">${insights.verification_gaps || 0} accounts</div>
                    </div>
                </div>
            </div>
            ` : ''}

            <!-- Platform Cards -->
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin-bottom: 16px;">
                ${platforms.map(platform => `
                    <div style="
                        background: white;
                        border: 1px solid #e1e4e7;
                        border-radius: 12px;
                        padding: 24px;
                        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                        font-family: 'Inter', Arial, sans-serif;
                        display: flex;
                        flex-direction: column;
                        gap: 12px;
                        transition: all 0.2s;
                        cursor: pointer;
                        min-height: 200px;
                    " onmouseenter="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.15)'"
                       onmouseleave="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)'">
                        
                        <!-- Platform Header -->
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                            <div style="flex: 1;">
                                <h3 style="font-size: 18px; font-weight: 600; margin: 0; color: #1a1a1a; display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                        ${this.getPlatformLogo(platform.name).replace('width: 24px; height: 24px', 'width: 20px; height: 20px')}
                                    </div>
                                    ${platform.name}
                                </h3>
                                <div style="margin-top: 4px;">
                                    ${platform.found 
                                        ? `<span style="
                                            display: inline-block;
                                            padding: 4px 8px;
                                            background: ${platform.verified ? '#10b981' : '#f59e0b'};
                                            color: white;
                                            border-radius: 12px;
                                            font-size: 11px;
                                            font-weight: 500;
                                            margin-right: 6px;
                                        ">${platform.verified ? '✓ Verified' : '⚠️ Unverified'}</span>`
                                        : `<span style="
                                            display: inline-block;
                                            padding: 4px 8px;
                                            background: #ef4444;
                                            color: white;
                                            border-radius: 12px;
                                            font-size: 11px;
                                            font-weight: 500;
                                        ">❌ Not Found</span>`
                                    }
                                    ${platform.confidence ? `
                                        <span style="
                                            display: inline-block;
                                            padding: 4px 8px;
                                            background: ${platform.confidence === 'high' ? '#3b82f6' : platform.confidence === 'medium' ? '#8b5cf6' : '#64748b'};
                                            color: white;
                                            border-radius: 12px;
                                            font-size: 11px;
                                            font-weight: 500;
                                        ">${platform.confidence.charAt(0).toUpperCase() + platform.confidence.slice(1)} Confidence</span>
                                    ` : ''}
                                </div>
                            </div>
                            <div style="flex-shrink: 0; margin-left: 12px;">
                                <span style="font-size: 24px; color: ${platform.found ? '#10b981' : '#ef4444'};">
                                    ${platform.found ? '✓' : '✗'}
                                </span>
                            </div>
                        </div>
                        
                        ${isProVersion && platform.found ? `
                        <!-- Pro Metrics -->
                        <div style="
                            display: grid; 
                            grid-template-columns: 1fr 1fr; 
                            gap: 8px; 
                            margin: 16px 0;
                            padding: 16px;
                            background: #f8fafc;
                            border-radius: 8px;
                            border: 1px solid #e4e7eb;
                        ">
                            <div style="text-align: center;">
                                <div style="font-size: 16px; font-weight: 600; color: #1a1a1a;">${formatFollowers(platform.followers_count || platform.subscribers_count || 0)}</div>
                                <div style="font-size: 12px; color: #6b7280; text-transform: uppercase; font-weight: 500;">Followers</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 16px; font-weight: 600; color: #1a1a1a;">${platform.engagement_level || 'Unknown'}</div>
                                <div style="font-size: 12px; color: #6b7280; text-transform: uppercase; font-weight: 500;">Engagement</div>
                            </div>
                            ${platform.search_ranking ? `
                            <div style="text-align: center;">
                                <div style="font-size: 16px; font-weight: 600; color: #1a1a1a;">#${platform.search_ranking}</div>
                                <div style="font-size: 12px; color: #6b7280; text-transform: uppercase; font-weight: 500;">Search Rank</div>
                            </div>
                            ` : ''}
                            ${platform.profile_completeness ? `
                            <div style="text-align: center;">
                                <div style="font-size: 16px; font-weight: 600; color: #1a1a1a;">${platform.profile_completeness}%</div>
                                <div style="font-size: 12px; color: #6b7280; text-transform: uppercase; font-weight: 500;">Complete</div>
                            </div>
                            ` : ''}
                        </div>
                        ` : ''}
                        
                        <!-- Platform Notes -->
                        ${platform.notes ? `
                            <p style="
                                font-size: 13px; 
                                color: #6b7280; 
                                line-height: 1.5; 
                                margin: 0;
                                flex: 1;
                            ">${platform.notes}</p>
                        ` : ''}
                        
                        <!-- Action Button -->
                        ${platform.found && platform.profile_url ? `
                            <a href="${platform.profile_url}" target="_blank" style="
                                display: block;
                                width: 100%;
                                padding: 8px 16px;
                                background: #3b82f6;
                                color: white;
                                border: none;
                                border-radius: 8px;
                                font-size: 12px;
                                font-weight: 500;
                                text-decoration: none;
                                text-align: center;
                                margin-top: auto;
                                transition: all 0.2s ease;
                                font-family: 'Inter', Arial, sans-serif;
                            " onmouseenter="this.style.background='#1d4ed8'" 
                               onmouseleave="this.style.background='#3b82f6'">View Profile →</a>
                        ` : ''}
                    </div>
                `).join('')}
            </div>

            <!-- Recommendations -->
            ${recommendations.length > 0 ? `
                <div style="
                    background: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 24px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-top: 24px;
                ">
                    <h3 style="font-size: 20px; font-weight: 600; color: #1a1a1a; margin: 0 0 16px 0; display: flex; align-items: center; gap: 8px;">
                        💡 Recommendations
                    </h3>
                    <div style="display: flex; flex-direction: column; gap: 12px;">
                        ${recommendations.map(rec => {
                            const priority = rec.priority?.toLowerCase() || 'medium';
                            const priorityColors = {
                                'high': { bg: '#fef2f2', border: '#ef4444', text: '#dc2626' },
                                'medium': { bg: '#fffbeb', border: '#f59e0b', text: '#d97706' },
                                'low': { bg: '#f0f9ff', border: '#3b82f6', text: '#2563eb' }
                            };
                            const colors = priorityColors[priority] || priorityColors['medium'];
                            
                            return `
                                <div style="
                                    padding: 16px;
                                    background: ${colors.bg};
                                    border-left: 4px solid ${colors.border};
                                    border-radius: 8px;
                                    border: 1px solid ${colors.border}33;
                                ">
                                    <div style="display: flex; align-items: flex-start; gap: 12px;">
                                        <span style="
                                            display: inline-block;
                                            padding: 4px 8px;
                                            background: ${colors.border};
                                            color: white;
                                            border-radius: 12px;
                                            font-size: 11px;
                                            font-weight: 600;
                                            text-transform: uppercase;
                                            flex-shrink: 0;
                                        ">${priority} Priority</span>
                                        <div style="flex: 1;">
                                            <div style="font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 4px;">${rec.platform}</div>
                                            <div style="font-size: 14px; color: #4b5563; line-height: 1.5;">${rec.reason}</div>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            ` : ''}
        `;
        
        // Store brand presence data globally for custom download function
        window.brandPresenceData = data;
        window.brandPresenceFullData = fullData;
        
        // Load jsPDF library if not already loaded
        if (typeof window.jsPDF === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
            script.onload = function() {
                console.log('jsPDF loaded successfully');
            };
            document.head.appendChild(script);
        }
        
        return html;
    }
    
    /**
     * Generate professional PDF report for brand presence analysis
     */
    generateBrandPresencePDF(data, fullData = null) {
        try {
            // Check if jsPDF is available
            if (typeof window.jsPDF === 'undefined') {
                this.showNotification('Loading PDF library, please try again in a moment...', 'info');
                // Load library and retry after 2 seconds
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
                script.onload = () => {
                    console.log('jsPDF loaded, you can now generate PDF');
                    this.showNotification('PDF library loaded! Click the button again.', 'success');
                };
                document.head.appendChild(script);
                return;
            }
            
            console.log('Starting PDF generation...');
            const { jsPDF } = window;
            const doc = new jsPDF();
            
            const platforms = data.platforms || [];
            const summary = data.summary || {};
            const recommendations = data.recommendations || [];
            const brandAnalysis = fullData?.brand_analysis || data.brand_analysis || {};
            
            const foundPlatforms = platforms.filter(p => p.found);
            const completionPercentage = Math.round(summary.completion_percentage || 0);
            
            let yPos = 20;
            const pageWidth = doc.internal.pageSize.width;
            const margin = 20;
            const contentWidth = pageWidth - (margin * 2);
            
            // Title
            doc.setFontSize(20);
            doc.setFont(undefined, 'bold');
            const title = `${brandAnalysis.brand_name || 'Brand'} Brand Analysis Report`;
            doc.text(title, margin, yPos);
            yPos += 15;
            
            // Title underline
            doc.setLineWidth(0.5);
            doc.line(margin, yPos, pageWidth - margin, yPos);
            yPos += 15;
            
            // Brand Information Section
            doc.setFontSize(14);
            doc.setFont(undefined, 'bold');
            doc.text('Brand Information', margin, yPos);
            yPos += 10;
            
            doc.setFontSize(10);
            doc.setFont(undefined, 'normal');
            doc.text(`Brand: ${brandAnalysis.brand_name || 'Unknown'}`, margin, yPos);
            yPos += 6;
            doc.text(`Website: ${brandAnalysis.website || 'N/A'}`, margin, yPos);
            yPos += 6;
            doc.text(`Analysis Date: ${new Date(brandAnalysis.analysis_date || Date.now()).toLocaleDateString('en-US', { 
                year: 'numeric', month: 'long', day: 'numeric' 
            })}`, margin, yPos);
            yPos += 6;
            doc.text(`Processing: ${brandAnalysis.processing_time || 'AI-powered analysis'}`, margin, yPos);
            yPos += 15;
            
            // Summary Section
            doc.setFontSize(14);
            doc.setFont(undefined, 'bold');
            doc.text('Summary', margin, yPos);
            yPos += 10;
            
            doc.setFontSize(10);
            doc.setFont(undefined, 'normal');
            doc.text(`Total Platforms Checked: ${platforms.length}`, margin, yPos);
            yPos += 6;
            doc.text(`Platforms Found: ${foundPlatforms.length}`, margin, yPos);
            yPos += 6;
            doc.text(`Platforms Missing: ${platforms.length - foundPlatforms.length}`, margin, yPos);
            yPos += 6;
            doc.text(`Completion: ${completionPercentage}%`, margin, yPos);
            yPos += 15;
            
            // Platform Presence Section
            doc.setFontSize(14);
            doc.setFont(undefined, 'bold');
            doc.text('Platform Presence', margin, yPos);
            yPos += 10;
            
            // Table headers
            doc.setFontSize(9);
            doc.setFont(undefined, 'bold');
            const headers = ['Platform', 'Status', 'Verified', 'Confidence', 'Notes'];
            const colWidths = [35, 25, 25, 25, 60];
            let xPos = margin;
            
            headers.forEach((header, i) => {
                doc.text(header, xPos, yPos);
                xPos += colWidths[i];
            });
            yPos += 8;
            
            // Table line
            doc.setLineWidth(0.3);
            doc.line(margin, yPos, pageWidth - margin, yPos);
            yPos += 5;
            
            // Platform rows
            doc.setFont(undefined, 'normal');
            platforms.forEach(platform => {
                if (yPos > 270) { // New page if needed
                    doc.addPage();
                    yPos = 20;
                }
                
                xPos = margin;
                const status = platform.found ? 'Found' : 'Not Found';
                const verified = platform.found ? (platform.verified ? 'Verified' : 'Unverified') : 'N/A';
                const confidence = platform.confidence ? platform.confidence.charAt(0).toUpperCase() + platform.confidence.slice(1) : 'N/A';
                const notes = platform.notes || '';
                
                const rowData = [platform.name, status, verified, confidence, notes];
                
                rowData.forEach((cell, i) => {
                    if (i === 4) { // Notes column - wrap text
                        const lines = doc.splitTextToSize(cell, colWidths[i] - 5);
                        doc.text(lines, xPos, yPos);
                    } else {
                        doc.text(cell, xPos, yPos);
                    }
                    xPos += colWidths[i];
                });
                yPos += 8;
            });
            
            yPos += 10;
            
            // Recommendations Section
            if (recommendations && recommendations.length > 0) {
                if (yPos > 250) {
                    doc.addPage();
                    yPos = 20;
                }
                
                doc.setFontSize(14);
                doc.setFont(undefined, 'bold');
                doc.text('Recommendations', margin, yPos);
                yPos += 10;
                
                doc.setFontSize(10);
                doc.setFont(undefined, 'normal');
                
                recommendations.forEach(rec => {
                    if (yPos > 270) {
                        doc.addPage();
                        yPos = 20;
                    }
                    
                    const priority = rec.priority ? rec.priority.charAt(0).toUpperCase() + rec.priority.slice(1) + ' Priority' : 'Priority';
                    doc.setFont(undefined, 'bold');
                    doc.text(`${rec.platform} - ${priority}`, margin, yPos);
                    yPos += 6;
                    
                    doc.setFont(undefined, 'normal');
                    const reasonLines = doc.splitTextToSize(rec.reason, contentWidth);
                    doc.text(reasonLines, margin, yPos);
                    yPos += reasonLines.length * 5 + 5;
                });
            }
            
            // Footer
            const totalPages = doc.internal.getNumberOfPages();
            for (let i = 1; i <= totalPages; i++) {
                doc.setPage(i);
                doc.setFontSize(8);
                doc.setFont(undefined, 'normal');
                doc.text(`Page ${i} of ${totalPages}`, pageWidth - 30, doc.internal.pageSize.height - 10);
                doc.text('Generated by Quantum Tasks AI', margin, doc.internal.pageSize.height - 10);
            }
            
            // Save PDF
            const brandName = (brandAnalysis.brand_name || 'Brand').replace(/[^a-zA-Z0-9]/g, '_');
            const date = new Date().toISOString().split('T')[0];
            const filename = `${brandName}_Brand_Analysis_${date}.pdf`;
            
            doc.save(filename);
            this.showNotification('PDF report generated successfully!', 'success');
            
        } catch (error) {
            console.error('Error generating PDF:', error);
            this.showNotification('PDF failed, generating text report instead...', 'info');
            
            // Fallback to text download
            try {
                const report = this.generateBrandPresenceTextReport(data, fullData);
                const brandAnalysis = fullData?.brand_analysis || data.brand_analysis || {};
                const brandName = (brandAnalysis.brand_name || 'Brand').replace(/[^a-zA-Z0-9]/g, '_');
                const date = new Date().toISOString().split('T')[0];
                const filename = `${brandName}_Brand_Analysis_${date}.txt`;
                
                const blob = new Blob([report], { type: 'text/plain;charset=utf-8' });
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
                
                this.showNotification('Text report downloaded successfully!', 'success');
            } catch (textError) {
                console.error('Text fallback also failed:', textError);
                this.showNotification('Both PDF and text generation failed', 'error');
            }
        }
    }
    
    /**
     * Generate text report for brand presence analysis (fallback)
     */
    generateBrandPresenceTextReport(data, fullData = null) {
        const platforms = data.platforms || [];
        const summary = data.summary || {};
        const recommendations = data.recommendations || [];
        const brandAnalysis = fullData?.brand_analysis || data.brand_analysis || {};
        
        const foundPlatforms = platforms.filter(p => p.found);
        const completionPercentage = Math.round(summary.completion_percentage || 0);
        
        // Generate text report
        let report = `${brandAnalysis.brand_name || 'Brand'} Brand Analysis Report\n`;
        report += `${'='.repeat(50)}\n\n`;
        
        // Brand Information
        report += `Brand Information\n`;
        report += `-----------------\n`;
        report += `Brand: ${brandAnalysis.brand_name || 'Unknown'}\n`;
        report += `Website: ${brandAnalysis.website || 'N/A'}\n`;
        report += `Analysis Date: ${new Date(brandAnalysis.analysis_date || Date.now()).toLocaleDateString('en-US', { 
            year: 'numeric', month: 'long', day: 'numeric' 
        })}\n`;
        report += `Processing: ${brandAnalysis.processing_time || 'AI-powered analysis'}\n\n`;
        
        // Summary
        report += `Summary\n`;
        report += `-------\n`;
        report += `Total Platforms Checked: ${platforms.length}\n`;
        report += `Platforms Found: ${foundPlatforms.length}\n`;
        report += `Platforms Missing: ${platforms.length - foundPlatforms.length}\n`;
        report += `Completion: ${completionPercentage}%\n\n`;
        
        // Platform Presence
        report += `Platform Presence\n`;
        report += `-----------------\n`;
        platforms.forEach(platform => {
            const status = platform.found ? 'Found' : 'Not Found';
            const verified = platform.found ? (platform.verified ? 'Verified' : 'Unverified') : 'N/A';
            const confidence = platform.confidence ? platform.confidence.charAt(0).toUpperCase() + platform.confidence.slice(1) : 'N/A';
            const url = platform.profile_url || 'N/A';
            const notes = platform.notes || '';
            
            report += `\n${platform.name}\n`;
            report += `  Status: ${status}\n`;
            report += `  Verified: ${verified}\n`;
            report += `  Confidence: ${confidence}\n`;
            report += `  URL: ${url}\n`;
            report += `  Notes: ${notes}\n`;
        });
        
        // Recommendations
        if (recommendations && recommendations.length > 0) {
            report += `\n\nRecommendations\n`;
            report += `---------------\n`;
            recommendations.forEach(rec => {
                const priority = rec.priority ? rec.priority.charAt(0).toUpperCase() + rec.priority.slice(1) + ' Priority' : 'Priority';
                report += `\n${rec.platform} – ${priority}\n`;
                report += `${rec.reason}\n`;
            });
        }
        
        report += `\n\nGenerated by Quantum Tasks AI\n`;
        return report;
    }
    
    /**
     * Show notification message
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        `;
        notification.textContent = message;
        
        // Add animation styles
        if (!document.getElementById('notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    /**
     * Display file processing results
     */
    displayFileProcessingResults(data) {
        // Use same method as regular execution results
        this.displayExecutionResults(data);
    }
    
    /**
     * Dynamic form validation based on form schema
     */
    initializeDynamicFormValidation() {
        const formGroups = document.querySelectorAll('.form-group');
        
        formGroups.forEach(group => {
            const field = group.querySelector('input, select, textarea');
            if (field) {
                field.addEventListener('blur', () => this.validateField(field));
                field.addEventListener('input', () => this.constructor.clearFieldError(field.id));
            }
        });
    }
    
    /**
     * Validate individual field
     */
    validateField(field) {
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required');
        
        if (isRequired && !value) {
            this.constructor.showFieldError(field.id, 'This field is required');
            return false;
        }
        
        // Type-specific validation
        if (field.type === 'email' && value && !this.isValidEmail(value)) {
            this.constructor.showFieldError(field.id, 'Please enter a valid email address');
            return false;
        }
        
        if (field.type === 'url' && value && !this.isValidUrl(value)) {
            this.constructor.showFieldError(field.id, 'Please enter a valid URL');
            return false;
        }
        
        this.constructor.clearFieldError(field.id);
        return true;
    }
    
    /**
     * Check if form is valid
     */
    isFormValid() {
        let isValid = true;
        const formGroups = document.querySelectorAll('.form-group');
        
        formGroups.forEach(group => {
            const field = group.querySelector('input, select, textarea');
            if (field && !this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    /**
     * Email validation helper
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    /**
     * URL validation helper
     */
    isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }
    
    /**
     * Show error message in results container
     */
    showErrorMessage(message) {
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsContent = document.getElementById('resultsContent');
        
        if (resultsContainer && resultsContent) {
            resultsContent.innerHTML = `
                <div style="
                    background: #fee2e2;
                    border: 1px solid #fecaca;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    color: #dc2626;
                    font-size: 16px;
                    font-weight: 500;
                    margin: 20px 0;
                ">
                    ${message}
                </div>
            `;
            
            // Show results container
            resultsContainer.style.display = 'block';
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    /**
     * Reset submit button to original state
     */
    resetSubmitButton() {
        const submitBtn = document.getElementById('generateBtn');
        if (submitBtn) {
            submitBtn.disabled = false;
            const agentIcon = this.getAgentIcon();
            submitBtn.textContent = `${agentIcon} Execute ${this.getAgentName()} (${this.price} AED)`;
        }
    }
    
    /**
     * Get agent icon (fallback to generic icon)
     */
    getAgentIcon() {
        const iconMap = {
            'social-ads-generator': '📢',
            'job-posting-generator': '💼',
            'pdf-summarizer': '📄',
            'five-whys-analyzer': '❓'
        };
        
        return iconMap[this.agentSlug] || '🤖';
    }
    
    /**
     * Get agent display name
     */
    getAgentName() {
        return this.agentSlug.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
}

// Global functions for button onclick handlers
function copyResults() {
    const content = document.getElementById('resultsContent');
    if (content) {
        const text = content.textContent || '';
        WorkflowsCore.copyToClipboard(text, 'Results copied to clipboard!');
    }
}

function downloadResults() {
    const agentSlug = document.body.getAttribute('data-agent-slug') || 'agent';
    
    // Special handling for brand presence analysis
    if (agentSlug === 'brand-digital-presence-finder' && window.brandPresenceData) {
        downloadBrandPresenceReport();
        return;
    }
    
    // Default behavior for other agents
    const content = document.getElementById('resultsContent');
    if (content) {
        const text = content.textContent || '';
        WorkflowsCore.downloadAsFile(text, `${agentSlug}-results.txt`, 'Results downloaded!');
    }
}

// Separate function specifically for brand presence analysis
let pdfLoadAttempts = 0;
const MAX_PDF_ATTEMPTS = 2;

function downloadBrandPresenceReport() {
    console.log('downloadBrandPresenceReport called, attempt:', pdfLoadAttempts + 1);
    console.log('brandPresenceData available:', !!window.brandPresenceData);
    
    // Try simple PDF generation first
    if (pdfLoadAttempts === 0) {
        pdfLoadAttempts++;
        console.log('Attempting to load jsPDF from CDN...');
        
        // Try loading from a different, more reliable CDN
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
        
        script.onload = function() {
            console.log('jsPDF loaded successfully');
            
            // Check all possible ways jsPDF might be exposed
            setTimeout(() => {
                console.log('Checking jsPDF availability...');
                console.log('window.jsPDF:', typeof window.jsPDF);
                console.log('window.jspdf:', typeof window.jspdf);  
                console.log('window.jspdf?.jsPDF:', typeof window.jspdf?.jsPDF);
                
                // Check the correct way according to 2025 documentation
                if (window.jspdf && window.jspdf.jsPDF) {
                    console.log('jsPDF found at window.jspdf.jsPDF (correct 2025 format)');
                    generateSimplePDF(window.brandPresenceData, window.brandPresenceFullData);
                } else if (window.jsPDF && typeof window.jsPDF === 'function') {
                    console.log('jsPDF found at window.jsPDF (alternative format)');
                    generateSimplePDF(window.brandPresenceData, window.brandPresenceFullData);
                } else {
                    console.log('jsPDF not found in expected locations, falling back to text');
                    console.log('Available window properties with "pdf":', Object.keys(window).filter(k => k.toLowerCase().includes('pdf')));
                    fallbackBrandPresenceTextDownload();
                }
            }, 500);
        };
        
        script.onerror = function() {
            console.error('Failed to load jsPDF from CDN');
            fallbackBrandPresenceTextDownload();
        };
        
        document.head.appendChild(script);
        return;
    }
    
    // If already attempted once, just use text
    console.log('PDF already attempted, using text download');
    fallbackBrandPresenceTextDownload();
    
    // PDF code disabled for now due to loading issues
    /*
    // Force load jsPDF if not available and not exceeded max attempts
    if (!window.jsPDF && pdfLoadAttempts < MAX_PDF_ATTEMPTS) {
        pdfLoadAttempts++;
        console.log('jsPDF not loaded, loading now... attempt:', pdfLoadAttempts);
        
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/jspdf@2.5.1/dist/jspdf.umd.min.js';
        script.onload = function() {
            console.log('jsPDF script loaded');
            setTimeout(() => {
                downloadBrandPresenceReport(); // Retry after loading
            }, 1000);
        };
        script.onerror = function() {
            console.error('Failed to load jsPDF, falling back to text');
            fallbackBrandPresenceTextDownload();
        };
        document.head.appendChild(script);
        return;
    }
    
    // If max attempts reached, fall back to text
    if (pdfLoadAttempts >= MAX_PDF_ATTEMPTS) {
        console.log('Max PDF attempts reached, falling back to text');
        fallbackBrandPresenceTextDownload();
        return;
    }
    
    try {
        if (window.jsPDF && window.brandPresenceData) {
            console.log('Both jsPDF and data available, attempting PDF generation...');
            generateBrandPresencePDFDirect(window.brandPresenceData, window.brandPresenceFullData);
        } else {
            console.log('Missing requirements, falling back to text');
            fallbackBrandPresenceTextDownload();
        }
    } catch (error) {
        console.error('Brand presence PDF download failed:', error);
        fallbackBrandPresenceTextDownload();
    }
    */
}

// Simple PDF generation function  
function generateSimplePDF(data, fullData = null) {
    try {
        console.log('Starting simple PDF generation...');
        
        // Get jsPDF constructor (2025 correct format)
        let jsPDFConstructor;
        if (window.jspdf && window.jspdf.jsPDF) {
            console.log('Using window.jspdf.jsPDF (2025 format)');
            const { jsPDF } = window.jspdf;
            jsPDFConstructor = jsPDF;
        } else if (window.jsPDF && typeof window.jsPDF === 'function') {
            console.log('Using window.jsPDF (legacy format)');
            jsPDFConstructor = window.jsPDF;
        } else {
            console.error('jsPDF constructor not found');
            console.log('Available:', { 
                'window.jspdf': !!window.jspdf, 
                'window.jsPDF': !!window.jsPDF,
                'window.jspdf?.jsPDF': !!window.jspdf?.jsPDF
            });
            throw new Error('jsPDF constructor not found');
        }
        
        console.log('Creating PDF document in landscape format...');
        const doc = new jsPDFConstructor('l', 'mm', 'a4'); // 'l' for landscape orientation
        
        const platforms = data.platforms || [];
        const brandAnalysis = fullData?.brand_analysis || data.brand_analysis || {};
        const foundPlatforms = platforms.filter(p => p.found);
        
        let yPos = 20;
        const margin = 20;
        const pageWidth = doc.internal.pageSize.width;
        
        // Title
        doc.setFontSize(18);
        doc.setFont(undefined, 'bold');
        doc.text(`${brandAnalysis.brand_name || 'Brand'} Brand Analysis Report`, margin, yPos);
        yPos += 15;
        
        // Underline
        doc.setLineWidth(0.5);
        doc.line(margin, yPos, pageWidth - margin, yPos);
        yPos += 15;
        
        // Brand Information
        doc.setFontSize(14);
        doc.setFont(undefined, 'bold');
        doc.text('Brand Information', margin, yPos);
        yPos += 10;
        
        doc.setFontSize(10);
        doc.setFont(undefined, 'normal');
        doc.text(`Brand: ${brandAnalysis.brand_name || 'Unknown'}`, margin, yPos);
        yPos += 6;
        doc.text(`Website: ${brandAnalysis.website || 'N/A'}`, margin, yPos);
        yPos += 6;
        doc.text(`Analysis Date: ${new Date().toLocaleDateString()}`, margin, yPos);
        yPos += 6;
        doc.text(`Processing: AI-powered analysis`, margin, yPos);
        yPos += 15;
        
        // Summary
        doc.setFontSize(14);
        doc.setFont(undefined, 'bold');
        doc.text('Summary', margin, yPos);
        yPos += 10;
        
        doc.setFontSize(10);
        doc.setFont(undefined, 'normal');
        doc.text(`Total Platforms Checked: ${platforms.length}`, margin, yPos);
        yPos += 6;
        doc.text(`Platforms Found: ${foundPlatforms.length}`, margin, yPos);
        yPos += 6;
        doc.text(`Platforms Missing: ${platforms.length - foundPlatforms.length}`, margin, yPos);
        yPos += 15;
        
        // Platform Presence Table (exactly like brandfind.html)
        doc.setFontSize(14);
        doc.setFont(undefined, 'bold');
        doc.text('Platform Presence', margin, yPos);
        yPos += 15;
        
        // Table setup for landscape format (much wider)
        const colWidths = [40, 25, 25, 25, 55, 100]; // Platform, Status, Verified, Confidence, URL, Notes
        const tableWidth = colWidths.reduce((a, b) => a + b, 0);
        const startX = margin;
        let currentX = startX;
        
        // Table headers (like brandfind.html)
        doc.setFillColor(241, 241, 241); // Light gray header
        doc.rect(startX, yPos, tableWidth, 8, 'F');
        
        doc.setFontSize(9);
        doc.setFont(undefined, 'bold');
        doc.setTextColor(0, 0, 0);
        
        const headers = ['Platform', 'Status', 'Verified', 'Confidence', 'Profile URL', 'Notes'];
        headers.forEach((header, i) => {
            doc.text(header, currentX + 2, yPos + 5);
            currentX += colWidths[i];
        });
        
        yPos += 8;
        
        // Header border
        doc.setDrawColor(204, 204, 204);
        doc.setLineWidth(0.5);
        doc.line(startX, yPos, startX + tableWidth, yPos);
        yPos += 2;
        
        // Table rows
        doc.setFontSize(8);
        doc.setFont(undefined, 'normal');
        
        platforms.forEach((platform, index) => {
            if (yPos > 180) { // Adjusted for landscape format
                doc.addPage();
                yPos = 20;
                
                // Repeat headers on new page
                doc.setFillColor(241, 241, 241);
                doc.rect(startX, yPos, tableWidth, 8, 'F');
                doc.setFontSize(9);
                doc.setFont(undefined, 'bold');
                doc.setTextColor(0, 0, 0);
                
                currentX = startX;
                headers.forEach((header, i) => {
                    doc.text(header, currentX + 2, yPos + 5);
                    currentX += colWidths[i];
                });
                yPos += 10;
                
                doc.setFontSize(8);
                doc.setFont(undefined, 'normal');
            }
            
            // Calculate row height based on notes content (no more truncation!)
            const notes = platform.notes || '';
            const notesLines = notes ? doc.splitTextToSize(notes, colWidths[5] - 4) : [''];
            const rowHeight = Math.max(14, notesLines.length * 4 + 10);
            
            currentX = startX;
            
            // Alternating row colors (like brandfind.html)
            if (index % 2 === 0) {
                doc.setFillColor(249, 249, 249); // Very light gray
                doc.rect(startX, yPos, tableWidth, rowHeight, 'F');
            }
            
            const status = platform.found ? 'Found' : 'Not Found';
            const verified = platform.found ? (platform.verified ? 'Verified' : 'Unverified') : 'N/A';
            const confidence = platform.confidence ? platform.confidence.charAt(0).toUpperCase() + platform.confidence.slice(1) : 'N/A';
            const profileUrl = platform.profile_url || '';
            
            // Platform name
            doc.setTextColor(0, 0, 0);
            doc.text(platform.name, currentX + 2, yPos + 7);
            currentX += colWidths[0];
            
            // Status (colored like brandfind.html badges)
            if (status === 'Found') {
                doc.setTextColor(40, 167, 69); // Green like .verified badge
            } else {
                doc.setTextColor(108, 117, 125); // Gray like .not-found badge
            }
            doc.text(status, currentX + 2, yPos + 7);
            currentX += colWidths[1];
            
            // Verified (colored like brandfind.html badges)
            if (verified === 'Verified') {
                doc.setTextColor(40, 167, 69); // Green
            } else if (verified === 'Unverified') {
                doc.setTextColor(220, 53, 69); // Red like .unverified badge
            } else {
                doc.setTextColor(108, 117, 125); // Gray
            }
            doc.text(verified, currentX + 2, yPos + 7);
            currentX += colWidths[2];
            
            // Confidence (colored like brandfind.html badges)
            if (confidence === 'High') {
                doc.setTextColor(0, 123, 255); // Blue like .high badge
            } else if (confidence === 'Medium') {
                doc.setTextColor(23, 162, 184); // Cyan like .medium badge
            } else if (confidence === 'Low') {
                doc.setTextColor(255, 193, 7); // Yellow like .low badge
                doc.setTextColor(0, 0, 0); // Black text for readability on yellow
            } else {
                doc.setTextColor(108, 117, 125); // Gray
            }
            doc.text(confidence, currentX + 2, yPos + 7);
            currentX += colWidths[3];
            
            // Profile URL (clickable and shows actual URL)
            if (profileUrl) {
                doc.setTextColor(0, 123, 255); // Blue like links in brandfind.html
                const displayUrl = profileUrl.length > 25 ? profileUrl.substring(0, 22) + '...' : profileUrl;
                doc.text(displayUrl, currentX + 2, yPos + 7);
                // Make URL clickable
                doc.link(currentX + 2, yPos + 2, colWidths[4] - 4, 10, { url: profileUrl });
            } else {
                doc.setTextColor(108, 117, 125); // Gray
                doc.text('N/A', currentX + 2, yPos + 7);
            }
            currentX += colWidths[4];
            
            // Notes (full text with wrapping, no truncation!)
            doc.setTextColor(0, 0, 0);
            if (notesLines.length > 0 && notesLines[0]) {
                doc.text(notesLines, currentX + 2, yPos + 7);
            }
            
            yPos += rowHeight;
            
            // Row border
            doc.setDrawColor(204, 204, 204);
            doc.setLineWidth(0.3);
            doc.line(startX, yPos, startX + tableWidth, yPos);
        });
        
        yPos += 15;
        
        // Recommendations Section (like brandfind.html)
        if (data.recommendations && data.recommendations.length > 0) {
            if (yPos > 240) {
                doc.addPage();
                yPos = 20;
            }
            
            doc.setFontSize(14);
            doc.setFont(undefined, 'bold');
            doc.setTextColor(0, 0, 0);
            doc.text('Recommendations', margin, yPos);
            yPos += 15;
            
            data.recommendations.forEach(rec => {
                if (yPos > 250) {
                    doc.addPage();
                    yPos = 20;
                }
                
                const priority = rec.priority ? rec.priority.charAt(0).toUpperCase() + rec.priority.slice(1) : 'Unknown';
                
                // Recommendation box background (like brandfind.html .recommendation)
                const boxHeight = 20;
                doc.setFillColor(233, 236, 239); // Light gray background
                doc.rect(margin, yPos, pageWidth - margin * 2, boxHeight, 'F');
                
                // Left border color based on priority (like brandfind.html)
                if (priority.toLowerCase() === 'high') {
                    doc.setFillColor(0, 123, 255); // Blue
                } else if (priority.toLowerCase() === 'medium') {
                    doc.setFillColor(23, 162, 184); // Cyan
                } else {
                    doc.setFillColor(108, 117, 125); // Gray
                }
                doc.rect(margin, yPos, 3, boxHeight, 'F'); // Left border
                
                // Platform name
                doc.setFontSize(11);
                doc.setFont(undefined, 'bold');
                doc.setTextColor(0, 0, 0);
                doc.text(`${rec.platform}`, margin + 8, yPos + 8);
                
                // Priority badge background (like brandfind.html badges)
                const badgeText = `${priority} Priority`;
                const badgeX = margin + 8 + doc.getTextWidth(`${rec.platform} `) + 10;
                const badgeWidth = doc.getTextWidth(badgeText) + 8;
                
                if (priority.toLowerCase() === 'high') {
                    doc.setFillColor(0, 123, 255); // Blue like .high badge
                } else if (priority.toLowerCase() === 'medium') {
                    doc.setFillColor(23, 162, 184); // Cyan like .medium badge  
                } else {
                    doc.setFillColor(108, 117, 125); // Gray
                }
                doc.rect(badgeX, yPos + 4, badgeWidth, 8, 'F');
                
                // Badge text
                doc.setFontSize(8);
                doc.setFont(undefined, 'bold');
                doc.setTextColor(255, 255, 255); // White text
                doc.text(badgeText, badgeX + 4, yPos + 9);
                
                // Reason text
                doc.setFontSize(9);
                doc.setFont(undefined, 'normal');
                doc.setTextColor(0, 0, 0);
                const reasonLines = doc.splitTextToSize(rec.reason, pageWidth - margin * 2 - 20);
                doc.text(reasonLines.slice(0, 1), margin + 8, yPos + 16); // One line only
                
                yPos += boxHeight + 5;
            });
            
            yPos += 5;
        }
        
        // Footer
        const totalPages = doc.internal.getNumberOfPages();
        for (let i = 1; i <= totalPages; i++) {
            doc.setPage(i);
            doc.setFontSize(8);
            doc.text(`Page ${i} of ${totalPages}`, pageWidth - 30, doc.internal.pageSize.height - 10);
            doc.text('Generated by Quantum Tasks AI', margin, doc.internal.pageSize.height - 10);
        }
        
        // Save PDF
        const brandName = (brandAnalysis.brand_name || 'Brand').replace(/[^a-zA-Z0-9]/g, '_');
        const date = new Date().toISOString().split('T')[0];
        const filename = `${brandName}_Brand_Analysis_${date}.pdf`;
        
        console.log('Saving PDF:', filename);
        doc.save(filename);
        
        console.log('PDF generated successfully!');
        if (window.WorkflowsCore) {
            WorkflowsCore.showToast('PDF report downloaded successfully!', 'success');
        }
        
    } catch (error) {
        console.error('Simple PDF generation failed:', error);
        throw error; // Re-throw to trigger fallback
    }
}

// Direct PDF generation function for brand presence (keep for compatibility)
function generateBrandPresencePDFDirect(data, fullData = null) {
    try {
        console.log('Starting direct PDF generation...');
        console.log('window.jsPDF:', window.jsPDF);
        
        if (!window.jsPDF) {
            throw new Error('jsPDF not available');
        }
        
        const { jsPDF } = window;
        console.log('jsPDF constructor:', jsPDF);
        
        if (typeof jsPDF !== 'function') {
            throw new Error('jsPDF is not a function');
        }
        
        console.log('Creating new jsPDF document...');
        const doc = new jsPDF();
        console.log('jsPDF document created successfully');
        
        const platforms = data.platforms || [];
        const summary = data.summary || {};
        const recommendations = data.recommendations || [];
        const brandAnalysis = fullData?.brand_analysis || data.brand_analysis || {};
        
        const foundPlatforms = platforms.filter(p => p.found);
        const completionPercentage = Math.round(summary.completion_percentage || 0);
        
        let yPos = 20;
        const pageWidth = doc.internal.pageSize.width;
        const margin = 20;
        
        // Title
        doc.setFontSize(20);
        doc.setFont(undefined, 'bold');
        const title = `${brandAnalysis.brand_name || 'Brand'} Brand Analysis Report`;
        doc.text(title, margin, yPos);
        yPos += 15;
        
        // Title underline
        doc.setLineWidth(0.5);
        doc.line(margin, yPos, pageWidth - margin, yPos);
        yPos += 15;
        
        // Brand Information Section
        doc.setFontSize(14);
        doc.setFont(undefined, 'bold');
        doc.text('Brand Information', margin, yPos);
        yPos += 10;
        
        doc.setFontSize(10);
        doc.setFont(undefined, 'normal');
        doc.text(`Brand: ${brandAnalysis.brand_name || 'Unknown'}`, margin, yPos);
        yPos += 6;
        doc.text(`Website: ${brandAnalysis.website || 'N/A'}`, margin, yPos);
        yPos += 6;
        doc.text(`Analysis Date: ${new Date().toLocaleDateString('en-US', { 
            year: 'numeric', month: 'long', day: 'numeric' 
        })}`, margin, yPos);
        yPos += 6;
        doc.text(`Processing: AI-powered analysis`, margin, yPos);
        yPos += 15;
        
        // Summary Section
        doc.setFontSize(14);
        doc.setFont(undefined, 'bold');
        doc.text('Summary', margin, yPos);
        yPos += 10;
        
        doc.setFontSize(10);
        doc.setFont(undefined, 'normal');
        doc.text(`Total Platforms Checked: ${platforms.length}`, margin, yPos);
        yPos += 6;
        doc.text(`Platforms Found: ${foundPlatforms.length}`, margin, yPos);
        yPos += 6;
        doc.text(`Platforms Missing: ${platforms.length - foundPlatforms.length}`, margin, yPos);
        yPos += 6;
        doc.text(`Completion: ${completionPercentage}%`, margin, yPos);
        yPos += 15;
        
        // Platform Presence Table (like brandfind.html)
        doc.setFontSize(14);
        doc.setFont(undefined, 'bold');
        doc.text('Platform Presence', margin, yPos);
        yPos += 12;
        
        // Table headers
        doc.setFontSize(9);
        doc.setFont(undefined, 'bold');
        const headers = ['Platform', 'Status', 'Verified', 'Confidence', 'Profile URL', 'Notes'];
        const colWidths = [28, 18, 18, 18, 35, 53];
        let xPos = margin;
        
        // Draw header background
        doc.setFillColor(241, 241, 241); // Light gray background
        doc.rect(margin, yPos - 3, pageWidth - margin * 2, 8, 'F');
        
        // Header text
        doc.setTextColor(0, 0, 0);
        headers.forEach((header, i) => {
            doc.text(header, xPos + 1, yPos + 2);
            xPos += colWidths[i];
        });
        yPos += 8;
        
        // Header border
        doc.setLineWidth(0.5);
        doc.line(margin, yPos, pageWidth - margin, yPos);
        yPos += 3;
        
        // Platform rows
        doc.setFont(undefined, 'normal');
        doc.setFontSize(8);
        
        platforms.forEach((platform, index) => {
            if (yPos > 270) { // New page if needed
                doc.addPage();
                yPos = 20;
                
                // Redraw headers on new page
                doc.setFontSize(9);
                doc.setFont(undefined, 'bold');
                doc.setFillColor(241, 241, 241);
                doc.rect(margin, yPos - 3, pageWidth - margin * 2, 8, 'F');
                
                xPos = margin;
                headers.forEach((header, i) => {
                    doc.text(header, xPos + 1, yPos + 2);
                    xPos += colWidths[i];
                });
                yPos += 8;
                doc.setLineWidth(0.5);
                doc.line(margin, yPos, pageWidth - margin, yPos);
                yPos += 3;
                
                doc.setFont(undefined, 'normal');
                doc.setFontSize(8);
            }
            
            // Alternate row colors
            if (index % 2 === 0) {
                doc.setFillColor(249, 249, 249); // Very light gray
                doc.rect(margin, yPos - 2, pageWidth - margin * 2, 12, 'F');
            }
            
            xPos = margin;
            const status = platform.found ? 'Found' : 'Not Found';
            const verified = platform.found ? (platform.verified ? 'Verified' : 'Unverified') : 'N/A';
            const confidence = platform.confidence ? platform.confidence.charAt(0).toUpperCase() + platform.confidence.slice(1) : 'N/A';
            const profileUrl = platform.profile_url ? 'Profile' : 'N/A';
            const notes = platform.notes || '';
            
            const rowData = [platform.name, status, verified, confidence, profileUrl, notes];
            
            // Set colors based on status
            rowData.forEach((cell, i) => {
                if (i === 1) { // Status column
                    if (status === 'Found') {
                        doc.setTextColor(40, 167, 69); // Green
                    } else {
                        doc.setTextColor(220, 53, 69); // Red
                    }
                } else if (i === 2) { // Verified column  
                    if (verified === 'Verified') {
                        doc.setTextColor(40, 167, 69); // Green
                    } else if (verified === 'Unverified') {
                        doc.setTextColor(220, 53, 69); // Red
                    } else {
                        doc.setTextColor(108, 117, 125); // Gray
                    }
                } else if (i === 3) { // Confidence column
                    if (confidence === 'High') {
                        doc.setTextColor(0, 123, 255); // Blue
                    } else if (confidence === 'Medium') {
                        doc.setTextColor(23, 162, 184); // Cyan
                    } else if (confidence === 'Low') {
                        doc.setTextColor(255, 193, 7); // Yellow/Orange
                    } else {
                        doc.setTextColor(108, 117, 125); // Gray
                    }
                } else {
                    doc.setTextColor(0, 0, 0); // Black for other columns
                }
                
                if (i === 5) { // Notes column - wrap text
                    const lines = doc.splitTextToSize(cell, colWidths[i] - 2);
                    doc.text(lines.slice(0, 2), xPos + 1, yPos + 2); // Max 2 lines
                } else {
                    // Truncate long text
                    const truncated = cell.length > 15 ? cell.substring(0, 12) + '...' : cell;
                    doc.text(truncated, xPos + 1, yPos + 2);
                }
                xPos += colWidths[i];
            });
            
            yPos += 12;
            
            // Row border
            doc.setDrawColor(204, 204, 204); // Light gray
            doc.setLineWidth(0.3);
            doc.line(margin, yPos, pageWidth - margin, yPos);
        });
        
        // Recommendations Section (like brandfind.html)
        if (recommendations && recommendations.length > 0) {
            yPos += 15;
            if (yPos > 250) {
                doc.addPage();
                yPos = 20;
            }
            
            doc.setFontSize(14);
            doc.setFont(undefined, 'bold');
            doc.setTextColor(0, 0, 0);
            doc.text('Recommendations', margin, yPos);
            yPos += 15;
            
            recommendations.forEach(rec => {
                if (yPos > 260) {
                    doc.addPage();
                    yPos = 20;
                }
                
                const priority = rec.priority ? rec.priority.charAt(0).toUpperCase() + rec.priority.slice(1) : 'Unknown';
                
                // Draw recommendation box (like brandfind.html)
                doc.setFillColor(233, 236, 239); // Light gray background
                doc.rect(margin, yPos - 2, pageWidth - margin * 2, 18, 'F');
                
                // Left border color based on priority
                if (priority.toLowerCase().includes('high')) {
                    doc.setFillColor(0, 123, 255); // Blue
                } else if (priority.toLowerCase().includes('medium')) {
                    doc.setFillColor(23, 162, 184); // Cyan
                } else {
                    doc.setFillColor(108, 117, 125); // Gray
                }
                doc.rect(margin, yPos - 2, 3, 18, 'F'); // Left border
                
                // Platform name and priority badge
                doc.setFontSize(11);
                doc.setFont(undefined, 'bold');
                doc.setTextColor(0, 0, 0);
                doc.text(`${rec.platform}`, margin + 8, yPos + 4);
                
                // Priority badge
                const badgeX = margin + 8 + doc.getTextWidth(`${rec.platform} `) + 5;
                
                // Badge background color
                if (priority.toLowerCase().includes('high')) {
                    doc.setFillColor(0, 123, 255); // Blue
                } else if (priority.toLowerCase().includes('medium')) {
                    doc.setFillColor(23, 162, 184); // Cyan  
                } else {
                    doc.setFillColor(108, 117, 125); // Gray
                }
                
                const badgeWidth = doc.getTextWidth(`${priority} Priority`) + 6;
                // Use regular rect instead of roundedRect for compatibility
                doc.rect(badgeX, yPos + 1, badgeWidth, 6, 'F');
                
                // Badge text
                doc.setFontSize(8);
                doc.setFont(undefined, 'bold');
                doc.setTextColor(255, 255, 255); // White text
                doc.text(`${priority} Priority`, badgeX + 3, yPos + 4.5);
                
                // Reason text
                doc.setFontSize(9);
                doc.setFont(undefined, 'normal');
                doc.setTextColor(0, 0, 0);
                const reasonLines = doc.splitTextToSize(rec.reason, pageWidth - margin * 2 - 15);
                doc.text(reasonLines.slice(0, 2), margin + 8, yPos + 10); // Max 2 lines
                
                yPos += 22;
            });
        }
        
        // Footer
        const totalPages = doc.internal.getNumberOfPages();
        for (let i = 1; i <= totalPages; i++) {
            doc.setPage(i);
            doc.setFontSize(8);
            doc.setFont(undefined, 'normal');
            doc.text(`Page ${i} of ${totalPages}`, pageWidth - 30, doc.internal.pageSize.height - 10);
            doc.text('Generated by Quantum Tasks AI', margin, doc.internal.pageSize.height - 10);
        }
        
        // Save PDF
        const brandName = (brandAnalysis.brand_name || 'Brand').replace(/[^a-zA-Z0-9]/g, '_');
        const date = new Date().toISOString().split('T')[0];
        const filename = `${brandName}_Brand_Analysis_${date}.pdf`;
        
        doc.save(filename);
        console.log('PDF saved successfully:', filename);
        
        // Show success message
        if (window.WorkflowsCore) {
            WorkflowsCore.showToast('PDF report downloaded successfully!', 'success');
        }
        
    } catch (error) {
        console.error('Direct PDF generation failed:', error);
        throw error; // Re-throw to trigger fallback
    }
}

// Fallback text download for brand presence
function fallbackBrandPresenceTextDownload() {
    try {
        if (!window.brandPresenceData) {
            WorkflowsCore.showToast('No brand data available for download', 'error');
            return;
        }
        
        const data = window.brandPresenceData;
        const fullData = window.brandPresenceFullData;
        const platforms = data.platforms || [];
        const brandAnalysis = fullData?.brand_analysis || data.brand_analysis || {};
        
        let report = `${brandAnalysis.brand_name || 'Brand'} Brand Analysis Report\n`;
        report += `${'='.repeat(50)}\n\n`;
        
        // Brand Information
        report += `Brand Information\n-----------------\n`;
        report += `Brand: ${brandAnalysis.brand_name || 'Unknown'}\n`;
        report += `Website: ${brandAnalysis.website || 'N/A'}\n`;
        report += `Analysis Date: ${new Date().toLocaleDateString('en-US', { 
            year: 'numeric', month: 'long', day: 'numeric' 
        })}\n`;
        report += `Processing: AI-powered analysis\n\n`;
        
        // Platform Summary
        const foundPlatforms = platforms.filter(p => p.found);
        report += `Summary\n-------\n`;
        report += `Total Platforms: ${platforms.length}\n`;
        report += `Found: ${foundPlatforms.length}\n`;
        report += `Missing: ${platforms.length - foundPlatforms.length}\n\n`;
        
        // Platform Details
        report += `Platform Details\n----------------\n`;
        platforms.forEach(platform => {
            const status = platform.found ? 'Found' : 'Not Found';
            const verified = platform.found ? (platform.verified ? 'Verified' : 'Unverified') : 'N/A';
            report += `\n${platform.name}:\n`;
            report += `  Status: ${status}\n`;
            report += `  Verified: ${verified}\n`;
            report += `  Notes: ${platform.notes || 'N/A'}\n`;
            if (platform.profile_url) {
                report += `  URL: ${platform.profile_url}\n`;
            }
        });
        
        report += `\n\nGenerated by Quantum Tasks AI\n`;
        
        const brandName = (brandAnalysis.brand_name || 'Brand').replace(/[^a-zA-Z0-9]/g, '_');
        const filename = `${brandName}_Brand_Analysis_${new Date().toISOString().split('T')[0]}.txt`;
        
        WorkflowsCore.downloadAsFile(report, filename, 'Brand analysis report downloaded!');
        
    } catch (error) {
        console.error('Fallback text download failed:', error);
        WorkflowsCore.showToast('Download failed', 'error');
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
    
    // Clear validation errors
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        const field = group.querySelector('input, select, textarea');
        if (field) {
            WorkflowsCore.clearFieldError(field.id);
        }
    });
    
    // Scroll back to form
    const formSection = document.getElementById('agentForm');
    if (formSection) {
        formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Quick Agents Panel Functions
function toggleQuickAgents() {
    const panel = document.getElementById('quickAgentsPanel');
    const overlay = document.getElementById('quickAgentsOverlay');
    
    if (panel && overlay) {
        const isOpen = panel.getAttribute('aria-hidden') === 'false';
        
        if (isOpen) {
            // Close panel
            panel.setAttribute('aria-hidden', 'true');
            overlay.setAttribute('aria-hidden', 'true');
            panel.style.transform = 'translateX(100%)';
            overlay.style.opacity = '0';
            overlay.style.visibility = 'hidden';
        } else {
            // Open panel
            panel.setAttribute('aria-hidden', 'false');
            overlay.setAttribute('aria-hidden', 'false');
            panel.style.transform = 'translateX(0)';
            overlay.style.opacity = '1';
            overlay.style.visibility = 'visible';
        }
    }
}

function closeQuickAgents() {
    const panel = document.getElementById('quickAgentsPanel');
    const overlay = document.getElementById('quickAgentsOverlay');
    
    if (panel && overlay) {
        panel.setAttribute('aria-hidden', 'true');
        overlay.setAttribute('aria-hidden', 'true');
        panel.style.transform = 'translateX(100%)';
        overlay.style.opacity = '0';
        overlay.style.visibility = 'hidden';
    }
}

// Close panel with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeQuickAgents();
    }
});

// Initialize AgentsCore when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('agentForm')) {
        window.agentsCore = new AgentsCore();
    }
});