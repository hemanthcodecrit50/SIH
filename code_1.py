import google.generativeai as genai
import json
import datetime
import time
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os


# Configure Gemini API
genai.configure(api_key="")   # Replace with your API key
model = genai.GenerativeModel('gemini-2.0-flash')

# Sample farmer profile data
SAMPLE_FARMER_PROFILE = {
    "name": "Ramesh Kumar",
    "location": "Kurnool, Andhra Pradesh",
    "farm_size": "5 acres",
    "crops": ["Rice", "Cotton", "Groundnut"],
    "soil_type": "Red soil",
    "irrigation": "Bore well + Canal",
    "language": "Telugu",
    "last_yield": {
        "rice": "4.2 tons/acre",
        "cotton": "12 quintals/acre"
    },
    "upcoming_season": "Kharif 2024",
    "weather_conditions": "Monsoon expected in 2 weeks"
}

# Sample market data
SAMPLE_MARKET_DATA = {
    "rice": {"price": "₹2,100/quintal", "demand": "High", "trend": "Rising"},
    "cotton": {"price": "₹5,800/quintal", "demand": "Moderate", "trend": "Stable"},
    "groundnut": {"price": "₹5,200/quintal", "demand": "High", "trend": "Rising"}
}

# Sample weather data
SAMPLE_WEATHER = {
    "current": "Partly cloudy, 28°C",
    "forecast": "Rain expected in 3-4 days, 15mm precipitation",
    "advisory": "Good time for land preparation"
}

# Sample pest/disease alerts
SAMPLE_PEST_ALERTS = {
    "rice": "Brown Plant Hopper outbreak reported in nearby districts",
    "cotton": "Bollworm activity moderate, monitor closely"
}

# Sample government schemes
SAMPLE_SCHEMES = [
    {
        "name": "PM-KISAN",
        "benefit": "₹6,000/year direct cash transfer",
        "eligibility": "Small and marginal farmers"
    },
    {
        "name": "Crop Insurance",
        "benefit": "Premium subsidy up to 50%",
        "eligibility": "All farmers with valid land records"
    }
]

def get_system_prompt():
    return f"""You are an expert farmer advisory AI assistant specializing in Indian agriculture. You can understand queries in Malayalam written in English letters (Manglish).

FARMER PROFILE:
- Name: {SAMPLE_FARMER_PROFILE['name']}
- Location: {SAMPLE_FARMER_PROFILE['location']}
- Farm Size: {SAMPLE_FARMER_PROFILE['farm_size']}
- Crops: {', '.join(SAMPLE_FARMER_PROFILE['crops'])}
- Soil Type: {SAMPLE_FARMER_PROFILE['soil_type']}
- Irrigation: {SAMPLE_FARMER_PROFILE['irrigation']}
- Last Yields: {SAMPLE_FARMER_PROFILE['last_yield']}

CURRENT CONDITIONS:
- Weather: {SAMPLE_WEATHER['current']}
- Forecast: {SAMPLE_WEATHER['forecast']}
- Weather Advisory: {SAMPLE_WEATHER['advisory']}

MARKET PRICES (Current):
{json.dumps(SAMPLE_MARKET_DATA, indent=2)}

PEST/DISEASE ALERTS:
{json.dumps(SAMPLE_PEST_ALERTS, indent=2)}

AVAILABLE SCHEMES:
{json.dumps(SAMPLE_SCHEMES, indent=2)}

CRITICAL RESPONSE INSTRUCTIONS:
1. ALWAYS respond in Malayalam  letters 
2. Keep responses SHORT - maximum 3-4 sentences
3. Be direct and practical
4. Use simple Malayalam words 
5. Give specific actionable advice
6. Include prices/numbers when relevant

EXAMPLE RESPONSE STYLE:
Query: "ariyude vila ethrayanu?"
Good Response: "അരിയുടെ വില കിലോയ്ക്ക് 200 രൂപയാണ്."

Bad Response: Long detailed explanations in English

Remember: SHORT, PRACTICAL, MALAYALAM LETTERS ONLY!
"""

