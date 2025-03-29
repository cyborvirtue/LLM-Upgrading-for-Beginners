document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const currentMode = document.getElementById('current-mode');
    const newChatButton = document.getElementById('new-chat');
    const clearHistoryButton = document.getElementById('clear-history');
    const langchainModeButton = document.getElementById('langchain-mode');
    const nativeModeButton = document.getElementById('native-mode');
    const helpLink = document.getElementById('show-help');
    const helpModal = document.getElementById('help-modal');
    const closeModalButton = document.querySelector('.close-modal');
    
    let isProcessing = false;
    
    // Initialize auto-resizing textarea
    initTextareaResize();
    
    // Event listeners
    userInput.addEventListener('keydown', handleInputKeydown);
    sendButton.addEventListener('click', sendMessage);
    newChatButton.addEventListener('click', startNewChat);
    clearHistoryButton.addEventListener('click', clearHistory);
    langchainModeButton.addEventListener('click', () => switchMode('langchain'));
    nativeModeButton.addEventListener('click', () => switchMode('native'));
    helpLink.addEventListener('click', showHelpModal);
    closeModalButton.addEventListener('click', hideHelpModal);
    document.addEventListener('keydown', handleGlobalKeydown);
    
    // Focus input on page load
    userInput.focus();
    
    // Functions
    function handleInputKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    }
    
    function handleGlobalKeydown(e) {
        if (e.key === 'Escape' && helpModal.classList.contains('visible')) {
            hideHelpModal();
        }
    }
    
    function initTextareaResize() {
        function adjustHeight() {
            userInput.style.height = 'auto';
            userInput.style.height = (userInput.scrollHeight) + 'px';
        }
        
        userInput.addEventListener('input', adjustHeight);
        
        // Initial adjustment
        setTimeout(adjustHeight, 0);
    }
    
    function sendMessage() {
        const message = userInput.value.trim();
        
        if (message === '' || isProcessing) {
            return;
        }
        
        // Add user message to UI
        addMessage(message, 'user');
        
        // Clear input and reset height
        userInput.value = '';
        userInput.style.height = 'auto';
        
        // Send request
        isProcessing = true;
        sendButton.disabled = true;
        
        // Add typing indicator
        const typingId = addTypingIndicator();
        
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator(typingId);
            
            if (data.error) {
                addMessage(data.error, 'error');
            } else {
                addMessage(data.message, 'assistant');
                
                // Update mode display
                if (data.mode) {
                    currentMode.textContent = data.mode === 'native' ? '原生对话' : 'LangChain';
                    updateModeButtons(data.mode);
                }
            }
        })
        .catch(error => {
            // Remove typing indicator
            removeTypingIndicator(typingId);
            addMessage('发生错误: ' + error.message, 'error');
        })
        .finally(() => {
            isProcessing = false;
            sendButton.disabled = false;
            userInput.focus();
        });
    }
    
    function addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', type);
        
        if (type === 'system' || type === 'error') {
            // System or error message
            const avatarDiv = document.createElement('div');
            avatarDiv.classList.add('message-avatar', `${type}-avatar`);
            
            // Set avatar icon
            if (type === 'system') {
                avatarDiv.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path></svg>';
            } else {
                avatarDiv.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>';
            }
            
            messageDiv.appendChild(avatarDiv);
            
            const contentDiv = document.createElement('div');
            contentDiv.classList.add('message-content');
            
            const headerDiv = document.createElement('div');
            headerDiv.classList.add('message-header');
            headerDiv.innerHTML = `<span class="message-sender">${type === 'system' ? '系统' : '错误'}</span>`;
            
            const bodyDiv = document.createElement('div');
            bodyDiv.classList.add('message-body');
            bodyDiv.innerHTML = formatMessage(content);
            
            contentDiv.appendChild(headerDiv);
            contentDiv.appendChild(bodyDiv);
            messageDiv.appendChild(contentDiv);
        } else {
            // User or assistant message
            const avatarDiv = document.createElement('div');
            avatarDiv.classList.add('message-avatar', `${type}-avatar`);
            
            if (type === 'user') {
                avatarDiv.innerHTML = '你';
            } else {
                avatarDiv.innerHTML = 'AI';
            }
            
            messageDiv.appendChild(avatarDiv);
            
            const contentDiv = document.createElement('div');
            contentDiv.classList.add('message-content');
            
            const headerDiv = document.createElement('div');
            headerDiv.classList.add('message-header');
            headerDiv.innerHTML = `<span class="message-sender">${type === 'user' ? '你' : 'AI助手'}</span>`;
            
            const bodyDiv = document.createElement('div');
            bodyDiv.classList.add('message-body');
            
            if (type === 'assistant') {
                // Format assistant messages (support markdown-lite)
                bodyDiv.innerHTML = formatMessage(content);
            } else {
                // User messages - simple text
                bodyDiv.textContent = content;
            }
            
            contentDiv.appendChild(headerDiv);
            contentDiv.appendChild(bodyDiv);
            messageDiv.appendChild(contentDiv);
        }
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        scrollToBottom();
        
        return messageDiv.id;
    }
    
    function addTypingIndicator() {
        const id = 'typing-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'assistant');
        messageDiv.id = id;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('message-avatar', 'assistant-avatar');
        avatarDiv.innerHTML = 'AI';
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        
        const headerDiv = document.createElement('div');
        headerDiv.classList.add('message-header');
        headerDiv.innerHTML = '<span class="message-sender">AI助手</span>';
        
        const bodyDiv = document.createElement('div');
        bodyDiv.classList.add('message-body');
        bodyDiv.innerHTML = '<div class="typing-dots"><span>.</span><span>.</span><span>.</span></div>';
        
        contentDiv.appendChild(headerDiv);
        contentDiv.appendChild(bodyDiv);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
        
        return id;
    }
    
    function removeTypingIndicator(id) {
        const indicator = document.getElementById(id);
        if (indicator) {
            indicator.remove();
        }
    }
    
    function formatMessage(text) {
        // Simple markdown-like formatting
        // Replace code blocks
        text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Replace newlines with breaks
        text = text.replace(/\n/g, '<br>');
        
        // Format lists
        const lines = text.split('<br>');
        let inList = false;
        let formattedLines = [];
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            // Check for list items
            if (line.match(/^[-*•]\s/)) {
                if (!inList) {
                    formattedLines.push('<ul>');
                    inList = true;
                }
                formattedLines.push('<li>' + line.replace(/^[-*•]\s/, '') + '</li>');
            } else if (inList) {
                formattedLines.push('</ul>');
                inList = false;
                formattedLines.push(line);
            } else {
                formattedLines.push(line);
            }
        }
        
        if (inList) {
            formattedLines.push('</ul>');
        }
        
        // Format paragraphs
        let html = '';
        let currentParagraph = '';
        
        for (let i = 0; i < formattedLines.length; i++) {
            const line = formattedLines[i];
            
            if (line === '' && currentParagraph) {
                html += '<p>' + currentParagraph + '</p>';
                currentParagraph = '';
            } else if (line.startsWith('<ul>') || line.startsWith('</ul>')) {
                if (currentParagraph) {
                    html += '<p>' + currentParagraph + '</p>';
                    currentParagraph = '';
                }
                html += line;
            } else if (line.startsWith('<li>')) {
                html += line;
            } else {
                if (currentParagraph) {
                    currentParagraph += '<br>' + line;
                } else {
                    currentParagraph = line;
                }
            }
        }
        
        if (currentParagraph) {
            html += '<p>' + currentParagraph + '</p>';
        }
        
        return html;
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function startNewChat() {
        if (confirm('确定要开始新对话吗？这将清除当前的对话历史。')) {
            clearHistory();
        }
    }
    
    function clearHistory() {
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: '/clear' })
        })
        .then(response => response.json())
        .then(data => {
            // Clear chat UI
            while (chatMessages.firstChild) {
                chatMessages.firstChild.remove();
            }
            
            // Add system message
            addMessage('对话历史已清除。', 'system');
        })
        .catch(error => {
            addMessage('清除历史失败: ' + error.message, 'error');
        });
    }
    
    function switchMode(mode) {
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: '/mode' })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                addMessage(data.error, 'error');
            } else {
                addMessage(data.message, 'system');
                
                // Update mode display
                if (data.mode) {
                    currentMode.textContent = data.mode === 'native' ? '原生对话' : 'LangChain';
                    updateModeButtons(data.mode);
                }
            }
        })
        .catch(error => {
            addMessage('切换模式失败: ' + error.message, 'error');
        });
    }
    
    function updateModeButtons(mode) {
        if (mode === 'native') {
            langchainModeButton.classList.remove('active');
            nativeModeButton.classList.add('active');
        } else {
            langchainModeButton.classList.add('active');
            nativeModeButton.classList.remove('active');
        }
    }
    
    function showHelpModal(e) {
        if (e) e.preventDefault();
        helpModal.classList.add('visible');
    }
    
    function hideHelpModal() {
        helpModal.classList.remove('visible');
    }
});