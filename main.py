# https://github.com/patrickdarbeau/groq_whisperer

import os
import tempfile
import wave
import pyaudio
import keyboard
import pyautogui
import pyperclip
from groq import Groq
import shutil 
from dotenv import load_dotenv
import signal
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import tkinter.font as tkfont

# Charger les variables d'environnement
load_dotenv()

# Configuration
MAX_RECORDING_TIME = 300  # 5 minutes maximum
RECORD_KEY = "pause"      # Touche d'enregistrement
AUDIO_SAVE_DIR = "audio"  # Dossier de sauvegarde audio
TEXT_SAVE_DIR = "transcriptions"  # Dossier de sauvegarde des textes

# Set up Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class GroqWhispererGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Groq Whisperer")
        self.root.geometry("400x700")
        self.root.configure(bg='#D2D2EB')
        
        # Variables d'état
        self.is_recording = False
        self.recording_thread = None
        self.frames = []
        self.sample_rate = 16000
        
        # Configuration des styles
        self.setup_styles()
        
        # Création de l'interface
        self.create_widgets()
        
        # Démarrer la surveillance des touches
        self.start_key_monitoring()
        
    def setup_styles(self):
        """Configure les styles pour l'interface"""
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', 
                           background='#D2D2EB', 
                           foreground='#ffffff',
                           font=('Arial', 16, 'bold'))
        
        self.style.configure('Subtitle.TLabel',
                           background='#D2D2EB',
                           foreground='#ffffff',
                           font=('Arial', 12))
        
        self.style.configure('Record.TButton',
                           background='#e74c3c',
                           foreground='white',
                           font=('Arial', 14, 'bold'))
        
        self.style.configure('Success.TLabel',
                           background='#D2D2EB',
                           foreground='#2ecc71',
                           font=('Arial', 11))
        
        self.style.configure('Info.TLabel',
                           background='#D2D2EB',
                           foreground='#3498db',
                           font=('Arial', 10, 'italic'))
        
    def create_widgets(self):
        """Crée tous les widgets de l'interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, 
                               text="🎤 Groq Whisperer", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        

       # Sous-titre
        subtitle_label = ttk.Label(main_frame,
                                  text="(c) Patrick DARBEAU",
                                  style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 20))

        # Sous-titre
        subtitle_label = ttk.Label(main_frame,
                                  text="               Enregistrez votre voix\net obtenez une transcription instantanée\n    dans l'application de votre choix",
                                  style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 20))
        
        # Frame de statut
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Indicateur d'enregistrement
        self.record_indicator = tk.Label(status_frame, 
                                        text="● PRÊT", 
                                        bg='#27ae60',
                                        fg='white',
                                        font=('Arial', 12, 'bold'),
                                        padx=15,
                                        pady=8,
                                        relief='raised')
        self.record_indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        # Instructions
        instructions_label = ttk.Label(status_frame,
                                      text=f"Ouvrez votre application cible et\ncliquez sur le lieu d'insertion\nAppuyez sur {RECORD_KEY.upper()} pour enregistrer\nRelachez {RECORD_KEY.upper()} pour transcrire",
                                      
                                      
                                      style='Info.TLabel')
        instructions_label.pack(side=tk.LEFT)
        
        # Zone de transcription
        transcription_frame = ttk.LabelFrame(main_frame, 
                                           text=" Transcription ", 
                                           padding="10")
        transcription_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.transcription_text = scrolledtext.ScrolledText(
            transcription_frame,
            wrap=tk.WORD,
            font=('Arial', 11),
            bg='#ecf0f1',
            fg='#2c3e50',
            padx=10,
            pady=10,
            height=10
        )
        self.transcription_text.pack(fill=tk.BOTH, expand=True)
        
        # Frame des contrôles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X)
        
        # Bouton de copie
        self.copy_button = ttk.Button(controls_frame,
                                     text="📋 Copier la transcription",
                                     command=self.copy_transcription,
                                     state='disabled')
        self.copy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton d'effacement
        clear_button = ttk.Button(controls_frame,
                                 text="🗑️ Effacer",
                                 command=self.clear_transcription)
        clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton pour quitter
        quit_button = ttk.Button(controls_frame,
                                text="🚪 Quitter",
                                command=self.quit_application)
        quit_button.pack(side=tk.LEFT)
        
        # Informations de configuration
        config_frame = ttk.LabelFrame(main_frame, 
                                     text=" Configuration ", 
                                     padding="10")
        config_frame.pack(fill=tk.X)
        
        config_text = f"""
