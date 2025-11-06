import os
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from datetime import datetime
from typing import Dict, List, Optional

class FrechaServicesChatbot:
    def __init__(self):
        self.company_name = "Frecha iotech"
        self.user_name = None
        self.current_language = "swahili"
        self.conversation_history = []
        self.lead_data = {}
        
        self.providers = ["Vodacom", "Yas", "Airtel", "Halotel"]
        
        self.translations = self.load_translations()
        self.bundle_plans = self.load_bundle_plans()
        self.sme_services = self.load_sme_services()

    def load_translations(self):
        return {
            "english": {
                "greeting": [
                    f"Welcome to {self.company_name}! Your trusted partner for bundle routers and SME services. How can I assist you today?",
                    f"Hello! Welcome to {self.company_name} - connecting businesses with reliable internet solutions. What can I help you with?"
                ],
                "providers": f"Our trusted providers: 🟥 Vodacom, 🟦 Yas, 🟨 Airtel, 🟩 Halotel",
                "main_services": "We offer:\n📦 BUNDLE ROUTERS - Home & Business Internet\n🏢 SME SERVICES - Business Solutions\n💰 AFFORDABLE PRICING - Best rates",
                "help": "I can help you with:\n• Bundle router plans & pricing\n• SME service packages\n• Provider comparisons\n• New connection setup\n• Technical support\n• Payment options",
                "bundle_help": "📦 BUNDLE ROUTERS - Choose from various data plans for home and business use",
                "sme_help": "🏢 SME SERVICES - Business-grade internet and dedicated support",
                "goodbye": f"Thank you for choosing {self.company_name}!",
                "contact_info": f"📞 Contact {self.company_name}:\nPhone: +255 757 315 593\nEmail: frechaiotech@gmail.com\nLocation: Dodoma",
                "lead_capture": "To serve you better, may I know:\n1. Your name\n2. Business location\n3. Current internet provider\n4. Your specific needs",
                "thank_lead": "Thank you {name}! Our team will contact you shortly.",
                "provider_specific": "Which provider? Vodacom, Yas, Airtel, or Halotel?",
                "price_inquiry": "What's your budget? We have options from TZS 10,000 to 100,000",
                "language_switched": "🌍 Switched to English! How can I help you?"
            },
            "swahili": {
                "greeting": [
                    f"Karibu {self.company_name}! Mshirika wako wa kuaminika kwa bundle router na huduma za SME. Ninaweza kukusaidiaje leo?",
                    f"Hujambo! Karibu {self.company_name} - tunaunganisha biashara kwa suluhisho bora za intaneti. Ninaweza kukusaidia nini?"
                ],
                "providers": f"Watoa huduma wetu: 🟥 Vodacom, 🟦 Yas, 🟨 Airtel, 🟩 Halotel",
                "main_services": "Tunatoa:\n📦 BUNDLE ROUTER - Intaneti ya Nyumba na Biashara\n🏢 HUDUMA ZA SME - Suluhisho za Biashara\n💰 BEI NZURI - Bei bora zaidi",
                "help": "Naweza kukusaidia kuhusu:\n• Mipango ya bundle router na bei\n• Vifurushi vya huduma za SME\n• Kulinganisha watoa huduma\n• Kuanzisha muunganisho mpya\n• Usaidizi wa kiufundi\n• Njia za malipo",
                "bundle_help": "📦 BUNDLE ROUTER - Chagua mipango mbalimbali ya data",
                "sme_help": "🏢 HUDUMA ZA SME - Intaneti ya kiwango cha biashara",
                "goodbye": f"Asante kwa kuchagua {self.company_name}!",
                "contact_info": f"📞 Wasiliana na {self.company_name}:\nSimu: +255 757 315 593\nBarua pepe: frechaiotech@gmail.com\nMahali: Dodoma",
                "lead_capture": "Ili kukuhudumia vyema, naomba kujua:\n1. Jina lako\n2. Mahali pa biashara\n3. Mtoa huduma wa sasa\n4. Mahitaji yako maalum",
                "thank_lead": "Asante {name}! Timu yetu itawasiliana nawe hivi karibuni.",
                "provider_specific": "Unapenda mtoa huduma gani? Vodacom, Yas, Airtel, au Halotel?",
                "price_inquiry": "Una bajeti ya kiasi gani? Tuna chaguzi kutoka TZS 10,000 hadi 100,000",
                "language_switched": "🌍 Nimebadilisha lugha kwa Kiswahili! Ninaweza kukusaidiaje?"
            }
        }

    def load_bundle_plans(self):
        return {
            "vodacom": [
                {"name": "DATA PLAN", "price": "TZS 15,000", "data": "10GB", "validity": "30 days"},
                {"name": "UNLIMITED", "price": "TZS 240,000", "data": "Unlimited", "speed": "30Mbps", "validity": "30 days"}
            ],
            "yas": [
                {"name": "Yas Home", "price": "TZS 10,000", "data": "10GB", "speed": "8Mbps", "validity": "30 days"},
                {"name": "Yas Router", "price": "TZS 250,000", "data": "unlimited", "speed": "30Mbps", "validity": "30 days"}
            ],
            "airtel": [
                {"name": "Airtel Home", "price": "TZS 60,000", "data": "75GB", "speed": "10Mbps", "validity": "30 days"},
                {"name": "Airtel Router", "price": "TZS 100,000", "data": "unlimited", "speed": "25Mbps", "validity": "30 days"}
            ],
            "halotel": [
                {"name": "Halo Home", "price": "TZS 46,000", "data": "60GB", "speed": "8Mbps", "validity": "30 days"},
                {"name": "Halo Business", "price": "TZS 38,000", "data": "50GB", "speed": "15Mbps", "validity": "30 days"}
            ]
        }

    def load_sme_services(self):
        return {
            "startup": {
                "name": "Startup Special",
                "price": "TZS 70,000/month",
                "features": ["Shared 10Mbps line", "Business router", "Basic support"],
                "providers": ["Yas", "Halotel", "Airtel"]
            },
            "premium_sme": {
                "name": "SME Premium", 
                "price": "TZS 100,000/month",
                "features": ["Dedicated 50Mbps", "Advanced security", "24/7 Support"],
                "providers": ["Vodacom", "Airtel"]
            }
        }

    def get_response(self, user_input: str) -> str:
        if not user_input or user_input.strip() == "":
            return self.t("help")

        user_input_lower = user_input.lower().strip()
        
        # Language detection
        if any(word in user_input_lower for word in ['english', 'kiingereza']):
            self.current_language = "english"
            return self.t("language_switched")
        
        if any(word in user_input_lower for word in ['swahili', 'kiswahili']):
            self.current_language = "swahili"
            return self.t("language_switched")

        # Store conversation
        self.conversation_history.append({
            "user": user_input,
            "timestamp": datetime.now().isoformat(),
            "language": self.current_language
        })
        
        # Save to database (silently in background)
        self.save_conversation(user_input, "")
        
        # Intent detection
        if any(word in user_input_lower for word in ['hello', 'hi', 'hey', 'mambo', 'habari', 'hujambo']):
            response = self.t("greeting")
        elif any(word in user_input_lower for word in ['help', 'msaada']):
            response = self.t("help")
        elif any(word in user_input_lower for word in ['bundle', 'router', 'data', 'intaneti']):
            response = self.handle_bundle_inquiry(user_input_lower)
        elif any(word in user_input_lower for word in ['sme', 'business', 'biashara']):
            response = self.handle_sme_inquiry(user_input_lower)
        elif any(word in user_input_lower for word in ['vodacom', 'yas', 'airtel', 'halotel']):
            response = self.show_provider_bundles(user_input_lower)
        elif any(word in user_input_lower for word in ['price', 'cost', 'bei']):
            response = self.t("price_inquiry")
        elif any(word in user_input_lower for word in ['contact', 'call', 'simu']):
            response = self.t("contact_info")
        elif any(word in user_input_lower for word in ['bye', 'quit', 'kwaheri']):
            response = self.t("goodbye")
        else:
            response = self.t("help")
        
        # Update conversation with bot response (silently)
        self.update_conversation(user_input, response)
        
        return response

    def handle_bundle_inquiry(self, text: str) -> str:
        for provider in self.providers:
            if provider.lower() in text:
                return self.show_provider_bundles(provider.lower())
        return self.show_all_bundles()

    def handle_sme_inquiry(self, text: str) -> str:
        return self.show_all_sme_packages()

    def show_all_bundles(self) -> str:
        response = "📦 BUNDLE PLANS:\n\n"
        for provider in self.providers:
            plans = self.bundle_plans[provider.lower()]
            response += f"**{provider}**\n"
            for plan in plans:
                response += f"• {plan['name']}: {plan['price']} - {plan['data']}\n"
            response += "\n"
        return response

    def show_provider_bundles(self, provider: str) -> str:
        if provider not in self.bundle_plans:
            return "Provider not found."
        
        plans = self.bundle_plans[provider]
        response = f"📦 {provider.upper()} PLANS:\n\n"
        for plan in plans:
            response += f"• {plan['name']}: {plan['price']}\n"
            response += f"  Data: {plan['data']}\n"
            if 'speed' in plan:
                response += f"  Speed: {plan['speed']}\n"
            response += f"  Validity: {plan['validity']}\n\n"
        return response

    def show_all_sme_packages(self) -> str:
        response = "🏢 SME PACKAGES:\n\n"
        for package_key, package in self.sme_services.items():
            response += f"• {package['name']}: {package['price']}\n"
            response += f"  Providers: {', '.join(package['providers'])}\n\n"
        return response

    def save_conversation(self, user_message: str, bot_response: str):
        """Save conversation to database (background process)"""
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                cur.execute(
                    'INSERT INTO conversations (user_message, bot_response, language) VALUES (%s, %s, %s)',
                    (user_message, bot_response, self.current_language)
                )
                conn.commit()
                cur.close()
                conn.close()
        except Exception as e:
            # Silently fail - don't show errors to users
            pass

    def update_conversation(self, user_message: str, bot_response: str):
        """Update conversation with bot response (background process)"""
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                cur.execute(
                    'UPDATE conversations SET bot_response = %s WHERE user_message = %s AND bot_response = %s',
                    (bot_response, user_message, "")
                )
                conn.commit()
                cur.close()
                conn.close()
        except Exception as e:
            # Silently fail - don't show errors to users
            pass

    def save_lead(self, lead_data: dict) -> bool:
        """Save lead to database (background process)"""
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                cur.execute(
                    '''INSERT INTO leads (name, location, current_provider, needs, contact, language) 
                       VALUES (%s, %s, %s, %s, %s, %s)''',
                    (lead_data.get('name'), lead_data.get('location'), lead_data.get('provider'),
                     lead_data.get('needs'), lead_data.get('contact'), self.current_language)
                )
                conn.commit()
                cur.close()
                conn.close()
                return True
        except Exception as e:
            # Silently fail - don't show errors to users
            pass
        return False

    def t(self, key: str) -> str:
        translations = self.translations.get(self.current_language, {})
        translation = translations.get(key, key)
        if isinstance(translation, list):
            return random.choice(translation)
        return translation