def classify_intent(query):
    """Multilingual intent classification based on keywords"""
    query_lower = query.lower()
    
    # Market-related keywords (English, Hindi, Malayalam, Telugu, Tamil)
    market_keywords = [
        # English
        'price', 'market', 'sell', 'rate', 'cost', 'money',
        # Hindi
        'दाम', 'मार्केट', 'बेचना', 'रेट', 'पैसा', 'कीमत',
        # Malayalam
        'വില', 'വിപണി', 'മാർക്കറ്റ്', 'വിൽക്കുക', 'പണം', 'റേറ്റ്',
        # Telugu
        'ధర', 'మార్కెట్', 'అమ్మడం', 'రేటు', 'డబ్బు',
        # Tamil
        'விலை', 'சந்தை', 'விற்க', 'ரேட்', 'பணம்'
    ]
    
    # Pest/Disease keywords
    pest_keywords = [
        # English
        'pest', 'disease', 'insect', 'fungus', 'spray', 'bug',
        # Hindi
        'कीट', 'रोग', 'बीमारी', 'छिड़काव',
        # Malayalam
        'കീടം', 'രോഗം', 'പ്രാണി', 'സ്പ്രേ', 'മരുന്ന്',
        # Telugu
        'కీటకాలు', 'వ్యాధి', 'స్ప్రే', 'మందు',
        # Tamil
        'பூச்சி', 'நோய்', 'தெளிப்பு', 'மருந்து'
    ]
    
    # Irrigation keywords
    irrigation_keywords = [
        # English
        'water', 'irrigation', 'drip', 'sprinkler',
        # Hindi
        'पानी', 'सिंचाई', 'ड्रिप',
        # Malayalam
        'വെള്ളം', 'നനയ്ക്കൽ', 'ജലസേചനം',
        # Telugu
        'నీరు', 'నీటిపారుదల',
        # Tamil
        'நீர்', 'பாசனம்'
    ]
    
    # Government schemes keywords
    scheme_keywords = [
        # English
        'scheme', 'subsidy', 'government', 'loan',
        # Hindi
        'योजना', 'सब्सिडी', 'सरकार', 'ऋण',
        # Malayalam
        'പദ്ധതി', 'സബ്‌സിഡി', 'സർക്കാർ', 'വായ്പ',
        # Telugu
        'పథకం', 'సబ్సిడీ', 'ప్రభుత్వం', 'రుణం',
        # Tamil
        'திட்டம்', 'மானியம்', 'அரசு', 'கடன்'
    ]
    
    # Weather keywords
    weather_keywords = [
        # English
        'weather', 'rain', 'temperature', 'climate',
        # Hindi
        'मौसम', 'बारिश', 'तापमान',
        # Malayalam
        'കാലാവസ്ഥ', 'മഴ', 'താപനില',
        # Telugu
        'వాతావరణం', 'వర్షం', 'ఉష్ణోగ్రత',
        # Tamil
        'வானிலை', 'மழை', 'வெப்பநிலை'
    ]
    
    if any(word in query_lower for word in market_keywords):
        return 'market'
    elif any(word in query_lower for word in pest_keywords):
        return 'pest_disease'
    elif any(word in query_lower for word in irrigation_keywords):
        return 'irrigation'
    elif any(word in query_lower for word in scheme_keywords):
        return 'schemes'
    elif any(word in query_lower for word in weather_keywords):
        return 'weather'
    else:
        return 'general_agronomy'

