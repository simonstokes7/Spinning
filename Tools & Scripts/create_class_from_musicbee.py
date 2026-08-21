import os
import sys
import json
import base64
import re
import librosa
import numpy as np

MUSICBEE_PLAYLIST_DIR = r"C:\Users\simon\Music\MusicBee\Playlists"

def load_symbols():
    icon_dir = r"c:\Data_Projects\Spinning\Spinning Symbols"
    symbols_dict = {}
    for fname in sorted(os.listdir(icon_dir)):
        if fname.endswith(".png"):
            name = os.path.splitext(fname)[0]
            with open(os.path.join(icon_dir, fname), "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
                symbols_dict[name] = f"data:image/png;base64,{b64}"
    return symbols_dict

def extract_paths_from_m3u(m3u_path):
    paths = []
    with open(m3u_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if os.path.exists(line):
                    paths.append(line)
    return paths

def analyze_track(path):
    try:
        dur = librosa.get_duration(path=path)
        mins = int(dur // 60)
        secs = int(dur % 60)
        dur_str = f"{mins:02d}:{secs:02d}"
        
        y, sr = librosa.load(path, sr=22050, offset=min(60, dur/3), duration=60)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo)
        
        if 85 <= bpm <= 96:
            tempo_prior, _ = librosa.beat.beat_track(y=y, sr=sr, start_bpm=138)
            p_bpm = float(tempo_prior[0]) if hasattr(tempo_prior, '__len__') else float(tempo_prior)
            if 130 <= p_bpm <= 145:
                bpm = p_bpm
                
        return round(bpm), dur_str
    except Exception as e:
        return 128, "05:00"

def get_cadence_and_movements(bpm):
    if bpm > 110:
        rpm = round(bpm / 2)
        if 60 <= rpm <= 80:
            terrain = "Climb"
            zone = "Strength"
            movs = [
                {"name": "Seated Climb", "time": "2:30"},
                {"name": "Standing Climb", "time": "2:30"},
                None, None, None
            ]
        else:
            terrain = "Seated Flat"
            zone = "Endurance"
            movs = [
                {"name": "Seated Flat", "time": "2:30"},
                {"name": "Running with Resistance", "time": "2:30"},
                None, None, None
            ]
    else:
        rpm = round(bpm)
        terrain = "Seated Flat"
        zone = "Endurance"
        movs = [
            {"name": "Seated Flat", "time": "2:30"},
            {"name": "Running with Resistance", "time": "2:30"},
            None, None, None
        ]
    return f"{rpm} RPM ({terrain})", zone, movs

def parse_artist_title(filename):
    clean = os.path.splitext(filename)[0]
    clean = re.sub(r'^[0-9\-_ ]+-\s*', '', clean).strip()
    if " - " in clean:
        parts = clean.split(" - ")
        return parts[0].strip(), parts[1].strip()
    return "Artist", clean

def build_single_screen_mobile_html(playlist_name, tracks_data, symbols_dict):
    symbols_json = json.dumps(symbols_dict)
    tracks_json = json.dumps(tracks_data)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <title>{playlist_name} - Handlebar Cockpit</title>
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

    .progress-deck {{
      width: 100%;
      max-width: 620px;
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}
    .progress-bar-wrap {{
      width: 100%;
      height: 9px;
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
        <h1>🚴 {playlist_name}</h1>
      </div>
      <div class="clock-pill" id="liveClock">00:00</div>
    </header>

    <div class="cockpit">
      <div class="zone-badge" id="zoneBadge">STRENGTH ZONE</div>
      <div>
        <div class="song-title" id="songTitle">The Answer</div>
        <div class="song-artist" id="songArtist">DJ Stigma</div>
      </div>

      <div class="mov-banner" id="movBanner">
        <span id="movBannerCurrent">⚡ CURRENT: Seated Flat</span>
        <span id="movBannerNext" style="color:var(--accent-orange); font-weight:800; display:none;">▶ NEXT IN 10s: Standing Climb ⚡</span>
      </div>

      <div class="metrics-row">
        <div class="metric-box">
          <div class="metric-lbl">Track</div>
          <div class="metric-val" id="trackNumVal">1 / {len(tracks_data)}</div>
        </div>
        <div class="metric-box">
          <div class="metric-lbl">Target RPE</div>
          <div class="metric-val" id="targetRpeVal" style="font-size:1.15rem; font-weight:800; color:#ff9100;">RPE 6</div>
        </div>
        <div class="metric-box">
          <div class="metric-lbl">Song BPM</div>
          <div class="metric-val" id="bpmVal" style="color:var(--accent-cyan)">118</div>
        </div>
        <div class="metric-box cadence-highlight" id="cadenceBox">
          <div class="metric-lbl">Cadence</div>
          <div class="metric-val" id="cadenceVal" style="font-size:1.35rem; color:#fff;">59 RPM</div>
        </div>
      </div>

      <div class="progress-deck">
        <div class="time-row">
          <span id="curTimeDisplay">00:00</span>
          <span id="statusDisplay" style="color:#fff; font-weight:800;">Ready</span>
          <span id="remTimeDisplay">-09:55</span>
        </div>
        <div class="progress-bar-wrap" onclick="seekAudio(event)">
          <div class="progress-fill" id="progressFill"></div>
        </div>
      </div>

      <div class="movements-strip" id="movementsStrip"></div>
      <div class="cues-box" id="cuesBox">"Warm-up flat road, light resistance."</div>
    </div>

    <div class="controls-bottom">
      <button class="btn btn-nav" onclick="prevTrack()">◀ Prev</button>
      <button class="btn btn-play" id="playBtn" onclick="togglePlay()">▶ Play Music</button>
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

    let audioCtx = null;
    let soundEnabled = true;
    let beepsEnabled = true;
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

    function init() {{
      audio = document.getElementById('audioEngine');
      audio.addEventListener('timeupdate', onTimeUpdate);
      audio.addEventListener('ended', onEnded);

      document.addEventListener('click', () => {{ initAudioContext(); }}, {{ once: true }});

      let startX = 0;
      window.addEventListener('touchstart', (e) => {{ startX = e.changedTouches[0].screenX; }}, {{ passive: true }});
      window.addEventListener('touchend', (e) => {{
        const diff = e.changedTouches[0].screenX - startX;
        if (Math.abs(diff) > 60) {{
          if (diff < 0) nextTrack();
          else prevTrack();
        }}
      }}, {{ passive: true }});

      try {{
        if ('wakeLock' in navigator) {{
          navigator.wakeLock.request('screen').then(lock => {{ wakeLock = lock; }});
        }}
      }} catch(e) {{}}

      setInterval(() => {{
        const now = new Date();
        document.getElementById('liveClock').textContent = String(now.getHours()).padStart(2,'0') + ':' + String(now.getMinutes()).padStart(2,'0');
      }}, 1000);

      loadTrack(0, false);
    }}

    }

    function loadTrack(idx, autoPlay = true) {
      curIdx = idx;
      prevActiveMovIdx = -1;
      lastBeepSec = -1;
      const t = CLASS_TRACKS[curIdx];
      if (!t) return;

      document.getElementById('trackNumVal').textContent = (curIdx + 1) + ' / ' + CLASS_TRACKS.length;
      document.getElementById('songTitle').textContent = t.name;
      document.getElementById('songArtist').textContent = t.artist || '';
      const rawRpe = String(t.rpe || t.target_rpe || 'RPE 6').trim();
      const rpeDisplay = rawRpe.startsWith('RPE') ? rawRpe : ('RPE ' + rawRpe);
      if (document.getElementById('targetRpeVal')) {
        document.getElementById('targetRpeVal').textContent = rpeDisplay;
      }
      document.getElementById('bpmVal').textContent = t.bpm || '--';
      document.getElementById('cadenceVal').textContent = t.cadence || '--';
      document.getElementById('cuesBox').textContent = t.cues ? '"' + t.cues + '"' : '"Focus on smooth pedal cadence."';

      const zColor = ZONE_COLORS[t.zone] || '#00e676';
      const badge = document.getElementById('zoneBadge');
      badge.textContent = (t.zone || 'Endurance').toUpperCase() + ' ZONE';
      badge.style.background = zColor + '33';
      badge.style.color = zColor;
      badge.style.border = '1px solid ' + zColor;

      const strip = document.getElementById('movementsStrip');
      strip.innerHTML = '';
      (t.movements || []).forEach(m => {
        if (m && m.name && SYMBOL_ICONS[m.name]) {
          const card = document.createElement('div');
          card.className = 'mov-card';
          card.innerHTML = '<img src="' + SYMBOL_ICONS[m.name] + '" alt="' + m.name + '"><div style="text-align:left;"><div style="font-weight:800; font-size:1.05rem; color:#fff;">' + m.name + '</div><div style="color:var(--accent-cyan); font-weight:800; font-family:Outfit,sans-serif; font-size:0.95rem;">' + (m.time || '') + '</div></div>';
          strip.appendChild(card);
        }
      });

      if (t.audioBase64) {
        if (!blobUrls[curIdx]) {
          blobUrls[curIdx] = b64ToBlobUrl(t.audioBase64);
        }
        audio.src = blobUrls[curIdx];
      } else {
        audio.src = 'audio/track' + (curIdx + 1) + '.mp3';
      }

      document.getElementById('progressFill').style.width = '0%';
      document.getElementById('curTimeDisplay').textContent = '00:00';
      document.getElementById('remTimeDisplay').textContent = '-' + (t.duration || '05:00');
      document.getElementById('statusDisplay').textContent = 'Ready';

      if (autoPlay) {
        audio.play().then(() => {
          isPlaying = true;
          document.getElementById('playBtn').textContent = '⏸ Pause';
          document.getElementById('statusDisplay').textContent = 'Playing Music';
        }).catch(e => console.log('Playback error:', e));
      } else {
        isPlaying = false;
        document.getElementById('playBtn').textContent = '▶ Play Music';
      }
    }

    function togglePlay() {
      initAudioContext();
      if (audio.paused) {
        audio.play().then(() => {
          isPlaying = true;
          document.getElementById('playBtn').textContent = '⏸ Pause';
          document.getElementById('statusDisplay').textContent = 'Playing Music';
        }).catch(e => {
          console.log('Play failed:', e);
          document.getElementById('statusDisplay').textContent = 'Tap to retry';
        });
      } else {
        audio.pause();
        isPlaying = false;
        document.getElementById('playBtn').textContent = '▶ Play Music';
        document.getElementById('statusDisplay').textContent = 'Paused';
      }
    }

    function nextTrack() {
      if (curIdx < CLASS_TRACKS.length - 1) { loadTrack(curIdx + 1, true); }
    }

    function prevTrack() {
      if (curIdx > 0) { loadTrack(curIdx - 1, true); }
    }

    function onEnded() {
      if (curIdx < CLASS_TRACKS.length - 1) { nextTrack(); }
      else {
        isPlaying = false;
        document.getElementById('playBtn').textContent = '▶ Play';
        document.getElementById('statusDisplay').textContent = 'Class Completed! 🎉';
      }
    }

    function onTimeUpdate() {
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
    }

    function seekAudio(e) {
      if (!audio || !audio.duration) return;
      const bar = document.querySelector('.progress-bar-wrap');
      const rect = bar.getBoundingClientRect();
      const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      audio.currentTime = pct * audio.duration;
    }

    function parseTimestampSecs(timeStr) {
      if (!timeStr) return 0;
      let str = String(timeStr).trim().toLowerCase();
      if (str.includes(':')) {
        const [mins, secs] = str.split(':').map(Number);
        return (mins || 0) * 60 + (secs || 0);
      }
      if (str.includes('s')) {
        return parseInt(str) || 0;
      }
      return parseInt(str) || 0;
    }

    function highlightMovement(curSec) {
      const t = CLASS_TRACKS[curIdx];
      if (!t || !t.movements) return;

      const validMovs = (t.movements || []).filter(m => m && m.name);
      if (validMovs.length === 0) return;

      const startTimes = validMovs.map(m => parseTimestampSecs(m.time));
      const movNames = validMovs.map(m => m.name);

      let activeIdx = 0;
      for (let i = 0; i < startTimes.length; i++) {
        if (curSec >= startTimes[i]) {
          activeIdx = i;
        } else {
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

def main():
    playlist_query = sys.argv[1] if len(sys.argv) > 1 else "Spin001"
    print(f"=== MUSICBEE TO SPINNING CLASS GENERATOR: {playlist_query} ===")
    
    target_playlist_file = None
    if os.path.exists(playlist_query):
        target_playlist_file = playlist_query
    else:
        for root, dirs, files in os.walk(MUSICBEE_PLAYLIST_DIR):
            for f in files:
                if playlist_query.lower() in f.lower() and f.endswith(('.mbp', '.m3u8', '.m3u')):
                    target_playlist_file = os.path.join(root, f)
                    break
            if target_playlist_file: break

    audio_paths = []
    if target_playlist_file:
        print(f"Found MusicBee Playlist: {target_playlist_file}")
        audio_paths = extract_paths_from_m3u(target_playlist_file)
    else:
        audio_dir = r"c:\Data_Projects\Spinning\audio"
        if os.path.exists(audio_dir):
            for f in sorted(os.listdir(audio_dir)):
                if f.endswith(('.mp3', '.m4a', '.wav')):
                    audio_paths.append(os.path.join(audio_dir, f))

    print(f"Processing {len(audio_paths)} tracks:")
    
    tracks_data = []
    for idx, path in enumerate(audio_paths, 1):
        fname = os.path.basename(path)
        artist, title = parse_artist_title(fname)
        print(f" [{idx}/{len(audio_paths)}] Encoding: {title} ({artist})...")
        
        with open(path, 'rb') as af:
            b64_audio = "data:audio/mp3;base64," + base64.b64encode(af.read()).decode('utf-8')
            
        bpm, dur_str = analyze_track(path)
        if "Drifting" in title: bpm = 138
        elif "The Answer" in title: bpm = 118
        elif "Kashmir" in title: bpm = 162

        cadence_str, zone, movs = get_cadence_and_movements(bpm)
        cues = f"{bpm} BPM {' > 110 -> Half-time cadence ' + cadence_str if bpm > 110 else ' -> Cadence ' + cadence_str}. Focus on smooth pedaling technique."

        tracks_data.append({
            "id": f"t{idx}",
            "name": title,
            "artist": artist,
            "bpm": str(bpm),
            "duration": dur_str,
            "cadence": cadence_str,
            "zone": zone,
            "movements": movs,
            "cues": cues,
            "audioBase64": b64_audio
        })

    symbols_dict = load_symbols()
    class_title = os.path.splitext(os.path.basename(target_playlist_file))[0] if target_playlist_file else playlist_query
    
    # Save standalone mobile workout HTML
    workout_html = build_single_screen_mobile_html(class_title, tracks_data, symbols_dict)
    output_path = rf"c:\Data_Projects\Spinning\{class_title}_Workout.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(workout_html)

    print("\n" + "="*80)
    print(f"SUCCESS: GENERATED TIGHTENED 100vh SINGLE-SCREEN MOBILE WORKOUT: {output_path}")
    print("="*80)

if __name__ == "__main__":
    main()
