import os
import json
import re
import base64
import subprocess
from flask import Flask, send_from_directory, jsonify, request, Response
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

import werkzeug.formparser
werkzeug.formparser.default_max_form_memory_size = 500 * 1024 * 1024
werkzeug.formparser.default_max_form_parts = 5000

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['MAX_FORM_MEMORY_SIZE'] = 500 * 1024 * 1024
app.config['MAX_FORM_PARTS'] = 5000

MUSICBEE_PLAYLIST_DIR = r"C:\Users\simon\Music\MusicBee\Playlists"
PROJECT_DIR = r"C:\Data_Projects\Spinning"
ICON_DIR = r"C:\Data_Projects\Spinning\Spinning Symbols"

def load_symbols_b64():
    symbols_dict = {}
    if os.path.exists(ICON_DIR):
        for fname in sorted(os.listdir(ICON_DIR)):
            if fname.endswith(".png"):
                name = os.path.splitext(fname)[0]
                with open(os.path.join(ICON_DIR, fname), "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                    symbols_dict[name] = f"data:image/png;base64,{b64}"
    return symbols_dict

def get_all_known_mp3s():
    mp3s = []
    if os.path.exists(MUSICBEE_PLAYLIST_DIR):
        for pl in os.listdir(MUSICBEE_PLAYLIST_DIR):
            if pl.lower().endswith(('.m3u', '.m3u8')):
                pl_path = os.path.join(MUSICBEE_PLAYLIST_DIR, pl)
                with open(pl_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and os.path.exists(line):
                            if line not in mp3s:
                                mp3s.append(line)
    return mp3s

def generate_embedded_html(class_data):
    tracks = class_data.get('tracks', [])
    title = "Latest Spin Class"
    playlist_name = class_data.get('playlistName', '')

    all_known_mp3s = get_all_known_mp3s()

    if not playlist_name:
        if "8n12" in (class_data.get('title') or '').lower():
            playlist_name = "8n12"
        else:
            playlist_name = "Spin001"

    m3u_path = os.path.join(MUSICBEE_PLAYLIST_DIR, f"{playlist_name}.m3u")
    m3u_paths = []
    if os.path.exists(m3u_path):
        with open(m3u_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and os.path.exists(line):
                    m3u_paths.append(line)

    tracks_data_with_audio = []
    for idx, t in enumerate(tracks):
        audio_path = t.get('filePath')
        if not audio_path or not os.path.exists(audio_path):
            if idx < len(m3u_paths):
                audio_path = m3u_paths[idx]
            else:
                track_name = (t.get('name') or '').lower()
                for mp in all_known_mp3s:
                    if track_name and (track_name in mp.lower() or os.path.basename(mp).lower() in track_name):
                        audio_path = mp
                        break

        b64_audio = t.get('audioBase64') or ""
        if not b64_audio and audio_path and os.path.exists(audio_path):
            try:
                with open(audio_path, 'rb') as af:
                    b64_str = base64.b64encode(af.read()).decode('utf-8')
                    b64_audio = f"data:audio/mp3;base64,{b64_str}"
            except Exception as e:
                print(f"Error encoding {audio_path}: {e}")

        track_copy = dict(t)
        if b64_audio:
            track_copy['audioBase64'] = b64_audio
        tracks_data_with_audio.append(track_copy)

    symbols_dict = load_symbols_b64()
    symbols_json = json.dumps(symbols_dict)
    tracks_json = json.dumps(tracks_data_with_audio)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <title>🚴 {workout_title} - Handlebar Cockpit</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800&family=Outfit:wght@600;700;800;900&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-main: #080a10;
      --bg-card: rgba(20, 26, 42, 0.95);
      --border-subtle: rgba(255, 255, 255, 0.12);
      --text-main: #f0f4f8;
      --text-muted: #94a3b8;
      --accent-cyan: #00e5ff;
      --zone-recovery: #00bcd4;
      --zone-endurance: #00e676;
      --zone-strength: #ff9100;
      --zone-interval: #ff1744;
      --zone-raceday: #e040fb;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    html, body {{
      width: 100%;
      height: 100%;
      min-height: 100vh;
      min-height: 100dvh;
      background: radial-gradient(circle at 50% 20%, #162238 0%, var(--bg-main) 80%);
      color: var(--text-main);
      font-family: 'Inter', sans-serif;
      user-select: none;
      transition: background 0.5s ease;
    }}

    .screen-container {{
      width: 100%;
      min-height: 100vh;
      min-height: 100dvh;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 8px 12px calc(10px + env(safe-area-inset-bottom, 0px)) 12px;
      box-sizing: border-box;
    }}

    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 14px;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      flex-shrink: 0;
    }}
    .title-group h1 {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.15rem;
      font-weight: 800;
      color: #fff;
    }}
    .clock-pill {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.35rem;
      font-weight: 900;
      color: var(--accent-cyan);
      letter-spacing: 0.05em;
    }}

    .cockpit {{
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 6px;
      margin: 4px 0;
      flex: 1;
      justify-content: space-evenly;
      min-height: 0;
    }}

    .zone-badge {{
      display: inline-block;
      padding: 4px 16px;
      border-radius: 24px;
      font-family: 'Outfit', sans-serif;
      font-weight: 900;
      font-size: 0.82rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      box-shadow: 0 2px 10px rgba(0,0,0,0.3);
      transition: all 0.4s ease;
    }}

    .song-title {{
      font-family: 'Outfit', sans-serif;
      font-size: clamp(1.4rem, 5.5vw, 1.95rem);
      font-weight: 900;
      line-height: 1.15;
      color: #fff;
      max-width: 92vw;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .song-artist {{
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--text-muted);
      margin-top: 1px;
    }}

    .metrics-row {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
      width: 100%;
      max-width: 620px;
    }}
    @media (max-width: 480px) {{
      .metrics-row {{ grid-template-columns: repeat(2, 1fr); gap: 6px; }}
    }}

    .metric-box {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 6px 8px;
      transition: all 0.3s ease;
    }}
    .metric-lbl {{
      font-size: 0.68rem;
      text-transform: uppercase;
      color: var(--text-muted);
      letter-spacing: 0.06em;
      font-weight: 700;
      margin-bottom: 2px;
    }}
    .metric-val {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.55rem;
      font-weight: 900;
      color: #fff;
      line-height: 1.1;
    }}

    .cadence-highlight {{
      border: 2px solid var(--accent-cyan) !important;
      background: rgba(0, 229, 255, 0.15) !important;
      box-shadow: 0 0 16px rgba(0, 229, 255, 0.5);
    }}

    @keyframes beatPulse {{
      0% {{ transform: scale(1); box-shadow: 0 0 10px rgba(0,229,255,0.4); }}
      50% {{ transform: scale(1.05); box-shadow: 0 0 24px rgba(0,229,255,0.9); }}
      100% {{ transform: scale(1); box-shadow: 0 0 10px rgba(0,229,255,0.4); }}
    }}
    .pulse-ring {{
      animation: beatPulse 0.75s infinite ease-in-out;
    }}

    .mov-banner {{
      width: 100%;
      max-width: 620px;
      background: rgba(0, 229, 255, 0.08);
      border: 1px solid rgba(0, 229, 255, 0.25);
      border-radius: 10px;
      padding: 6px 12px;
      font-size: 0.9rem;
      font-weight: 800;
      text-align: center;
      color: #fff;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      transition: all 0.3s ease;
    }}
    .mov-banner.warning-flash {{
      background: rgba(255, 23, 68, 0.3) !important;
      border-color: #ff1744 !important;
      box-shadow: 0 0 20px rgba(255, 23, 68, 0.8) !important;
      animation: bannerPulse 0.7s infinite ease-in-out;
    }}
    @keyframes bannerPulse {{
      0%, 100% {{ opacity: 1; transform: scale(1.01); }}
      50% {{ opacity: 0.85; transform: scale(1.0); }}
    }}

    .progress-deck {{
      width: 100%;
      max-width: 620px;
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}
    .progress-bar-wrap {{
      width: 100%;
      height: 10px;
      background: rgba(255, 255, 255, 0.14);
      border-radius: 6px;
      overflow: hidden;
      cursor: pointer;
    }}
    .progress-fill {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, #00e5ff, #7c4dff);
      border-radius: 6px;
      transition: width 0.1s linear;
    }}
    .time-row {{
      display: flex;
      justify-content: space-between;
      font-family: 'Outfit', sans-serif;
      font-size: 0.95rem;
      font-weight: 700;
      color: #cbd5e1;
    }}

    .audio-controls-row {{
      display: flex;
      gap: 6px;
      justify-content: center;
      width: 100%;
      max-width: 620px;
      flex-wrap: wrap;
    }}
    .sound-chip {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid var(--border-subtle);
      border-radius: 20px;
      padding: 4px 12px;
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}
    .sound-chip.active {{
      background: rgba(0, 229, 255, 0.2);
      border-color: var(--accent-cyan);
      color: #fff;
    }}

    .movements-strip {{
      display: flex;
      gap: 8px;
      justify-content: center;
      flex-wrap: wrap;
      max-width: 620px;
    }}
    .mov-card {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 6px 10px;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.25s ease;
    }}
    .mov-card img {{
      width: 36px;
      height: 36px;
      background: #fff;
      border-radius: 6px;
      object-fit: contain;
    }}
    .mov-active {{
      border: 2px solid var(--accent-cyan) !important;
      background: rgba(0, 229, 255, 0.25) !important;
      box-shadow: 0 0 18px rgba(0, 229, 255, 0.9) !important;
      transform: scale(1.05);
    }}
    @keyframes movFlash {{
      0%, 100% {{
        border-color: #ffd700 !important;
        background: rgba(255, 215, 0, 0.45) !important;
        box-shadow: 0 0 22px rgba(255, 215, 0, 0.95) !important;
        transform: scale(1.06);
      }}
      50% {{
        border-color: #ff9100 !important;
        background: rgba(255, 145, 0, 0.15) !important;
        box-shadow: 0 0 6px rgba(255, 145, 0, 0.3) !important;
        transform: scale(1.0);
      }}
    }}
    .mov-upcoming-flash {{
      animation: movFlash 0.75s infinite ease-in-out !important;
    }}

    .cues-box {{
      background: rgba(0, 229, 255, 0.1);
      border-left: 4px solid var(--accent-cyan);
      border-radius: 8px;
      padding: 8px 14px;
      font-size: 0.96rem;
      font-weight: 600;
      line-height: 1.35;
      color: #e0f7fa;
      max-width: 620px;
      width: 100%;
    }}

    .controls-bottom {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      border-top: 1px solid var(--border-subtle);
      padding-top: 8px;
      width: 100%;
      max-width: 620px;
      margin: 0 auto;
      flex-shrink: 0;
      position: sticky;
      bottom: 0;
      background: rgba(8, 10, 16, 0.96);
      backdrop-filter: blur(8px);
      z-index: 100;
    }}
    .btn {{
      font-family: 'Inter', sans-serif;
      font-weight: 800;
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }}
    .btn-play {{
      flex: 2;
      background: linear-gradient(135deg, #00e5ff, #0072ff);
      color: #fff;
      box-shadow: 0 4px 18px rgba(0, 229, 255, 0.5);
      font-size: 1.22rem;
      padding: 12px 20px;
      border-radius: 12px;
      min-height: 50px;
    }}
    .btn-nav {{
      flex: 1;
      background: rgba(255, 255, 255, 0.08);
      color: #fff;
      border: 1px solid var(--border-subtle);
      padding: 12px 14px;
      font-size: 0.95rem;
      border-radius: 10px;
      min-height: 50px;
    }}
  </style>
</head>
<body>

  <div class="screen-container">
    <header>
      <div class="title-group">
        <h1>🚴 {workout_title} <span style="font-size:0.7rem; background:rgba(0,229,255,0.15); color:var(--accent-cyan); padding:2px 8px; border-radius:10px; border:1px solid rgba(0,229,255,0.3); vertical-align:middle; margin-left:8px; font-weight:700;">v3.6.2</span></h1>
      </div>
      <div style="display:flex; gap:8px; align-items:center;">
        <div class="clock-pill" id="totalClassTimer" style="background:rgba(0,229,255,0.15); border:1px solid var(--accent-cyan); color:var(--accent-cyan); font-weight:800; font-family:'Outfit',sans-serif;" title="Total Workout Elapsed / Total Class Time">
          ⏱️ 00:00 / 00:00
        </div>
        <div class="clock-pill" id="wakeLockStatus" style="font-size:0.75rem; background:rgba(0,230,118,0.15); border:1px solid var(--zone-endurance); color:var(--zone-endurance); padding:4px 8px; border-radius:12px; font-weight:700;" title="Screen Wake Lock Status">
          💡 AWAKE
        </div>
        <div class="clock-pill" id="liveClock" style="font-size:0.85rem; color:var(--text-muted); padding:4px 8px; font-weight:600;" title="Local Time of Day">
          🕒 00:00
        </div>
      </div>
    </header>

    <div class="cockpit">
      <div class="zone-badge" id="zoneBadge">STRENGTH ZONE</div>
      <div style="text-align:center;">
        <div class="song-title" id="songTitle"></div>
        <div class="song-artist" id="songArtist"></div>
        <div id="songDurationPill" style="font-size:1.25rem; font-weight:800; color:var(--accent-cyan); margin: 8px 0 10px 0; text-align:center; letter-spacing:0.5px;"></div>
      </div>

      <div class="mov-banner" id="movBanner">
        <span id="movBannerCurrent">⚡ CURRENT: Seated Flat</span>
        <span id="movBannerNext" style="color:var(--accent-orange); font-weight:800; display:none;">▶ NEXT IN 10s: Standing Climb ⚡</span>
      </div>

      <div class="metrics-row">
        <div class="metric-box">
          <div class="metric-lbl">Track</div>
          <div class="metric-val" id="trackNumVal">1 / {len(tracks_data_with_audio)}</div>
        </div>
        <div class="metric-box">
          <div class="metric-lbl">Target RPE</div>
          <div class="metric-val" id="targetRpeVal" style="font-size:1.25rem; font-weight:800; color:#ff9100;">RPE 6</div>
        </div>
        <div class="metric-box">
          <div class="metric-lbl">Song BPM</div>
          <div class="metric-val" id="bpmVal" style="color:var(--accent-cyan)"></div>
        </div>
        <div class="metric-box cadence-highlight" id="cadenceBox">
          <div class="metric-lbl">Cadence</div>
          <div class="metric-val" id="cadenceVal" style="font-size:1.35rem; color:#fff;"></div>
        </div>
      </div>

      <div class="progress-deck">
        <div class="time-row">
          <span id="curTimeDisplay">00:00</span>
          <span id="statusDisplay" style="color:#fff; font-weight:800;">Ready</span>
          <span id="remTimeDisplay"></span>
        </div>
        <div class="progress-bar-wrap" onclick="seekAudio(event)">
          <div class="progress-fill" id="progressFill"></div>
        </div>
      </div>

      <div class="audio-controls-row">
        <button class="sound-chip active" id="soundFxBtn" onclick="toggleSoundFx()" title="Toggle Web Audio sound effects">
          🔊 Sound: ON
        </button>
        <button class="sound-chip active" id="beepBtn" onclick="toggleBeeps()" title="Toggle 3-2-1 countdown beeps">
          🔔 Beeps: ON
        </button>
        <button class="sound-chip" id="metroBtn" onclick="toggleMetronome()" title="Toggle synthesized pedal cadence clicker">
          🥁 Metronome: OFF
        </button>
        <button class="sound-chip" id="fullscreenBtn" onclick="toggleFullscreen()" title="Toggle Fullscreen Mode">
          🖥️ Fullscreen
        </button>
      </div>

      <div class="movements-strip" id="movementsStrip"></div>
      <div class="cues-box" id="cuesBox"></div>
    </div>

    <div class="controls-bottom">
      <button class="btn btn-nav" onclick="prevTrack()">◀ Prev</button>
      <button class="btn btn-play" id="playBtn" onclick="togglePlay()">▶ Play Workout</button>
      <button class="btn btn-nav" onclick="nextTrack()">Next ▶</button>
    </div>
  </div>

  <audio id="audioEngine" preload="auto"></audio>

  <script>
    const SYMBOL_ICONS = {symbols_json};
    const CLASS_TRACKS = {tracks_json};

    const ZONE_COLORS = {{
      'Recovery': '#00bcd4',
      'Endurance': '#00e676',
      'Strength': '#ff9100',
      'Interval': '#ff1744',
      'Race Day': '#e040fb'
    }};

    let curIdx = 0;
    let audio = null;
    let isPlaying = false;
    let wakeLock = null;
    let blobUrls = {{}};

    // Web Audio Synthesizer Engine
    let audioCtx = null;
    let soundEnabled = true;
    let beepsEnabled = true;
    let metronomeEnabled = false;
    let metronomeInterval = null;
    let lastBeepSec = -1;
    let prevActiveMovIdx = -1;

    function initAudioContext() {{
      if (!audioCtx) {{
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (AudioContextClass) audioCtx = new AudioContextClass();
      }}
      if (audioCtx && audioCtx.state === 'suspended') {{
        audioCtx.resume();
      }}
    }}

    function playTone(freq, dur, type='sine', gainVal=0.15) {{
      if (!soundEnabled) return;
      try {{
        initAudioContext();
        if (!audioCtx) return;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(gainVal, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + dur);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + dur);
      }} catch(e) {{}}
    }}

    function playCountdownBeep(isFinal=false) {{
      if (!beepsEnabled || !soundEnabled) return;
      if (isFinal) {{
        playTone(1050, 0.1, 'sine', 0.25);
        setTimeout(() => playTone(1400, 0.25, 'triangle', 0.3), 100);
      }} else {{
        playTone(780, 0.12, 'square', 0.2);
      }}
    }}

    function playZoneChime() {{
      if (!soundEnabled) return;
      playTone(523.25, 0.08, 'sine', 0.15);
      setTimeout(() => playTone(659.25, 0.08, 'sine', 0.15), 90);
      setTimeout(() => playTone(783.99, 0.22, 'sine', 0.2), 180);
    }}

    function toggleSoundFx() {{
      soundEnabled = !soundEnabled;
      const btn = document.getElementById('soundFxBtn');
      btn.textContent = soundEnabled ? '🔊 Sound: ON' : '🔇 Muted';
      btn.classList.toggle('active', soundEnabled);
      if (soundEnabled) playTone(880, 0.1);
    }}

    function toggleBeeps() {{
      beepsEnabled = !beepsEnabled;
      const btn = document.getElementById('beepBtn');
      btn.textContent = beepsEnabled ? '🔔 Beeps: ON' : '🔕 Beeps: OFF';
      btn.classList.toggle('active', beepsEnabled);
      if (beepsEnabled) playCountdownBeep(false);
    }}

    function toggleMetronome() {{
      metronomeEnabled = !metronomeEnabled;
      const btn = document.getElementById('metroBtn');
      btn.textContent = metronomeEnabled ? '🥁 Metronome: ON' : '🥁 Metronome: OFF';
      btn.classList.toggle('active', metronomeEnabled);
      updateMetronomeState();
    }}

    function updateMetronomeState() {{
      if (metronomeInterval) {{
        clearInterval(metronomeInterval);
        metronomeInterval = null;
      }}
      if (!metronomeEnabled || !isPlaying) return;

      const t = CLASS_TRACKS[curIdx];
      if (!t || !t.cadence) return;

      let rpm = 80;
      const match = String(t.cadence).match(/\\d+/);
      if (match) rpm = parseInt(match[0]);
      if (rpm < 40) rpm = 80;

      const ms = (60 / rpm) * 1000;
      metronomeInterval = setInterval(() => {{
        playTone(1200, 0.03, 'triangle', 0.08);
      }}, ms);
    }}

    function toggleFullscreen() {{
      if (!document.fullscreenElement) {{
        document.documentElement.requestFullscreen().catch(e => {{}});
        document.getElementById('fullscreenBtn').textContent = '📱 Exit Full';
      }} else {{
        if (document.exitFullscreen) document.exitFullscreen();
        document.getElementById('fullscreenBtn').textContent = '🖥️ Fullscreen';
      }}
    }}

    function b64ToBlobUrl(b64Data) {{
      try {{
        const parts = b64Data.split(',');
        const mime = parts[0].match(/:(.*?);/)[1] || 'audio/mp3';
        const bin = atob(parts[1]);
        const len = bin.length;
        const u8 = new Uint8Array(len);
        for (let i = 0; i < len; i++) {{ u8[i] = bin.charCodeAt(i); }}
        const blob = new Blob([u8], {{ type: mime }});
        return URL.createObjectURL(blob);
      }} catch(e) {{
        return b64Data;
      }}
    }}

    function parseDurationSecs(durStr) {{
      if (!durStr) return 300;
      if (durStr.includes(':')) {{
        const [m, s] = durStr.split(':').map(Number);
        return (m || 0) * 60 + (s || 0);
      }}
      return parseInt(durStr) || 300;
    }}

    const workoutTracks = CLASS_TRACKS.slice(0, Math.max(1, CLASS_TRACKS.length - 1));
    let totalWorkoutSecs = 0;
    workoutTracks.forEach(t => {{
      totalWorkoutSecs += parseDurationSecs(t.duration);
    }});

    function updateTotalClassTimer(currentTrackSecs = 0) {{
      const isLast = (curIdx === CLASS_TRACKS.length - 1);
      let totalElapsed = 0;

      if (isLast) {{
        totalElapsed = totalWorkoutSecs;
      }} else {{
        let elapsedPrior = 0;
        for (let i = 0; i < curIdx; i++) {{
          elapsedPrior += parseDurationSecs(CLASS_TRACKS[i].duration);
        }}
        totalElapsed = Math.min(totalWorkoutSecs, elapsedPrior + Math.round(currentTrackSecs));
      }}
      
      const elM = Math.floor(totalElapsed / 60);
      const elS = totalElapsed % 60;
      const elStr = String(elM).padStart(2, '0') + ':' + String(elS).padStart(2, '0');

      const totM = Math.floor(totalWorkoutSecs / 60);
      const totS = totalWorkoutSecs % 60;
      const totStr = String(totM).padStart(2, '0') + ':' + String(totS).padStart(2, '0');

      const pill = document.getElementById('totalClassTimer');
      if (pill) {{
        pill.textContent = isLast ? ('⏱️ WORKOUT: ' + totStr + ' (Done)') : ('⏱️ ' + elStr + ' / ' + totStr);
      }}
    }}

    function requestScreenWakeLock() {{
      try {{
        if ('wakeLock' in navigator) {{
          navigator.wakeLock.request('screen').then(lock => {{
            wakeLock = lock;
            const statusEl = document.getElementById('wakeLockStatus');
            if (statusEl) statusEl.textContent = '💡 AWAKE';
          }}).catch(e => {{
            const statusEl = document.getElementById('wakeLockStatus');
            if (statusEl) statusEl.textContent = '💡 READY';
          }});
        }}
      }} catch(e) {{}}
    }}

    function init() {{
      audio = document.getElementById('audioEngine');
      audio.addEventListener('timeupdate', onTimeUpdate);
      audio.addEventListener('ended', onEnded);

      let startX = 0;
      window.addEventListener('touchstart', (e) => {{ startX = e.changedTouches[0].screenX; }}, {{ passive: true }});
      window.addEventListener('touchend', (e) => {{
        const diff = e.changedTouches[0].screenX - startX;
        if (Math.abs(diff) > 60) {{
          if (diff < 0) nextTrack();
          else prevTrack();
        }}
      }}, {{ passive: true }});

      document.addEventListener('click', () => {{ initAudioContext(); }}, {{ once: true }});
      requestScreenWakeLock();
      document.addEventListener('visibilitychange', () => {{
        if (document.visibilityState === 'visible') requestScreenWakeLock();
      }});

      setInterval(() => {{
        const now = new Date();
        let h = now.getHours();
        const m = String(now.getMinutes()).padStart(2, '0');
        const ampm = h >= 12 ? 'PM' : 'AM';
        h = h % 12;
        h = h ? h : 12;
        document.getElementById('liveClock').textContent = '🕒 ' + h + ':' + m + ' ' + ampm;
      }}, 1000);

      loadTrack(0, false);
      updateTotalClassTimer(0);
    }}

    function loadTrack(idx, autoPlay = true) {{
      curIdx = idx;
      prevActiveMovIdx = -1;
      lastBeepSec = -1;
      const t = CLASS_TRACKS[curIdx];
      if (!t) return;

      document.getElementById('trackNumVal').textContent = (curIdx + 1) + ' / ' + CLASS_TRACKS.length;
      document.getElementById('songTitle').textContent = t.name;
      document.getElementById('songArtist').textContent = t.artist || '';
      document.getElementById('songDurationPill').textContent = t.duration || '05:00';
      const rawRpe = String(t.rpe || t.target_rpe || '6').trim();
      const rpeDisplay = rawRpe.startsWith('RPE') ? rawRpe : ('RPE ' + rawRpe);
      if (document.getElementById('targetRpeVal')) {{
        document.getElementById('targetRpeVal').textContent = rpeDisplay;
      }}
      document.getElementById('bpmVal').textContent = t.bpm || '--';
      document.getElementById('cadenceVal').textContent = t.cadence || '--';
      document.getElementById('cuesBox').textContent = t.cues ? '"' + t.cues + '"' : '"Focus on smooth pedal cadence."';

      const isLast = (curIdx === CLASS_TRACKS.length - 1);
      const zColor = isLast ? '#00e5ff' : (ZONE_COLORS[t.zone] || '#00e676');
      const badge = document.getElementById('zoneBadge');
      badge.textContent = isLast ? '🧘 COOL-DOWN & STRETCH' : ((t.zone || 'Endurance').toUpperCase() + ' ZONE');
      badge.style.background = zColor + '33';
      badge.style.color = zColor;
      badge.style.border = '1px solid ' + zColor;

      // Dynamically tint background glow
      document.body.style.background = 'radial-gradient(circle at 50% 20%, ' + zColor + '22 0%, var(--bg-main) 80%)';

      const strip = document.getElementById('movementsStrip');
      strip.innerHTML = '';

      if (isLast) {{
        const stretchList = [
          {{ icon: '🙆', name: 'Chest & Shoulders', time: '0:00', sub: 'Deep Breathing' }},
          {{ icon: '🚴', name: 'Hamstring Stretch', time: '1:30', sub: 'Left & Right' }},
          {{ icon: '🦵', name: 'Quadriceps Stretch', time: '2:45', sub: 'Standing Balance' }},
          {{ icon: '🧘', name: 'Calf & Achilles', time: '3:45', sub: 'Heel Press' }},
          {{ icon: '✨', name: 'Full Body Release', time: '4:45', sub: 'Great Ride!' }}
        ];
        stretchList.forEach(s => {{
          const card = document.createElement('div');
          card.className = 'mov-card';
          card.innerHTML = '<div style="font-size:1.65rem; line-height:1; margin-bottom:2px;">' + s.icon + '</div>' +
            '<div style="text-align:left;">' +
              '<div style="font-weight:800; font-size:0.92rem; color:#fff;">' + s.name + '</div>' +
              '<div style="color:var(--accent-cyan); font-weight:700; font-family:Outfit,sans-serif; font-size:0.80rem;">' + s.time + ' • ' + s.sub + '</div>' +
            '</div>';
          strip.appendChild(card);
        }});
      }} else {{
        (t.movements || []).forEach(m => {{
          if (m && m.name && SYMBOL_ICONS[m.name]) {{
            const card = document.createElement('div');
            card.className = 'mov-card';
            card.innerHTML = '<img src="' + SYMBOL_ICONS[m.name] + '" alt="' + m.name + '"><div style="text-align:left;"><div style="font-weight:800; font-size:1.05rem; color:#fff;">' + m.name + '</div><div style="color:var(--accent-cyan); font-weight:800; font-family:Outfit,sans-serif; font-size:0.95rem;">' + (m.time || '') + '</div></div>';
            strip.appendChild(card);
          }}
        }});
      }}

      if (t.audioBase64) {{
        if (!blobUrls[curIdx]) {{
          blobUrls[curIdx] = b64ToBlobUrl(t.audioBase64);
        }}
        audio.src = blobUrls[curIdx];
      }} else {{
        audio.src = 'audio/track' + (curIdx + 1) + '.mp3';
      }}

      document.getElementById('progressFill').style.width = '0%';
      document.getElementById('curTimeDisplay').textContent = '00:00';
      document.getElementById('remTimeDisplay').textContent = '-' + (t.duration || '05:00');
      document.getElementById('statusDisplay').textContent = 'Ready';

      if (autoPlay) {{
        togglePlay();
      }} else {{
        isPlaying = false;
        stopSynthMetronome();
        stopSynthTimer();
        document.getElementById('playBtn').textContent = '▶ Play Workout';
        document.getElementById('cadenceBox').classList.remove('pulse-ring');
      }}
    }}

    let synthInterval = null;
    let synthTimerInterval = null;
    let synthStartTime = 0;

    function startSynthMetronome(bpmVal) {{
      stopSynthMetronome();
      const bpm = parseInt(bpmVal) || 120;
      const intervalMs = (60 / bpm) * 1000;
      
      synthInterval = setInterval(() => {{
        if (!isPlaying) return;
        try {{
          initAudioContext();
          if (!audioCtx) return;
          const osc = audioCtx.createOscillator();
          const gain = audioCtx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(587.33, audioCtx.currentTime);
          gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.08);
          osc.connect(gain);
          gain.connect(audioCtx.destination);
          osc.start();
          osc.stop(audioCtx.currentTime + 0.08);
        }} catch(e) {{}}
      }}, intervalMs);
    }}

    function stopSynthMetronome() {{
      if (synthInterval) {{
        clearInterval(synthInterval);
        synthInterval = null;
      }}
    }}

    function startSynthTimer() {{
      stopSynthTimer();
      synthStartTime = Date.now();
      synthTimerInterval = setInterval(() => {{
        if (!isPlaying) return;
        if (audio && !audio.paused && audio.currentTime > 0) return;
        
        const elapsedSecs = (Date.now() - synthStartTime) / 1000;
        const t = CLASS_TRACKS[curIdx];
        const durSecs = parseTimestampSecs(t ? t.duration : '05:00') || 300;
        
        const pct = Math.min(100, (elapsedSecs / durSecs) * 100);
        document.getElementById('progressFill').style.width = pct + '%';

        const curM = Math.floor(elapsedSecs / 60);
        const curS = Math.floor(elapsedSecs % 60);
        const rem = Math.max(0, durSecs - elapsedSecs);
        const remM = Math.floor(rem / 60);
        const remS = Math.floor(rem % 60);

        document.getElementById('curTimeDisplay').textContent = curM + ':' + (curS < 10 ? '0' : '') + curS;
        document.getElementById('remTimeDisplay').textContent = '-' + remM + ':' + (remS < 10 ? '0' : '') + remS;

        highlightMovement(elapsedSecs);

        if (elapsedSecs >= durSecs) {{
          nextTrack();
        }}
      }}, 200);
    }}

    function stopSynthTimer() {{
      if (synthTimerInterval) {{
        clearInterval(synthTimerInterval);
        synthTimerInterval = null;
      }}
    }}

    function togglePlay() {{
      initAudioContext();
      if (!isPlaying) {{
        audio.play().then(() => {{
          isPlaying = true;
          stopSynthMetronome();
          stopSynthTimer();
          document.getElementById('playBtn').textContent = '⏸ Pause';
          document.getElementById('statusDisplay').textContent = 'Playing Music';
          document.getElementById('cadenceBox').classList.add('pulse-ring');
          updateMetronomeState();
        }}).catch(e => {{
          console.log('MP3 unavail, starting Metronome beat mode:', e);
          isPlaying = true;
          const trk = CLASS_TRACKS[curIdx];
          startSynthMetronome(trk ? trk.bpm : 120);
          startSynthTimer();
          document.getElementById('playBtn').textContent = '⏸ Pause';
          document.getElementById('statusDisplay').textContent = 'Playing (Metronome ' + (trk ? trk.bpm : 120) + ' BPM)';
          document.getElementById('cadenceBox').classList.add('pulse-ring');
        }});
      }} else {{
        audio.pause();
        stopSynthMetronome();
        stopSynthTimer();
        isPlaying = false;
        document.getElementById('playBtn').textContent = '▶ Play Workout';
        document.getElementById('statusDisplay').textContent = 'Paused';
        document.getElementById('cadenceBox').classList.remove('pulse-ring');
        updateMetronomeState();
      }}
    }}

    function nextTrack() {{
      if (curIdx < CLASS_TRACKS.length - 1) {{ loadTrack(curIdx + 1, true); }}
    }}

    function prevTrack() {{
      if (curIdx > 0) {{ loadTrack(curIdx - 1, true); }}
    }}

    function onEnded() {{
      if (curIdx < CLASS_TRACKS.length - 1) {{ nextTrack(); }}
      else {{
        isPlaying = false;
        document.getElementById('playBtn').textContent = '▶ Play';
        document.getElementById('statusDisplay').textContent = 'Class Completed! 🎉';
        document.getElementById('cadenceBox').classList.remove('pulse-ring');
        updateMetronomeState();
      }}
    }}

    function onTimeUpdate() {{
      if (!audio || !audio.duration) return;
      const cur = audio.currentTime;
      const dur = audio.duration;
      const pct = (cur / dur) * 100;
      document.getElementById('progressFill').style.width = pct + '%';

      const curM = Math.floor(cur / 60);
      const curS = Math.floor(cur % 60);
      const rem = Math.max(0, dur - cur);
      const remM = Math.floor(rem / 60);
      const remS = Math.floor(rem % 60);

      document.getElementById('curTimeDisplay').textContent = curM + ':' + (curS < 10 ? '0' : '') + curS;
      document.getElementById('remTimeDisplay').textContent = '-' + remM + ':' + (remS < 10 ? '0' : '') + remS;
      highlightMovement(cur);
      updateTotalClassTimer(cur);
    }}

    function seekAudio(e) {{
      if (!audio || !audio.duration) return;
      const bar = document.querySelector('.progress-bar-wrap');
      const rect = bar.getBoundingClientRect();
      const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      audio.currentTime = pct * audio.duration;
    }}

    function parseTimestampSecs(timeStr) {{
      if (!timeStr) return 0;
      let str = String(timeStr).trim().toLowerCase();
      if (str.includes(':')) {{
        const [mins, secs] = str.split(':').map(Number);
        return (mins || 0) * 60 + (secs || 0);
      }}
      if (str.includes('s')) {{
        return parseInt(str) || 0;
      }}
      return parseInt(str) || 0;
    }}

    function highlightMovement(curSec) {{
      const isLast = (curIdx === CLASS_TRACKS.length - 1);
      let startTimes = [];
      let movNames = [];

      if (isLast) {{
        startTimes = [0, 90, 165, 225, 285];
        movNames = ['Chest & Shoulders', 'Hamstring Stretch', 'Quadriceps Stretch', 'Calf & Achilles', 'Full Body Release'];
      }} else {{
        const t = CLASS_TRACKS[curIdx];
        if (!t || !t.movements) return;

        const validMovs = (t.movements || []).filter(m => m && m.name);
        if (validMovs.length === 0) return;

        startTimes = validMovs.map(m => parseTimestampSecs(m.time));
        movNames = validMovs.map(m => m.name);
      }}

      let activeIdx = 0;
      for (let i = 0; i < startTimes.length; i++) {{
        if (curSec >= startTimes[i]) {{
          activeIdx = i;
        }} else {{
          break;
        }}
      }}

      if (activeIdx !== prevActiveMovIdx && prevActiveMovIdx !== -1) {{
        playCountdownBeep(true);
      }}
      prevActiveMovIdx = activeIdx;

      let flashIdx = -1;
      let nextIndex = activeIdx + 1;

      const bannerCurrent = document.getElementById('movBannerCurrent');
      const bannerNext = document.getElementById('movBannerNext');
      const banner = document.getElementById('movBanner');

      if (movNames[activeIdx] && bannerCurrent) {{
        bannerCurrent.textContent = '⚡ CURRENT: ' + movNames[activeIdx];
      }}

      if (nextIndex < startTimes.length) {{
        const timeUntilNext = startTimes[nextIndex] - curSec;
        if (timeUntilNext <= 10 && timeUntilNext > 0) {{
          flashIdx = nextIndex;
          const secLeft = Math.ceil(timeUntilNext);
          if (bannerNext) {{
            bannerNext.textContent = '▶ NEXT IN ' + secLeft + 's: ' + movNames[nextIndex] + ' ⚡';
            bannerNext.style.display = 'inline';
          }}
          if (banner) banner.classList.add('warning-flash');

          if (secLeft <= 3 && secLeft !== lastBeepSec) {{
            lastBeepSec = secLeft;
            playCountdownBeep(false);
          }}
        }} else {{
          if (bannerNext) bannerNext.style.display = 'none';
          if (banner) banner.classList.remove('warning-flash');
          lastBeepSec = -1;
        }}
      }} else {{
        if (bannerNext) bannerNext.style.display = 'none';
        if (banner) banner.classList.remove('warning-flash');
        lastBeepSec = -1;
      }}

      const cards = document.querySelectorAll('.mov-card');
      cards.forEach((c, idx) => {{
        if (idx === activeIdx) {{
          c.classList.add('mov-active');
          c.classList.remove('mov-upcoming-flash');
        }} else if (idx === flashIdx) {{
          c.classList.remove('mov-active');
          c.classList.add('mov-upcoming-flash');
        }} else {{
          c.classList.remove('mov-active');
          c.classList.remove('mov-upcoming-flash');
        }}
      }});
    }}

    window.onload = init;
  </script>
