# 🚴 Spinning® Class Builder & Handlebar Cockpit
## Comprehensive System Guide & Instructor Manual

---

## 🛠️ PART 1: Technical Architecture & System Overview (For Admin / Simon)

### 1. Dual Execution Modes

The Spinning® Class Builder application is designed to operate seamlessly in two distinct execution environments:

#### A. Local Server / Admin Mode (`spinning_server.py`)
- **Environment**: Running locally on your PC via Python Flask (`http://localhost:8080` or `http://192.168.68.52:8080`).
- **Capabilities**:
  - Full access to local PC filesystem and MusicBee playlist directory (`Playlists/`).
  - Enables the **`🐙 Send to GitHub`** button on the toolbar.
  - Automatically bakes local audio files into `Latest_Spin_Class_Workout.html` and executes `git push` to deploy updates to GitHub Pages in the background.

#### B. Hosted Client Mode (`simonstokes7.github.io`)
- **Environment**: Running in a web browser on any device (laptop, iPad, phone) hosted on GitHub Pages.
- **Capabilities**:
  - 100% client-side HTML5/JavaScript application with zero backend requirements.
  - Automatically hides developer-only server buttons (e.g., `🐙 Send to GitHub`) when viewed on `github.io` to avoid server error popups for guest users.
  - All class profile drafts, saved classes, and track library presets are stored in browser `localStorage`.
  - Enables guest instructors to build, customize, save, import/export JSON backups, and play classes completely locally or offline.

---

### 2. Data Storage & Persistence

The application uses a 3-layer persistence strategy:

1. **Browser LocalStorage**:
   - `spinning_builder_class_v30`: Active class draft. Automatically saves on every edit.
   - `spinning_saved_classes_library`: Stored collection of full class profiles.
   - `spinning_saved_tracks_library`: Stored collection of individual pre-engineered track presets (BPM, Cadence, Energy Zone, Target RPE, 6 movement slots, cues).
2. **JSON Import / Export**:
   - Allows instructors to export class profiles (`.json`) or track libraries (`.json`) to back up their work or share class templates with other instructors.
3. **Standalone HTML Workout Export**:
   - Generates a single, self-contained `.html` workout file (`📲 Export for Phone`) with all audio, timers, and movement animations embedded. Instructors can open this file on any phone or tablet without internet.

---

### 3. Cockpit Playback & Fallback Engine

- **Native Audio Mode**: Plays MP3 files attached to tracks (or loaded via `🎵 Load MP3s` button).
- **Web Audio Metronome Fallback**: If MP3 files are not attached or unavailable on the device, clicking **`▶ Play Workout`** automatically launches the Web Audio Synth Metronome (beating at the track's target BPM e.g., 118 BPM) and drives the workout timer.
- **Visual & Audio Cues**: Workout progress bar ticks smoothly, active movement cards highlight, upcoming movement cards flash gold 10 seconds before transition (`.mov-upcoming-flash`), warning alert banner countdowns trigger (`#movBannerNext`), and 3-2-1 audio beeps sound.

---

## 📋 PART 2: Instructor User Guide (For Guest Instructors & Friends)

Welcome to the **Spinning® Class Profile Builder**! This tool allows you to design, customize, and teach official Spinning® class profiles with exact cadence, energy zones, movement transitions, and instructor coaching cues.

---

### 🚀 Step 1: Open the Builder
1. Open **`https://simonstokes7.github.io/Spinning/builder.html`** in any web browser on your laptop, tablet, or phone.
2. No login, installation, or account is needed!

---

### 🛠️ Step 2: Build Your Spin Class
1. **Class Header**:
   - Enter your **Class Title** (e.g. *Spin 001 - High Energy Endurance*).
   - Enter your **Instructor Name**.
   - Choose the **Primary Energy Zone** for the ride:
     - **Recovery Zone** (50-65% HR)
     - **Endurance Zone** (65-75% HR)
     - **Strength Zone** (75-85% HR)
     - **Interval Zone** (65-92% HR)
     - **Race Day Zone** (80-92% HR)
2. **Ride Profile Journey**:
   - As you configure track durations and energy zones, the visual profile curve at the top automatically updates to display your class elevation journey.

---

### 🎵 Step 3: Configure Each Track
For each track in your workout:
1. **Song Title & Artist**: Enter the song details.
2. **Song BPM**: Type the song's BPM. The builder automatically calculates the recommended Spinning® Cadence (RPM) and terrain (Climb vs. Seated Flat).
3. **Duration**: Set the track duration (e.g., `05:30`).
4. **Energy Zone & Target RPE**: Select the target effort level from **RPE 1-3 (Easy)** to **RPE 10 (Maximal)**.
5. **Movements & Transitions (Up to 6 per Track)**:
   - Click any slot to choose a Spinning® movement symbol (*Seated Flat, Standing Flat, Seated Climb, Standing Climb, Jumps, Jumps on a Hill, Running with Resistance, Sprints*).
   - Enter the start timestamp for each movement (e.g., `0:00`, `2:00`, `3:30`).
6. **Coaching Cues**: Type your instructor coaching notes, cadence instructions, and motivational cues.

---

### 🎧 Step 4: Listen to Music While Building
- Click the **`▶ Play`** button directly on any track card to listen to the song while configuring your movement slots.
- Watch the live time display (`01:24 / 05:30`) or click along the progress bar to seek.
- Click **`⏱️ Use Timestamp`** at any time during playback to automatically copy the live audio timestamp into your next empty movement slot!

---

### 💾 Step 5: Save & Re-Use Tracks
- **Save Whole Class**: Click **`💾 Save Class`** in the top toolbar to save your class into your browser's **`📂 My Classes`** library.
- **Save Individual Tracks (Track Library)**:
  - Found a track combination you love? Click the **`⭐`** button on any track card to save that pre-engineered track preset into your **`⭐ Track Library`**.
  - Next time you build a class, open **`⭐ Track Library`** and click **`➕ Insert Track`** to add it to your new class in 1 click!

---

### 📲 Step 6: Teach Your Class on the Bike
1. **Export for Phone**: Click **`📲 Export for Phone`** to download a single, standalone workout file to your phone or tablet.
2. **Mount on Handlebars**: Open the downloaded file on your phone or tablet mounted on your Spin bike handlebar.
3. **Teach**: Press **`▶ Play Workout`**! The Cockpit displays large, high-visibility metrics, active movement cards, 10-second pre-flashing alerts, and audio countdown beeps to keep your class perfectly in sync.
