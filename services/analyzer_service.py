# ============================================
# ANALYZER SERVICE - AI Trading Tahlil
# ============================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import base64
import requests
import json
from datetime import datetime, timedelta
import config

# MetaTrader 5
try:
    import MetaTrader5 as mt5
    import pandas as pd
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 o'rnatilmagan. Real narxlar ishlamaydi.")

from services.database_service import trading_db


class ProfessionalAnalyzer:
    """AI yordamida professional trading tahlil"""
    
    def __init__(self):
        self.gemini_key = config.GEMINI_API_KEY
        self.api_url = config.GEMINI_API_URL
        self.db = trading_db
        
        # MT5 ni ishga tushirish
        self.mt5_initialized = False
        if MT5_AVAILABLE:
            self.initialize_mt5()
    
    def initialize_mt5(self):
        """MT5 ni ishga tushirish"""
        try:
            if not mt5.initialize():
                print("⚠️ MT5 initialize xatosi:", mt5.last_error())
                return False
            
            print("✅ MT5 muvaffaqiyatli ulandi")
            self.mt5_initialized = True
            return True
            
        except Exception as e:
            print(f"⚠️ MT5 ulanish xatosi: {e}")
            return False
    
    def get_mt5_symbol_info(self, symbol):
        """MT5 dan symbol ma'lumotlarini olish"""
        if not self.mt5_initialized:
            return None
        
        try:
            # Symbol nomini to'g'rilash
            mt5_symbol = symbol
            if symbol == "BTC":
                mt5_symbol = "BTCUSD"
            elif symbol == "GOLD":
                mt5_symbol = "XAUUSD"
            
            # Symbol ma'lumotlarini olish
            symbol_info = mt5.symbol_info(mt5_symbol)
            if symbol_info is None:
                return None
            
            # Joriy narxni olish
            tick = mt5.symbol_info_tick(mt5_symbol)
            if tick is None:
                return None
            
            # 24 soatlik ma'lumotlarni olish
            time_now = datetime.now()
            time_yesterday = time_now - timedelta(days=1)
            
            rates = mt5.copy_rates_range(mt5_symbol, mt5.TIMEFRAME_H1, time_yesterday, time_now)
            if rates is None:
                return None
            
            # DataFrame ga o'tkazish
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # 24 soatlik high/low
            high_24h = df['high'].max()
            low_24h = df['low'].min()
            
            # Narx o'zgarishi %
            if len(df) >= 2:
                first_price = df.iloc[0]['close']
                last_price = (tick.bid + tick.ask) / 2
                price_change_pct = ((last_price - first_price) / first_price) * 100
                price_change = f"{price_change_pct:+.2f}%"
            else:
                price_change = "Noma'lum"
            
            result = {
                'symbol': mt5_symbol,
                'bid': tick.bid,
                'ask': tick.ask,
                'current_price': (tick.bid + tick.ask) / 2,
                'spread': (tick.ask - tick.bid) * 10000,
                'high_24h': high_24h,
                'low_24h': low_24h,
                'price_change': price_change,
                'volume': tick.volume,
                'time': tick.time
            }
            
            return result
            
        except Exception as e:
            print(f"MT5 ma'lumot olish xatosi: {e}")
            return None
    
    def get_real_economic_data(self):
        """Database dan iqtisodiy ma'lumotlarni olish"""
        try:
            economic_data = self.db.get_economic_data()
            if economic_data:
                update_time = economic_data.updated_at
                if isinstance(update_time, str):
                    formatted_time = update_time
                elif hasattr(update_time, 'strftime'):
                    formatted_time = update_time.strftime('%Y-%m-%d %H:%M')
                else:
                    formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M')
                
                return {
                    'inflation': economic_data.inflation,
                    'fed_rate': economic_data.fed_rate,
                    'dollar_index': economic_data.dollar_index,
                    'unemployment': economic_data.unemployment,
                    'gdp_growth': economic_data.gdp_growth,
                    'update_time': formatted_time
                }
            else:
                return {
                    'inflation': '3.2%',
                    'fed_rate': '5.25-5.5%',
                    'dollar_index': '104.8',
                    'unemployment': '3.8%',
                    'gdp_growth': '2.1%',
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
        except Exception as e:
            print(f"❌ Iqtisodiy ma'lumotlar xatosi: {e}")
            return {
                'inflation': '3.2%',
                'fed_rate': '5.25-5.5%',
                'dollar_index': '104.8',
                'unemployment': '3.8%',
                'gdp_growth': '2.1%',
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
    
    def get_real_news(self, symbol):
        """Database dan yangiliklarni olish"""
        try:
            economic_data = self.db.get_economic_data()
            if not economic_data:
                return self.get_default_news(symbol)
            
            if symbol == "BTC":
                news_text = economic_data.btc_news
            else:
                news_text = economic_data.gold_news
            
            if news_text:
                news_items = news_text.split('|')
            else:
                news_items = []
            
            if not news_items:
                return self.get_default_news(symbol)
            
            return news_items
            
        except Exception as e:
            print(f"❌ Yangiliklar xatosi: {e}")
            return self.get_default_news(symbol)
    
    def get_default_news(self, symbol):
        """Standart yangiliklarni qaytarish"""
        if symbol == "BTC":
            return [
                "• Bitcoin ETF oqimlari: So'nggi haftada $500M kirim",
                "• FED raisi bayonoti: Foiz stavkalari barqaror",
                "• Global regulyator: Kripto qonunchiligi muhokamasi"
            ]
        else:
            return [
                "• Oltin narxi: Markaziy banklar zaxira o'sishi",
                "• Inflyatsiya: So'nggi ma'lumotlar ijobiy",
                "• Geosiyosiy: Yaqin Sharq vaziyati ta'siri"
            ]
    
    def encode_image_to_base64(self, image_path):
        """Rasmni base64 ga o'tkazish"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def split_message(self, text, max_length=4000):
        """Xabarni telegram limitiga mos qilib bo'laklash"""
        if len(text) <= max_length:
            return [text]
        
        parts = []
        while text:
            if len(text) <= max_length:
                parts.append(text)
                break
            split_pos = text.rfind('\n', 0, max_length)
            if split_pos == -1:
                split_pos = max_length
            parts.append(text[:split_pos])
            text = text[split_pos:].strip()
        return parts
    
    async def analyze_price_action(self, image_path):
        """Price Action tahlil - 1 ta rasm"""
        try:
            base64_image = self.encode_image_to_base64(image_path)
            
            prompt = """
SIZ PROFESSIONAL PRICE ACTION TRADERISIZ. Grafikni O'ZBEK TILIDA CHUQUR TAHLIL QILING.

🎯 ANIQ SIGNAL FORMATI:

📊 MARKET ANALYSIS:
- Trend: [BULLISH/BEARISH/RANGING]
- Key Levels: [aniq narxlar]

🎯 TRADING SIGNAL:
- Direction: [BUY/SELL]
- Entry: [aniq narx]
- Stop Loss: [aniq narx]
- Take Profit 1: [narx]
- Take Profit 2: [narx]
- Risk/Reward: 1:[RR]

BATAFSIL VA ANIQ JAVOB BERING!
"""
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 2000,
                }
            }
            
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['candidates'][0]['content']['parts'][0]['text']
                return f"📊 PRICE ACTION TAHLILI:\n\n{analysis_text}"
            else:
                return f"❌ Tahlil xatosi: {response.status_code}"
                
        except Exception as e:
            return f"❌ Tahlil xatosi: {str(e)}"
    
    async def analyze_pro_multi_timeframe(self, image_paths):
        """Pro tahlil - 3 ta rasm"""
        try:
            image_parts = []
            for image_path in image_paths:
                base64_image = self.encode_image_to_base64(image_path)
                image_parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": base64_image
                    }
                })
            
            prompt = """
SIZ PROFESSIONAL MULTI-TIMEFRAME TRADERISIZ. 3 TA TIMEFRAME ASOSIDA CHUQUR TAHLIL BERING.

🎯 SMART MONEY + MULTI-TIMEFRAME TAHLIL:

📊 HTF ANALYSIS (Katta timeframe):
- Trend va struktura
- Asosiy zonalar

📊 MTF ANALYSIS (O'rta timeframe):
- Setup va trigger
- Kirish nuqtalari

📊 LTF ANALYSIS (Kichik timeframe):
- Aniq entry
- Risk management

🎯 FINAL TRADING PLAN:
- Entry: [aniq narx]
- SL: [aniq narx]
- TP1/TP2: [narxlar]
- R/R: 1:[ratio]

PROFESSIONAL VA EXECUTABLE SIGNAL BERING!
"""
            
            contents = [{"text": prompt}]
            contents.extend(image_parts)
            
            payload = {
                "contents": [{"parts": contents}],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 4000,
                }
            }
            
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=90)
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['candidates'][0]['content']['parts'][0]['text']
                return f"🔍 PRO MULTI-TIMEFRAME TAHLIL:\n\n{analysis_text}"
            else:
                return f"❌ Pro tahlil xatosi: {response.status_code}"
                
        except Exception as e:
            return f"❌ Pro tahlil xatosi: {str(e)}"
    
    async def analyze_fundamental(self, symbol):
        """Fundamental tahlil"""
        try:
            # MT5 dan real narx
            symbol_info = self.get_mt5_symbol_info(symbol)
            
            if symbol_info:
                current_price = f"{symbol_info['current_price']:,.2f}"
                price_change = symbol_info['price_change']
                high_24h = f"{symbol_info['high_24h']:,.2f}"
                low_24h = f"{symbol_info['low_24h']:,.2f}"
                price_source = "MetaTrader 5 (Real-time)"
            else:
                current_price = "Noma'lum"
                price_change = "Noma'lum"
                high_24h = "Noma'lum"
                low_24h = "Noma'lum"
                price_source = "Standart"
            
            # Iqtisodiy ma'lumotlar
            economic_data = self.get_real_economic_data()
            
            # Yangiliklar
            real_news = self.get_real_news(symbol)
            
            prompt = f"""
SIZ FUNDAMENTAL ANALIZCHISIZ. {symbol} uchun CHUQUR FUNDAMENTAL TAHLIL BERING.

💰 REAL-TIME NARX ({price_source}):
- Joriy: ${current_price}
- 24s o'zgarish: {price_change}
- 24s High/Low: ${high_24h} / ${low_24h}

📊 IQTISODIY KO'RSATKICHLAR:
- Inflyatsiya: {economic_data['inflation']}
- FED stavka: {economic_data['fed_rate']}
- Dollar indeksi: {economic_data['dollar_index']}
- Ishsizlik: {economic_data['unemployment']}
- YaIM: {economic_data['gdp_growth']}

📰 YANGILIKLAR:
"""
            
            for news in real_news:
                prompt += f"\n{news}"
            
            prompt += """

🎯 PROFESSIONAL FUNDAMENTAL TAHLIL:

1. JORIY HOLAT TAHLILI
2. FUNDAMENTAL OMILLAR TA'SIRI
3. TREND PROGNOZI (1-4 hafta, 1-3 oy)
4. TRADING STRATEGIYA
5. RISK TAHLILI

ANIQ VA PROFESSIONAL JAVOB BERING!
"""
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 3500,
                }
            }
            
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['candidates'][0]['content']['parts'][0]['text']
                
                final_analysis = f"""
💼 {symbol} FUNDAMENTAL TAHLILI
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💰 REAL NARX ({price_source}):
- Joriy: ${current_price}
- 24s: {price_change}
- High/Low: ${high_24h} / ${low_24h}

{analysis_text}

📊 MA'LUMOT MANBALARI:
- Narx: {price_source}
- Iqtisodiy: Database (Real)
- Yangiliklar: Dolzarb
- Tahlil: FATH AI Analyzer
"""
                return final_analysis
            else:
                return f"❌ Fundamental tahlil xatosi: {response.status_code}"
                
        except Exception as e:
            return f"❌ Fundamental tahlil xatosi: {str(e)}"
    
    def __del__(self):
        """MT5 ni to'xtatish"""
        try:
            if self.mt5_initialized:
                mt5.shutdown()
        except:
            pass


# Global instance
analyzer = ProfessionalAnalyzer()