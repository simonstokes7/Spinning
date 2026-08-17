import os
import json
import re
import base64
import subprocess
from flask import Flask, send_from_directory, jsonify, request, Response
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

app = Flask(__name__, static_folder='.', static_url_path='')

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

        b64_audio = ""
        if audio_path and os.path.exists(audio_path):
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
  <title>🚴 Latest Spin Class - Handlebar Cockpit</title>
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
        <h1>🚴 Latest Spin Class</h1>
      </div>
      <div class="clock-pill" id="liveClock">00:00</div>
    </header>

    <div class="cockpit">
      <div class="zone-badge" id="zoneBadge">STRENGTH ZONE</div>
      <div>
        <div class="song-title" id="songTitle"></div>
        <div class="song-artist" id="songArtist"></div>
      </div>

      <div class="metrics-row">
        <div class="metric-box">
          <div class="metric-lbl">Track</div>
          <div class="metric-val" id="trackNumVal">1 / {len(tracks_data_with_audio)}</div>
        </div>
        <div class="metric-box">
          <div class="metric-lbl">Song BPM</div>
          <div class="metric-val" id="bpmVal" style="color:var(--accent-cyan)"></div>
        </div>
        <div class="metric-box">
          <div class="metric-lbl">Cadence</div>
          <div class="metric-val" id="cadenceVal" style="font-size:1.35rem; color:#fff;"></div>
        </div>
        <div class="metric-box">
          <div class="metric-lbl">Duration</div>
          <div class="metric-val" id="durationVal"></div>
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

    function loadTrack(idx, autoPlay = true) {{
      curIdx = idx;
      const t = CLASS_TRACKS[curIdx];
      if (!t) return;

      document.getElementById('trackNumVal').textContent = (curIdx + 1) + ' / ' + CLASS_TRACKS.length;
      document.getElementById('songTitle').textContent = t.name;
      document.getElementById('songArtist').textContent = t.artist || '';
      document.getElementById('bpmVal').textContent = t.bpm || '--';
      document.getElementById('cadenceVal').textContent = t.cadence || '--';
      document.getElementById('durationVal').textContent = t.duration || '05:00';
      document.getElementById('cuesBox').textContent = t.cues ? '"' + t.cues + '"' : '"Focus on smooth pedal cadence."';

      const isLast = (curIdx === CLASS_TRACKS.length - 1);
      const zColor = isLast ? '#00e5ff' : (ZONE_COLORS[t.zone] || '#00e676');
      const badge = document.getElementById('zoneBadge');
      badge.textContent = isLast ? '🧘 COOL-DOWN & STRETCH' : ((t.zone || 'Endurance').toUpperCase() + ' ZONE');
      badge.style.background = zColor + '33';
      badge.style.color = zColor;
      badge.style.border = '1px solid ' + zColor;

      const strip = document.getElementById('movementsStrip');
      strip.innerHTML = '';
      (t.movements || []).forEach(m => {{
        if (m && m.name && SYMBOL_ICONS[m.name]) {{
          const card = document.createElement('div');
          card.className = 'mov-card';
          card.innerHTML = '<img src="' + SYMBOL_ICONS[m.name] + '" alt="' + m.name + '"><div style="text-align:left;"><div style="font-weight:800; font-size:1.05rem; color:#fff;">' + m.name + '</div><div style="color:var(--accent-cyan); font-weight:800; font-family:Outfit,sans-serif; font-size:0.95rem;">' + (m.time || '') + '</div></div>';
          strip.appendChild(card);
        }}
      }});

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
        audio.play().then(() => {{
          isPlaying = true;
          document.getElementById('playBtn').textContent = '⏸ Pause';
          document.getElementById('statusDisplay').textContent = 'Playing';
        }}).catch(e => console.log('Playback error:', e));
      }} else {{
        isPlaying = false;
        document.getElementById('playBtn').textContent = '▶ Play Workout';
      }}
    }}

    function togglePlay() {{
      if (audio.paused) {{
        audio.play().then(() => {{
          isPlaying = true;
          document.getElementById('playBtn').textContent = '⏸ Pause';
          document.getElementById('statusDisplay').textContent = 'Playing';
        }}).catch(e => {{
          console.log('Play failed:', e);
          document.getElementById('statusDisplay').textContent = 'Tap to retry';
        }});
      }} else {{
        audio.pause();
        isPlaying = false;
        document.getElementById('playBtn').textContent = '▶ Play Workout';
        document.getElementById('statusDisplay').textContent = 'Paused';
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
    }}

    function seekAudio(e) {{
      if (!audio || !audio.duration) return;
      const bar = document.querySelector('.progress-bar-wrap');
      const rect = bar.getBoundingClientRect();
      const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      audio.currentTime = pct * audio.duration;
    }}

    function highlightMovement(curSec) {{
      const t = CLASS_TRACKS[curIdx];
      if (!t || !t.movements) return;

      let accum = 0;
      let activeIdx = -1;

      for (let i = 0; i < t.movements.length; i++) {{
        const m = t.movements[i];
        if (!m || !m.name) continue;
        let mDur = 60;
        if (m.time) {{
          if (m.time.includes(':')) {{
            const [mins, secs] = m.time.split(':').map(Number);
            mDur = (mins || 0) * 60 + (secs || 0);
          }} else if (m.time.toLowerCase().includes('s')) {{
            mDur = parseInt(m.time) || 30;
          }}
        }}
        if (curSec >= accum && curSec < accum + mDur) {{
          activeIdx = i;
          break;
        }}
        accum += mDur;
      }}

      const cards = document.querySelectorAll('.mov-card');
      cards.forEach((c, idx) => {{
        if (idx === activeIdx) c.classList.add('mov-active');
        else c.classList.remove('mov-active');
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

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        playlist_name = data.get('name', '8n12')
        m3u_path = data.get('path', '')
    else:
        playlist_name = request.args.get('name', '8n12')
        m3u_path = request.args.get('path', '')
    
    if not m3u_path and os.path.exists(MUSICBEE_PLAYLIST_DIR):
        candidate = os.path.join(MUSICBEE_PLAYLIST_DIR, f"{playlist_name}.m3u")
        if os.path.exists(candidate):
            m3u_path = candidate

    if not m3u_path or not os.path.exists(m3u_path):
        return jsonify({'error': f'Playlist not found at {m3u_path}'}), 404

    paths = []
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
                    bpm = round(float(val))
                except Exception:
                    pass
            if 'TIT2' in id3 and str(id3['TIT2']).strip():
                title = str(id3['TIT2']).strip()
            if 'TPE1' in id3 and str(id3['TPE1']).strip():
                artist = str(id3['TPE1']).strip()
        except Exception:
            pass

        if not bpm:
            bpm_match = re.search(r'\((\d{2,3})\s*BPM\)', filename, re.IGNORECASE)
            if bpm_match:
                bpm = int(bpm_match.group(1))
            else:
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
        if is_last_track:
            zone = "Recovery"
            cadence = "Easy Spin & Stretch"
            cues = "Down-tempo cool-down. Lower heart rate with an easy pedal spin, then dismount and full-body stretch out."
            movements = [
                {"name": "Seated Flat", "time": dur_str},
                None, None, None, None, None
            ]
        elif bpm > 110:
            rpm = round(bpm / 2)
            if 60 <= rpm <= 80:
                cadence = f"{rpm} RPM (Climb)"
                zone = "Strength"
                half_time = f"{int(dur_sec//120)}:{int((dur_sec%120)//2):02d}" if dur_sec > 60 else "1:00"
                movements = [
                    {"name": "Seated Climb", "time": half_time},
                    {"name": "Standing Climb", "time": half_time},
                    None, None, None, None
                ]
            else:
                cadence = f"{rpm} RPM (Seated Flat)"
                zone = "Endurance"
                half_time = f"{int(dur_sec//120)}:{int((dur_sec%120)//2):02d}" if dur_sec > 60 else "1:00"
                movements = [
                    {"name": "Seated Flat", "time": half_time},
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
                {"name": "Seated Flat", "time": half_time},
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

    filename = "Latest_Spin_Class_Workout.html"
    save_path = os.path.join(PROJECT_DIR, filename)
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return Response(
        html_content,
        mimetype="text/html",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

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

    # Git operations
    git_msg = "Updated Latest Spin Class (Handlebar Mobile Workout)"
    try:
        if not os.path.exists(os.path.join(PROJECT_DIR, ".git")):
            subprocess.run(["git", "init"], cwd=PROJECT_DIR, check=True)

        subprocess.run(["git", "add", "-f", "Latest_Spin_Class_Workout.html", "index.html", "README.md", ".gitignore"], cwd=PROJECT_DIR, check=True)
        subprocess.run(["git", "commit", "-m", git_msg], cwd=PROJECT_DIR, capture_output=True)

        # Check if remote origin exists
        res = subprocess.run(["git", "remote", "get-url", "origin"], cwd=PROJECT_DIR, capture_output=True, text=True)
        remote_url = res.stdout.strip()

        pushed = False
        if remote_url:
            push_res = subprocess.run(["git", "push", "-u", "origin", "main"], cwd=PROJECT_DIR, capture_output=True, text=True)
            if push_res.returncode == 0 or "Everything up-to-date" in push_res.stderr:
                pushed = True

        size_mb = round(os.path.getsize(latest_path) / 1024 / 1024, 1)

        return jsonify({
            'success': True,
            'message': f'Overwritten and saved Latest Spin Class ({size_mb} MB)!',
            'pushed': pushed,
            'remote_url': remote_url,
            'size_mb': size_mb
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('.', path, conditional=True)

if __name__ == '__main__':
    port = 8080
    print(f"Flask Spinning Server starting on http://192.168.68.52:{port}/")
    app.run(host='0.0.0.0', port=port, threaded=True)