# Database connection for Railway PostgreSQL
def get_db_connection():
    """Get connection to Railway PostgreSQL database"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            return psycopg2.connect(database_url)
        return None
    except Exception as e:
        # Silently fail - database operations are optional
        return None

def init_database():
    """Initialize database tables on Railway (background process)"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        # Create conversations table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                user_message TEXT NOT NULL,
                bot_response TEXT,
                language VARCHAR(10),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create leads table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                location VARCHAR(100),
                current_provider VARCHAR(50),
                needs TEXT,
                contact VARCHAR(100),
                language VARCHAR(10),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'new'
            )
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        # Silently fail - don't affect user experience
        pass

# Flask App
app = Flask(__name__)
CORS(app)
chatbot = FrechaServicesChatbot()

# Initialize database when app starts (silently)
init_database()

@app.route('/')
def home():
    """Show only the chatbot interface - no admin info"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Frecha iotech</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
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
            
            .company-tagline {
                font-size: 1.1em;
                opacity: 0.9;
                margin-bottom: 15px;
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
            
            button:hover {
                background: #5a6fd8;
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
                    <div class="provider-tag">🟨 Airtel</div>
                    <div class="provider-tag">🟩 Halotel</div>
                </div>
            </div>
            
            <div class="chat-area">
                <div class="quick-actions">
                    <button class="quick-btn" onclick="sendQuickMessage('mambo')">👋 Mambo</button>
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

            function sendMessage() {
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

                // Send to server
                fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
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
                })
                .catch(error => {
                    chatBox.removeChild(loadingMessage);
                    
                    const errorMessage = document.createElement('div');
                    errorMessage.className = 'message bot-message';
                    errorMessage.textContent = 'Samahani, kuna tatizo la kiufundi. Tafadhali jaribu tena.';
                    chatBox.appendChild(errorMessage);
                    chatBox.scrollTop = chatBox.scrollHeight;
                });
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
    """Main chatbot endpoint - only endpoint users can access"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        bot_response = chatbot.get_response(user_message)
        
        return jsonify({
            'response': bot_response,
            'language': chatbot.current_language,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Sorry, something went wrong. Please try again.'}), 500

@app.route('/health')
def health():
    """Simple health check - returns minimal info"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Frecha iotech Chatbot Running...")
    print("📍 Access at: http://0.0.0.0:" + str(port))
    app.run(host='0.0.0.0', port=port, debug=False)