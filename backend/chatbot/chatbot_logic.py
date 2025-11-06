import random
from typing import Dict, List, Optional

class FrechaServicesChatbot:
    def __init__(self):
        self.company_name = "Frecha iotech"
        self.current_language = "swahili"
        
        self.translations = self.load_translations()
        self.bundle_plans = self.load_bundle_plans()
        self.sme_services = self.load_sme_services()

    def load_translations(self):
        return {
            "english": {
                "greeting": f"Welcome to {self.company_name}! Your trusted partner for bundle routers and SME services.",
                "help": "I can help with:\n• Bundle router plans\n• SME services\n• Provider comparisons\n• Contact information",
                "contact_info": "📞 Phone: +255 757 315 593\n✉️ Email: frechaiotech@gmail.com\n📍 Location: Dodoma",
                "language_switched": "🌍 Switched to English!",
                "providers": "Our providers: 🟥 Vodacom, 🟦 Yas, 🟨 Airtel, 🟩 Halotel"
            },
            "swahili": {
                "greeting": f"Karibu {self.company_name}! Mshirika wako wa kuaminika kwa bundle router na huduma za SME.",
                "help": "Naweza kukusaidia kuhusu:\n• Mipango ya bundle router\n• Huduma za SME\n• Kulinganisha watoa huduma\n• Mawasiliano",
                "contact_info": "📞 Simu: +255 757 315 593\n✉️ Barua pepe: frechaiotech@gmail.com\n📍 Mahali: Dodoma",
                "language_switched": "🌍 Nimebadilisha lugha kwa Kiswahili!",
                "providers": "Watoa huduma wetu: 🟥 Vodacom, 🟦 Yas, 🟨 Airtel, 🟩 Halotel"
            }
        }

    def load_bundle_plans(self):
        return {
            "vodacom": [
                {"name": "DATA PLAN", "price": "TZS 15,000", "data": "10GB"},
                {"name": "UNLIMITED HOME", "price": "TZS 240,000", "data": "Unlimited"}
            ],
            "yas": [
                {"name": "Yas Home", "price": "TZS 50,000", "data": "60GB"},
                {"name": "Yas Business", "price": "TZS 100,000", "data": "125GB"}
            ],
            "airtel": [
                {"name": "Airtel Home", "price": "TZS 60,000", "data": "75GB"},
                {"name": "Airtel Business", "price": "TZS 100,000", "data": "Unlimited"}
            ],
            "halotel": [
                {"name": "Halo Home", "price": "TZS 46,000", "data": "60GB"},
                {"name": "Halo Business", "price": "TZS 38,000", "data": "50GB"}
            ]
        }

    def load_sme_services(self):
        return {
            "startup": {
                "name": "Startup Special",
                "price": "TZS 120,000/month",
                "features": ["Shared 10Mbps", "Business router", "Basic support"]
            },
            "premium": {
                "name": "SME Premium", 
                "price": "TZS 350,000/month",
                "features": ["Dedicated 50Mbps", "Advanced security", "24/7 Support"]
            }
        }

    def get_response(self, user_input: str) -> str:
        user_input_lower = user_input.lower().strip()
        
        # Language switching
        if any(word in user_input_lower for word in ['english', 'kiingereza']):
            self.current_language = "english"
            return self.t("language_switched")
        
        if any(word in user_input_lower for word in ['swahili', 'kiswahili']):
            self.current_language = "swahili"
            return self.t("language_switched")

        # Intent detection
        if any(word in user_input_lower for word in ['hello', 'hi', 'mambo', 'habari']):
            return f"{self.t('greeting')}\n\n{self.t('providers')}"
        
        elif any(word in user_input_lower for word in ['help', 'msaada']):
            return self.t("help")
        
        elif any(word in user_input_lower for word in ['bundle', 'router', 'data']):
            return self.handle_bundle_inquiry(user_input_lower)
        
        elif any(word in user_input_lower for word in ['sme', 'business', 'biashara']):
            return self.handle_sme_inquiry()
        
        elif any(word in user_input_lower for word in ['vodacom', 'yas', 'airtel', 'halotel']):
            return self.show_provider_bundles(user_input_lower)
        
        elif any(word in user_input_lower for word in ['contact', 'call', 'simu', 'wasiliana']):
            return self.t("contact_info")
        
        else:
            return self.t("help")

    def handle_bundle_inquiry(self, text: str) -> str:
        for provider in ["vodacom", "yas", "airtel", "halotel"]:
            if provider in text:
                return self.show_provider_bundles(provider)
        return self.show_all_bundles()

    def show_all_bundles(self) -> str:
        response = "📦 BUNDLE ROUTER PLANS:\n\n"
        for provider, plans in self.bundle_plans.items():
            response += f"**{provider.upper()}**\n"
            for plan in plans:
                response += f"• {plan['name']}: {plan['price']} - {plan['data']}\n"
            response += "\n"
        return response

    def show_provider_bundles(self, provider: str) -> str:
        if provider in self.bundle_plans:
            plans = self.bundle_plans[provider]
            response = f"📦 {provider.upper()} PLANS:\n\n"
            for plan in plans:
                response += f"• {plan['name']}: {plan['price']} - {plan['data']}\n"
            return response
        return "Provider not found."

    def handle_sme_inquiry(self) -> str:
        response = "🏢 SME BUSINESS SOLUTIONS:\n\n"
        for package_key, package in self.sme_services.items():
            response += f"• {package['name']}: {package['price']}\n"
            response += f"  Features: {', '.join(package['features'])}\n\n"
        return response

    def t(self, key: str) -> str:
        return self.translations[self.current_language].get(key, key)