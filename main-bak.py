# https://github.com/patrickdarbeau/groq_dictate

import os
import tempfile
import wave
import pyaudio
import keyboard
import pyautogui
import pyperclip
from groq import Groq
import shutil
import signal
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration
MAX_RECORDING_TIME = 300  # 5 minutes maximum
RECORD_KEY = "pause"

# Vérifier la clé API
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("❌ ERREUR: La clé API Groq n'est pas configurée.")
    print("💡 Créez un fichier .env avec GROQ_API_KEY=votre_clé_api")
    sys.exit(1)

# Set up Groq client
client = Groq(api_key=api_key)

print("\n🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸") 
print("\n🔸  Enregistrez l'audio du microphone dans une application texte  🔸\n")
print("🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸\n\n") 

def record_audio(sample_rate=16000, channels=1, chunk=1024):
    """
    Enregistrez l'audio du microphone pendant que le bouton PAUSE est maintenu enfoncé.
    """
    try:
        # Vérifier les périphériques audio disponibles
        p = pyaudio.PyAudio()
        
        # Lister les périphériques d'entrée
        print("🔍 Recherche de périphériques audio...")
        input_devices = []
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info.get('maxInputChannels') > 0:
                input_devices.append(device_info)
                print(f"   📢 {device_info['index']}: {device_info['name']} (canaux: {device_info['maxInputChannels']})")
        
        if not input_devices:
            print("❌ Aucun périphérique d'entrée audio trouvé")
            p.terminate()
            return None, None
        
        print(f"✅ {len(input_devices)} périphérique(s) d'entrée trouvé(s)")
        
        # Ouvrir le flux audio avec le périphérique par défaut
        stream = p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk,
            input_device_index=None,  # Utiliser le périphérique par défaut
        )

        print(f"\n👉 Appuyez sur le bouton {RECORD_KEY.upper()} pour démarrer l'enregistrement...")
        
        # Attendre que l'utilisateur appuie sur PAUSE
        keyboard.wait(RECORD_KEY)
        
        print("🔸 Enregistrement en cours... (Relâchez PAUSE pour arrêter)")
        
        frames = []
        import time
        start_time = time.time()
        frames_recorded = 0
        
        # Boucle d'enregistrement
        while True:
            try:
                # Lire les données audio
                data = stream.read(chunk, exception_on_overflow=False)
                frames.append(data)
                frames_recorded += 1
                
                # Afficher un point toutes les 50 frames pour montrer l'activité
                if frames_recorded % 50 == 0:
                    print(".", end="", flush=True)
                
                # Vérifier si la touche PAUSE est relâchée
                if not keyboard.is_pressed(RECORD_KEY):
                    break
                    
                # Vérifier la limite de temps
                if time.time() - start_time > MAX_RECORDING_TIME:
                    print("\n⏰ Temps d'enregistrement maximum atteint (5 minutes)")
                    break
                    
            except Exception as e:
                print(f"\n⚠️ Erreur de lecture audio: {e}")
                continue

        print("\n🔸 Enregistrement terminé.")
        stream.stop_stream()
        stream.close()
        p.terminate()

        if len(frames) == 0:
            print("⚠️ Aucun audio enregistré")
            return None, None

        duration = len(frames) * chunk / sample_rate
        print(f"✅ {len(frames)} blocs audio enregistrés ({duration:.1f} secondes)")
        return frames, sample_rate
        
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement audio: {e}")
        try:
            p.terminate()
        except:
            pass
        return None, None


def save_audio(frames, sample_rate):
    """
    Enregistrez l'audio enregistré dans un fichier WAV temporaire.
    """
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            wf = wave.open(temp_audio.name, "wb")
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(sample_rate)
            wf.writeframes(b"".join(frames))
            wf.close()
            print(f"✅ Audio enregistré dans le fichier temporaire: {temp_audio.name}")
            return temp_audio.name
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde audio: {e}")
        return None


def transcribe_audio(audio_file_path):
    """
    Transcrivez l'audio à l'aide de l'implémentation Whisper de Groq.
    """
    try:
        with open(audio_file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(audio_file_path), file.read()),
                model="whisper-large-v3",
                #prompt="""L'audio est celui d'un programmeur discutant de problèmes de programmation, le programmeur utilise principalement Python et peut mentionner des bibliothèques Python ou du code de référence dans son discours.""",
                prompt="""Audio à transcrire""",
                response_format="text",
                language="fr",
            )
        return transcription  # Ceci est maintenant directement le texte de transcription
    except Exception as e:
        print(f"💥 Une erreur s'est produite: {str(e)}")
        return None


def copy_transcription_to_clipboard(text):
    """
    Copiez le texte transcrit dans le presse-papiers à l'aide de pyperclip.
    """
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")


def copier_fichier(source, destination_dir):
    """
    Copie le fichier source vers le répertoire de destination.
    """
    try:
        # Vérifier si le fichier source existe
        if not os.path.exists(source):
            print(f"❌ Erreur: Le fichier source '{source}' n'existe pas.")
            return False
            
        # Vérifier si le répertoire de destination existe, sinon le créer
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
            
        # Construire le chemin de destination complet
        filename = os.path.basename(source)
        destination_path = os.path.join(destination_dir, filename)
        
        # Copier le fichier
        shutil.copy(source, destination_path)
        print(f"✅ Fichier '{source}' copié vers '{destination_path}'.")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la copie: {e}")
        return False



def signal_handler(sig, frame):
    """Gestionnaire pour l'interruption Ctrl+C"""
    print("\n\n👋 Arrêt de Groq Whisperer...")
    sys.exit(0)

def main():
    # Enregistrer le gestionnaire de signal pour Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print("💡 Pour arrêter le programme, appuyez sur Ctrl+C")
    
    while True:
        # Enregistrer l'audio
        frames, sample_rate = record_audio()
        
        # Vérifier si l'enregistrement a réussi
        if frames is None or sample_rate is None:
            print("❌ Échec de l'enregistrement audio, nouvelle tentative...")
            continue

        # Enregistrer l'audio dans un fichier temporaire
        temp_audio_file = save_audio(frames, sample_rate)
        if temp_audio_file is None:
            print("❌ Échec de la sauvegarde audio, nouvelle tentative...")
            continue
            
        print(f"✅ Fichier audio enregistré dans : {temp_audio_file}")

        # Transcrire l'audio
        print("🔸 Transcription en cours...")
        transcription = transcribe_audio(temp_audio_file)

        # Copier la transcription dans le presse-papiers puis dans l'app de destination
        if transcription:
            print("\n✨ Transcription:\n")
            print(transcription)
            print("\n🔸 Copie de la transcription dans le presse-papiers...")
            copy_transcription_to_clipboard(transcription)
            print("✅ Transcription copiée dans le presse-papiers et collée dans l'application.")
        else:
            print("💥 La transcription a échoué.")

        # Copier le fichier audio temporaire dans un répertoire de sauvegarde
        backup_dir = "audio"
        copier_fichier(temp_audio_file, backup_dir)

        # Nettoyer le fichier temporaire
        try:
            os.unlink(temp_audio_file)
        except Exception as e:
            print(f"⚠️ Impossible de supprimer le fichier temporaire: {e}")

        print(f"\n👉 Prêt pour le prochain enregistrement. Appuyez sur {RECORD_KEY.upper()} pour démarrer.")


if __name__ == "__main__":
    main()


