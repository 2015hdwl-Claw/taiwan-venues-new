/**
 * 活動大師 AI 助理 - Chat Widget
 *
 * 提供浮動對話視窗，連接 api/assistant.js
 */

(function() {
    'use strict';

    // State
    let isOpen = false;
    let currentVenueId = null;
    let currentVenueName = null;
    let messages = [];

    // API endpoint (relative for same-origin)
    const API_ENDPOINT = '/api/assistant';

    // Quick action suggestions
    const QUICK_ACTIONS = [
        '這個場地可以帶外食嗎？',
        '進場佈置有什麼限制？',
        '取消訂位的規定是什麼？',
        '場地有哪些潛在風險？'
    ];

    /**
     * Initialize chat widget
     */
    function init() {
        createChatWidget();
        loadHistory();
    }

    /**
     * Create chat widget DOM
     */
    function createChatWidget() {
        // Create toggle button
        const toggle = document.createElement('button');
        toggle.className = 'chat-toggle';
        toggle.id = 'chatToggle';
        toggle.innerHTML = `
            <svg viewBox="0 0 24 24">
                <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                <path d="M7 9h10v2H7zm0-3h10v2H7z"/>
            </svg>
        `;
        toggle.onclick = toggleChat;
        document.body.appendChild(toggle);

        // Create chat window
        const chatWindow = document.createElement('div');
        chatWindow.className = 'chat-window';
        chatWindow.id = 'chatWindow';
        chatWindow.innerHTML = `
            <div class="chat-header">
                <div class="chat-header-title">
                    <h3>🤖 場地顧問</h3>
                    <span>AI 助理</span>
                </div>
                <button class="chat-close" onclick="window.toggleChat()">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M18 6L6 18M6 6l12 12"/>
                    </svg>
                </button>
            </div>
            <div class="venue-context" id="venueContext" style="display: none;">
                <span>針對 <span class="venue-name" id="contextVenueName"></span> 提問</span>
                <span class="clear-context" onclick="window.clearVenueContext()">清除 ✕</span>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="message assistant">
                    👋 你好！我是活動大師的 AI 場地顧問。我可以幫你查詢場地的規定、限制和注意事項。請問有什麼想了解的？
                </div>
            </div>
            <div class="quick-actions" id="quickActions">
                ${QUICK_ACTIONS.map(action =>
                    `<button class="quick-action" onclick="window.sendQuickMessage('${action}')">${action}</button>`
                ).join('')}
            </div>
            <div class="chat-input-container">
                <input
                    type="text"
                    class="chat-input"
                    id="chatInput"
                    placeholder="輸入問題..."
                    onkeypress="if(event.key==='Enter')window.sendMessage()"
                >
                <button class="chat-send" id="chatSend" onclick="window.sendMessage()">
                    <svg viewBox="0 0 24 24">
                        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                    </svg>
                </button>
            </div>
        `;
        document.body.appendChild(chatWindow);

        // Expose global functions
        window.toggleChat = toggleChat;
        window.sendMessage = sendMessage;
        window.sendQuickMessage = sendQuickMessage;
        window.clearVenueContext = clearVenueContext;
        window.setVenueContext = setVenueContext;
    }

    /**
     * Toggle chat window visibility
     */
    function toggleChat() {
        isOpen = !isOpen;
        const chatWindow = document.getElementById('chatWindow');
        if (isOpen) {
            chatWindow.classList.add('open');
            document.getElementById('chatInput').focus();
        } else {
            chatWindow.classList.remove('open');
        }
    }

    /**
     * Set venue context (called from venue.html)
     */
    function setVenueContext(venueId, venueName) {
        currentVenueId = venueId;
        currentVenueName = venueName;
        const contextEl = document.getElementById('venueContext');
        const nameEl = document.getElementById('contextVenueName');
        if (contextEl && nameEl) {
            contextEl.style.display = 'flex';
            nameEl.textContent = venueName;
        }
    }

    /**
     * Clear venue context
     */
    function clearVenueContext() {
        currentVenueId = null;
        currentVenueName = null;
        const contextEl = document.getElementById('venueContext');
        if (contextEl) {
            contextEl.style.display = 'none';
        }
    }

    /**
     * Send a quick action message
     */
    function sendQuickMessage(text) {
        const input = document.getElementById('chatInput');
        input.value = text;
        sendMessage();
    }

    /**
     * Send message to API
     */
    async function sendMessage() {
        const input = document.getElementById('chatInput');
        const query = input.value.trim();

        if (!query) return;

        // Clear input
        input.value = '';

        // Add user message to UI
        addMessage('user', query);

        // Show typing indicator
        showTyping();

        try {
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query,
                    venueId: currentVenueId
                })
            });

            const data = await response.json();

            // Hide typing
            hideTyping();

            if (data.success) {
                // Format assistant response
                const formattedResponse = formatResponse(data);
                addMessage('assistant', formattedResponse, data);
            } else {
                addMessage('assistant', `❌ 發生錯誤：${data.error || '未知錯誤'}`, null, true);
            }

        } catch (error) {
            hideTyping();
            addMessage('assistant', `❌ 網路錯誤，請稍後再試`, null, true);
            console.error('Chat error:', error);
        }
    }

    /**
     * Format API response for display
     */
    function formatResponse(data) {
        let html = `<div class="answer">${escapeHtml(data.answer)}</div>`;

        if (data.hasKnowledge && data.sources?.length > 0) {
            html += `
                <div class="sources">
                    <div class="sources-title">📚 資料來源</div>
                    ${data.sources.map(s => `
                        <div class="source-item">
                            <span>${s.venueName}</span>
                            <span class="confidence ${s.confidence === 'unverified' ? 'unverified' : ''}">${s.confidence === 'confirmed' ? '已確認' : '待確認'}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        } else if (!data.hasKnowledge) {
            html += `
                <div class="suggestion">
                    💡 您可以透過本平台生成詢問信，我們會協助您向場地方查詢此資訊。
                </div>
            `;
        }

        return html;
    }

    /**
     * Add message to chat
     */
    function addMessage(role, content, data = null, isError = false) {
        const messagesEl = document.getElementById('chatMessages');
        const messageEl = document.createElement('div');
        messageEl.className = `message ${role}${isError ? ' error' : ''}`;

        if (role === 'assistant' && data) {
            messageEl.innerHTML = content;
        } else {
            messageEl.textContent = content;
        }

        messagesEl.appendChild(messageEl);
        messagesEl.scrollTop = messagesEl.scrollHeight;

        // Save to history
        messages.push({ role, content, timestamp: Date.now() });
        saveHistory();
    }

    /**
     * Show typing indicator
     */
    function showTyping() {
        const messagesEl = document.getElementById('chatMessages');
        const typing = document.createElement('div');
        typing.className = 'typing-indicator';
        typing.id = 'typingIndicator';
        typing.innerHTML = '<span></span><span></span><span></span>';
        messagesEl.appendChild(typing);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    /**
     * Hide typing indicator
     */
    function hideTyping() {
        const typing = document.getElementById('typingIndicator');
        if (typing) typing.remove();
    }

    /**
     * Escape HTML for safe display
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/\n/g, '<br>');
    }

    /**
     * Save chat history to localStorage
     */
    function saveHistory() {
        try {
            localStorage.setItem('chatHistory', JSON.stringify(messages.slice(-50)));
        } catch (e) {
            // Ignore storage errors
        }
    }

    /**
     * Load chat history from localStorage
     */
    function loadHistory() {
        try {
            const saved = localStorage.getItem('chatHistory');
            if (saved) {
                messages = JSON.parse(saved);
                // Don't restore old messages to UI, keep it fresh
            }
        } catch (e) {
            // Ignore storage errors
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
