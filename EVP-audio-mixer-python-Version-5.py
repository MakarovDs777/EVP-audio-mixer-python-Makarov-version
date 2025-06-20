import tkinter as tk
from tkinter import filedialog, messagebox
import os
import random
from pydub import AudioSegment
from moviepy.editor import VideoFileClip

# Глобальный список выбранных файлов
selected_files = []

def extract_audio_from_video(video_path):
    try:
        clip = VideoFileClip(video_path)
        audio_path = os.path.splitext(video_path)[0] + "_temp_audio.mp3"
        clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
        clip.close()
        return audio_path
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось извлечь аудио из видео: {e}")
        return None

def convert_audio_to_bytes(path):
    with open(path, 'rb') as f:
        return f.read()

def save_bytes_as_audio(byte_data, output_path):
    with open(output_path, 'wb') as f:
        f.write(byte_data)

def create_eghf():
    # Получаем длину в секундах из поля ввода
    try:
        duration_sec = int(entry_duration.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число для длины.")
        return

    # Получаем количество ЭГФ
    try:
        count = int(entry_count.get())
        if count <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите положительное целое число для количества.")
        return

    # Создаем папку для сохранения
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_dir = os.path.join(desktop_path, "Множества ЭГФ")
    os.makedirs(output_dir, exist_ok=True)

    for i in range(1, count + 1):
        combined_bytes = bytearray()
        header_length = 100
        block_size = 64

        for file_path in selected_files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.mp4', '.avi', '.mov', '.mkv']:
                # Извлекаем аудио из видео
                audio_path = extract_audio_from_video(file_path)
                if not audio_path:
                    continue
                byte_data = convert_audio_to_bytes(audio_path)
                # Удаляем временный файл
                os.remove(audio_path)
            else:
                # Аудио файл
                byte_data = convert_audio_to_bytes(file_path)

            byte_list = list(byte_data)
            data_to_shuffle = byte_list[header_length:]
            num_blocks = len(data_to_shuffle) // block_size
            blocks = [data_to_shuffle[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
            random.shuffle(blocks)
            shuffled_data = [byte for block in blocks for byte in block]
            byte_list[header_length:] = shuffled_data
            shuffled_byte_data = bytes(byte_list)
            combined_bytes.extend(shuffled_byte_data)

        # Обрезаем итоговый байтовый поток до нужной длины
        sample_rate = 44100
        channels = 2
        bytes_per_sample = 2
        total_bytes = int((duration_sec * sample_rate * channels * bytes_per_sample))
        trimmed_bytes = combined_bytes[:total_bytes]

        # Создаем имя файла
        output_filename = f"Множества ЭГФ_{i}.mp3"
        output_path = os.path.join(output_dir, output_filename)

        # Создаем аудио из байтов
        save_bytes_as_audio(trimmed_bytes, output_path)

    messagebox.showinfo("Готово", f"Множество ЭГФ создано в папке: {output_dir}")

# Создаем интерфейс
root = tk.Tk()
root.title("EVP-аудиомикшер 5")
root.geometry("600x600")

# Поле для ввода длины
tk.Label(root, text="Длина ЭГФ (сек):").pack(pady=5)
entry_duration = tk.Entry(root)
entry_duration.pack(pady=5)
entry_duration.insert(0, "60")  # по умолчанию 60 секунд

# Поле для количества ЭГФ
tk.Label(root, text="Количество ЭГФ:").pack(pady=5)
entry_count = tk.Entry(root)
entry_count.pack(pady=5)
entry_count.insert(0, "1")  # по умолчанию 1

# Область для списка выбранных файлов
listbox = tk.Listbox(root, width=70)
listbox.pack(pady=10)

# --- Функция выбора файлов ---
def select_files():
    global selected_files
    file_paths = filedialog.askopenfilenames(
        title="Выберите файлы",
        filetypes=[
            ("Аудио и видео файлы", "*.mp3;*.wav;*.ogg;*.mp4;*.avi;*.mov;*.mkv"),
            ("Все файлы", "*.*")
        ]
    )
    if file_paths:
        for path in file_paths:
            selected_files.append(path)
            listbox.insert(tk.END, path)

tk.Button(root, text="Выбрать файлы", command=select_files).pack(pady=5)

# --- Удаление выбранных ---
def remove_selected():
    global selected_files
    selected_indices = listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("Предупреждение", "Выберите файл для удаления.")
        return
    for index in reversed(selected_indices):
        listbox.delete(index)
        del selected_files[index]

tk.Button(root, text="Удалить выбранное", command=remove_selected).pack(pady=5)

# --- Создать ЭГФ ---
tk.Button(root, text="Создать ЭГФ", command=create_eghf).pack(pady=5)

root.mainloop()
