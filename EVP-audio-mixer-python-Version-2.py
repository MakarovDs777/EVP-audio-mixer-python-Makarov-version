import tkinter as tk
from tkinter import filedialog
import random
import numpy as np
import pygame
from threading import Thread
from pydub import AudioSegment

def convert_audio_to_segments(path):
    audio = AudioSegment.from_file(path)  # Загружаем аудиофайл
    segments = []
    current_time = 0

    while current_time < len(audio):
        segment_duration_ms = random.randint(100, 1000)  # Случайная длительность от 100 мс до 1000 мс
        segment = audio[current_time:current_time + segment_duration_ms]  # Получаем кусок аудио
        segments.append(segment.raw_data)  # Добавляем сырье в список сегментов
        current_time += segment_duration_ms  # Обновляем текущее время

    return segments, audio.frame_rate  # Возвращаем список сегментов и частоту дискретизации

def mix_audio_segments(segments):
    random.shuffle(segments)  # Перемешиваем сегменты
    return b''.join(segments)  # Соединяем сегменты обратно в один поток байтов

def play_sound(shuffled_audio, sample_rate):
    pygame.mixer.init(frequency=sample_rate, size=-16, channels=1)
    sound = pygame.mixer.Sound(buffer=shuffled_audio)
    sound.play()

def start_audio_mosaic():
    audio_file_path = filedialog.askopenfilename(
        title="Выберите аудио файл", 
        filetypes=[("Audio Files", "*.wav;*.mp3;*.ogg;*.flac")]
    )

    if audio_file_path:
        segments, sample_rate = convert_audio_to_segments(audio_file_path)  # Получаем сегменты состояния
        shuffled_audio = mix_audio_segments(segments)  # Перемешиваем сегменты

        # Запуск воспроизведения перемешанного аудио
        Thread(target=play_sound, args=(shuffled_audio, sample_rate), daemon=True).start()

# Создание графического интерфейса
root = tk.Tk()
root.title("Генератор случайного аудио")

start_button = tk.Button(root, text="Начать", command=start_audio_mosaic)
start_button.pack(pady=20)

# Запустить основной цикл интерфейса
root.mainloop()
