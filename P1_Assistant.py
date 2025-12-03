import speech_recognition as sr
import pyttsx3
import datetime
import pyjokes
import requests
import pywhatkit
import wikipedia
import threading
import time
import re
import webbrowser

# -------------------------------
# Initialize speech engine
# -------------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 200)
engine.setProperty('volume', 1)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # 0 = male, 1 = female

# -------------------------------
# Helper Functions
# -------------------------------
def talk(text):
    """Speak the text aloud"""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def take_command():
    """Listen to user voice and return text"""
    listener = sr.Recognizer()
    command = ""
    try:
        with sr.Microphone() as source:
            print("\nListening...")
            listener.pause_threshold = 1.2
            voice = listener.listen(source, timeout=5, phrase_time_limit=10)
            command = listener.recognize_google(voice)
            command = command.lower()
            print(f"You said: {command}\n")
    except sr.WaitTimeoutError:
        talk("I didn't hear anything.")
    except sr.UnknownValueError:
        talk("Sorry, I didn't catch that.")
    except sr.RequestError:
        talk("Network error, please check your connection.")
    return command

# -------------------------------
# Feature Functions
# -------------------------------
def get_time():
    return datetime.datetime.now().strftime("It’s %I:%M %p.")

def tell_joke():
    return pyjokes.get_joke()

def get_weather(city="Bangalore"):
    api_key = "44f76144b1872671abc60ba1bb3e00fc"  # Replace with your key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url).json()
        if response.get("cod") != 200:
            return "Sorry, I couldn’t fetch the weather right now."
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        return f"It’s {temp}°C with {desc} in {city}."
    except:
        return "Network issue while fetching weather."

def get_news():
    api_key = "6df3de5dde784bc599e2f6d042db9c65"  # Replace with your key
    url = f"https://newsapi.org/v2/everything?q=technology&language=en&apiKey={api_key}"
    try:
        response = requests.get(url).json()
        articles = response.get("articles", [])[:3]

        if not articles:
            talk("Sorry, I couldn’t find any news right now.")
            return

        talk("Here are the latest headlines:")

        for i, article in enumerate(articles, start=1):
            title = article.get("title")
            if title:
                talk(f"Headline {i}: {title}")
                time.sleep(0.5)

    except Exception as e:
        print("News fetch error:", e)
        talk("There was a problem fetching the news.")

def play_youtube(song):
    pywhatkit.playonyt(song)
    talk(f"Playing {song} on YouTube.")

def reminder_task(msg, delay):
    time.sleep(delay)
    talk(f"Reminder: {msg}")

def set_reminder(task, minutes):
    delay = minutes * 60
    threading.Thread(target=reminder_task, args=(task, delay)).start()
    talk(f"Reminder set for {task} in {minutes} minutes.")

def define_term(term):
    try:
        summary = wikipedia.summary(term, sentences=2)
        return summary
    except:
        return f"Sorry, I couldn’t find information about {term}."

def open_website(url, name="website"):
    talk(f"Opening {name}...")
    webbrowser.open(url)


def close_assistant():
    try:
        talk("Goodbye! Have a great day!")
        time.sleep(0.5)  # Let speech finish
        engine.stop()    # Stop engine safely
    except Exception:
        pass
    finally:
        exit()

# -------------------------------
# Command Processing
# -------------------------------
def run_assistant():
    command = take_command()
    if not command:
        return

    # Time
    if "time" in command:
        talk(get_time())

    # Joke
    elif "joke" in command:
        talk(tell_joke())

    # Weather
    elif "weather" in command:
        city = "Bangalore"
        match = re.search(r"in (.+)", command)
        if match:
            city = match.group(1)
        talk(get_weather(city))

    # News
    elif "news" in command:
        get_news()

    # YouTube
    elif "open youtube and play" in command:
        song = command.replace("open youtube and play", "").strip()
        play_youtube(song)
    elif "open youtube" in command:
        open_website("https://www.youtube.com", "YouTube")
    elif "play" in command:
        song = command.replace("play", "").strip()
        play_youtube(song)

    # Reminders
    elif "remind" in command:
        talk("What should I remind you about?")
        task = take_command()
        talk("After how many minutes?")
        try:
            minutes = int(re.findall(r"\d+", take_command())[0])
            set_reminder(task, minutes)
        except:
            talk("Sorry, I did not understand the duration.")

    # Wikipedia Definitions
    elif "define" in command:
        term = command.replace("define", "").strip()
        talk(define_term(term))

    # Open websites
    elif "open google" in command:
        open_website("https://www.google.com", "Google")
    elif "open gmail" in command:
        open_website("https://mail.google.com", "Gmail")

    # Stop/Exit
    elif "stop" in command or "exit" in command:
        close_assistant()

    # Default
    else:
        talk("I’m not sure how to help with that yet.")

# -------------------------------
# Run Assistant
# -------------------------------
if __name__ == "__main__":
    talk("Hello! I am your personal voice assistant. How can I help you today?")
    while True:
        run_assistant()


