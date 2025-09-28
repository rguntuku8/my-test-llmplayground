class LLMPlayground {
    constructor() {
        this.currentModel = 'gpt-4o';
        this.settings = {
            model: 'gpt-4o',
            temperature: 0.7,
            maxTokens: 2048,
            presencePenalty: 0,
            frequencyPenalty: 0,
            topP: 1.0,
            seed: null,
            stopSequence: '',
            systemPrompt: ''
        };
        this.conversationHistory = [];
        this.isSettingsOpen = false;
        this.isFirstMessage = true;
        this.sliderUpdateTimeouts = {};
        
        this.initializeElements();
        this.bindEvents();
        this.updateSliderValues();
        this.initializeSliders();
        
        // Initialize input area
        this.autoResizeTextarea();
        this.ensureInputVisibility();
        
        // Setup window resize listener for responsive layout
        this.setupResizeListener();
    }
    
    initializeElements() {
        // Main elements
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.chatMessages = document.getElementById('chatMessages');
        this.modelSelect = document.getElementById('modelSelect');
        this.settingsPanel = document.getElementById('settingsPanel');
        
        // Settings panel elements
        this.settingsPanel = document.getElementById('settingsPanel');
        this.settingsToggle = document.getElementById('settingsToggle');
        this.resetSettings = document.getElementById('resetSettings');
        this.clearPrompt = document.getElementById('clearPrompt');
        
        // Model settings elements
        this.modelSelect = document.getElementById('modelSelect');
        this.temperatureSlider = document.getElementById('temperature');
        this.temperatureValue = document.getElementById('temperatureDisplay');
        this.maxTokensSlider = document.getElementById('maxTokens');
        this.maxTokensValue = document.getElementById('maxTokensDisplay');
        this.presencePenaltySlider = document.getElementById('presencePenalty');
        this.presencePenaltyValue = document.getElementById('presencePenaltyDisplay');
        this.frequencyPenaltySlider = document.getElementById('frequencyPenalty');
        this.frequencyPenaltyValue = document.getElementById('frequencyPenaltyDisplay');
        this.topPSlider = document.getElementById('topP');
        this.topPValue = document.getElementById('topPDisplay');
        this.seedInput = document.getElementById('seed');
        this.randomizeSeedBtn = document.getElementById('randomizeSeed');
        this.stopSequenceInput = document.getElementById('stopSequence');
        this.clearStopBtn = document.getElementById('clearStop');
        this.systemPrompt = document.getElementById('systemPrompt');
        
        // Other elements
        this.exportBtn = document.querySelector('.export-btn');
    }
    
    bindEvents() {
        // Send message events
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Settings panel events
        this.settingsToggle.addEventListener('click', () => this.toggleSettings());
        this.resetSettings.addEventListener('click', () => this.resetToDefaults());
        this.clearPrompt.addEventListener('click', () => this.clearSystemPrompt());

        // Model selection
        this.modelSelect.addEventListener('change', (e) => {
            this.currentModel = e.target.value;
            this.settings.model = e.target.value;
            this.updateModelDisplay();
        });

        // Temperature slider
        this.temperatureSlider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            this.settings.temperature = value;
            
            // Immediate visual feedback
            this.temperatureValue.textContent = this.formatSliderValue(value, 1);
            
            // Debounced background update to prevent erratic behavior
            if (this.sliderUpdateTimeouts.temperature) {
                clearTimeout(this.sliderUpdateTimeouts.temperature);
            }
            this.sliderUpdateTimeouts.temperature = setTimeout(() => {
                this.updateSliderBackground(this.temperatureSlider, 0, 2);
            }, 10);
        });

        // Max tokens slider
        this.maxTokensSlider.addEventListener('input', (e) => {
            this.settings.maxTokens = parseInt(e.target.value);
            this.maxTokensValue.textContent = this.formatSliderValue(this.settings.maxTokens, 0);
            this.updateSliderBackground(this.maxTokensSlider, 256, 4096);
        });

        // Presence penalty slider
        this.presencePenaltySlider.addEventListener('input', (e) => {
            this.settings.presencePenalty = parseFloat(e.target.value);
            this.presencePenaltyValue.textContent = this.formatSliderValue(this.settings.presencePenalty, 1);
            this.updateSliderBackground(this.presencePenaltySlider, -2, 2);
        });

        // Frequency penalty slider
        this.frequencyPenaltySlider.addEventListener('input', (e) => {
            this.settings.frequencyPenalty = parseFloat(e.target.value);
            this.frequencyPenaltyValue.textContent = this.formatSliderValue(this.settings.frequencyPenalty, 1);
            this.updateSliderBackground(this.frequencyPenaltySlider, -2, 2);
        });

        // Top P slider
        this.topPSlider.addEventListener('input', (e) => {
            this.settings.topP = parseFloat(e.target.value);
            this.topPValue.textContent = this.formatSliderValue(this.settings.topP, 2);
            this.updateSliderBackground(this.topPSlider, 0, 1);
        });

        // Seed input
        this.seedInput.addEventListener('input', (e) => {
            const value = e.target.value;
            this.settings.seed = value === '' ? null : parseInt(value);
        });

        // Randomize seed button
        this.randomizeSeedBtn.addEventListener('click', () => {
            const randomSeed = Math.floor(Math.random() * 2147483647);
            this.seedInput.value = randomSeed;
            this.settings.seed = randomSeed;
        });

        // Stop sequence input
        this.stopSequenceInput.addEventListener('input', (e) => {
            this.settings.stopSequence = e.target.value;
        });

        // Clear stop sequences button
        this.clearStopBtn.addEventListener('click', () => {
            this.stopSequenceInput.value = '';
            this.settings.stopSequence = '';
        });

        // System prompt
        this.systemPrompt.addEventListener('input', (e) => {
            this.settings.systemPrompt = e.target.value;
        });

        // Export conversation
        if (this.exportBtn) {
            this.exportBtn.addEventListener('click', () => this.exportConversation());
        }

        // Close settings when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.settingsPanel.contains(e.target) && this.settingsPanel.classList.contains('open')) {
                this.toggleSettings();
            }
        });

        // Enhanced direction tracking for all sliders
        this.setupSliderDirectionTracking();
    }

    setupSliderDirectionTracking() {
        const sliders = [
            { element: this.temperatureSlider, min: 0, max: 2 },
            { element: this.maxTokensSlider, min: 256, max: 4096 },
            { element: this.presencePenaltySlider, min: -2, max: 2 },
            { element: this.frequencyPenaltySlider, min: -2, max: 2 }
        ];

        sliders.forEach(({ element, min, max }) => {
            if (!element) return;

            // Track mouse/touch start position for better direction detection
            let startX = 0;
            let isDragging = false;
            let hasMovedDuringDrag = false;

            // Enhanced click-to-position functionality
            element.addEventListener('click', (e) => {
                if (!hasMovedDuringDrag) {
                    // Immediate position update on click
                    this.updateSliderPosition(element, e, min, max);
                }
            });

            element.addEventListener('mousedown', (e) => {
                startX = e.clientX;
                isDragging = true;
                hasMovedDuringDrag = false;
                element.classList.add('dragging');
                
                // Immediate position update on mousedown
                this.updateSliderPosition(element, e, min, max);
            });

            element.addEventListener('touchstart', (e) => {
                startX = e.touches[0].clientX;
                isDragging = true;
                hasMovedDuringDrag = false;
                element.classList.add('dragging');
                
                // Immediate position update on touchstart
                this.updateSliderPosition(element, e, min, max);
            });

            element.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                hasMovedDuringDrag = true;
                this.handleSliderDirectionalMove(element, e.clientX, startX, min, max);
            });

            element.addEventListener('touchmove', (e) => {
                if (!isDragging) return;
                hasMovedDuringDrag = true;
                this.handleSliderDirectionalMove(element, e.touches[0].clientX, startX, min, max);
            });

            const endDrag = () => {
                isDragging = false;
                element.classList.remove('dragging');
                // Reset movement tracking after a short delay
                setTimeout(() => {
                    hasMovedDuringDrag = false;
                }, 10);
            };

            element.addEventListener('mouseup', endDrag);
            element.addEventListener('touchend', endDrag);
            document.addEventListener('mouseup', endDrag);
        });
    }

    handleSliderDirectionalMove(slider, currentX, startX, min, max) {
        const deltaX = currentX - startX;
        const isMovingRight = deltaX > 0;
        const isMovingLeft = deltaX < 0;

        // Store direction for enhanced visual feedback
        slider.dataset.direction = isMovingRight ? 'right' : isMovingLeft ? 'left' : 'static';
        
        // Update background with enhanced direction awareness
        this.updateSliderBackground(slider, min, max);
    }

    updateSliderPosition(slider, event, min, max) {
        // Calculate the new value based on click/touch position
        const rect = slider.getBoundingClientRect();
        const clientX = event.touches ? event.touches[0].clientX : event.clientX;
        const percentage = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
        
        // Calculate the new value within the slider's range
        const range = max - min;
        const newValue = min + (percentage * range);
        
        // Apply step rounding if the slider has a step attribute
        const step = parseFloat(slider.step) || 0.1;
        const steppedValue = Math.round(newValue / step) * step;
        const clampedValue = Math.max(min, Math.min(max, steppedValue));
        
        // Update the slider value immediately
        slider.value = clampedValue;
        
        // Trigger the input event to update the display and background
        const inputEvent = new Event('input', { bubbles: true });
        slider.dispatchEvent(inputEvent);
        
        // Force immediate visual update
        this.updateSliderBackground(slider, min, max);
    }

    formatSliderValue(value, decimalPlaces = 1) {
        // Format the value with consistent decimal places
        if (decimalPlaces === 0) {
            return Math.round(value).toString();
        }
        return parseFloat(value).toFixed(decimalPlaces);
    }
    
    updateSliderValues() {
        if (this.temperatureValue && this.temperatureSlider) {
            this.temperatureValue.textContent = this.formatSliderValue(this.temperatureSlider.value, 1);
        }
        if (this.maxTokensValue && this.maxTokensSlider) {
            this.maxTokensValue.textContent = this.maxTokensSlider.value;
        }
        if (this.presencePenaltyValue && this.presencePenaltySlider) {
            this.presencePenaltyValue.textContent = this.presencePenaltySlider.value;
        }
        if (this.frequencyPenaltyValue && this.frequencyPenaltySlider) {
            this.frequencyPenaltyValue.textContent = this.frequencyPenaltySlider.value;
        }
        if (this.topPValue && this.topPSlider) {
            this.topPValue.textContent = this.formatSliderValue(this.topPSlider.value, 2);
        }
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    ensureInputVisibility() {
        // Ensure the input container is visible
        const inputContainer = document.querySelector('.input-container');
        if (inputContainer) {
            inputContainer.style.display = 'block';
            inputContainer.style.visibility = 'visible';
            inputContainer.style.opacity = '1';
        }
        
        // Ensure the message input is visible and focusable
        if (this.messageInput) {
            this.messageInput.style.display = 'block';
            this.messageInput.style.visibility = 'visible';
            this.messageInput.style.opacity = '1';
            
            // Focus the input after a short delay to ensure it's ready
            setTimeout(() => {
                this.messageInput.focus();
            }, 100);
        }
        
        // Ensure the chat container has the correct class
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer && !this.isFirstMessage) {
            chatContainer.classList.remove('initial-state');
            chatContainer.classList.add('conversation-started');
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Handle first message transition
        if (this.isFirstMessage) {
            this.transitionToConversationMode();
            this.isFirstMessage = false;
        }
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.autoResizeTextarea();
        
        // Ensure input remains visible and focused
        this.ensureInputVisibility();
        
        // Show typing indicator
        const typingId = this.showTypingIndicator();
        
        try {
            // Simulate API call (replace with actual API integration)
            const response = await this.callLLMAPI(message);
            this.removeTypingIndicator(typingId);
            this.addMessage(response, 'assistant');
            
            // Ensure input remains visible and focused after response
            this.ensureInputVisibility();
        } catch (error) {
            this.removeTypingIndicator(typingId);
            this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant', true);
            console.error('API Error:', error);
            
            // Ensure input remains visible and focused after error
            this.ensureInputVisibility();
        }
    }
    
    transitionToConversationMode() {
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            // Remove initial state and add conversation started state
            chatContainer.classList.remove('initial-state');
            chatContainer.classList.add('conversation-started');
        }
        
        // Ensure input visibility after transition
        setTimeout(() => {
            this.ensureInputVisibility();
        }, 100);
    }
    
    async callLLMAPI(message) {
        try {
            // Prepare request payload
            const requestData = {
                message: message,
                model: this.currentModel,
                settings: this.settings,
                conversation_history: this.conversationHistory
            };

            // Make API request to backend
            const response = await fetch('http://localhost:5001/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (data.success) {
                return data.response;
            } else {
                // Handle different types of errors
                let errorMessage = data.error || 'Unknown error occurred';
                
                if (data.error_type === 'validation_error') {
                    errorMessage = `Validation Error: ${data.error}`;
                } else if (data.error_type === 'provider_unavailable') {
                    errorMessage = `Provider Unavailable: ${data.error}`;
                } else if (data.error_type === 'server_error') {
                    errorMessage = `Server Error: ${data.error}`;
                }
                
                throw new Error(errorMessage);
            }
        } catch (error) {
            // Handle network errors and other exceptions
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                return `Connection Error: Unable to connect to the backend server. Please ensure the Python backend is running on http://localhost:5001`;
            } else if (error.message.includes('rate limit')) {
                return `Rate Limit: ${error.message}`;
            } else if (error.message.includes('API key') || error.message.includes('unauthorized')) {
                return `Authentication Error: ${error.message}`;
            } else {
                return `Error: ${error.message}`;
            }
        }
    }
    
    addMessage(content, sender, isError = false) {
        // Remove welcome message if it exists
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        if (isError) {
            messageContent.style.backgroundColor = '#dc2626';
        }
        messageContent.textContent = content;
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        
        // Ensure proper scrollable layout
        this.ensureScrollableLayout();
        
        // Smooth scroll to bottom
        setTimeout(() => {
            this.scrollToBottom(true);
        }, 100);
        
        // Add to conversation history
        this.conversationHistory.push({ sender, content, timestamp: new Date() });
    }
    
    showTypingIndicator() {
        const typingId = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant';
        typingDiv.id = typingId;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<i class="fas fa-robot"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = '<div class="typing-indicator">Thinking...</div>';
        
        typingDiv.appendChild(avatar);
        typingDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
        
        return typingId;
    }
    
    removeTypingIndicator(typingId) {
        const typingElement = document.getElementById(typingId);
        if (typingElement) {
            typingElement.remove();
        }
    }
    
    scrollToBottom(smooth = true) {
        if (smooth) {
            this.chatMessages.scrollTo({
                top: this.chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        } else {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
    }
    
    ensureScrollableLayout() {
        // Ensure the chat messages area is properly configured for scrolling
        const chatContainer = document.querySelector('.chat-container');
        const chatMessages = this.chatMessages;
        const inputContainer = document.querySelector('.input-container');
        
        if (chatContainer && chatMessages && inputContainer) {
            // Calculate available height for messages
            const containerHeight = chatContainer.clientHeight;
            const inputHeight = inputContainer.offsetHeight;
            const availableHeight = containerHeight - inputHeight;
            
            // Ensure messages area doesn't exceed available space
            chatMessages.style.maxHeight = `${availableHeight}px`;
            
            // Ensure smooth scrolling is enabled
            chatMessages.style.scrollBehavior = 'smooth';
            
            // Auto-scroll to bottom if user is near the bottom
            const isNearBottom = chatMessages.scrollTop + chatMessages.clientHeight >= chatMessages.scrollHeight - 100;
            if (isNearBottom) {
                this.scrollToBottom(true);
            }
        }
    }
    
    setupResizeListener() {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            // Debounce resize events for better performance
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.ensureScrollableLayout();
                this.ensureInputVisibility();
            }, 150);
        });
    }
    
    toggleSettings() {
        this.isSettingsOpen = !this.isSettingsOpen;
        this.settingsPanel.classList.toggle('open', this.isSettingsOpen);
    }

    resetToDefaults() {
        // Reset to default values
        this.settings = {
            model: 'gpt-4',
            temperature: 0.7,
            maxTokens: 2048,
            presencePenalty: 0,
            frequencyPenalty: 0,
            topP: 1.0,
            seed: null,
            stopSequence: '',
            systemPrompt: ''
        };

        // Update UI elements
        this.modelSelect.value = this.settings.model;
        this.temperatureSlider.value = this.settings.temperature;
        this.temperatureValue.textContent = this.formatSliderValue(this.settings.temperature, 1);
        this.maxTokensSlider.value = this.settings.maxTokens;
        this.maxTokensValue.textContent = this.formatSliderValue(this.settings.maxTokens, 0);
        this.presencePenaltySlider.value = this.settings.presencePenalty;
        this.presencePenaltyValue.textContent = this.formatSliderValue(this.settings.presencePenalty, 1);
        this.frequencyPenaltySlider.value = this.settings.frequencyPenalty;
        this.frequencyPenaltyValue.textContent = this.formatSliderValue(this.settings.frequencyPenalty, 1);
        this.topPSlider.value = this.settings.topP;
        this.topPValue.textContent = this.formatSliderValue(this.settings.topP, 2);
        this.seedInput.value = '';
        this.stopSequenceInput.value = this.settings.stopSequence;
        this.systemPrompt.value = this.settings.systemPrompt;

        // Update slider backgrounds
        this.updateSliderBackground(this.temperatureSlider, 0, 2);
        this.updateSliderBackground(this.maxTokensSlider, 256, 4096);
        this.updateSliderBackground(this.presencePenaltySlider, -2, 2);
        this.updateSliderBackground(this.frequencyPenaltySlider, -2, 2);
        this.updateSliderBackground(this.topPSlider, 0, 1);

        this.updateModelDisplay();
    }

    clearSystemPrompt() {
        this.settings.systemPrompt = '';
        this.systemPrompt.value = '';
    }

    updateSliderBackground(slider, min, max) {
        const value = parseFloat(slider.value);
        const percentage = ((value - min) / (max - min)) * 100;
        
        // Enhanced direction detection using both value change and mouse tracking
        if (!slider.previousValue) {
            slider.previousValue = value;
        }
        
        const valueDirection = value > slider.previousValue ? 'right' : value < slider.previousValue ? 'left' : 'static';
        const mouseDirection = slider.dataset.direction || 'static';
        const direction = mouseDirection !== 'static' ? mouseDirection : valueDirection;
        
        slider.previousValue = value;
        
        // Dynamic color based on value position and direction
        let activeColor = '#4f46e5'; // Default blue
        let glowColor = 'rgba(79, 70, 229, 0.3)';
        const trackColor = '#3f3f3f'; // Default gray
        
        // Different color schemes based on slider type
        if (slider.id === 'temperature') {
            // Temperature: Cool to warm gradient
            const tempRatio = percentage / 100;
            activeColor = `hsl(${240 - (tempRatio * 60)}, 70%, ${55 + (tempRatio * 10)}%)`;
            glowColor = `hsla(${240 - (tempRatio * 60)}, 70%, 55%, 0.3)`;
        } else if (slider.id === 'maxTokens') {
            // Max Tokens: Green gradient for capacity
            const tokenRatio = percentage / 100;
            activeColor = `hsl(${200 + (tokenRatio * 40)}, 65%, ${50 + (tokenRatio * 15)}%)`;
            glowColor = `hsla(${200 + (tokenRatio * 40)}, 65%, 50%, 0.3)`;
        } else if (slider.id === 'presencePenalty' || slider.id === 'frequencyPenalty') {
            // Penalty sliders: Purple to orange gradient
            const penaltyRatio = percentage / 100;
            activeColor = `hsl(${260 - (penaltyRatio * 80)}, 70%, ${55 + (penaltyRatio * 10)}%)`;
            glowColor = `hsla(${260 - (penaltyRatio * 80)}, 70%, 55%, 0.3)`;
        }
        
        // Enhanced directional fill logic with smooth transitions
        if (direction === 'right') {
            // Moving right: Progressive fill with vibrant color
            const intensity = Math.min(1, percentage / 100);
            const enhancedColor = this.enhanceColorIntensity(activeColor, intensity);
            slider.style.background = `linear-gradient(to right, ${enhancedColor} 0%, ${enhancedColor} ${percentage}%, ${trackColor} ${percentage}%, ${trackColor} 100%)`;
            slider.style.setProperty('--fill-direction', '1');
        } else if (direction === 'left') {
            // Moving left: Progressive fade to gray with subtle color retention
            const fadeIntensity = Math.max(0.3, percentage / 100);
            const fadedColor = this.fadeColorToGray(activeColor, fadeIntensity);
            slider.style.background = `linear-gradient(to right, ${fadedColor} 0%, ${fadedColor} ${percentage}%, ${trackColor} ${percentage}%, ${trackColor} 100%)`;
            slider.style.setProperty('--fill-direction', '-1');
        } else {
            // Static position: Standard fill
            slider.style.background = `linear-gradient(to right, ${activeColor} 0%, ${activeColor} ${percentage}%, ${trackColor} ${percentage}%, ${trackColor} 100%)`;
            slider.style.setProperty('--fill-direction', '0');
        }
        
        // Update thumb color dynamically
        slider.style.setProperty('--thumb-color', activeColor);
        slider.style.setProperty('--thumb-glow', glowColor);
    }

    enhanceColorIntensity(color, intensity) {
        // Enhance color saturation and brightness when moving right
        if (color.startsWith('hsl')) {
            const match = color.match(/hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)/);
            if (match) {
                const [, h, s, l] = match;
                const enhancedS = Math.min(100, parseInt(s) + (intensity * 20));
                const enhancedL = Math.min(70, parseInt(l) + (intensity * 10));
                return `hsl(${h}, ${enhancedS}%, ${enhancedL}%)`;
            }
        }
        return color;
    }

    fadeColorToGray(color, fadeIntensity) {
        // Gradually fade color towards gray when moving left
        if (color.startsWith('hsl')) {
            const match = color.match(/hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)/);
            if (match) {
                const [, h, s, l] = match;
                const fadedS = Math.max(20, parseInt(s) * fadeIntensity);
                const fadedL = Math.max(40, parseInt(l) * fadeIntensity);
                return `hsl(${h}, ${fadedS}%, ${fadedL}%)`;
            }
        }
        return color;
    }

    initializeSliders() {
        // Set initial slider backgrounds and display values
        if (this.temperatureSlider) {
            this.updateSliderBackground(this.temperatureSlider, 0, 2);
            if (this.temperatureValue) {
                this.temperatureValue.textContent = this.formatSliderValue(this.temperatureSlider.value, 1);
            }
        }
        if (this.maxTokensSlider) {
            this.updateSliderBackground(this.maxTokensSlider, 256, 4096);
            if (this.maxTokensDisplay) {
                this.maxTokensDisplay.textContent = this.formatSliderValue(this.maxTokensSlider.value, 0);
            }
        }
        if (this.presencePenaltySlider) {
            this.updateSliderBackground(this.presencePenaltySlider, -2, 2);
            if (this.presencePenaltyDisplay) {
                this.presencePenaltyDisplay.textContent = this.formatSliderValue(this.presencePenaltySlider.value, 1);
            }
        }
        if (this.frequencyPenaltySlider) {
            this.updateSliderBackground(this.frequencyPenaltySlider, -2, 2);
            if (this.frequencyPenaltyDisplay) {
                this.frequencyPenaltyDisplay.textContent = this.formatSliderValue(this.frequencyPenaltySlider.value, 1);
            }
        }
        if (this.topPSlider) {
            this.updateSliderBackground(this.topPSlider, 0, 1);
            if (this.topPValue) {
                this.topPValue.textContent = this.formatSliderValue(this.topPSlider.value, 2);
            }
        }
    }
    
    updateModelDisplay() {
        // Update any model-specific UI elements
        console.log(`Switched to model: ${this.currentModel}`);
    }
    
    exportConversation() {
        const conversation = {
            model: this.currentModel,
            settings: this.settings,
            messages: this.conversationHistory,
            exportedAt: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(conversation, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `llm-conversation-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Initialize the playground when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.playground = new LLMPlayground();
    
    // Focus on input initially
    document.getElementById('messageInput').focus();
    
    // Add some demo functionality
    console.log('LLM Playground initialized!');
    console.log('Available methods:', {
        sendMessage: 'playground.sendMessage()',
        exportConversation: 'playground.exportConversation()',
        toggleSettings: 'playground.toggleSettings()'
    });
});

// Add some CSS animations for typing indicator
const style = document.createElement('style');
style.textContent = `
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .typing-indicator::after {
        content: '';
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: currentColor;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    @keyframes typing {
        0%, 80%, 100% {
            opacity: 0;
        }
        40% {
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);