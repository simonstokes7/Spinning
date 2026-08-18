import os
import librosa
import numpy as np

tracks = [
    ("The Answer", r"C:\Users\simon\Music\Workout - non 8and 12\-1 - The Answer (120 BPM).mp3"),
    ("Puff & Jimmy - Kashmir", r"C:\Users\simon\Music\Workout - non 8and 12\Puff and Jimmy - Kashmir.mp3"),
    ("Drifting away (Original mix)", r"C:\Users\simon\Music\Workout - non 8and 12\00 - Drifting away (Original mix).mp3"),
    ("Hung Up (SDP's Extended Dub)", r"C:\Users\simon\Music\Workout - non 8and 12\-1 - Hung Up (SDP's Extended Dub).mp3"),
    ("Hallowed Be Thy Name", r"C:\Users\simon\Music\Workout - non 8and 12\09 - Hallowed Be Thy Name.mp3"),
    ("Find Yourself (Original Mix)", r"C:\Users\simon\Music\Workout - non 8and 12\-1 - Find Yourself (Original Mix) - Unknown Artist - Climb - Spin.mp3"),
    ("Nebula - one workout", r"C:\Users\simon\Music\WORKING\Nebula - one workout.mp3")
]

print("=== RUNNING AUDIO BEAT ANALYSIS ON SPIN001 TRACKS ===")

results = []

for name, path in tracks:
    if not os.path.exists(path):
        print(f"File not found: {path}")
        continue
    
    print(f"Analyzing: {name}...")
    try:
        y, sr = librosa.load(path, sr=22050, duration=150, offset=40)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo)
        
        full_duration = librosa.get_duration(path=path)
        mins, secs = divmod(int(full_duration), 60)
        
        results.append({
            "name": name,
            "file": os.path.basename(path),
            "bpm": round(bpm, 1),
            "duration": f"{mins:02d}:{secs:02d}",
            "seconds": int(full_duration)
        })
        print(f"   -> BPM: {round(bpm, 1)} | Duration: {mins:02d}:{secs:02d}")
    except Exception as e:
        print(f"   -> Error analyzing {name}: {e}")

print("\n" + "=" * 80)
print(f"{'#':<3} {'TRACK NAME':<30} {'BPM':<8} {'DURATION':<10} {'SPINNING CADENCE & TERRAIN':<30}")
print("=" * 80)
for idx, r in enumerate(results, 1):
    bpm = r['bpm']
    if 120 <= bpm <= 145:
        half_cadence = round(bpm / 2)
        cadence_desc = f"{half_cadence} RPM (Climb) / {round(bpm)} RPM (Sprint)"
    elif 80 <= bpm <= 110:
        cadence_desc = f"{round(bpm)} RPM (Flat / Running / Jumps)"
    elif 60 <= bpm <= 80:
        cadence_desc = f"{round(bpm)} RPM (Heavy Climb)"
    else:
        cadence_desc = f"{round(bpm)} RPM"
        
    print(f"{idx:<3} {r['name']:<30} {r['bpm']:<8} {r['duration']:<10} {cadence_desc:<30}")
print("=" * 80)
