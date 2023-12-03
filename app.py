from flask import Flask, render_template, request, send_from_directory, flash
from bark import SAMPLE_RATE, generate_audio, preload_models
import numpy as np
from scipy.io.wavfile import write as write_wav
from nltk import sent_tokenize
import os
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Set a secret key for session management
app.secret_key = 'b#y2L"F4Q8z\n\xec]/'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/convert_to_speech', methods=['POST'])
def convert_to_speech():
    text = request.form.get('text')
    selected_voice = request.form.get('voice')

    if not selected_voice:
        selected_voice = "v2/en_speaker_3"

    print(f"Selected Voice: {selected_voice}")

    if text:
        try:
            # Split the text into sentences using NLTK
            sentences = sent_tokenize(text)

            audio_chunks = []
            max_length = 0

            for i, sentence in enumerate(sentences):
                # Generate audio for the sentence using the selected voice
                audio_chunk = generate_audio(sentence, history_prompt=selected_voice)
                audio_chunks.append(audio_chunk)

                if len(audio_chunk) > max_length:
                    max_length = len(audio_chunk)

            # Zero-pad shorter audio chunks to the length of the longest chunk
            for i in range(len(audio_chunks)):
                audio_chunk = audio_chunks[i]
                if len(audio_chunk) < max_length:
                    padding = max_length - len(audio_chunk)
                    audio_chunks[i] = np.pad(audio_chunk, (0, padding), mode='constant')

            # Concatenate the audio chunks
            audio_array = np.concatenate(audio_chunks)

            # Save audio to a temporary WAV file
            temp_audio_path = os.path.join('/tmp', "temp.wav")
            write_wav(temp_audio_path, SAMPLE_RATE, audio_array)

            # Set the audio path to be used in the template
            audio_path = f'/audio/{os.path.basename(temp_audio_path)}'

            return render_template('home.html', audio_path=audio_path)

        except Exception as e:
            flash(f"Error: {e}")
            logging.exception("Error during audio generation:")

    return render_template('home.html')


# Serve audio files directly
@app.route('/audio/<filename>')
def audio(filename):
    return send_from_directory('/tmp', filename)

# Run the app
if __name__ == '__main__':
    app.run()
