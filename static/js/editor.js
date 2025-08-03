class ModernAIEditor {
    constructor() {
        this.titleInput = document.getElementById('title-input');
        this.editor = document.getElementById('editor');
        this.suggestionControls = document.getElementById('suggestion-controls');
        this.statusIndicator = document.getElementById('status-indicator');
        this.aiStatus = document.getElementById('ai-status');
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
        // Add event listeners
        this.editor.addEventListener('input', (e) => this.handleTextInput(e));
        this.editor.addEventListener('keydown', (e) => this.handleKeyDown(e));
        this.titleInput.addEventListener('input', (e) => this.handleTitleInput(e));
        
        // Button event listeners
        this.acceptBtn.addEventListener('click', () => this.acceptSuggestion());
        this.tryAgainBtn.addEventListener('click', () => this.requestNewSuggestion());
        this.dismissBtn.addEventListener('click', () => this.dismissSuggestion());
        
        // Initialize stats
        this.updateStats();
        this.updateAIStatus('Ready - Start writing with a title');
        
        console.log('Modern AI editor initialized');
    }
    
    handleTitleInput(event) {
        this.clearSuggestion();
        
        if (!this.titleInput.value.trim()) {
            this.updateAIStatus('Enter a title to enable AI suggestions');
        } else if (this.getTextContent().trim()) {
            this.updateAIStatus('Ready');
            this.debouncedAIRequest();
        } else {
            this.updateAIStatus('Ready - Start writing');
        }
    }
    
    handleTextInput(event) {
        // Update stats immediately
        this.updateStats();
        
        // Clear current suggestion when user types
        this.clearSuggestion();
        
        // Only make AI request if title is provided
        if (!this.titleInput.value.trim()) {
            this.updateAIStatus('Enter a title to enable AI suggestions');
            return;
        }
        
        // Trigger debounced AI request
        this.updateAIStatus('Ready');
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
        
        // Show loading state
        this.showLoadingState();
        
        // Set new timer
        this.debounceTimer = setTimeout(() => {
            this.makeAIRequest();
        }, this.debounceDelay);
    }
    
    async makeAIRequest() {
        const title = this.titleInput.value.trim();
        const text = this.getTextContent().trim();
        
        if (!title) {
            this.hideLoadingState();
            return;
        }
        
        // Generate unique request ID
        const requestId = ++this.currentRequestId;
        
        try {
            this.updateAIStatus('Generating suggestion...');
            
            const response = await fetch('/api/ai-assist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    text: text
                })
            });
            
            const result = await response.json();
            
            // Check if this is still the latest request
            if (requestId !== this.currentRequestId) {
                return;
            }
            
            if (result.success && result.suggestions && result.suggestions.length > 0) {
                // Get the first continuation suggestion
                const continuationSuggestion = result.suggestions.find(s => s.type === 'continuation') || result.suggestions[0];
                this.showInlineSuggestion(continuationSuggestion.text);
                this.updateAIStatus('AI suggestion ready');
            } else {
                this.updateAIStatus('No suggestions available');
                this.hideLoadingState();
            }
            
        } catch (error) {
            if (requestId !== this.currentRequestId) {
                return;
            }
            
            console.error('AI request error:', error);
            this.updateAIStatus('Failed to get suggestions');
            this.hideLoadingState();
        }
    }
    
    showInlineSuggestion(suggestion) {
        this.hideLoadingState();
        
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
        
        // Update stats and status
        this.updateStats();
        this.updateAIStatus('Suggestion applied');
        
        // Focus editor
        this.editor.focus();
        
        // Request new suggestion after a brief delay
        setTimeout(() => {
            this.debouncedAIRequest();
        }, 1000);
    }
    
    requestNewSuggestion() {
        if (!this.currentSuggestion) return;
        
        this.clearSuggestion();
        this.updateAIStatus('Getting new suggestion...');
        this.makeAIRequest();
    }
    
    dismissSuggestion() {
        this.clearSuggestion();
        this.updateAIStatus('Suggestion dismissed');
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
    
    showLoadingState() {
        this.statusIndicator.classList.remove('hidden');
    }
    
    hideLoadingState() {
        this.statusIndicator.classList.add('hidden');
    }
    
    updateAIStatus(message) {
        const statusDiv = this.aiStatus.querySelector('div');
        const dot = statusDiv.querySelector('div');
        
        // Update status color based on message
        if (message.includes('ready') || message.includes('Ready')) {
            dot.className = 'w-2 h-2 bg-green-400 rounded-full mr-2';
        } else if (message.includes('Generating') || message.includes('Getting')) {
            dot.className = 'w-2 h-2 bg-yellow-400 rounded-full mr-2 animate-pulse';
        } else if (message.includes('Failed') || message.includes('error')) {
            dot.className = 'w-2 h-2 bg-red-400 rounded-full mr-2';
        } else {
            dot.className = 'w-2 h-2 bg-blue-400 rounded-full mr-2';
        }
        
        // Update text
        statusDiv.childNodes[1].textContent = message;
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
}

// Initialize editor when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.editor = new ModernAIEditor();
});