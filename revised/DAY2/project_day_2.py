from openai import OpenAI, chat
from dotenv import load_dotenv
import sounddevice as sd
import scipy.io.wavfile as wav
from pathlib import Path
# from playsound import playsound
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def record_audio(filename="user.wav", duration=5, sample_rate=16000, device=1):
    print("Silahkan Tuan Berbicara... (5 detik)")
    
    sd.default.device = (device, None)  # Set input device
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='int16'
    )
    sd.wait()
    wav.write(filename, sample_rate, audio)
    print("Perekaman suara tuan Selesai.\n")
    return filename

def speech_to_text(audio_path):
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text"
        )
    print("Tuan Berkata:", result)
    return str(result)

def ask_ai(user_text, chat_history):
    chat_history.append({"role": "user", "content": user_text})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=chat_history,
        temperature=0.7,
    )
    
    ai_text = response.choices[0].message.content
    print("Toe-Yul:", ai_text, "\n")
    
    chat_history.append({"role": "assistant", "content": ai_text})
    return ai_text, chat_history

def text_to_speech(text, out_file="output/toeyul.mp3"):
    out_file = Path(out_file)
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
    ) as response:
        response.stream_to_file(out_file)
    
    print("Memutar suara Toe-Yul...")
    abs_path = os.path.abspath(out_file)
    os.startfile(abs_path)

def main():
    print("Toe-Yul Voice Assistant")
    print("Ucapkan 'Keluar' untuk mengakhiri percakapan.\n")
    
    chat_history = [
        {"role": "system", "content": "Anda adalah Toe-Yul, asisten suara yang berbicara dengan penuh kesopanan dan ramah dalam bahasa Indonesia."},
    ]
    
    while True:
        audio_input = record_audio(duration=5)
        user_text = speech_to_text(audio_input).strip().lower()
        
        if user_text == 'keluar':
            print("Terima kasih telah menggunakan hamba Tuan. Senang bisa membantu.")
            break
        
        ai_text, chat_history = ask_ai(user_text, chat_history)
        text_to_speech(ai_text)

if __name__ == "__main__":
    main()