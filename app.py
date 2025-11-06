import os
import psycopg2
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AdminReporter:
    def __init__(self):
        self.admin_email = os.environ.get('ADMIN_EMAIL', 'frechaiotech@gmail.com')
        self.smtp_config = {
            'server': os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
            'port': int(os.environ.get('SMTP_PORT', 587)),
            'username': os.environ.get('SMTP_USERNAME', ''),
            'password': os.environ.get('SMTP_PASSWORD', '')
        }
    
    def send_daily_report(self):
        """Send daily activity report to admin"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get today's stats
            today = datetime.now().date()
            cur.execute('''
                SELECT COUNT(*) as total_chats, 
                       COUNT(DISTINCT user_message) as unique_conversations,
                       language,
                       COUNT(*) as language_count
                FROM conversations 
                WHERE DATE(timestamp) = %s 
                GROUP BY language
            ''', (today,))
            
            language_stats = cur.fetchall()
            
            # Get popular services
            cur.execute('''
                SELECT user_message, COUNT(*) as count
                FROM conversations 
                WHERE DATE(timestamp) = %s 
                GROUP BY user_message 
                ORDER BY count DESC 
                LIMIT 10
            ''', (today,))
            
            popular_services = cur.fetchall()
            
            cur.close()
            conn.close()
            
            # Generate report
            report = self.generate_daily_report(today, language_stats, popular_services)
            
            # Send email
            self.send_email(
                subject=f"📊 Frecha Chatbot Daily Report - {today}",
                body=report
            )
            
            return True
        except Exception as e:
            print(f"Error sending daily report: {e}")
            return False
    
    def send_lead_alert(self, lead_data):
        """Send immediate alert when lead is captured"""
        try:
            subject = "🚨 NEW LEAD CAPTURED - Frecha iotech"
            body = f"""
            🎯 NEW LEAD ALERT 🎯
            
            📋 Lead Details:
            • Name: {lead_data.get('name', 'Not provided')}
            • Location: {lead_data.get('location', 'Not provided')}
            • Current Provider: {lead_data.get('provider', 'Not provided')}
            • Needs: {lead_data.get('needs', 'Not provided')}
            • Contact: {lead_data.get('contact', 'Not provided')}
            • Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            ⚡ Action Required: Follow up within 24 hours!
            """
            
            self.send_email(subject, body)
            return True
        except Exception as e:
            print(f"Error sending lead alert: {e}")
            return False
    
    def generate_daily_report(self, date, language_stats, popular_services):
        """Generate formatted daily report"""
        total_chats = sum([stat[0] for stat in language_stats])
        
        report = f"""
        📊 FRECHA IOTECH CHATBOT DAILY REPORT
        📅 Date: {date}
        ⏰ Generated: {datetime.now().strftime('%H:%M:%S')}
        ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

        📈 ACTIVITY SUMMARY:
        • Total Conversations: {total_chats}
        • Unique Interactions: {sum([stat[1] for stat in language_stats])}

        🌍 LANGUAGE USAGE:
        """
        
        for lang_stat in language_stats:
            lang = "Swahili" if lang_stat[2] == "swahili" else "English"
            report += f"   • {lang}: {lang_stat[3]} conversations\n"
        
        report += f"""
        🔥 POPULAR SERVICES:
        """
        
        for service in popular_services[:5]:
            service_name = service[0][:30] + "..." if len(service[0]) > 30 else service[0]
            report += f"   • {service_name}: {service[1]} inquiries\n"
        
        report += f"""
        💡 RECOMMENDATIONS:
        • Focus on most inquired services
        • Follow up on leads promptly
        • Monitor language preferences

        🤖 Chatbot URL: https://frecha-chatbot.up.railway.app
        📞 Contact: +255 757 315 593
        """
        
        return report
    
    def send_email(self, subject, body):
        """Send email using SMTP"""
        try:
            if not all([self.smtp_config['username'], self.smtp_config['password']]):
                print("SMTP credentials not configured. Email not sent.")
                return False
            
            msg = MimeMultipart()
            msg['From'] = self.smtp_config['username']
            msg['To'] = self.admin_email
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            server.starttls()
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email sent: {subject}")
            return True
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False

class FrechaServicesChatbot:
    def __init__(self):
        self.company_name = "Frecha iotech"
        self.user_name = None
        self.current_language = "swahili"
        self.conversation_history = []
        self.lead_data = {}
        self.admin_reporter = AdminReporter()
        
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
                "goodbye": f"Thank you for choosing {self.company_name}! Our team will contact you shortly.",
                "contact_info": f"📞 Contact {self.company_name}:\nPhone: +255 757 315 593\nEmail: frechaiotech@gmail.com\nLocation: Dodoma",
                "lead_capture": "To serve you better and provide personalized offers, may I know:\n1. Your name\n2. Business location\n3. Current internet provider\n4. Your specific needs\n5. Contact information (phone/email)",
                "thank_lead": "Thank you {name}! Our team will contact you within 24 hours with the best offers for your location.",
                "provider_specific": "Which provider? Vodacom, Yas, Airtel, or Halotel?",
                "price_inquiry": "What's your budget? We have options from TZS 10,000 to 500,000+",
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
                "goodbye": f"Asante kwa kuchagua {self.company_name}! Timu yetu itawasiliana nawe ndani ya masaa 24.",
                "contact_info": f"📞 Wasiliana na {self.company_name}:\nSimu: +255 757 315 593\nBarua pepe: frechaiotech@gmail.com\nMahali: Dodoma",
                "lead_capture": "Ili kukuhudumia vyema na kukupatia ofuri bora, naomba kujua:\n1. Jina lako\n2. Mahali pa biashara\n3. Mtoa huduma wa sasa\n4. Mahitaji yako maalum\n5. Mawasiliano (simu/barua pepe)",
                "thank_lead": "Asante {name}! Timu yetu itawasiliana nawe ndani ya masaa 24 kwa ofuri bora zaidi kwa eneo lako.",
                "provider_specific": "Unapenda mtoa huduma gani? Vodacom, Yas, Airtel, au Halotel?",
                "price_inquiry": "Una bajeti ya kiasi gani? Tuna chaguzi kutoka TZS 10,000 hadi 500,000+",
                "language_switched": "🌍 Nimebadilisha lugha kwa Kiswahili! Ninaweza kukusaidiaje?"
            }
        }

    def load_bundle_plans(self):
        return {
            "vodacom": [
                {"name": "DATA PLAN", "price": "TZS 15,000", "data": "10GB", "validity": "30 days"},
                {"name": "UNLIMITED HOME", "price": "TZS 240,000", "data": "Unlimited", "speed": "30Mbps", "validity": "30 days"}
            ],
            "yas": [
                {"name": "Yas Home", "price": "TZS 50,000", "data": "60GB", "speed": "8Mbps", "validity": "30 days"},
                {"name": "Yas Business", "price": "TZS 100,000", "data": "125GB", "speed": "15Mbps", "validity": "30 days"}
            ],
            "airtel": [
                {"name": "Airtel Home", "price": "TZS 60,000", "data": "75GB", "speed": "10Mbps", "validity": "30 days"},
                {"name": "Airtel Business", "price": "TZS 100,000", "data": "Unlimited", "speed": "25Mbps", "validity": "30 days"}
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
                "price": "TZS 120,000/month",
                "features": ["Shared 10Mbps line", "Business router", "Basic support", "Flexible contract"],
                "providers": ["Yas", "Halotel", "Airtel"]
            },
            "premium_sme": {
                "name": "SME Premium", 
                "price": "TZS 350,000/month",
                "features": ["Dedicated 50Mbps line", "Advanced security", "24/7 Support", "Static IP"],
                "providers": ["Vodacom", "Airtel"]
            },
            "enterprise": {
                "name": "Enterprise Solution",
                "price": "TZS 500,000+/month",
                "features": ["Custom bandwidth", "Dedicated fiber", "SLA Agreement", "24/7 Dedicated support"],
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
        
        # Save conversation to database
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
        elif any(word in user_input_lower for word in ['buy', 'order', 'nunua', 'agiza']):
            response = self.handle_lead_capture(user_input_lower)
        elif any(word in user_input_lower for word in ['bye', 'quit', 'kwaheri']):
            response = self.t("goodbye")
        else:
            response = self.t("help")
        
        # Update conversation with bot response
        self.update_conversation(user_input, response)
        
        return response

    def handle_bundle_inquiry(self, text: str) -> str:
        for provider in self.providers:
            if provider.lower() in text:
                return self.show_provider_bundles(provider.lower())
        return self.show_all_bundles()

    def handle_sme_inquiry(self, text: str) -> str:
        return self.show_all_sme_packages()

    def handle_lead_capture(self, text: str) -> str:
        """Handle purchase/order inquiries and capture leads"""
        return self.t("lead_capture")

    def show_all_bundles(self) -> str:
        response = "📦 BUNDLE ROUTER PLANS:\n\n"
        for provider in self.providers:
            plans = self.bundle_plans[provider.lower()]
            response += f"**{provider.upper()}**\n"
            for plan in plans:
                response += f"• {plan['name']}: {plan['price']} - {plan['data']}"
                if 'speed' in plan:
                    response += f" at {plan['speed']}"
                response += "\n"
            response += "\n"
        response += "💡 *Reply with provider name for detailed plans*"
        return response

    def show_provider_bundles(self, provider: str) -> str:
        if provider not in self.bundle_plans:
            return "Provider not found."
        
        plans = self.bundle_plans[provider]
        response = f"📦 {provider.upper()} BUNDLE PLANS:\n\n"
        for plan in plans:
            response += f"• {plan['name']}: {plan['price']}\n"
            response += f"  📊 Data: {plan['data']}\n"
            if 'speed' in plan:
                response += f"  🚀 Speed: {plan['speed']}\n"
            response += f"  📅 Validity: {plan['validity']}\n\n"
        
        response += "🚀 *Ready to order? Reply with your contact details!*"
        return response

    def show_all_sme_packages(self) -> str:
        response = "🏢 SME BUSINESS SOLUTIONS:\n\n"
        for package_key, package in self.sme_services.items():
            response += f"• {package['name']}: {package['price']}\n"
            response += f"  📡 Providers: {', '.join(package['providers'])}\n"
            response += f"  ✨ Features: {', '.join(package['features'][:2])}\n\n"
        
        response += "💼 *Contact us for custom business solutions!*"
        return response

    def save_conversation(self, user_message: str, bot_response: str):
        """Save conversation to database"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO conversations (user_message, bot_response, language) VALUES (%s, %s, %s)',
                (user_message, bot_response, self.current_language)
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error saving conversation: {e}")

    def update_conversation(self, user_message: str, bot_response: str):
        """Update conversation with bot response"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'UPDATE conversations SET bot_response = %s WHERE user_message = %s AND bot_response = %s',
                (bot_response, user_message, "")
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error updating conversation: {e}")

    def save_lead(self, lead_data: dict) -> bool:
        """Save lead and send immediate alert to admin"""
        try:
            conn = get_db_connection()
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
            
            # Send immediate alert to admin
            self.admin_reporter.send_lead_alert(lead_data)
            
            return True
        except Exception as e:
            print(f"Error saving lead: {e}")
            return False

    def t(self, key: str) -> str:
        translations = self.translations.get(self.current_language, {})
        translation = translations.get(key, key)
        if isinstance(translation, list):
            return random.choice(translation)
        return translation

# Database connection
def get_db_connection():
    if 'DATABASE_URL' in os.environ:
        return psycopg2.connect(os.environ['DATABASE_URL'])
    return None

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        
        # Conversations table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                user_message TEXT NOT NULL,
                bot_response TEXT,
                language VARCHAR(10),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Leads table
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
        
        # Analytics table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id SERIAL PRIMARY KEY,
                metric VARCHAR(50),
                value INTEGER,
                date DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        conn.commit()
        cur.close()
        conn.close()

# Flask App
app = Flask(__name__)
CORS(app)
chatbot = FrechaServicesChatbot()
admin_reporter = AdminReporter()

# Initialize database on startup
init_db()

@app.route('/')
def home():
    return jsonify({
        "message": "Frecha iotech Chatbot API", 
        "status": "running",
        "features": ["chat", "lead_capture", "admin_reports", "analytics"],
        "version": "2.0"
    })

@app.route('/chat', methods=['POST'])
def chat():
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
        return jsonify({'error': str(e)}), 500

@app.route('/save_lead', methods=['POST'])
def save_lead():
    try:
        data = request.get_json()
        success = chatbot.save_lead(data)
        
        if success:
            # Send thank you message
            thank_you = chatbot.t("thank_lead").format(name=data.get('name', ''))
            return jsonify({
                'status': 'success', 
                'message': 'Lead saved successfully',
                'thank_you': thank_you
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to save lead'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/report/daily', methods=['POST'])
def send_daily_report():
    """Manually trigger daily report"""
    try:
        success = admin_reporter.send_daily_report()
        if success:
            return jsonify({'status': 'success', 'message': 'Daily report sent'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send report'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/stats')
def admin_stats():
    """Get admin statistics"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Total conversations
        cur.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cur.fetchone()[0]
        
        # Total leads
        cur.execute('SELECT COUNT(*) FROM leads')
        total_leads = cur.fetchone()[0]
        
        # Today's activity
        today = datetime.now().date()
        cur.execute('SELECT COUNT(*) FROM conversations WHERE DATE(timestamp) = %s', (today,))
        today_conversations = cur.fetchone()[0]
        
        # Language distribution
        cur.execute('SELECT language, COUNT(*) FROM conversations GROUP BY language')
        language_stats = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'total_conversations': total_conversations,
            'total_leads': total_leads,
            'today_conversations': today_conversations,
            'language_distribution': dict(language_stats),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy', 
        'service': 'Frecha iotech Chatbot',
        'version': '2.0',
        'features': ['admin_reports', 'lead_alerts', 'analytics']
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting Enhanced Frecha iotech Chatbot...")
    print("📍 Server will run at: http://0.0.0.0:" + str(port))
    print("🎯 Features: Admin Reports, Lead Alerts, Analytics")
    print("📧 Admin Email: " + os.environ.get('ADMIN_EMAIL', 'Not configured'))
    app.run(host='0.0.0.0', port=port, debug=False)