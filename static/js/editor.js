class ModernAIEditor {
    constructor() {
        this.titleInput = document.getElementById('title-input');
        this.editor = document.getElementById('editor');
        this.suggestionControls = document.getElementById('suggestion-controls');
        this.wordCountEl = document.getElementById('word-count');
        this.charCountEl = document.getElementById('char-count');
        this.readingTimeEl = document.getElementById('reading-time');
        
        // Button references
        this.acceptBtn = document.getElementById('accept-btn');
        this.tryAgainBtn = document.getElementById('try-again-btn');
        this.dismissBtn = document.getElementById('dismiss-btn');
        
        this.debounceTimer = null;
        this.debounceDelay = 1500;
        this.currentRequestId = 0;
        this.currentSuggestion = null;
        this.suggestionElement = null;
        this.originalRange = null;
        
        this.init();
    }
    
    init() {
        // Force disable spellcheck on editor elements
        this.editor.spellcheck = false;
        this.editor.setAttribute('spellcheck', 'false');
        this.titleInput.spellcheck = false;
        this.titleInput.setAttribute('spellcheck', 'false');
        
        // Add event listeners
        this.editor.addEventListener('input', (e) => this.handleTextInput(e));
        this.editor.addEventListener('keydown', (e) => this.handleKeyDown(e));
        this.titleInput.addEventListener('input', (e) => this.handleTitleInput(e));
        this.titleInput.addEventListener('keydown', (e) => this.handleTitleKeyDown(e));
        
        // Button event listeners
        this.acceptBtn.addEventListener('click', () => this.acceptSuggestion());
        this.tryAgainBtn.addEventListener('click', () => this.requestNewSuggestion());
        this.dismissBtn.addEventListener('click', () => this.dismissSuggestion());
        
        // Initialize stats
        this.updateStats();
        
        console.log('Modern AI editor initialized');
    }
    
    handleTitleInput(event) {
        // Clear any existing suggestions when title changes
        this.clearSuggestion();
        
        // Schedule auto-save but don't trigger AI suggestions for title
        if (window.scheduleAutoSave) {
            window.scheduleAutoSave();
        }
    }
    
    handleTitleKeyDown(event) {
        // Prevent Enter key from triggering any AI generation in title
        if (event.key === 'Enter') {
            event.preventDefault();
            // Instead, focus on the editor when Enter is pressed in title
            this.editor.focus();
            // Position cursor at the end of editor content
            const selection = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(this.editor);
            range.collapse(false);
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }
    
    handleTextInput(event) {
        // Update stats immediately
        this.updateStats();
        
        // Clear current suggestion when user types
        this.clearSuggestion();
        
        // Only make AI request if title is provided
        if (!this.titleInput.value.trim()) {
            return;
        }
        
        // Trigger debounced AI request
        this.debouncedAIRequest();
    }
    
    handleKeyDown(event) {
        // Handle suggestion shortcuts
        if (this.currentSuggestion) {
            if (event.key === 'Tab') {
                event.preventDefault();
                if (event.shiftKey) {
                    this.requestNewSuggestion();
                } else {
                    this.acceptSuggestion();
                }
                return;
            }
            
            if (event.key === 'Escape') {
                event.preventDefault();
                this.dismissSuggestion();
                return;
            }
        }
    }
    
    getTextContent() {
        return this.editor.textContent || '';
    }
    
    debouncedAIRequest() {
        // Clear existing timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        // Set new timer
        this.debounceTimer = setTimeout(() => {
            this.makeAIRequest();
        }, this.debounceDelay);
    }
    
    async makeAIRequest() {
        const title = this.titleInput.value.trim();
        const text = this.getTextContent().trim();
        
        if (!title) {
            return;
        }
        
        // Generate unique request ID
        const requestId = ++this.currentRequestId;
        
        try {
            const response = await fetch('/api/ai-assist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    text: text,
                    current_text_id: window.currentActiveTextId || null
                })
            });
            
            const result = await response.json();
            
            // Check if this is still the latest request
            if (requestId !== this.currentRequestId) {
                return;
            }
            
            // Handle subscription required response
            if (response.status === 403 && result.error === 'Subscription required') {
                // Show pricing message and redirect
                this.showSubscriptionAlert(result);
                return;
            }
            
            if (result.success && result.suggestions && result.suggestions.length > 0) {
                // Get the first continuation suggestion
                const continuationSuggestion = result.suggestions.find(s => s.type === 'continuation') || result.suggestions[0];
                this.showInlineSuggestion(continuationSuggestion.text);
            }
            
        } catch (error) {
            if (requestId !== this.currentRequestId) {
                return;
            }
            
            console.error('AI request error:', error);
        }
    }
    
    showInlineSuggestion(suggestion) {
        
        // Store the current selection/cursor position
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            this.originalRange = selection.getRangeAt(0).cloneRange();
        }
        
        // Clean the suggestion
        const cleanedSuggestion = this.cleanSuggestion(suggestion);
        this.currentSuggestion = cleanedSuggestion;
        
        console.log('Showing suggestion:', cleanedSuggestion);
        
        // Create suggestion element
        this.suggestionElement = document.createElement('span');
        this.suggestionElement.className = 'ai-suggestion';
        this.suggestionElement.textContent = cleanedSuggestion;
        this.suggestionElement.spellcheck = false;
        this.suggestionElement.setAttribute('spellcheck', 'false');
        
        // Insert suggestion at cursor position
        if (this.originalRange) {
            this.originalRange.insertNode(this.suggestionElement);
        } else {
            // Fallback: append to end
            this.editor.appendChild(this.suggestionElement);
        }
        
        // Position and show controls
        this.positionControls();
        this.suggestionControls.classList.remove('hidden');
    }
    
    cleanSuggestion(suggestion) {
        const userText = this.getTextContent().replace(/\s+/g, ' ').trim();
        const suggestionLower = suggestion.toLowerCase().trim();
        const userTextLower = userText.toLowerCase();
        
        // If suggestion starts with user's text, remove the duplicate part
        if (suggestionLower.startsWith(userTextLower)) {
            return suggestion.substring(userText.length).trim();
        }
        
        return suggestion.trim();
    }
    
    positionControls() {
        if (!this.suggestionElement) return;
        
        const rect = this.suggestionElement.getBoundingClientRect();
        const editorRect = this.editor.getBoundingClientRect();
        
        // Position below the suggestion
        this.suggestionControls.style.top = (rect.bottom + 10) + 'px';
        this.suggestionControls.style.left = Math.max(10, rect.left) + 'px';
    }
    
    acceptSuggestion() {
        if (!this.currentSuggestion || !this.suggestionElement) return;
        
        console.log('Accepting suggestion:', this.currentSuggestion);
        
        // Replace suggestion element with plain text
        const textNode = document.createTextNode(this.currentSuggestion);
        this.suggestionElement.parentNode.replaceChild(textNode, this.suggestionElement);
        
        // Position cursor after the inserted text
        const selection = window.getSelection();
        const range = document.createRange();
        range.setStartAfter(textNode);
        range.collapse(true);
        selection.removeAllRanges();
        selection.addRange(range);
        
        // Clear suggestion
        this.clearSuggestion();
        
        // Update stats
        this.updateStats();
        
        // Focus editor
        this.editor.focus();
        
        // Trigger auto-save and auto-resize for the accepted content
        if (window.scheduleAutoSave) {
            window.scheduleAutoSave();
        }
        if (window.autoResizeEditor) {
            setTimeout(window.autoResizeEditor, 10);
        }
        
        // Request new suggestion after a brief delay
        setTimeout(() => {
            this.debouncedAIRequest();
        }, 1000);
    }
    
    requestNewSuggestion() {
        if (!this.currentSuggestion) return;
        
        this.clearSuggestion();
        this.makeAIRequest();
    }
    
    dismissSuggestion() {
        this.clearSuggestion();
        this.editor.focus();
    }
    
    clearSuggestion() {
        if (this.suggestionElement && this.suggestionElement.parentNode) {
            this.suggestionElement.parentNode.removeChild(this.suggestionElement);
        }
        
        this.currentSuggestion = null;
        this.suggestionElement = null;
        this.originalRange = null;
        this.suggestionControls.classList.add('hidden');
    }
    
    
    updateStats() {
        const text = this.getTextContent();
        
        // Word count
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        this.wordCountEl.textContent = words;
        
        // Character count
        const chars = text.length;
        this.charCountEl.textContent = chars;
        
        // Reading time (average 200 words per minute)
        const readingTime = Math.max(1, Math.ceil(words / 200));
        this.readingTimeEl.textContent = `${readingTime} min`;
    }
    
    showSubscriptionAlert(result) {
        // Clear any existing suggestion first
        this.clearSuggestion();
        
        let message = 'Your free trial has expired. Please choose a plan to continue using AI assistance.';
        
        if (result.trial_expired) {
            message = 'Your free trial has expired. Please choose a plan to continue.';
        } else if (result.subscription_status === 'past_due') {
            message = 'Your subscription payment is overdue. Please update your payment method.';
        } else if (result.subscription_status === 'canceled') {
            message = 'Your subscription has been canceled. Please choose a plan to continue.';
        }
        
        // Show alert with option to go to pricing
        if (confirm(message + '\n\nWould you like to view our pricing plans?')) {
            window.location.href = result.redirect_url || '/pricing';
        }
    }
}

// Initialize editor when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.editor = new ModernAIEditor();
});