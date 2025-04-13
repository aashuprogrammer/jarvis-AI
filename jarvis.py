import webbrowser
import datetime
import requests
import speech_recognition as sr
import pyttsx3
import time
from bs4 import BeautifulSoup
import wikipedia
import re

class WebAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        try:
            self.engine = pyttsx3.init()
            # Set a slower rate for better understanding
            self.engine.setProperty('rate', 150)
            
            # Get and print all available voices
            voices = self.engine.getProperty('voices')
            print("Available voices:")
            for i, voice in enumerate(voices):
                print(f"Voice {i}: {voice.name}")
            
            # You can change this number to select different voices
            voice_choice = 1  # 0 for David, 1 for Sara
            self.engine.setProperty('voice', voices[voice_choice].id)
            print(f"Using voice: {voices[voice_choice].name}")
            
        except Exception as e:
            print(f"Error initializing speech engine: {e}")
            self.engine = None
            
        self.is_active = True
        print("Web Assistant started!")
        self.speak("Hello! I'm your web assistant. What would you like me to do?")

    def speak(self, text):
        """Function to make the system speak text"""
        print(f"Assistant: {text}")
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Speech error: {e}")

    def listen(self):
        """Function to listen to user's voice"""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"You said: {text}")
                    return text.lower()
                except sr.UnknownValueError:
                    self.speak("I didn't understand, please repeat")
                    return ""
                except sr.RequestError:
                    self.speak("Sorry, I can't listen right now")
                    return ""
        except Exception as e:
            print(f"Error with speech recognition: {e}")
            # Fall back to text input
            text = input("Enter your command: ")
            return text.lower()

    def open_website(self, site):
        """Function to open a website"""
        try:
            # Clean the site string
            site = site.strip().replace(" ", "")
            if "." not in site:
                site = site + ".com"
            if not site.startswith(('http://', 'https://')):
                site = f"https://{site}"
            webbrowser.open(site)
            self.speak(f"Opened {site}")
        except Exception as e:
            self.speak(f"Problem opening website: {e}")

    def close_current_tab(self):
        """Function to attempt to close current tab"""
        self.speak("I'll try to close the current tab")
        try:
            import pyautogui
            pyautogui.hotkey('ctrl', 'w')
            self.speak("Tab closed")
        except Exception as e:
            self.speak("Unable to close tab. You may need to close it manually")
            print(f"Error closing tab: {e}")

    def play_youtube_song(self, song_name):
        """Function to play a song on YouTube"""
        if not song_name:
            self.speak("Please specify a song name")
            return
            
        search_query = song_name.replace(" ", "+") + "+song"
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
        self.speak(f"Searching for {song_name} on YouTube")
        # Wait a bit and then simulate clicking the first video
        time.sleep(3)
        try:
            import pyautogui
            pyautogui.press('enter')
        except Exception as e:
            self.speak("Please click on the video you want to play")
            print(f"Error with auto-play: {e}")

    def google_search(self, query):
        """Function to search on Google"""
        if not query:
            self.speak("Please specify what you want to search for")
            return
            
        search_query = query.replace(" ", "+")
        webbrowser.open(f"https://www.google.com/search?q={search_query}")
        self.speak(f"Searching Google for {query}")

    def get_date_time(self):
        """Function to get current date and time"""
        now = datetime.datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%I:%M %p")
        self.speak(f"Today is {date_str} and the current time is {time_str}")

    def get_weather(self, city=""):
        """Function to get weather information"""
        if not city:
            self.speak("Please specify a city for weather information")
            return
            
        try:
            # Using OpenWeatherMap API with your API key
            API_KEY = "48fb88cb67e1f25b221b3fc1178ed753"
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            
            response = requests.get(url)
            data = response.json()
            
            if data.get("cod") != "404":
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                humidity = data["main"]["humidity"]
                self.speak(f"The temperature in {city} is {temp} degrees Celsius with {desc}. The humidity is {humidity}%.")
            else:
                self.speak("City not found")
                
        except Exception as e:
            # Alternative method if API doesn't work
            self.speak(f"I'm having trouble getting weather data. Opening a weather website for {city} instead.")
            webbrowser.open(f"https://www.weather.com/weather/today/l/{city}")
            print(f"Weather API error: {e}")

    def get_information(self, query):
        """Get information about a topic using Wikipedia"""
        try:
            # Clean up the query
            query = query.replace("what is", "").replace("who is", "").replace("tell me about", "").strip()
            
            # Search Wikipedia
            result = wikipedia.summary(query, sentences=2)
            self.speak(f"According to Wikipedia: {result}")
            
            # Open Wikipedia page for more information
            self.speak("I'm opening the Wikipedia page for more information.")
            wikipedia_url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
            webbrowser.open(wikipedia_url)
            
        except wikipedia.exceptions.DisambiguationError as e:
            options = e.options[:5]  # Limit to 5 options
            options_text = ", ".join(options)
            self.speak(f"There are multiple results for {query}. Some options are: {options_text}")
            
        except wikipedia.exceptions.PageError:
            self.speak(f"I couldn't find information about {query} on Wikipedia.")
            # Fall back to a Google search
            self.speak("Let me search Google for you instead.")
            self.google_search(query)
            
        except Exception as e:
            self.speak(f"I'm having trouble finding information. Let me search Google for you instead.")
            self.google_search(query)
            print(f"Information retrieval error: {e}")

    def get_news(self):
        """Fetch top headlines from a news website using BeautifulSoup"""
        try:
            # BBC News as example (use a site that allows scraping or has an API)
            url = "https://www.bbc.com/news"
            headers = {'User-Agent': 'Mozilla/5.0'}  # To avoid bot detection
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find headline elements (adjust selector based on site structure)
            headlines = soup.find_all('h3', class_=re.compile('gs-c-promo-heading__title'), limit=3)
            
            if headlines:
                self.speak("Here are the top news headlines:")
                for i, headline in enumerate(headlines, 1):
                    title = re.sub(r'\s+', ' ', headline.text.strip())  # Clean text with regex
                    self.speak(f"Headline {i}: {title}")
            else:
                self.speak("I couldn't find any headlines right now.")
                
        except Exception as e:
            self.speak("Sorry, I couldn't fetch the news. Let me search for news instead.")
            self.google_search("latest news")
            print(f"News scraping error: {e}")

    def chat(self, message):
        """Function to respond to basic chat messages and questions"""
        message = message.lower()
        
        # Basic greetings
        if "hello" in message or "hi" in message:
            self.speak("Hello! How can I help you today?")
        
        elif "how are you" in message:
            self.speak("I'm functioning well, thank you for asking!")
            
        elif "your name" in message:
            self.speak("I'm your web assistant, created to help you with web tasks.")
            
        elif "thank" in message:
            self.speak("You're welcome! Is there anything else I can help with?")
            
        elif "bye" in message or "exit" in message or "quit" in message:
            self.speak("Goodbye! Have a great day!")
            self.is_active = False
        
        # Knowledge-based questions
        elif "what is" in message or "who is" in message or "tell me about" in message:
            self.get_information(message)
            
        # JavaScript specific question
        elif "javascript" in message or "java script" in message:
            js_info = "JavaScript is a programming language"
            self.speak(js_info)
            self.speak("Would you like me to search for more information about JavaScript?")
            
        else:
            self.speak("I'm not sure how to respond to that.")
            self.speak("Try again with a different command or question.")

    def process_command(self, command):
        """Process the user's command with regex for better parsing"""
        if not command:
            return
            
        command = command.lower()
        
        # Regex patterns for parsing
        website_pattern = r'open\s+(?:the\s+)?(?:website\s+)?([\w\.-]+)'  # Matches "open google.com", "open the website youtube.com"
        song_pattern = r'play\s+(?:a\s+)?(?:song\s+)?(.+?)(?:\s+on\s+youtube)?$'  # Matches "play despacito", "play a song called shape of you"
        news_pattern = r'(?:get|tell me|what\'?s)\s+(?:the\s+)?news'  # Matches "get news", "what's the news"
        weather_pattern = r'weather\s+(?:in\s+)?(.+)'  # Matches "weather in London", "weather New York"
        search_pattern = r'(?:search|google)\s+(?:for\s+)?(.+)'  # Matches "search for Python", "google Python tutorials"
        
        # News command
        if re.search(news_pattern, command):
            self.get_news()
            return
        
        # Website command
        website_match = re.search(website_pattern, command)
        if website_match:
            site = website_match.group(1).strip()
            self.open_website(site)
            return
            
        # YouTube song command
        song_match = re.search(song_pattern, command)
        if song_match:
            song = song_match.group(1).strip()
            self.speak(f"Playing {song} on YouTube")
            self.play_youtube_song(song)
            return
        
        # Weather command
        weather_match = re.search(weather_pattern, command)
        if weather_match:
            city = weather_match.group(1).strip()
            self.get_weather(city)
            return
        
        # Search command
        search_match = re.search(search_pattern, command)
        if search_match:
            query = re.sub(r'\s+', ' ', search_match.group(1).strip())  # Clean extra spaces
            self.google_search(query)
            return
        
        # Other existing commands
        if "close" in command and ("website" in command or "tab" in command or "page" in command):
            self.close_current_tab()
            return
        
        if any(word in command for word in ["date", "time", "day", "today"]):
            self.get_date_time()
            return
        
        if any(phrase in command for phrase in ["what is", "who is", "tell me about"]):
            self.get_information(command)
            return
        
        # Default to chat
        self.chat(command)

    def run(self):
        """Main function to run the assistant"""
        try:
            while self.is_active:
                command = self.listen()
                self.process_command(command)
        except KeyboardInterrupt:
            print("\nStopping the assistant...")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            print("Web Assistant has been stopped.")


if __name__ == "__main__":
    try:
        # First make sure we have the wikipedia package
        try:
            import wikipedia
        except ImportError:
            print("Installing wikipedia package...")
            import pip
            pip._internal.main(['install', 'wikipedia'])
            import wikipedia
            
        # Create and run the assistant
        assistant = WebAssistant()
        assistant.run()
    except Exception as e:
        print(f"Failed to start the assistant: {e}")
        input("Press Enter to exit...")