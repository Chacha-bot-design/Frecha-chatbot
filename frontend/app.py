import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Django backend URL (will be set in Railway)
DJANGO_BACKEND_URL = os.environ.get('DJANGO_BACKEND_URL', 'http://localhost:8000')

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Frecha iotech</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea, #764ba2);
                min-height: 100vh; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                padding: 20px; 
            }
            .container { 
                width: 100%; 
                max-width: 800px; 
                background: white; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
                overflow: hidden; 
            }
            .header { 
                background: linear-gradient(135deg, #2c3e50, #3498db); 
                color: white; 
                text-align: center; 
                padding: 30px 20px; 
            }
            .company-name { 
                font-size: 2.5em; 
                font-weight: bold; 
                margin-bottom: 10px; 
            }
            .providers {
                display: flex;
                justify-content: center;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 15px;
            }
            .provider-tag {
                background: rgba(255,255,255,0.2);
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 0.9em;
            }
            .chat-area { 
                padding: 20px; 
            }
            .quick-actions {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 8px;
                margin-bottom: 15px;
            }
            .quick-btn {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.8em;
                text-align: center;
            }
            .quick-btn:hover {
                background: #5a6fd8;
            }
            .chat-box { 
                height: 300px; 
                border: 1px solid #ddd; 
                border-radius: 10px; 
                padding: 15px; 
                overflow-y: auto; 
                background: #f9f9f9; 
                margin-bottom: 15px; 
            }
            .message { 
                margin: 10px 0; 
                padding: 10px; 
                border-radius: 10px; 
                max-width: 80%; 
            }
            .user-message { 
                background: #667eea; 
                color: white; 
                margin-left: auto; 
                text-align: right; 
            }
            .bot-message { 
                background: white; 
                border: 1px solid #ddd; 
                white-space: pre-line; 
            }
            .input-area { 
                display: flex; 
                gap: 10px; 
            }
            input { 
                flex: 1; 
                padding: 12px; 
                border: 1px solid #ddd; 
                border-radius: 8px; 
                font-size: 1em; 
            }
            button { 
                background: #667eea; 
                color: white; 
                border: none; 
                padding: 12px 20px; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 1em; 
            }
            .language-indicator {
                position: absolute;
                top: 15px;
                right: 15px;
                background: rgba(255,255,255,0.2);
                padding: 5px 10px;
                border-radius: 10px;
                font-size: 0.8em;
            }
            @media (max-width: 600px) {
                .quick-actions {
                    grid-template-columns: repeat(2, 1fr);
                }
                .company-name {
                    font-size: 2em;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="language-indicator" id="lang-indicator">SW</div>
                <div class="company-name">FRECHA IOTECH</div>
                <div class="company-tagline">Your Trusted Internet Solutions Partner</div>
                <div class="providers">
                    <div class="provider-tag">🟥 Vodacom</div>
                    <div class="provider-tag">🟦 Yas</div>
                    <div class="provider-tag">🟥 Airtel</div>
                    <div class="provider-tag">🟨Halotel</div>
                </div>
            </div>
            
            <div class="chat-area">
                <div class="quick-actions">
                    <button class="quick-btn" onclick="sendQuickMessage('Habari')">🤖 Habari</button>
                    <button class="quick-btn" onclick="sendQuickMessage('bundle')">📦 Bundle</button>
                    <button class="quick-btn" onclick="sendQuickMessage('vodacom')">🟥 Vodacom</button>
                    <button class="quick-btn" onclick="sendQuickMessage('SME')">🏢 SME</button>
                    <button class="quick-btn" onclick="sendQuickMessage('bei nafuu')">💰 Bei Nafuu</button>
                    <button class="quick-btn" onclick="sendQuickMessage('wasiliana')">📞 Wasiliana</button>
                    <button class="quick-btn" onclick="sendQuickMessage('english')">🔤 English</button>
                    <button class="quick-btn" onclick="sendQuickMessage('kiswahili')">🇹🇿 Kiswahili</button>
                </div>
                
                <div id="chat-box" class="chat-box">
                    <div class="bot-message">Karibu Frecha iotech! Ninaweza kukusaidiaje kuhusu bundle router au huduma za SME leo?</div>
                </div>
                
                <div class="input-area">
                    <input type="text" id="user-input" placeholder="Andika ujumbe wako..." onkeypress="handleKeyPress(event)">
                    <button onclick="sendMessage()">Tuma</button>
                </div>
            </div>
        </div>

        <script>
            function updateLanguageIndicator(lang) {
                document.getElementById('lang-indicator').textContent = lang === 'swahili' ? 'SW' : 'EN';
                const input = document.getElementById('user-input');
                input.placeholder = lang === 'swahili' ? 'Andika ujumbe wako...' : 'Type your message...';
            }

            function sendQuickMessage(message) {
                document.getElementById('user-input').value = message;
                sendMessage();
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }

            async function sendMessage() {
                const input = document.getElementById('user-input');
                const message = input.value.trim();
                const chatBox = document.getElementById('chat-box');
                
                if (!message) {
                    alert('Tafadhali andika ujumbe!');
                    return;
                }

                // Add user message to chat
                const userMessage = document.createElement('div');
                userMessage.className = 'message user-message';
                userMessage.textContent = message;
                chatBox.appendChild(userMessage);
                
                // Clear input
                input.value = '';
                
                // Show loading
                const loadingMessage = document.createElement('div');
                loadingMessage.className = 'message bot-message';
                loadingMessage.textContent = 'Inafikiri...';
                chatBox.appendChild(loadingMessage);
                chatBox.scrollTop = chatBox.scrollHeight;

                try {
                    // Send to backend
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message: message })
                    });
                    
                    const data = await response.json();
                    
                    // Remove loading message
                    chatBox.removeChild(loadingMessage);
                    
                    // Add bot response
                    const botMessage = document.createElement('div');
                    botMessage.className = 'message bot-message';
                    botMessage.textContent = data.response;
                    chatBox.appendChild(botMessage);
                    
                    // Update language indicator
                    if (data.language) {
                        updateLanguageIndicator(data.language);
                    }
                    
                    chatBox.scrollTop = chatBox.scrollHeight;
                } catch (error) {
                    chatBox.removeChild(loadingMessage);
                    
                    const errorMessage = document.createElement('div');
                    errorMessage.className = 'message bot-message';
                    errorMessage.textContent = 'Samahani, kuna tatizo la kiufundi. Tafadhali jaribu tena.';
                    chatBox.appendChild(errorMessage);
                    chatBox.scrollTop = chatBox.scrollHeight;
                }
            }

            // Initialize
            updateLanguageIndicator('swahili');
            document.getElementById('user-input').focus();
        </script>
    </body>
    </html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    """Forward chat requests to Django backend"""
    try:
        data = request.get_json()
        
        # Send to Django backend
        response = requests.post(
            f'{DJANGO_BACKEND_URL}/api/chat/',
            json=data,
            timeout=10
        )
        
        return jsonify(response.json())
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'response': 'Samahani, huduma haipatikani kwa sasa. Tafadhali jaribu tena baadaye.',
            'language': 'swahili'
        }), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Frecha Chatbot Frontend'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)