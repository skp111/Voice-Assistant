import speech_recognition as sr  # For converting speech to text
import webbrowser  # To open URLs in the default web browser
import pyttsx3  # For converting text to speech
import requests  # For sending HTTP requests (e.g., to fetch news)
import google.generativeai as genai  # To use Google's Gemini AI model
from pytube import Search  # To search YouTube videos

recognizer = sr.Recognizer()  # Create a recognizer object for speech recognition
engine = pyttsx3.init()  # Initialize the text-to-speech engine
newsapi = '{Your news api}'  # News API key for fetching news

def speak(text):  # Function to speak the given text
    engine.setProperty('volume', 1.0)  # Volume: 0.0 to 1.0 (1.0 is max)
    voices = engine.getProperty('voices')  #This line retrieves a list of all available voices
    engine.setProperty('voice', voices[1].id)  # Try 0 for male or 1 for female
    engine.setProperty('rate', 175)  # Adjust speed (words per minute)
    engine.say(text)  # Queue the text for speaking
    engine.runAndWait()  # Process and speak the queued text

def aiProcess(command):  # Function to process user queries using Gemini AI
    genai.configure(api_key='{your gemini api}')  # Set Gemini API key
    model = genai.GenerativeModel(model_name='gemini-2.0-flash')  # Load the Gemini model
    prompt=f'''Please keep the response clear and suitable to be read aloud. 
               Avoid symbols like * or -.") and here is the {command}'''   # Generate content from user query with given promts.
    response = model.generate_content(prompt)   # Generate response using Gemini
    return response.text  # Return the response text

def processCommand(command):  # Function to handle recognized commands
    if "open google" in command.lower():  # If user says "open Google"
        webbrowser.open("https://google.com")  # Open Google in browser
    elif "open facebook" in command.lower():  # If user says "open Facebook"
        webbrowser.open("https://facebook.com")  # Open Facebook in browser
    elif "open youtube" in command.lower():  # If user says "open YouTube"
        webbrowser.open("https://youtube.com")  # Open YouTube in browser
    elif "open linkedin" in command.lower():  # If user says "open LinkedIn"
        webbrowser.open("https://linkedin.com")  # Open LinkedIn in browser

    elif command.lower().startswith("play"):  # If command starts with "play"
        song = command.lower().replace("play ","")  # Extract song name

        if not song:  # If song name is empty
            speak("Please say the name of the song to play.")  # Prompt user
        else:
            speak(f"Searching YouTube for {song}")  # Inform the user
            try:
                search = Search(song)  # Search for the song on YouTube
                results = search.results  # Get the search results
                if results:  # If there are results
                    url = results[0].watch_url  # Get the URL of the first video
                    speak(f"Playing {song} on YouTube.")  # Speak confirmation
                    webbrowser.open(url)  # Open the YouTube video in browser
                else:
                    speak("Sorry, I couldn't find that song on YouTube.")  # No results found
            except Exception as e:  # Catch any errors during search
                print(f"Error while searching for song: {e}")  # Print error
                speak("Something went wrong while searching for the song.")  # Speak error

    elif "news" in command.lower():  # If the command asks for news
        try:
            speak("Fetching the latest news headlines...")  # Inform user
            response = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&pageSize=10&apiKey={newsapi}")  # Call News API
            
            if response.status_code == 200:  # Check if response is OK
                data = response.json()  # Parse the JSON response
                articles = data.get('articles', [])  # Get the list of articles
                
                if not articles:  # If no articles were found
                    speak("Sorry, I couldn't find any news articles.")  # Inform user
                else:
                    speak("Here are the top ten news headlines.")  # Announce news
                    for article in articles[:10]:  # Loop over top 10 articles
                        title = article.get('title')  # Get article title
                        if title:  # If title exists
                            print(f"News: {title}")  # Print title
                            speak(title)  # Speak title
            else:
                print(f"News API error. Status code: {response.status_code}")  # Log error
                speak("Sorry, I couldn't fetch the news right now.")  # Speak error

        except Exception as e:  # Handle API or network errors
            print(f"News fetch error: {e}")  # Log exception
            speak("Something went wrong while fetching the news.")  # Speak error

    else:  # For any other unrecognized command
        try:
            speak("Let me find...")  # Inform user
            output = aiProcess(command)  # Get AI-generated response
            print(f"AI Response: {output}")  # Print the response
            speak(output)  # Speak the response
        except Exception as e:  # Handle Gemini AI errors
            print(f"AI Processing error: {e}")  # Log error
            speak("Sorry, I couldn't process that request.")  # Speak error

if __name__ == "__main__":  # If this file is run directly
    speak("Activating jarvis")  # Greet the user
    
    while True:  # Infinite loop for continuous listening
        try:
            with sr.Microphone() as source:  # Use system microphone
                recognizer.adjust_for_ambient_noise(source, duration=1)  # Cancel out ambient noise
                print("Listening...")  # Display prompt
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)  # Listen for speech
            
            word = recognizer.recognize_google(audio)  # Convert audio to text
            print(f"I said: {word}")  # Print recognized word
            
            if word.lower() == "jarvis":  # If user says "NOVA"
                speak("Yes Sameer, how can I help you?")  # Respond to user
                
                with sr.Microphone() as source:  # Use microphone again
                    print("Listening for your command...")  # Prompt user
                    recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for noise again
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)  # Listen for the actual command
                    command = recognizer.recognize_google(audio)  # Convert audio to text
                    print(f"Command received: {command}")  # Print command
                    processCommand(command)  # Handle the command

        except sr.UnknownValueError:  # If audio couldn't be understood
            print("Could not understand audio.")  # Print error
        except sr.RequestError as e:  # If there's an error with the Google API
            print(f"Google Speech Recognition error: {e}")  # Print API error
        except Exception as e:  # Catch-all for other exceptions
            print(f"Unable to hear!! {e}")  # Print generic error
