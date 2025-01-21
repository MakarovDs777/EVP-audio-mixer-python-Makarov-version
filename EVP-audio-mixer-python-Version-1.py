import tkinter as tk
from tkinter import filedialog
import random
import numpy as np
import pygame
from threading import Thread
import time
from pydub import AudioSegment

class AudioMosaic:
    def __init__(self):
        self.segments = []
        self.sample_rate = 0
        self.is_playing = False
        pygame.mixer.init()  # Инициализация pygame mixer при создании объекта

    def convert_audio_to_segments(self, path, segment_duration_ms=500):  # Фиксированная длительность 500 мс
        audio = AudioSegment.from_file(path)  # Загружаем аудиофайл
        self.segments = []
        current_time = 0

        while current_time < len(audio):
            segment = audio[current_time:current_time + segment_duration_ms]  # Получаем кусок аудио
            self.segments.append(segment.raw_data)  # Добавляем сырье в список сегментов
            current_time += segment_duration_ms  # Обновляем текущее время
        
        self.sample_rate = audio.frame_rate  # Сохраняем частоту дискретизации

    def mix_audio_segments(self):
        random.shuffle(self.segments)  # Перемешиваем сегменты
        return b''.join(self.segments)  # Соединяем сегменты обратно в один поток байтов

    def play_audio(self):
        self.is_playing = True
        while self.is_playing:
            shuffled_audio = self.mix_audio_segments()  # Перемешиваем аудио каждый раз
            
            # Преобразование байтов в массив NumPy и создание звука
            sound_array = np.frombuffer(shuffled_audio, dtype=np.int16)
            pygame.mixer.Sound(buffer=sound_array).play()

            # Даем время на воспроизведение сегментов
            time.sleep(len(shuffled_audio) / (self.sample_rate * 2))  # Подсчет времени в секунды

    def stop_audio(self):
        self.is_playing = False  # Устанавливаем флаг в False
        pygame.mixer.stop()  # Останавливаем воспроизведение музыки

def start_audio_mosaic(audio_mosaic):
    audio_file_path = filedialog.askopenfilename(
        title="Выберите аудио файл", 
        filetypes=[("Audio Files", "*.wav;*.mp3;*.ogg;*.flac")]
    )

    if audio_file_path:
        audio_mosaic.convert_audio_to_segments(audio_file_path)  # Получаем сегменты состояния
        Thread(target=audio_mosaic.play_audio, daemon=True).start()  # Запуск воспроизведения перемешанного аудио

# Создание графического интерфейса
root = tk.Tk()
root.title("Генератор случайного аудио")
root.geometry("320x120")  # Установка размера окна

audio_mosaic = AudioMosaic()

start_button = tk.Button(root, text="Начать", command=lambda: start_audio_mosaic(audio_mosaic))
start_button.pack(pady=20)

stop_button = tk.Button(root, text="Стоп", command=audio_mosaic.stop_audio)
stop_button.pack(pady=10)

# Запустить основной цикл интерфейса
root.mainloop()
