import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
import speech_recognition as sr
import os
import subprocess
import webbrowser
from gtts import gTTS
import tempfile
import platform

class VoiceAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PERSONAL VOICE ASSISTANT")
        self.root.geometry("1000x800")
        self.setup_ui()
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # For temporary audio files
        self.temp_dir = tempfile.mkdtemp()
        
    def setup_ui(self):
        # Main title
        font = ('times', 15, 'bold')
        self.title = tk.Label(self.root, text='PERSONAL VOICE ASSISTANT')
        self.title.config(font=font, height=3, width=80)
        self.title.pack(pady=10)
        
        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        ff = ('times', 12, 'bold')
        
        self.offline_btn = tk.Button(button_frame, text="Offline Mathematical Operations", 
                                   command=self.offline, font=ff)
        self.offline_btn.pack(side=tk.LEFT, padx=10)
        
        self.online_btn = tk.Button(button_frame, text="Online Operations", 
                                 command=self.online, font=ff)
        self.online_btn.pack(side=tk.LEFT, padx=10)
        
        self.exit_btn = tk.Button(button_frame, text="Exit", 
                                command=self.close, font=ff)
        self.exit_btn.pack(side=tk.LEFT, padx=10)
        
        # Text output area
        self.text = tk.Text(self.root, height=20, width=100, wrap=tk.WORD)
        self.scroll = ttk.Scrollbar(self.root, command=self.text.yview)
        self.text.configure(yscrollcommand=self.scroll.set)
        
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
    def play_audio(self, text_data):
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", dir=self.temp_dir, delete=False) as fp:
                tts = gTTS(text=text_data, lang='en', slow=False)
                tts.save(fp.name)
                
                if platform.system() == 'Windows':
                    os.startfile(fp.name)
                elif platform.system() == 'Darwin':
                    subprocess.call(['afplay', fp.name])
                else:
                    subprocess.call(['aplay', fp.name])
                    
        except Exception as e:
            self.text.insert(tk.END, f"Error playing audio: {str(e)}\n")
            
    def run_offline(self, data):
        try:
            data = data.lower()
            current = 0
            total = 0
            count = 0
            arr = data.split(" ")
            i = 0
            
            while i < len(arr):
                if arr[i].isnumeric():
                    current = float(arr[i])
                    count += 1
                    if total == 0:
                        total = current
                
                if arr[i] in ['into', '*'] and i+1 < len(arr):
                    i += 1
                    if arr[i].isnumeric():
                        current = float(arr[i])
                        total *= current
                
                elif arr[i] in ['plus', '+'] and i+1 < len(arr):
                    i += 1
                    if arr[i].isnumeric():
                        current = float(arr[i])
                        total += current
                
                elif arr[i] in ['minus', '-'] and i+1 < len(arr):
                    i += 1
                    if arr[i].isnumeric():
                        current = float(arr[i])
                        total -= current
                
                elif arr[i] == 'divide' and current != 0:
                    total /= current
                
                elif arr[i] == 'percentage' and count != 0:
                    total /= count
                
                elif arr[i] == 'power' and i+1 < len(arr):
                    i += 1
                    if arr[i].isnumeric():
                        current = float(arr[i])
                        total = pow(total, current)
                
                elif arr[i] == 'table' and i+2 < len(arr):
                    i += 2
                    if arr[i].isnumeric():
                        current = int(arr[i])
                        for k in range(1, 11):
                            self.text.insert(tk.END, f"{current} * {k} = {current * k}\n")
                
                i += 1
            
            return total
        
        except Exception as e:
            self.text.insert(tk.END, f"Error in calculation: {str(e)}\n")
            return "Error"

    def offline(self):
        self.text.delete('1.0', tk.END)
        self.text.insert(tk.END, "Listening for mathematical operations...\n")
        self.root.update()
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
                
                try:
                    data = self.recognizer.recognize_google(audio)
                    self.text.insert(tk.END, f"Received Command: {data}\n")
                    total = self.run_offline(data)
                    self.text.insert(tk.END, f"\nComputed Result: {total}\n")
                    self.play_audio(f"The result is {total}")
                    
                except sr.UnknownValueError:
                    self.text.insert(tk.END, "Could not understand audio\n")
                except sr.RequestError as e:
                    self.text.insert(tk.END, f"Recognition error: {str(e)}\n")
                    
        except Exception as e:
            self.text.insert(tk.END, f"Error: {str(e)}\n")

    def run_online(self, command):
        try:
            data = command.lower().strip()
            arr = data.split(" ")
            i = 0
            
            while i < len(arr):
                if arr[i] == 'search' and i+1 < len(arr):
                    query = '+'.join(arr[i+1:])
                    webbrowser.open_new_tab(f"https://www.google.com/search?q={query}")
                    break
                
                elif arr[i] == 'settings' and platform.system() == 'Windows':
                    subprocess.Popen(["control"])
                    break
                
                elif arr[i] == 'wi-fi' and i+1 < len(arr):
                    if platform.system() == 'Windows':
                        if arr[i+1] == 'on':
                            os.system("netsh interface set interface 'Wi-Fi' enabled")
                        elif arr[i+1] == 'off':
                            os.system("netsh interface set interface 'Wi-Fi' disabled")
                    break
                
                elif arr[i] == 'open' and i+1 < len(arr):
                    name = arr[i+1].strip()
                    common_paths = [
                        os.path.expanduser('~'),
                        os.path.join(os.path.expanduser('~'), 'Documents'),
                        os.path.join(os.path.expanduser('~'), 'Downloads')
                    ]
                    
                    for path in common_paths:
                        for ext in ['.txt', '.doc', '.docx', '.pdf', '.jpg', '.png', '.gif']:
                            file_path = os.path.join(path, name + ext)
                            if os.path.exists(file_path):
                                if platform.system() == 'Windows':
                                    os.startfile(file_path)
                                elif platform.system() == 'Darwin':
                                    subprocess.call(['open', file_path])
                                else:
                                    subprocess.call(['xdg-open', file_path])
                                return
                    
                    self.text.insert(tk.END, f"File {name} not found in common locations\n")
                    break
                
                i += 1
                
        except Exception as e:
            self.text.insert(tk.END, f"Error executing online command: {str(e)}\n")

    def online(self):
        self.text.delete('1.0', tk.END)
        self.text.insert(tk.END, "Listening for online commands...\n")
        self.root.update()
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
                
                try:
                    data = self.recognizer.recognize_google(audio)
                    self.text.insert(tk.END, f"Received Command: {data}\n")
                    self.run_online(data)
                    
                except sr.UnknownValueError:
                    self.text.insert(tk.END, "Could not understand audio\n")
                except sr.RequestError as e:
                    self.text.insert(tk.END, f"Recognition error: {str(e)}\n")
                    
        except Exception as e:
            self.text.insert(tk.END, f"Error: {str(e)}\n")

    def close(self):
        try:
            # Clean up temporary files
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
            
            os.rmdir(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up: {e}")
            
        self.root.destroy()

def main():
    root = tk.Tk()
    app = VoiceAssistantApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()