• Touche d'enregistrement : {RECORD_KEY.upper()}
• Temps maximum : {MAX_RECORDING_TIME} secondes
• Dossier audio : {AUDIO_SAVE_DIR}/
• Dossier transcriptions : {TEXT_SAVE_DIR}/
• Appuyez sur Ctrl+C pour quitter
        """
        
        config_label = ttk.Label(config_frame,
                                text=config_text,
                                style='Info.TLabel',
                                justify=tk.LEFT)
        config_label.pack(anchor=tk.W)
        
    def start_key_monitoring(self):
        """Démarre la surveillance des touches en arrière-plan"""
        def monitor_keys():
            while True:
                if keyboard.is_pressed(RECORD_KEY) and not self.is_recording:
                    self.start_recording()
                elif not keyboard.is_pressed(RECORD_KEY) and self.is_recording:
                    self.stop_recording()
                time.sleep(0.1)
        
        monitor_thread = threading.Thread(target=monitor_keys, daemon=True)
        monitor_thread.start()
        
    def start_recording(self):
        """Démarre l'enregistrement audio"""
        self.is_recording = True
        self.frames = []
        
        # Mettre à jour l'interface
        self.root.after(0, self.update_record_indicator, "● ENREGISTREMENT", '#e74c3c')
        self.root.after(0, self.add_to_transcription, "\n🔸 Enregistrement en cours...\n")
        
        # Démarrer l'enregistrement dans un thread séparé
        self.recording_thread = threading.Thread(target=self.record_audio_thread)
        self.recording_thread.start()
        
    def stop_recording(self):
        """Arrête l'enregistrement audio"""
        self.is_recording = False
        
        # Mettre à jour l'interface
        self.root.after(0, self.update_record_indicator, "● TRAITEMENT", '#f39c12')
        self.root.after(0, self.add_to_transcription, "🔸 Enregistrement terminé. Transcription en cours...\n")
        
    def record_audio_thread(self):
        """Thread d'enregistrement audio"""
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=1024,
        )
        
        start_time = time.time()
        
        while self.is_recording:
            data = stream.read(1024)
            self.frames.append(data)
            
            # Vérifier le temps d'enregistrement maximum
            elapsed_time = time.time() - start_time
            if elapsed_time >= MAX_RECORDING_TIME:
                self.root.after(0, self.add_to_transcription, 
                              "🔸 Temps d'enregistrement maximum atteint.\n")
                self.is_recording = False
                break
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Traiter l'audio enregistré
        if self.frames:
            self.process_recorded_audio()
        else:
            self.root.after(0, self.update_record_indicator, "● PRÊT", '#27ae60')
            self.root.after(0, self.add_to_transcription, "🔸 Aucun audio enregistré.\n")
            
    def process_recorded_audio(self):
        """Traite l'audio enregistré"""
        try:
            # Sauvegarder l'audio temporairement
            temp_audio_file = self.save_audio(self.frames, self.sample_rate)
            
            # Transcrire l'audio
            transcription = self.transcribe_audio(temp_audio_file)
            
            # Sauvegarder le fichier audio
            self.copier_fichier(temp_audio_file, AUDIO_SAVE_DIR)
            
            # Nettoyer le fichier temporaire
            os.unlink(temp_audio_file)
            
            # Mettre à jour l'interface
            if transcription:
                self.root.after(0, self.add_to_transcription, f"\n✨ Transcription :\n\n{transcription}\n\n")
                self.root.after(0, self.enable_copy_button)
                self.root.after(0, self.copy_to_clipboard, transcription)
                
                # Sauvegarder la transcription dans un fichier
                self.sauvegarder_transcription(transcription)
            else:
                self.root.after(0, self.add_to_transcription, "💥 La transcription a échoué.\n")
                
        except Exception as e:
            self.root.after(0, self.add_to_transcription, f"💥 Erreur : {str(e)}\n")
            
        finally:
            self.root.after(0, self.update_record_indicator, "● PRÊT", '#27ae60')
            
    def save_audio(self, frames, sample_rate):
        """Sauvegarde l'audio dans un fichier temporaire"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            wf = wave.open(temp_audio.name, "wb")
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(sample_rate)
            wf.writeframes(b"".join(frames))
            wf.close()
            return temp_audio.name
            
    def transcribe_audio(self, audio_file_path):
        """Transcrit l'audio avec l'API Groq"""
        try:
            with open(audio_file_path, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(os.path.basename(audio_file_path), file.read()),
                    model="whisper-large-v3",
                    prompt="""Audio à transcrire""",
                    response_format="text",
                    language="fr",
                )
            return transcription
        except Exception as e:
            print(f"Erreur de transcription: {str(e)}")
            return None
            
    def copier_fichier(self, source, destination_dir):
        """Sauvegarde le fichier audio"""
        try:
            if not os.path.exists(source):
                return
                
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
                
            # Générer un nom de fichier avec date et heure
            from datetime import datetime
            current_time = datetime.now()
            filename = f"recording_{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.wav"
            destination = os.path.join(destination_dir, filename)
            
            shutil.copy(source, destination)
            self.root.after(0, self.add_to_transcription, f"✅ Audio sauvegardé: {filename}\n")
            
        except Exception as e:
            print(f"Erreur de sauvegarde: {e}")
            
    def sauvegarder_transcription(self, text):
        """Sauvegarde la transcription dans un fichier texte"""
        try:
            if not text or not text.strip():
                return
                
            # Créer le dossier de sauvegarde s'il n'existe pas
            if not os.path.exists(TEXT_SAVE_DIR):
                os.makedirs(TEXT_SAVE_DIR)
                
            # Générer un nom de fichier avec date et heure
            from datetime import datetime
            current_time = datetime.now()
            filename = f"transcription_{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
            filepath = os.path.join(TEXT_SAVE_DIR, filename)
            
            # Sauvegarder le texte
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
                
            self.root.after(0, self.add_to_transcription, f"✅ Transcription sauvegardée: {filename}\n")
            return filepath
            
        except Exception as e:
            print(f"Erreur de sauvegarde de transcription: {e}")
            return None
            
    def copy_to_clipboard(self, text):
        """Copie le texte dans le presse-papiers et le colle automatiquement"""
        pyperclip.copy(text)
        # Attendre un court instant pour s'assurer que le presse-papiers est mis à jour
        time.sleep(0.1)
        # Coller automatiquement dans l'application active
        pyautogui.hotkey("ctrl", "v")
        self.root.after(0, self.add_to_transcription, "🔸 Transcription copiée et collée automatiquement.\n")
        
    def update_record_indicator(self, text, color):
        """Met à jour l'indicateur d'enregistrement"""
        self.record_indicator.config(text=text, bg=color)
        
    def add_to_transcription(self, text):
        """Ajoute du texte à la zone de transcription"""
        self.transcription_text.insert(tk.END, text)
        self.transcription_text.see(tk.END)
        self.transcription_text.update()
        
    def copy_transcription(self):
        """Copie la transcription dans le presse-papiers"""
        text = self.transcription_text.get(1.0, tk.END).strip()
        if text:
            pyperclip.copy(text)
            messagebox.showinfo("Succès", "Transcription copiée dans le presse-papiers !")
            
    def clear_transcription(self):
        """Efface la zone de transcription"""
        self.transcription_text.delete(1.0, tk.END)
        self.copy_button.config(state='disabled')
        
    def enable_copy_button(self):
        """Active le bouton de copie"""
        self.copy_button.config(state='normal')
        
    def quit_application(self):
        """Ferme l'application proprement"""
        if messagebox.askokcancel("Quitter", "Êtes-vous sûr de vouloir quitter l'application ?"):
            print("🔸 Fermeture de l'application...")
            self.root.quit()
            self.root.destroy()

def signal_handler(sig, frame):
    """Gère l'arrêt du programme avec Ctrl+C"""
    print("\n🔸 Arrêt du programme...")
    sys.exit(0)

def main():
    # Enregistrer le gestionnaire de signal pour Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Créer l'interface graphique
    root = tk.Tk()
    app = GroqWhispererGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n🔸 Arrêt du programme...")
        sys.exit(0)

if __name__ == "__main__":
    main()
