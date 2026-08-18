# 🚴‍♂️ How Friends Can Build & Ride Classes on Their Own PC (Updated Guide)

With our latest updates, your friends can now design workouts, import playlists, and **even embed their own MP3 audio** directly inside their web browser with **zero installation required**!

---

## 🌟 Option 1: Browser-Only / Web Link (Zero Installation) ⭐ *Recommended for Friends*

Your friend simply opens your live web link in Chrome, Edge, or Safari:  
👉 **[https://simonstokes7.github.io/Spinning/builder.html](https://simonstokes7.github.io/Spinning/builder.html)**  
*(Or they can double-click a local copy of `Spinning Class Builder.html`).*

### ✅ What works completely out-of-the-box:
1. **Full Profile & Class Designer:**
   * Adjust song titles, artists, BPMs, target cadences (RPM), and energy zones.
   * Add any of the 5 official Spinning® movement types across all 6 slots with exact timestamps (`0:00`, `2:40`, `4:15`, etc.).
   * Automatic **`🧘 Cool-Down & Stretch`** mode on the final track.
   * Write instructor coaching cues and view the live interactive **Ride Profile Journey** graph.
2. **Importing Playlists:**
   * Click **`🎵 Import MusicBee Playlist`** &rarr; browse any `.m3u` or `.mbp` playlist file from their PC.
3. **📁 Attaching MP3 Audio (New!):**
   * They click **`🎵 Attach Audio Files`** in the top bar and select their 6–8 songs.
   * The browser automatically matches each MP3 to its track card and shows green **`🎵 [✓ Song.mp3]`** status pills.
   * If a song is missing, they can click **`➕ Attach MP3`** on that individual track.
4. **📲 Export for Phone with Music:**
   * They click **`📲 Export for Phone`** &rarr; the browser bakes their attached MP3s directly into a standalone **`Workout.html`** file.
   * They can send that single file to their phone (via AirDrop, email, or Google Drive) and ride on their bike handlebars completely offline!
5. **Class Sharing (`.json` blueprints):**
   * They can click **`📂 My Classes` &rarr; `Download Backup (.json)`** to export their workout plan and send it to you.
6. **Printable Cue Sheet:**
   * One-click clean printout of the entire ride overview and movement transitions.

### ⚠️ The ONLY Remaining Limitations in Browser-Only Mode:
1. **1-Click "Send to GitHub":** The `🐙 Send to GitHub` button is tied to your personal repository (`simonstokes7/Spinning`). A friend cannot push directly to your GitHub without your repository credentials (unless they send you their `.json` file for you to push).
2. **Auto-scanning Windows System Folders:** Because web browsers have strict security sandboxes, the browser asks them to click/browse their `.m3u` file or MP3s rather than silently scanning their `C:\Users\` drive in the background.

---

## 💻 Option 2: Full Setup (With Local Python Server)

If your friend is tech-savvy and wants to run their own local server:
1. They clone or download your repository.
2. Run `python spinning_server.py`.

### ✅ Additional Backend Perks:
* Automatic scanning of their private `C:\Users\<Name>\Music\MusicBee\Playlists` directory.
* Deep waveform beat analysis (`librosa`) for unlabelled audio tracks.
* 1-click publishing if they fork the repository to their own GitHub account.

---

## 🤝 The 3 Best Ways to Collaborate with Friends:

### Workflow A: They Build & Export on Their Own Phone (100% Independent)
1. Friend opens **`https://simonstokes7.github.io/Spinning/builder.html`**.
2. They design their ride (or import an `.m3u`).
3. They click **`🎵 Attach Audio Files`** to attach their MP3s.
4. They click **`📲 Export for Phone`** &rarr; ride independently on their bike handlebars!

### Workflow B: They Share Their Class Plan with You
1. Friend designs a class online and clicks **`📂 My Classes` &rarr; `Download Backup (.json)`**.
2. They send you the file (e.g. `Karen_Hill_Climb.json`).
3. You open it in your Builder (**`📂 My Classes` &rarr; `Open File`**), click **`🐙 Send to GitHub`**.
4. Both of you (and anyone in your spin class) can now open **`https://simonstokes7.github.io/Spinning/`** on your phones to ride together!

### Workflow C: Pure Visual Rhythm Guide (Music on Gym Speakers)
1. Play music playlist through Spotify / MusicBee on the room sound system.
2. Everyone opens **`https://simonstokes7.github.io/Spinning/`** on their handlebar phone mounts.
3. The handlebars act as the live visual HUD: RPM gauge, glowing movement cards, and coaching cues in real time!
