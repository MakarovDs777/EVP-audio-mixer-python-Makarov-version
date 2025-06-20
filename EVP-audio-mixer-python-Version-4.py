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
        segments = []
        current_time = 0
        while current_time < len(audio):
            segment_duration_ms = random.randint(100, 1000)
            segment = audio[current_time:current_time + segment_duration_ms]
            segments.append(segment.raw_data)
            current_time += segment_duration_ms
        return segments, audio.frame_rate

    def prepare_segments(self, files):
        all_segments = []
        sample_rate = 0
        for file in files:
            segments, rate = self.convert_audio_to_segments(file)
            all_segments.extend(segments)
            sample_rate = rate
        self.segments = all_segments
        self.sample_rate = sample_rate

    def mix_audio_segments(self):
        random.shuffle(self.segments)
        return b''.join(self.segments)

    def play_audio(self):
        self.is_playing = True
        # Получение настроек из интерфейса
        global mode, speed, min_time, max_time
        while self.is_playing:
            if mode.get() == "intermediate":
                # Генерируем случайное время
                interval_time = random.uniform(min_time.get(), max_time.get())
                # Выбираем случайный сегмент
                segment = random.choice(self.segments)
                # Воспроизводим сегмент
                sound_array = np.frombuffer(segment, dtype=np.int16)
                sound = pygame.mixer.Sound(buffer=sound_array)
                sound.play()
                # Ждем окончания воспроизведения сегмента
                duration = len(segment) / (self.sample_rate * 2)
                time.sleep(duration)
                # Минимальная задержка между сегментами для плавности
                time.sleep(0)  # 20 мс
            else:
                # Постоянный режим
                shuffled_audio = self.mix_audio_segments()
                sound_array = np.frombuffer(shuffled_audio, dtype=np.int16)
                sound = pygame.mixer.Sound(buffer=sound_array)
                sound.play()
                duration = len(shuffled_audio) / (self.sample_rate * 2)
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
root.title("EVP-аудиомикшер 4")
root.geometry("900x350")

audio_mosaic = AudioMosaic()

# --- Область для отображения выбранных аудио ---
frame_listbox = tk.Frame(root)
frame_listbox.pack(pady=10)

listbox = tk.Listbox(frame_listbox, width=70, height=8)
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
        filetypes=[("Audio Files", "*.wav;*.mp3;*.mp4;*.ogg;*.flac")]
    )
    if file_path:
        selected_audios.append(file_path)
        listbox.insert(tk.END, file_path)

# --- Удаление выбранного файла из списка ---
def remove_selected():
    global selected_audios
    selected_indices = listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("Предупреждение", "Выберите файл для удаления.")
        return
    for index in reversed(selected_indices):
        listbox.delete(index)
        del selected_audios[index]

# --- Воспроизведение и остановка ---
def start_audio():
    global selected_audios
    if not selected_audios:
        messagebox.showwarning("Предупреждение", "Пожалуйста, выберите аудиофайлы.")
        return
    # Объединяем сегменты из всех выбранных файлов
    audio_mosaic.prepare_segments(selected_audios)
    audio_mosaic.start_playback()

def stop_audio():
    global selected_audios
    audio_mosaic.stop_audio()

# --- Настройки режима ---
mode = tk.StringVar(value="constant")  # "constant" или "intermediate"

# --- Поля для диапазона времени ---
min_time = tk.DoubleVar(value=0.5)
max_time = tk.DoubleVar(value=2.0)

# --- Поле для скорости переключения ---
speed_var = tk.DoubleVar(value=1.0)

# --- Интерфейс ---
frame_controls = tk.Frame(root)
frame_controls.pack(pady=10)

# --- Кнопки режима ---
intermediate_button = tk.Radiobutton(frame_controls, text="Промежуточный режим", variable=mode, value="intermediate")
intermediate_button.pack(side=tk.LEFT, padx=10)

constant_button = tk.Radiobutton(frame_controls, text="Постоянный режим", variable=mode, value="constant")
constant_button.pack(side=tk.LEFT, padx=10)

# --- Поля диапазона времени ---
tk.Label(frame_controls, text="Мин. время (сек):").pack(side=tk.LEFT)
min_entry = tk.Entry(frame_controls, textvariable=min_time, width=5)
min_entry.pack(side=tk.LEFT, padx=5)

tk.Label(frame_controls, text="Макс. время (сек):").pack(side=tk.LEFT)
max_entry = tk.Entry(frame_controls, textvariable=max_time, width=5)
max_entry.pack(side=tk.LEFT, padx=5)

# --- Поле скорости ---
tk.Label(frame_controls, text="Скорость переключения:").pack(side=tk.LEFT)
speed_entry = tk.Entry(frame_controls, textvariable=speed_var, width=5)
speed_entry.pack(side=tk.LEFT, padx=5)

# --- Кнопки ---
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="Старт", command=start_audio)
start_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(button_frame, text="Стоп", command=stop_audio)
stop_button.pack(side=tk.LEFT, padx=10)

remove_button = tk.Button(root, text="Удалить выбранное", command=remove_selected)
remove_button.pack(pady=5)

# --- Кнопка выбора файла ---
select_button = tk.Button(root, text="Выбрать аудио", command=select_audio)
select_button.pack(pady=5)

# Запуск интерфейса
root.mainloop()
