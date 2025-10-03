import pyaudio
import wave
import tempfile

# Test simple d'enregistrement audio
p = pyaudio.PyAudio()

# Lister les périphériques
print('=== PÉRIPHÉRIQUES AUDIO ===')
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f'Input {i}: {info["name"]} (channels: {info["maxInputChannels"]})')

# Test d'enregistrement
print('\n=== TEST D\'ENREGISTREMENT ===')

# Demander à l'utilisateur de choisir un périphérique
device_index = int(input('Choisissez l\'index du microphone à utiliser: '))

# Attendre confirmation
input('Appuyez sur Entrée pour commencer l\'enregistrement de 3 secondes...')

stream = p.open(format=pyaudio.paInt16, 
                channels=1, 
                rate=16000, 
                input=True, 
                #input_device_index=device_index,
                frames_per_buffer=1024)

print('Enregistrement de 3 secondes...')
frames = []
for i in range(0, int(16000 / 1024 * 3)):
    data = stream.read(1024)
    frames.append(data)

stream.stop_stream()
stream.close()

# Sauvegarde
with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
    wf = wave.open(f.name, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f'Fichier créé: {f.name}')
    print(f'Taille du fichier: {len(b"".join(frames))} bytes')

p.terminate()
print('Test terminé')
