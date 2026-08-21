import os
import json
import base64
import re

# Read Base64 Spinning Symbols
icon_dir = r"c:\Data_Projects\Spinning\Spinning Symbols"
symbols_dict = {}
for fname in sorted(os.listdir(icon_dir)):
    if fname.endswith(".png"):
        name = os.path.splitext(fname)[0]
        with open(os.path.join(icon_dir, fname), "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            symbols_dict[name] = f"data:image/png;base64,{b64}"

symbols_json = json.dumps(symbols_dict)

sample_tracks = [
    {
        "name": "The Answer",
        "artist": "DJ Stigma",
        "bpm": "118",
        "duration": "09:55",
        "cadence": "59 RPM (Climb)",
        "zone": "Recovery",
        "movements": [
            { "name": "Seated Climb", "time": "3:00" },
            { "name": "Standing Climb", "time": "2:00" },
            { "name": "Seated Climb", "time": "2:00" },
            { "name": "Standing Climb", "time": "2:55" }
        ],
        "cues": "118 BPM > 110 -> Half-time cadence 59 RPM. Progressive climb building warm-up resistance."
    },
    {
        "name": "Kashmir",
        "artist": "Puff Daddy & Jimmy Page",
        "bpm": "162",
        "duration": "06:02",
        "cadence": "81 RPM (Seated Flat)",
        "zone": "Strength",
        "movements": [
            { "name": "Seated Flat", "time": "2:00" },
            { "name": "Running with Resistance", "time": "2:00" },
            { "name": "Seated Flat", "time": "1:00" },
            { "name": "Running with Resistance", "time": "1:02" }
        ],
        "cues": "162 BPM > 110 -> Half-time cadence 81 RPM. Strong rhythmic Seated Flat with moderate resistance."
    },
    {
        "name": "Drifting away",
        "artist": "Lange feat. Skye",
        "bpm": "138",
        "duration": "05:56",
        "cadence": "69 RPM (Climb)",
        "zone": "Endurance",
        "movements": [
            { "name": "Seated Climb", "time": "2:00" },
            { "name": "Standing Climb", "time": "1:30" },
            { "name": "Running with Resistance", "time": "1:00" },
            { "name": "Standing Climb", "time": "1:26" }
        ],
        "cues": "138 BPM > 110 -> Half-time cadence 69 RPM. Heavy steady hill climb in and out of the saddle."
    },
    {
        "name": "Hung Up",
        "artist": "Madonna (SDP Extended Dub)",
        "bpm": "129",
        "duration": "05:54",
        "cadence": "65 RPM (Climb / Jumps)",
        "zone": "Interval",
        "movements": [
            { "name": "Seated Climb", "time": "1:30" },
            { "name": "Jumps on a Hill", "time": "1:30" },
            { "name": "Standing Climb", "time": "1:30" },
            { "name": "Jumps on a Hill", "time": "1:24" }
        ],
        "cues": "129 BPM > 110 -> Half-time cadence 65 RPM. 8-count jumps on a hill with high resistance."
    },
    {
        "name": "Hallowed Be Thy Name",
        "artist": "Iron Maiden",
        "bpm": "103",
        "duration": "07:11",
        "cadence": "103 RPM (Seated Flat)",
        "zone": "Strength",
        "movements": [
            { "name": "Seated Flat", "time": "2:00" },
            { "name": "Running with Resistance", "time": "2:00" },
            { "name": "Seated Flat", "time": "1:30" },
            { "name": "Running with Resistance", "time": "1:41" }
        ],
        "cues": "103 BPM <= 110 -> Direct cadence 103 RPM. High tempo fast flat & running with resistance."
    },
    {
        "name": "Find Yourself",
        "artist": "John O'Callaghan (Original Mix)",
        "bpm": "136",
        "duration": "06:03",
        "cadence": "68 RPM (Climb)",
        "zone": "Race Day",
        "movements": [
            { "name": "Seated Climb", "time": "1:30" },
            { "name": "Standing Climb", "time": "1:30" },
            { "name": "Sprints on a Hill", "time": "30s x 2" },
            { "name": "Standing Climb", "time": "1:00" },
            { "name": "Sprints on a Hill", "time": "30s x 2" }
        ],
        "cues": "136 BPM > 110 -> Half-time cadence 68 RPM. Heavy climb with 30-second all-out sprint surges."
    },
    {
        "name": "Nebula - one workout",
        "artist": "Cool-down",
        "bpm": "92",
        "duration": "04:46",
        "cadence": "92 RPM (Seated Flat)",
        "zone": "Recovery",
        "movements": [
            { "name": "Seated Flat", "time": "4:46" }
        ],
        "cues": "92 BPM <= 110 -> Direct cadence 92 RPM. Easy spin flat road, lower heart rate to resting."
    }
]

tracks_json = json.dumps(sample_tracks)

mobile_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <title>Spinning® Handlebar Cockpit</title>
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
        <h1>🚴 Spin 001 - High Energy Endurance <span style="font-size:0.7rem; background:rgba(0,229,255,0.15); color:var(--accent-cyan); padding:2px 8px; border-radius:10px; border:1px solid rgba(0,229,255,0.3); vertical-align:middle; margin-left:8px; font-weight:700;">v3.5.0</span></h1>
      </div>
      <div style="display:flex; gap:10px; align-items:center;">
        <label style="cursor:pointer; font-size:0.75rem; background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.2); color:var(--accent-cyan); padding:4px 10px; border-radius:8px; font-weight:700;" title="Attach local MP3 music files from your phone or PC">
          🎵 Load MP3s <input type="file" multiple accept="audio/*,.mp3,.m4a" style="display:none;" onchange="handleCockpitAudioUpload(event)" />
        </label>
        <div class="clock-pill" id="liveClock">00:00</div>
      </div>
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
          <div class="metric-val" id="trackNumVal">1 / {len(sample_tracks)}</div>
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

    function loadTrack(idx, autoPlay = true) {{
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
      if (document.getElementById('targetRpeVal')) {{
        document.getElementById('targetRpeVal').textContent = rpeDisplay;
      }}
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
      (t.movements || []).forEach(m => {{
        if (m && m.name && SYMBOL_ICONS[m.name]) {{
          const card = document.createElement('div');
          card.className = 'mov-card';
          card.innerHTML = '<img src="' + SYMBOL_ICONS[m.name] + '" alt="' + m.name + '"><div style="text-align:left;"><div style="font-weight:800; font-size:1.05rem; color:#fff;">' + m.name + '</div><div style="color:var(--accent-cyan); font-weight:800; font-family:Outfit,sans-serif; font-size:0.95rem;">' + (m.time || '') + '</div></div>';
          strip.appendChild(card);
        }}
      }});

      if (t.audioUrl) {{
        audio.src = t.audioUrl;
      }} else if (t.audioBase64) {{
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

    function handleCockpitAudioUpload(e) {{
      const files = Array.from(e.target.files || []);
      if (files.length === 0) return;
      files.forEach((file, idx) => {{
        if (CLASS_TRACKS[idx]) {{
          CLASS_TRACKS[idx].audioUrl = URL.createObjectURL(file);
        }}
      }});
      loadTrack(curIdx, false);
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
        }}).catch(e => {{
          console.log('MP3 unavail, starting Metronome beat mode:', e);
          isPlaying = true;
          const trk = CLASS_TRACKS[curIdx];
          startSynthMetronome(trk ? trk.bpm : 120);
          startSynthTimer();
          document.getElementById('playBtn').textContent = '⏸ Pause';
          document.getElementById('statusDisplay').textContent = 'Playing (Metronome ' + (trk ? trk.bpm : 120) + ' BPM)';
        }});
      }} else {{
        audio.pause();
        stopSynthMetronome();
        stopSynthTimer();
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
      const t = CLASS_TRACKS[curIdx];
      if (!t || !t.movements) return;

      const validMovs = (t.movements || []).filter(m => m && m.name);
      if (validMovs.length === 0) return;

      const startTimes = validMovs.map(m => parseTimestampSecs(m.time));
      const movNames = validMovs.map(m => m.name);

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

with open(r"c:\Data_Projects\Spinning\index.html", "w", encoding="utf-8") as f:
    f.write(mobile_html)

print("SUCCESS: Created finished mobile workout index.html ready for GitHub Pages!")
