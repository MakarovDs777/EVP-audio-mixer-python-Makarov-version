import tkinter as tk
from tkinter import filedialog, messagebox
import random
import numpy as np
import pygame
from threading import Thread
import time
from pydub import AudioSegment

# Глобальный список выбранных аудио
selected_audios = []

class AudioMosaic:
    def __init__(self):
        self.segments = []
        self.sample_rate = 0
        self.is_playing = False
        self.thread = None
        pygame.mixer.init()

    def convert_audio_to_segments(self, path):
        audio = AudioSegment.from_file(path)
        self.segments = []
        current_time = 0
        while current_time < len(audio):
            segment_duration_ms = random.randint(100, 1000)
            segment = audio[current_time:current_time + segment_duration_ms]
            self.segments.append(segment.raw_data)
            current_time += segment_duration_ms
        self.sample_rate = audio.frame_rate

    def mix_audio_segments(self):
        random.shuffle(self.segments)
        return b''.join(self.segments)

    def play_audio(self):
        self.is_playing = True
        while self.is_playing:
            shuffled_audio = self.mix_audio_segments()
            sound_array = np.frombuffer(shuffled_audio, dtype=np.int16)
            sound = pygame.mixer.Sound(buffer=sound_array)
            sound.play()
            duration = len(shuffled_audio) / (self.sample_rate * 2)  # 2 байта на сэмпл
            time.sleep(duration)

    def start_playback(self):
        if not self.is_playing:
            self.thread = Thread(target=self.play_audio, daemon=True)
            self.thread.start()

    def stop_audio(self):
        self.is_playing = False
        pygame.mixer.stop()

# Создаем главное окно
root = tk.Tk()
root.title("Генератор случайного аудио")
root.geometry("400x350")  # Размер окна

audio_mosaic = AudioMosaic()

# --- Область для отображения выбранных аудио ---
frame_listbox = tk.Frame(root)
frame_listbox.pack(pady=10)

listbox = tk.Listbox(frame_listbox, width=50, height=8)
listbox.pack(side=tk.LEFT, padx=5)

scrollbar = tk.Scrollbar(frame_listbox, orient=tk.VERTICAL)
scrollbar.config(command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox.config(yscrollcommand=scrollbar.set)

# --- Функция выбора файла ---
def select_audio():
    global selected_audios
    file_path = filedialog.askopenfilename(
        title="Выберите аудио файл",
        filetypes=[("Audio Files", "*.wav;*.mp3;*.ogg;*.flac")]
    )
    if file_path:
        selected_audios.append(file_path)
        listbox.insert(tk.END, file_path)

# --- Кнопки управления воспроизведением ---
def start_audio():
    global selected_audios
    if not selected_audios:
        messagebox.showwarning("Предупреждение", "Пожалуйста, выберите аудиофайлы.")
        return
    # Загружаем сегменты для первого файла (или можно расширить)
    audio_mosaic.convert_audio_to_segments(selected_audios[0])
    audio_mosaic.start_playback()

def stop_audio():
    global selected_audios
    audio_mosaic.stop_audio()

# --- Кнопки ---
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="Старт", command=start_audio)
start_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(button_frame, text="Стоп", command=stop_audio)
stop_button.pack(side=tk.LEFT, padx=10)

# --- Кнопка выбора файла ---
select_button = tk.Button(root, text="Выбрать аудио", command=select_audio)
select_button.pack(pady=5)

# Запуск интерфейса
root.mainloop()