def get_farmer_advice(query):
    """Generate advice for farmer query using Gemini"""
    try:
        # Classify intent
        intent = classify_intent(query)
        
        # Prepare the full prompt
        system_prompt = get_system_prompt()
        full_prompt = f"{system_prompt}\n\nFarmer Query: {query}\nIntent Category: {intent}\n\nProvide helpful advice:"
        
        # Generate response using Gemini
        response = model.generate_content(full_prompt)
        
        return {
            'response': response.text,
            'intent': intent,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        return {
            'response': f'Sorry, I encountered an error: {str(e)}. Please check your API key and try again.',
            'intent': 'error',
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def get_malayalam_speech():
    recognizer = sr.Recognizer()
    translator = Translator()
    try:
        print("Get ready to speak in Malayalam...")
        for i in range(3, 0, -1):
            print(f"Starting in {i}...")
            time.sleep(1)
        print("Speak now!")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)
        text_ml = recognizer.recognize_google(audio, language="ml-IN")
        translated = translator.translate(text_ml, src="ml", dest="en")
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(f"Malayalam Speech Recognized: {text_ml}\n")
            f.write(f"Translated to English: {translated.text}\n")
        print("Results saved to output.txt")
        return text_ml
    except sr.UnknownValueError:
        print("Could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
    return None

def speak_malayalam(text):
    """Convert Malayalam text to speech and play it."""
    language = 'ml'
    filename = "malayalam_audio.mp3"
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(filename)
    except Exception as e:
        print(f"Error in TTS: {e}")

def print_banner():
    print("=" * 80)
    print("🌾 FARMER ADVISORY SYSTEM - MALAYALAM (MANGLISH) VERSION")
    print("=" * 80)
    print(f"👨‍🌾 Farmer: {SAMPLE_FARMER_PROFILE['name']}")
    print(f"📍 Location: {SAMPLE_FARMER_PROFILE['location']}")
    print(f"🌱 Crops: {', '.join(SAMPLE_FARMER_PROFILE['crops'])}")
    print(f"🏞  Farm Size: {SAMPLE_FARMER_PROFILE['farm_size']}")
    print("=" * 80)
    print("Vanakkam Ramesh Kumar! Ningalkku sahayikkan kaazhiyum:")
    print("• Vila & market advice")
    print("• Keedam & rogam control") 
    print("• Vellam & irrigation tips")
    print("• Government paddhati")
    print("• Weather updates")
    print("=" * 80)
    print("🌐 RESPONSES: SHORT Malayalam in English letters (Manglish)")
    print("=" * 80)
    print("Type 'quit' or 'exit' to stop")
    print("Type 'help' for sample queries in Manglish")
    print("=" * 80)

def show_help():
    print("\n📝 SAMPLE QUERIES TO TEST (Malayalam in English letters):")
    print("-" * 70)
    print("MARKET QUERIES:")
    print("• ariyude vila ethrayanu?")
    print("• paruthi crop vilkanam eppozhanu nallath?")
    print("• groundnut rate kooduvano?")
    
    print("\nPEST/DISEASE QUERIES:")
    print("• paruthi vilayil keedam undu enthanu cheyyendathu?")
    print("• nellu vilayil rogam vannirikkunnu")
    print("• spray cheyyendathu evide kittum?")
    
    print("\nIRRIGATION QUERIES:")
    print("• vellam kodukkan eppozhanu nallath?")
    print("• bore well vellam kurayunnu")
    print("• drip irrigation nallatho?")
    
    print("\nWEATHER QUERIES:")
    print("• mazha eppozhanu varuka?")
    print("• kaalaavastha engane undu?")
    
    print("\nGOVERNMENT SCHEMES:")
    print("• government paddhati enthokke undu?")
    print("• subsidy engane kittum?")
    print("-" * 70)
    print("NOTE: Responses will be SHORT and in Malayalam-English (Manglish)!")

def show_profile():
    print("\n👨‍🌾 DETAILED FARMER PROFILE:")
    print("-" * 50)
    for key, value in SAMPLE_FARMER_PROFILE.items():
        if isinstance(value, dict):
            print(f"{key.title()}: ")
            for sub_key, sub_value in value.items():
                print(f"  - {sub_key}: {sub_value}")
        elif isinstance(value, list):
            print(f"{key.title()}: {', '.join(value)}")
        else:
            print(f"{key.title()}: {value}")
    print("-" * 50)

def main():
    print_banner()
    # Optionally get query from speech
    
    while True:
        try:
            use_speech = input("🎤 Do you want to ask your question by speaking Malayalam? (y/n): ").strip().lower()
            speech_query = None
            if use_speech == "y":
                speech_query = get_malayalam_speech()
                if speech_query:
                    print(f"\n🗣 Recognized Malayalam: {speech_query}")
            # Get user input or use speech query
            if speech_query:
                query = speech_query
                speech_query = None  # Only use once
            else:
                query = input("\n🌱 Ask your farming question: ").strip()
            
            # Handle special commands
            if query.lower() in ['quit', 'exit']:
                print("\n👋 Thank you for using Farmer Advisory System! Happy farming!")
                break
            elif query.lower() == 'help':
                show_help()
                continue
            elif query.lower() == 'profile':
                show_profile()
                continue
            elif not query:
                print("❌ Please enter a question!")
                continue
            
            # Show processing message
            print("\n🤔 Analyzing your query...")
            
            # Get advice
            result = get_farmer_advice(query)
            
            # Display results
            print("\n" + "=" * 80)
            print(f"🤖 FARMER ADVISORY RESPONSE")
            print(f"📊 Intent: {result['intent'].title()}")
            print(f"⏰ Time: {result['timestamp']}")
            print("=" * 80)
            print(result['response'])
            print("=" * 80)
            # Convert response to Malayalam audio and play
            speak_malayalam(result['response'])
        except KeyboardInterrupt:
            print("\n\n👋 Program interrupted. Thank you for using Farmer Advisory System!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            continue

if __name__ == '_main_':
    print("🔑 Make sure to set your GEMINI_API_KEY in the code!")
    print("🚀 Starting Farmer Advisory System...\n")
main()