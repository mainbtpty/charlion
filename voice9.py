import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from bark import SAMPLE_RATE, generate_audio, preload_models
import numpy as np
from scipy.io.wavfile import write as write_wav
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showwarning
from playsound import playsound
import nltk
from nltk.tokenize import sent_tokenize
from transformers import AutoProcessor, BarkModel

# Download NLTK data (you need to run this line only once)
nltk.download('punkt')

# Function to convert text to speech using bark
def convert_to_speech():
    text = text_entry.get("1.0", "end-1c")  # Get text from the text box
    selected_voice = voice_combobox.get()  # Get the selected voice from the dropdown
    if not selected_voice:
        selected_voice = "v2/en_speaker_3"  # Use "v2/en_speaker_3" as the default if no option is selected
    if text:
        progress_bar["value"] = 0  # Reset progress  bar
        root.update()  # Update the main window to display the progress bar

        # Split the text into sentences using NLTK
        sentences = sent_tokenize(text)

        audio_chunks = []
        max_length = 0
        total_chunks = len(sentences)

        for i, sentence in enumerate(sentences):
            # Generate audio for the sentence using the selected voice
            audio_chunk = generate_audio(sentence, history_prompt=selected_voice)
            audio_chunks.append(audio_chunk)

            if len(audio_chunk) > max_length:
                max_length = len(audio_chunk)

            progress_bar["value"] = (i + 1) / total_chunks * 100
            percentage_label.config(text=f"{int(progress_bar['value'])}%")
            root.update()

        # Zero-pad shorter audio chunks to the length of the longest chunk
        for i in range(len(audio_chunks)):
            audio_chunk = audio_chunks[i]
            if len(audio_chunk) < max_length:
                padding = max_length - len(audio_chunk)
                audio_chunks[i] = np.pad(audio_chunk, (0, padding), mode='constant')

        # Concatenate the audio chunks
        audio_array = np.concatenate(audio_chunks)

        # Save audio to a WAV file
        file_path = asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if file_path:
            write_wav(file_path, SAMPLE_RATE, audio_array)

        play_button.config(state=tk.NORMAL)
        progress_bar["value"] = 100  # Set progress bar to completion
        percentage_label.config(text="100%")

    else:
        showwarning("Error", "Please enter text to convert.")

# Function to play the generated audio
def play_audio():
    text = text_entry.get("1.0", "end-1c")
    sentences = sent_tokenize(text)
    audio_chunks = []

    for sentence in sentences:
        audio_chunk = generate_audio(sentence, history_prompt=voice_combobox.get())
        audio_chunks.append(audio_chunk)

    audio_array = np.concatenate(audio_chunks)

    # Save audio to a temporary WAV file
    temp_audio_path = "temp.wav"
    write_wav(temp_audio_path, SAMPLE_RATE, audio_array)

    playsound(temp_audio_path)

# Create the main window
root = tk.Tk()
root.title("Text-to-Speech with CharlionAI")

# Create a label for the "Select Voice" dropdown
voice_label = ttk.Label(root, text="Select Voice")
voice_label.grid(row=0, column=0, padx=10, pady=10)

# Create the "Select Voice" dropdown
voice_combobox = ttk.Combobox(root, values=['v2/en_speaker_0','v2/en_speaker_1', 'v2/en_speaker_2', 'v2/en_speaker_3', 'v2/en_speaker_4', 'v2/en_speaker_5', 'v2/en_speaker_6', 'v2/en_speaker_7', 'v2/en_speaker_8', 'v2/en_speaker_9'])
voice_combobox.grid(row=1, column=0, padx=10, pady=10)

# Set the default value for the dropdown
voice_combobox.set('v2/en_speaker_3')

# Create and configure the text box
text_entry = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=15)
text_entry.grid(row=2, column=0, padx=10, pady=10, columnspan=2)

# Create the "Convert" button
convert_button = ttk.Button(root, text="Convert to Speech", command=convert_to_speech)
convert_button.grid(row=3, column=0, padx=10, pady=10)

# Create a label for the progress bar
progress_bar_label = ttk.Label(root, text="Conversion Progress")
progress_bar_label.grid(row=4, column=0, padx=10)

# Create the progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=5, column=0, padx=10, pady=10)

# Create the percentage label
percentage_label = ttk.Label(root, text="0%")
percentage_label.grid(row=6, column=0, padx=10)

# Create the "Play" button
play_button = ttk.Button(root, text="Play", state=tk.DISABLED, command=play_audio)
play_button.grid(row=7, column=0, padx=10, pady=10)

# Function to quit the application
def quit_app():
    root.destroy()

# Create the "Quit" button
quit_button = ttk.Button(root, text="Quit", command=quit_app)
quit_button.grid(row=8, column=0, padx=10, pady=10)

# Start the main loop
root.mainloop()
