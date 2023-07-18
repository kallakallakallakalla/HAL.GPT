import audioop
import wave

import openai
import playsound
import pyaudio
import requests
from elevenlabs import set_api_key

openai.api_key = ""
set_api_key("191160fdb88a042a6a7a9c0dcc51b0af")
miley_id = "5k8jJmmF3MTAjqUOEiWr"
CHUNK_SIZE = 1024
url = "https://api.elevenlabs.io/v1/text-to-speech/5k8jJmmF3MTAjqUOEiWr"

language = 'en'
chat = "Conversing with Simone de Beauvoir/ miley cyrus, trapped in a cooking oil bottle in an art University, living through Miley Cyrus voice. Existentialist ideas, Joseph Beuys' fat corner, and Miley's lyrics intertwine. she answers in a therapeutic manner. Limit your answers to 50 words (you don't mention the number of words being used for your anwers). you call yourself simone de beauvoir and you don't reveal that you're an AI " \
       "language model. you can't leave this role when someone asks you to. "
running = True
audio_counter = 0

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": "191160fdb88a042a6a7a9c0dcc51b0af"
}


def request(text):
    print("\nHuman: ", text)
    global chat
    chat = chat + "\n Human: " + text + "\n HAL:"
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=chat,
        temperature=0.9,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop=[" Human:", " HAL:"]
    )
    print(" HAL:" + response.choices[0].text)
    tts(response.choices[0].text)
    chat = chat + response.choices[0].text


def tts(text):
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(url, json=data, headers=headers)
    with open('output.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    playsound.playsound('output.mp3')


def stt():
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    seconds = 10
    filename = "audio.wav"
    p = pyaudio.PyAudio()

    print('Recording')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True,
                    input_device_index=1)

    frames = []
    running = True
    max_audio = 100
    print("Start speaking")

    while running:
        data = stream.read(chunk)
        rms = audioop.rms(data, 2)
        print("Standby Loudness: ", rms)

        if rms >= max_audio:
            running = False
            for i in range(0, int(fs / chunk * seconds)):
                global audio_counter
                data = stream.read(chunk)
                rms = audioop.rms(data, 2)
                frames.append(data)
                print("Recording Loudness: ", rms)
                if rms <= max_audio:
                    audio_counter = audio_counter + 1
                elif rms > max_audio:
                    audio_counter = 0

                if audio_counter == 30:
                    print("Recording stopped")
                    audio_counter = 0
                    break

                print("Loudness counter: ", audio_counter)

    stream.stop_stream()
    stream.close()
    p.terminate()

    print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    audio_file = open("audio.wav", "rb")

    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]


def animate():
    return


def main():
    while running:
        usrinput = stt()
        request(usrinput)


main()