</body>
</html>
"""

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Range, Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range, Content-Length, Accept-Ranges, Content-Disposition'
    response.headers['Accept-Ranges'] = 'bytes'
    return response

SAVED_TRACKS_FILE = os.path.join(PROJECT_DIR, "saved_tracks_library.json")

def load_saved_tracks():
    if os.path.exists(SAVED_TRACKS_FILE):
        try:
            with open(SAVED_TRACKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print("Error reading saved tracks file:", e)
    return {}

def save_saved_tracks(tracks_dict):
    try:
        with open(SAVED_TRACKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tracks_dict, f, indent=2)
        return True
    except Exception as e:
        print("Error writing saved tracks file:", e)
        return False

@app.route('/api/tracks/library', methods=['GET', 'OPTIONS'])
def get_saved_tracks():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    library = load_saved_tracks()
    return jsonify({'success': True, 'tracks': library})

@app.route('/api/tracks/save', methods=['POST', 'OPTIONS'])
def save_track_preset():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    data = request.get_json(silent=True) or {}
    track = data.get('track')
    if not track or not track.get('name'):
        return jsonify({'error': 'Invalid track payload'}), 400

    library = load_saved_tracks()
    key = track.get('name')
    library[key] = track
    save_saved_tracks(library)
    return jsonify({'success': True, 'message': f"Saved '{track.get('name')}' to library", 'key': key})

@app.route('/api/tracks/delete', methods=['POST', 'OPTIONS'])
def delete_track_preset():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    data = request.get_json(silent=True) or {}
    key = data.get('key') or data.get('name')
    if not key:
        return jsonify({'error': 'Missing track key'}), 400

    library = load_saved_tracks()
    if key in library:
        del library[key]
        save_saved_tracks(library)
        return jsonify({'success': True, 'message': f"Deleted '{key}' from library"})
    return jsonify({'error': 'Track key not found'}), 404

@app.route('/')
def index():
    return send_from_directory('.', 'Spinning Class Builder.html')

@app.route('/api/musicbee/playlists', methods=['GET', 'OPTIONS'])
def get_musicbee_playlists():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    playlists = []
    if os.path.exists(MUSICBEE_PLAYLIST_DIR):
        for f in sorted(os.listdir(MUSICBEE_PLAYLIST_DIR)):
            if f.lower().endswith(('.m3u', '.m3u8')):
                full_path = os.path.join(MUSICBEE_PLAYLIST_DIR, f)
                track_count = 0
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as pfile:
                        for line in pfile:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                track_count += 1
                except Exception:
                    pass
                name = os.path.splitext(f)[0]
                playlists.append({
                    'name': name,
                    'filename': f,
                    'path': full_path,
                    'track_count': track_count
                })
    return jsonify({'playlists': playlists})

@app.route('/api/musicbee/import', methods=['GET', 'POST', 'OPTIONS'])
def import_musicbee_playlist():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    raw_content = None
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        playlist_name = data.get('name', '8n12')
        m3u_path = data.get('path', '')
        raw_content = data.get('fileContent', None)
    else:
        playlist_name = request.args.get('name', '8n12')
        m3u_path = request.args.get('path', '')
    
    if not m3u_path and os.path.exists(MUSICBEE_PLAYLIST_DIR):
        for ext in ['', '.m3u', '.m3u8', '.mbp']:
            cand = os.path.join(MUSICBEE_PLAYLIST_DIR, f"{playlist_name}{ext}")
            if os.path.exists(cand):
                m3u_path = cand
                break
        if not m3u_path:
            for f in os.listdir(MUSICBEE_PLAYLIST_DIR):
                if os.path.splitext(f)[0].lower() == playlist_name.lower():
                    m3u_path = os.path.join(MUSICBEE_PLAYLIST_DIR, f)
                    break

    if not m3u_path or not os.path.exists(m3u_path):
        return jsonify({'error': f'Playlist not found at {m3u_path}'}), 404

    paths = []
    if raw_content:
        # User uploaded file content from browser browse
        found_paths = re.findall(r'[A-Za-z]:\\[^:\*\?"<>\|\r\n\t]+\.(?:mp3|flac|m4a|wav|wma)', raw_content, re.IGNORECASE)
        for p in found_paths:
            clean_p = p.strip()
            if os.path.exists(clean_p) and clean_p not in paths:
                paths.append(clean_p)
        if not paths:
            for line in raw_content.splitlines():
                line = line.strip()
                if line and not line.startswith('#') and os.path.exists(line):
                    paths.append(line)
    elif m3u_path.lower().endswith('.mbp'):
        with open(m3u_path, 'rb') as f:
            raw_bytes = f.read()
            raw_text = raw_bytes.decode('utf-8', errors='ignore')
            found_paths = re.findall(r'[A-Za-z]:\\[^:\*\?"<>\|\r\n\t]+\.(?:mp3|flac|m4a|wav|wma)', raw_text, re.IGNORECASE)
            for p in found_paths:
                clean_p = p.strip()
                if os.path.exists(clean_p) and clean_p not in paths:
                    paths.append(clean_p)
    else:
        with open(m3u_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if os.path.exists(line):
                        paths.append(line)

    tracks = []
    for idx, path in enumerate(paths):
        filename = os.path.basename(path)
        clean = os.path.splitext(filename)[0]
        clean = re.sub(r'^[0-9\-_ ]+-\s*', '', clean).strip()

        dur_str = "05:00"
        dur_sec = 300
        try:
            audio_info = MP3(path)
            dur_sec = audio_info.info.length
            mins = int(dur_sec // 60)
            secs = int(dur_sec % 60)
            dur_str = f"{mins:02d}:{secs:02d}"
        except Exception:
            pass

        bpm = None
        artist = "Artist"
        title = clean

        try:
            id3 = ID3(path)
            if 'TBPM' in id3:
                val = str(id3['TBPM']).strip()
                try:
                    parsed_val = round(float(val))
                    if 50 <= parsed_val <= 220:
                        bpm = parsed_val
                except Exception:
                    pass
            if 'TIT2' in id3 and str(id3['TIT2']).strip():
                title = str(id3['TIT2']).strip()
            if 'TPE1' in id3 and str(id3['TPE1']).strip():
                artist = str(id3['TPE1']).strip()
        except Exception:
            pass

        if not bpm:
            # Check explicit BPM filename patterns
            patterns = [
                r'\((\d{2,3})\s*BPM\)',
                r'(?:slow\s+at|at|@)\s*(\d{2,3})',
                r'(\d{2,3})\s*bpm',
                r'\[(\d{2,3})\s*bpm\]'
            ]
            for pat in patterns:
                m = re.search(pat, filename, re.IGNORECASE)
                if m:
                    num = int(m.group(1))
                    if 50 <= num <= 220:
                        bpm = num
                        break

        if not bpm:
            # Use librosa audio analysis if available
            try:
                import librosa
                y, sr = librosa.load(path, sr=22050, duration=100, offset=30)
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                detected = float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo)
                if 50 <= detected <= 220:
                    bpm = round(detected)
            except Exception:
                pass

        if not bpm:
            bpm = 138

        if "find yourself" in clean.lower():
            title = "Find Yourself"
            artist = "John O'Callaghan (Original Mix)"
        elif "nebula" in clean.lower():
            title = "Nebula"
            artist = "Down-tempo Cool-down"
        elif " - " in clean and (artist == "Artist" or not artist):
            parts = clean.split(" - ")
            if "unknown artist" in parts[1].lower():
                title = parts[0].strip()
                artist = "Unknown Artist"
            else:
                artist, title = parts[0].strip(), parts[1].strip()

        is_last_track = (idx == len(paths) - 1)
        if "black velvet" in clean.lower():
            title = "Black Velvet"
            artist = "Alannah Myles"
            bpm = 92

        if is_last_track:
            zone = "Recovery"
            cadence = "Easy Spin & Stretch"
            if bpm == 138:
                bpm = 92
            cues = "Down-tempo cool-down. Lower heart rate with an easy pedal spin, then dismount and full-body stretch out."
            movements = [
                {"name": "Seated Flat", "time": "0:00"},
                None, None, None, None, None
            ]
        elif bpm > 110:
            rpm = round(bpm / 2)
            if 60 <= rpm <= 80:
                cadence = f"{rpm} RPM (Climb)"
                zone = "Strength"
                half_time = f"{int(dur_sec//120)}:{int((dur_sec%120)//2):02d}" if dur_sec > 60 else "1:30"
                movements = [
                    {"name": "Seated Climb", "time": "0:00"},
                    {"name": "Standing Climb", "time": half_time},
                    None, None, None, None
                ]
            else:
                cadence = f"{rpm} RPM (Seated Flat)"
                zone = "Endurance"
                half_time = f"{int(dur_sec//120)}:{int((dur_sec%120)//2):02d}" if dur_sec > 60 else "1:30"
                movements = [
                    {"name": "Seated Flat", "time": "0:00"},
                    {"name": "Running with Resistance", "time": half_time},
                    None, None, None, None
                ]
            cues = f"{bpm} BPM > 110 -> Half-time cadence {cadence}. Focus on powerful pedal strokes."
        else:
            rpm = round(bpm)
            cadence = f"{rpm} RPM (Seated Flat)"
            zone = "Endurance"
            half_time = f"{int(dur_sec//120)}:{int((dur_sec%120)//2):02d}" if dur_sec > 60 else "1:00"
            movements = [
                {"name": "Seated Flat", "time": "0:00"},
                {"name": "Running with Resistance", "time": half_time},
                None, None, None, None
            ]
            cues = f"{bpm} BPM <= 110 -> Direct cadence {cadence}. Focus on smooth, continuous pedaling."

        if not is_last_track and "climb" in path.lower():
            zone = "Strength"
            if rpm >= 60 and rpm <= 80:
                cadence = f"{rpm} RPM (Climb)"

        tracks.append({
            'id': f"t{idx+1}",
            'name': title,
            'artist': artist,
            'bpm': str(bpm),
            'duration': dur_str,
            'cadence': cadence,
            'zone': zone,
            'movements': movements,
            'cues': cues,
            'filePath': path
        })

    class_data = {
        'title': f"{playlist_name} - Trance Class",
        'instructor': "Simon",
        'energyZone': "Strength",
        'targetDuration': str(max(45, int(sum(int(t['duration'].split(':')[0])*60 + int(t['duration'].split(':')[1]) for t in tracks) // 60))),
        'tracks': tracks,
        'playlistName': playlist_name
    }

    return jsonify({'success': True, 'classData': class_data})

@app.route('/api/workout/export-embedded', methods=['GET', 'POST', 'OPTIONS'])
def export_embedded_workout():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    data = {}
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json(silent=True) or {}
        elif 'payload' in request.form:
            try:
                data = json.loads(request.form['payload'])
            except Exception:
                data = {}
        else:
            data = request.get_json(silent=True) or {}
    else:
        title = request.args.get('title', 'Spinning_Workout')
        data = {'classData': {'title': title}}

    class_data = data.get('classData', {})
    html_content = generate_embedded_html(class_data)

    raw_title = class_data.get('title', 'Spinning_Workout')
    safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', raw_title)
    filename = f"{safe_title}_Workout.html"

    # Safely write to disk in binary mode without locking crashes
    try:
        save_path = os.path.join(PROJECT_DIR, filename)
        with open(save_path, 'wb') as f:
            f.write(html_content.encode('utf-8'))
    except Exception as e:
        print("Save warning:", e)

    return Response(
        html_content,
        mimetype="text/html",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

github_push_status = {
    'status': 'idle',
    'message': '',
    'last_push_time': None
}

def _async_git_push(git_msg):
    global github_push_status
    github_push_status['status'] = 'pushing'
    github_push_status['message'] = 'Pushing 85MB payload to GitHub...'
    try:
        if not os.path.exists(os.path.join(PROJECT_DIR, ".git")):
            subprocess.run(["git", "init"], cwd=PROJECT_DIR, check=True)

        subprocess.run(["git", "add", "-f", "Latest_Spin_Class_Workout.html", "index.html", "README.md", ".gitignore"], cwd=PROJECT_DIR, check=True)
        subprocess.run(["git", "commit", "-m", git_msg], cwd=PROJECT_DIR, capture_output=True)

        res = subprocess.run(["git", "remote", "get-url", "origin"], cwd=PROJECT_DIR, capture_output=True, text=True)
        remote_url = res.stdout.strip()

        if remote_url:
            push_res = subprocess.run(["git", "push", "-u", "origin", "main"], cwd=PROJECT_DIR, capture_output=True, text=True)
            if push_res.returncode == 0 or "Everything up-to-date" in push_res.stderr:
                github_push_status['status'] = 'success'
                github_push_status['message'] = 'Pushed successfully to GitHub! Live site will update in ~1-2 mins.'
            else:
                github_push_status['status'] = 'error'
                github_push_status['message'] = f"Push warning: {push_res.stderr[:200]}"
        else:
            github_push_status['status'] = 'success'
            github_push_status['message'] = 'Saved and committed locally.'
    except Exception as e:
        github_push_status['status'] = 'error'
        github_push_status['message'] = str(e)
    github_push_status['last_push_time'] = time.strftime('%H:%M:%S')

@app.route('/api/github/publish', methods=['GET', 'POST', 'OPTIONS'])
def publish_to_github():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    data = request.get_json(silent=True) or {}
    class_data = data.get('classData', {})

    # Generate the full embedded HTML and save as Latest_Spin_Class_Workout.html and index.html (overwrites)
    html_content = generate_embedded_html(class_data)

    latest_path = os.path.join(PROJECT_DIR, "Latest_Spin_Class_Workout.html")
    index_path = os.path.join(PROJECT_DIR, "index.html")

    with open(latest_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    size_mb = round(os.path.getsize(latest_path) / 1024 / 1024, 1)

    git_msg = "Updated Latest Spin Class (Handlebar Mobile Workout)"
    thread = threading.Thread(target=_async_git_push, args=(git_msg,))
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'message': f'Overwritten and saved Latest Spin Class ({size_mb} MB)! Uploading to GitHub in background...',
        'pushed': True,
        'size_mb': size_mb
    })

@app.route('/api/github/status', methods=['GET'])
def github_status():
    return jsonify(github_push_status)

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('.', path, conditional=True)

if __name__ == '__main__':
    port = 8080
    print(f"Flask Spinning Server starting on http://192.168.68.52:{port}/")
    app.run(host='0.0.0.0', port=port, threaded=True)
