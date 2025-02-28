import os
from flask import Flask, render_template, request, send_file
import yt_dlp
import whisper
from googletrans import Translator
from gtts import gTTS
import ffmpeg

app = Flask(__name__)

# Ensure output directory exists
os.makedirs("static", exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["youtube_url"]
        
        try:
            # Download YouTube video and audio using yt-dlp
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'static/audio.%(ext)s',  # Save audio in static folder
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                audio_path = f"static/audio.{info_dict['ext']}"  # Get the downloaded audio file path

            # Transcribe audio using OpenAI Whisper
            model = whisper.load_model("small")
            result = model.transcribe(audio_path)
            original_text = result["text"]

            # Translate text to English
            translator = Translator()
            translated_text = translator.translate(original_text, src='auto', dest='en').text

            # Convert to English speech
            tts = gTTS(translated_text, lang="en")
            voiceover_path = "static/voiceover.mp3"
            tts.save(voiceover_path)

            return render_template("index.html", voiceover=voiceover_path, transcription=translated_text)

        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")

@app.route("/download")
def download():
    return send_file("static/voiceover.mp3", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

