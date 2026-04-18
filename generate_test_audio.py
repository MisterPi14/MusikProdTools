import numpy as np
import librosa
import soundfile as sf

# Configuración
sr = 22050
duration = 30  # 30 segundos
bpm = 120
beats_per_bar = 4

# Crear posiciones de beats exactas
beat_interval = 60.0 / bpm
beat_times = np.arange(0, duration, beat_interval)

# Generar señal de clicks con longitud fija
clicks = librosa.clicks(times=beat_times, sr=sr, click_duration=0.1, click_freq=1000.0, length=sr*duration)

# Acentuar los downbeats (el primer golpe de cada compás)
downbeat_times = beat_times[::beats_per_bar]
downbeat_clicks = librosa.clicks(times=downbeat_times, sr=sr, click_duration=0.1, click_freq=2000.0, length=sr*duration)

# Mezclar, añadiendo ruido de fondo suave para que sea más natural
signal = clicks + downbeat_clicks * 1.5 
noise = np.random.randn(len(signal)) * 0.01
final_audio = signal + noise

# Guardar
sf.write("test_120bpm.wav", final_audio, sr)
print("Archivo test_120bpm.wav generado (120 BPM, 4/4)")
