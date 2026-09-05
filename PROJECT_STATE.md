# PROJECT STATE — Spinning® Class Builder

Living status file. Update it at the end of any session that changes code, versions,
or working practice. Newest entry first in the log.

Last updated: **2026-09-05** — `spinning_spotify_builder.html` v4.9.23: user hit a real Spotify sign-in redirect loop ("session expired" repeating, had to close the tab) — added a circuit breaker plus `show_dialog=true` on every login

---

**spinning_spotify_builder.html v4.9.23 (2026-09-05) — Spotify Sign-In Redirect Loop Circuit Breaker**
- User reported hitting a real, disruptive loop live on the deployed site:
  a "session expired" message kept repeating and they had to close the tab
  to escape it. Root cause not fully isolated with certainty — the likely
  candidate is Spotify silently reusing an older, narrower scope grant from
  before `playlist-modify-private` was added (v4.9.20) rather than
  re-prompting for the new permission, causing every write call to 401/403
  even immediately after a "successful" re-login, which `handleSpotifyAuthFailure()`
  would then send straight back through `beginSpotifyLogin()` again with no
  circuit breaker — but rather than assert that as fact without being able
  to observe the real network traffic, the fix makes the failure mode safe
  regardless of the exact trigger.
- **`show_dialog=true`** added to every `/authorize` call — forces Spotify to
  always show its consent screen rather than potentially silently reusing a
  stale prior grant, making a scope/permission mismatch visible to the user
  instead of failing invisibly.
- **Circuit breaker in `beginSpotifyLogin()`**: a `spotify_last_login_attempt`
  timestamp in `sessionStorage`, checked before every redirect. A second
  login attempt within 15 seconds of the last one — the signature of a loop,
  not a normal fresh sign-in — is blocked outright: no navigation, the
  pending-action tag is cleared (so a stale intent can't quietly resume into
  something confusing), and a clear diagnostic toast points at the most
  likely fix (checking the Development Mode user allowlist) instead of
  bouncing back to Spotify again. Cleared on a genuinely successful token
  exchange so a legitimate future re-login isn't wrongly treated as a loop.
  This protects all three entry points (Import, Save to Spotify, export's
  auto-sync, and any 401/403 hit mid-flow) since they all funnel through
  this one function to reach Spotify's login.
- Verified via Python esprima (0 errors) and headless Playwright: confirmed
  a normal login attempt still navigates correctly with both `show_dialog=true`
  and the full scope string present in the constructed URL; confirmed a
  second attempt within the 15s window produces **zero** navigation attempts,
  shows the breaker's toast, and clears the pending-action tag — with the
  page's own JS state left intact (an earlier test draft that aborted a real
  navigation via Playwright's route interception corrupted the page context
  entirely, `ReferenceError: beginSpotifyLogin is not defined` afterward,
  confirming `window.location.href` assignment is a real top-level
  navigation attempt even when the resulting request is blocked — switched
  to seeding `sessionStorage` directly to simulate "an attempt just
  happened" rather than actually triggering and aborting one). Zero console
  errors.
- **Still not fully diagnosed**: whether the root cause really was the scope-
  reuse theory above, since it couldn't be directly observed. If the user
  hits this again even with `show_dialog=true` forcing a fresh consent
  screen each time, that would rule out stale-scope-reuse and point at
  something else (e.g. a genuine backend issue on a specific endpoint) —
  worth capturing the exact toast sequence and, if possible, the network
  tab's actual 401/403 response body if it recurs.
- Snapshot: `Backups/spinning_spotify_builder_v4.9.23_AuthLoopBreaker_20260905_110053.html`.

---

**spinning_spotify_builder.html v4.9.22 (2026-09-05) — Post-Login Redirect Resumes the Action That Triggered It**
- User hit this live, for real, on the freshly-deployed Pages site: clicked
  "⚡ Export Mobile Cockpit HTML" while not signed in, went through the real
  Spotify consent screen, clicked Agree — and landed back on the **Import**
  modal instead of getting their export. Root cause: `handleSpotifyAuthRedirect()`
  (added in v4.9.19, when Import was the only thing that ever called
  `beginSpotifyLogin()`) unconditionally opened the import modal after any
  successful token exchange. v4.9.20/21 added two more callers of the same
  login path — "Save to Spotify" and export's auto-sync — but the redirect
  handler never learned to tell them apart.
- Fixed with a `sessionStorage` intent tag set by whichever action is about
  to (possibly) trigger a login redirect, read once by
  `handleSpotifyAuthRedirect()` and cleared immediately: `openSpotifyImportFlow()`
  sets `'import'`; `saveClassToSpotify(isRetry, resumeAs)` gained a second
  parameter and sets `resumeAs || 'save'` as its very first line (covers both
  its own direct "no token yet" check and any 401/403 hit deeper in the
  Me/create/rename/tracks calls, and survives its own 404-recovery retry by
  passing `resumeAs` through); `exportCockpitForPhone()` calls
  `saveClassToSpotify(false, 'export')` instead of the bare call. On
  successful token exchange, the redirect handler now reads the tag and
  calls `saveClassToSpotify()` (for `'save'`), `exportCockpitForPhone()` (for
  `'export'`), or `openSpotifyImportModal()` (default/`'import'`) —
  re-running the actual action from the top rather than leaving the user
  stranded on the wrong screen.
- Verified via Python esprima (0 errors) and headless Playwright: for each
  of the three intents, seeded `sessionStorage` (verifier + pending-action
  tag) via `add_init_script` so it's in place before the page's own
  `init()`/`handleSpotifyAuthRedirect()` fires naturally on load (an earlier
  test draft that instead called `handleSpotifyAuthRedirect()` manually after
  load was a dead end — the automatic on-load call had already consumed and
  stripped the `?code=` param by then, so the manual call silently no-opped;
  switching to seeding state before a real navigation exercises the actual
  end-to-end path instead), mocked `accounts.spotify.com/api/token` to
  return a valid token, and confirmed: `'import'` opens the import modal
  (element created, `display:flex`); `'save'` does **not** create the import
  modal and its own distinctive "only works from the hosted link" toast
  proves `saveClassToSpotify()` itself ran (this test happened to hit that
  particular one of its guards rather than reaching Spotify — the
  interesting confirmation is *which function* produced the message, not
  which of its internal branches fired); `'export'` triggers a real file
  download with zero further interaction needed. Zero console errors across
  all three.
- Snapshot: `Backups/spinning_spotify_builder_v4.9.22_AuthRedirectResumeFix_20260905_104615.html`.

---

**spinning_spotify_builder.html v4.9.21 (2026-09-05) — Version Bump Catch-Up (No New Code)**

**spinning_spotify_builder.html v4.9.21 (2026-09-05) — Version Bump Catch-Up (No New Code)**
- User noticed the version badge still read v4.9.20 after two further fixes
  had already shipped in this same session (the playlist name-sync fix, and
  wiring auto-sync into "⚡ Export Mobile Cockpit HTML" — both documented
  below under the v4.9.20 entry, since that's the version they were actually
  built under). Both should have bumped the version individually per this
  project's usual same-day-fix convention (see e.g. `8n12_weights_builder.html`
  v0.4.1/v0.4.2 below) — they didn't, which is what the user caught. This
  entry is the correction: bumped to v4.9.21 everywhere the version string
  appears (title, header badge, export script's embedded title, download
  filename). No functional code changed in this pass.
- Re-verified esprima (0 errors) after the bump.
- Snapshot: `Backups/spinning_spotify_builder_v4.9.21_AutoSyncOnExport_20260905_102202.html`.

---

**spinning_spotify_builder.html v4.9.20 (2026-09-05) — Save to Spotify (Create/Update Real Playlist) + Exported HUD Simplified to 2 Buttons**
- Same-session follow-up to v4.9.19's import feature. User tried the actual
  exported Mobile Cockpit HUD (screenshot) and found the per-track Spotify
  embed widget (`open.spotify.com/embed/track/...`) genuinely unusable during
  a live class: it's a separate, disconnected clock from the HUD's own
  workout timer — no code anywhere wired the two together (confirmed by
  reading `togglePlay()`/`nextTrack()` in the export generator: they only
  touch `curSec`/the local `<audio>` element, never the Spotify iframe).
  Real per-track flow would have required the instructor to manually tap
  Play inside a new, paused widget every single track, all class, with zero
  safety net if it drifted — correctly called out as "too chaotic."
- User's fix, agreed and built: **two buttons total, nothing per-track.**
  "🎵 Start Music" deep-links once to the class's real Spotify playlist
  (`open.spotify.com/playlist/{id}`), letting Spotify itself own track-to-
  track transitions in the background app while the existing "▶ Start
  Workout"/"⏸ Pause Workout" button (unchanged, was already named this)
  independently starts the HUD's own cue timer. Confirmed via
  `AskUserQuestion`: export goes **fully bare** (no per-track text/reference
  either, not even a passive song-name label) — matches "that's it" literally.
- This surfaced a second, genuinely new ask: since the builder was already
  assembling exactly the right structured data (a playlist could be born
  *from* the class), could it push that list *to* Spotify as a real playlist
  instead of requiring the instructor to hand-build one first? Yes — reuses
  the same PKCE login from v4.9.19, extended with one more scope
  (`playlist-modify-private`, confirmed via `AskUserQuestion` the created
  playlist should be **Private**).
- **New `saveClassToSpotify()`** (builder-side, new "💾 Save to Spotify"
  button next to Import): `GET /v1/me` for the user id, `POST
  /v1/users/{id}/playlists` (`public:false`) to create **once**, then `PUT
  .../tracks` (replace, chunked at 100) for every track carrying a Spotify
  link — re-running the button after edits reuses the stored playlist id and
  just replaces its contents in place rather than creating duplicates.
  Self-heals if that stored id 404s (e.g. instructor deleted the playlist
  directly in Spotify): clears it and creates fresh, once, automatically. Any
  401/403 (expired token, or an old session that predates the new scope)
  clears the stored token and re-triggers login. Tracks with no Spotify link
  attached are silently skipped, with the skip count named in the success
  toast. `window.spotifyClassPlaylistId`/`spotifyClassPlaylistUrl` (the
  latter already existed as an unpersisted global — this pass is what first
  made it survive a reload) now round-trip through `autoSave()`/
  `loadAutoSave()` **and** `saveClassJson()`/`parseAndLoadJsonFile()`, so the
  link to "this class's real Spotify playlist" travels with the class data
  either way it's persisted.
- **Export generator (`exportCockpitForPhone()`) simplified**: deleted the
  entire per-track `mStreamingBar` rebuild (the iframe-embed-or-SoundCloud-
  widget-plus-open-button block, previously re-run on every track change) and
  its now-dead supporting code (`extractSpotifyId()`, `lastRenderedStreamingIdx`).
  Replaced with one static button in the markup, `🎵 Start Music`
  (`id="mStartMusicBtn"`), calling a new top-level `startMusic()` that opens
  `classSpotifyPlaylistUrl` (already baked in at export time from
  `window.spotifyClassPlaylistUrl`) in a new tab, or alerts if none is linked
  yet. Left `togglePlay()`'s pre-existing (already-dead-in-practice, wrapped
  in try/catch, unrelated to this pass) SoundCloud-widget-control branch
  alone — it silently no-ops now that `mSoundCloudIframe` no longer exists in
  the markup, same as it would have for any SoundCloud track before this
  change since that widget was only ever built inside the now-deleted block.
- Verified via Python esprima (0 errors, live builder script) and headless
  Playwright throughout: **Save to Spotify** — mocked `/me` + create +
  tracks endpoints and confirmed a fresh save's exact call sequence and
  bodies (`public:false` in the create call, correct `spotify:track:` URIs in
  the `PUT`), confirmed a second save with a pre-existing playlist id skips
  creation entirely (only the `PUT` fires), confirmed a 404 on a stale stored
  id triggers exactly one clean recreate-and-retry ending in a fresh working
  playlist id, all with zero *thrown* console errors (the 404 case logs the
  network response itself, which is normal browser behavior unrelated to
  whether the code handled it — confirmed it did, via the correct final
  state). **Export**: triggered the real `exportCockpitForPhone()` export
  (blob intercepted via `expect_download`, saved to a scratch path, not the
  repo), esprima-validated the generated script standalone (0 errors),
  confirmed `mStreamingBar`/the embed iframe/`lastRenderedStreamingIdx` are
  gone from the output, then loaded the exported file fresh in its own page
  and confirmed clicking "🎵 Start Music" calls `window.open` with the exact
  linked playlist URL and clicking "▶ Start Workout" still correctly starts
  the HUD's own timer (label flips to "⏸ Pause Workout") — both independent,
  as designed, zero console errors.
- **Not yet done**: `git push` to publish this version to GitHub Pages (both
  this pass's and v4.9.19's changes are still only local), adding
  instructors' Spotify accounts to the Development Mode allowlist (max 5),
  and — new as of this pass — anyone who already signed in under v4.9.19's
  narrower read-only scope will hit a 401/403 on their first "Save to
  Spotify" attempt; the code self-heals this into a fresh login prompt
  automatically, so no dead end, just an extra one-time re-login.
- **Same-session follow-up**: user tested against a real exported HUD and a
  real Spotify playlist ("Spinning1") and reported two apparent problems.
  Both investigated before touching code: (1) the exported HUD still showing
  the old per-track widget/play-button turned out to be a stale file — its
  own version badge read v4.9.16, i.e. exported before this session's changes
  existed, not a regression; re-exporting from the live v4.9.20 builder is
  the fix (no code issue). (2) The "Spinning1" playlist (5 unrelated tracks,
  Public) not matching the live "Run the Hill" class (10 tracks) — confirmed
  via `AskUserQuestion` this playlist predated the "Save to Spotify" button
  entirely (made by hand / linked earlier), so no bug there either. While
  investigating #2, did find one genuine gap worth fixing anyway: repeat
  saves replaced a playlist's tracks but never its name, so renaming the
  class after the first save would leave the Spotify-side playlist's name
  stale. Fixed: `saveClassToSpotify()`'s reuse-existing-playlist branch now
  also issues `PUT /v1/playlists/{id}` with the current class title before
  replacing tracks. Verified via esprima (0 errors) and Playwright (mocked
  rename + tracks endpoints, confirmed the rename call fires with the live
  class title and precedes the tracks call, zero console errors).
- **Same-session follow-up**: user asked whether "Save to Spotify" should
  just happen automatically as part of "⚡ Export Mobile Cockpit HTML",
  rather than being a separate button the instructor has to remember to
  click before exporting (exactly the failure mode that produced the earlier
  stale-playlist confusion). Agreed and wired it in: `exportCockpitForPhone()`
  is now `async` and, only when the class has at least one Spotify-linked
  track (`classTracks.some(...)`, same check `saveClassToSpotify()` already
  uses — a class with zero Spotify tracks triggers no network calls, no
  login prompt, exports exactly as before), awaits
  `const syncResult = await saveClassToSpotify();` before building the
  export, so the freshly-created-or-updated playlist URL is what actually
  gets baked into `classSpotifyPlaylistUrl` for the exported "Start Music"
  button.
- **Redirect-safety fix made alongside this**: `saveClassToSpotify()` previously
  had no way to tell a caller "I'm about to navigate the whole page away to
  Spotify's login" vs. "I finished" vs. "I failed" — all three fell through
  to a bare `return`. Since `beginSpotifyLogin()` does a real
  `window.location.href` navigation, calling it partway through the (now
  awaited) export could otherwise let `exportCockpitForPhone()` carry on
  building/downloading the file in the gap before the browser actually
  unloads. Every exit point now returns a real value —
  `'redirecting'` (a login/auth-failure redirect was just triggered),
  `false` (finished, but nothing saved / a Spotify-side error, already
  toasted), or `true` (saved successfully) — and the export function checks
  for `'redirecting'` specifically and bails with no file produced in that
  case (any other outcome lets the export continue regardless, so a
  transient Spotify hiccup never blocks getting the file needed for class).
  The existing "💾 Save to Spotify" button's own behavior is unchanged by
  this — it never inspected the return value in the first place.
- Verified via Python esprima (0 errors) and headless Playwright, three
  scenarios: (1) class has Spotify-linked tracks + valid session → confirmed
  the sync's `/me` → create → tracks calls all complete, the exported file's
  baked-in `classSpotifyPlaylistUrl` matches the freshly-created playlist,
  *then* the download fires; (2) same class but no valid session (login
  redirect requested, the real `accounts.spotify.com` navigation blocked at
  the network layer for the test) → confirmed **zero** download occurs, i.e.
  export doesn't silently produce a stale/half-synced file; (3) class with no
  Spotify-linked tracks at all → confirmed zero Spotify network calls fire
  and the download proceeds immediately, unchanged from pre-existing
  behavior. Zero console errors in all three.
- Snapshot: `Backups/spinning_spotify_builder_v4.9.20_AutoSyncOnExport_20260905_102008.html`.

---

**spinning_spotify_builder.html v4.9.19 (2026-09-05) — Spotify Playlist Import via Authorization Code + PKCE**
- User asked whether the builder could import a Spotify playlist instead of
  adding/linking every track by hand. It couldn't: the only existing Spotify
  integration was per-track (`openSpotifyLinkModal`/`saveSpotifyLink`, paste
  one song link at a time) plus the unauthenticated oEmbed call
  (`fetchSpotifyTrackMetadata`) that fills in a track's title only — Spotify's
  oEmbed response has no artist field at all (documented in a comment at that
  call site already, confirmed against real tracks) — and a separate
  "🟢 Spotify Class Playlist Link" feature that only stores/opens a pasted
  playlist URL, never reads its contents.
- **Real playlist import requires the authenticated Web API**
  (`GET /v1/playlists/{id}/tracks`), which needs a login flow — worked through
  the tradeoffs with the user across several turns before building anything:
  - Client Credentials (app-only token, no login) was the first path
    considered since it needs no redirect and keeps the file double-click-able,
    but requires embedding a `client_secret` in a distributed static HTML
    file — user confirmed this is a genuine Spotify Developer Terms violation
    (secrets must stay server-side), and flagged plans to potentially scale
    this beyond one country/one sport, so building on a ToS-violating
    foundation was rejected in favor of doing it properly.
  - Settled on **Authorization Code + PKCE** (real Spotify login, no secret
    needed), which also lifts Client Credentials' "public playlists only"
    limitation. PKCE requires a real `http(s)` redirect URI — Spotify cannot
    redirect a login back to a `file://` page — so this feature **only works
    when the file is opened from its hosted GitHub Pages URL**,
    `https://simonstokes7.github.io/Spinning/spinning_spotify_builder.html`
    (already pushed there for this to work; must stay in sync with any future
    edit to this file). Confirmed with the user this scoping is fully
    reversible: nothing else in the file depends on hosting/login state, so
    deleting the import feature's code would return the file to being exactly
    as distributable/double-click-able as the other 5 builders.
- **Spotify Developer app registered** (user's own account, user
  `scalpelmtb`): Client ID `9049e07355e741cdb0ffe87a932115bb` embedded as a
  constant (`SPOTIFY_CLIENT_ID`) — safe to expose, PKCE never uses a secret.
  App is in **Development Mode**, capped at **5** explicitly-allowlisted
  Spotify accounts (Dashboard → Settings → User Management — confirmed from
  the real dashboard screen, correcting an earlier 25-user guess given before
  the app existed) until/unless a future Extended Quota Mode review is
  requested — flagged to the user as a real constraint on scaling instructor
  access, not yet acted on. User has added their own account (1/5) so far.
- **Implementation** (all new code, isolated from existing functions):
  `spotifyImportSupported()` gates every entry point on
  `location.origin + location.pathname` matching the registered redirect URI
  exactly, showing a toast instead of attempting login when opened locally.
  `beginSpotifyLogin()` generates a PKCE code verifier/challenge (raw
  `crypto.subtle.digest('SHA-256', ...)`, no library) and redirects to
  `accounts.spotify.com/authorize`. `handleSpotifyAuthRedirect()` (called from
  `init()`) exchanges a returned `?code=` for an access+refresh token pair
  (`sessionStorage`, not persisted across browser sessions) and strips the
  code from the URL via `history.replaceState`. `getValidSpotifyAccessToken()`
  transparently refreshes an expired token. `openSpotifyImportFlow()` (the new
  button's handler) reuses a valid session or triggers login; once signed in,
  `loadSpotifyPlaylistPreview()` paginates `/v1/playlists/{id}/tracks` (handles
  playlists over 100 tracks via the response's `next` link) into a preview
  list (name/artist/duration), and `confirmSpotifyPlaylistImport()` appends
  them as new `classTracks` entries (name/artist/duration/spotifyUrl/
  spotifyTrackId pre-filled, movement slots default same as `addNewTrack()`).
  Scopes requested: `playlist-read-private playlist-read-collaborative`, so
  instructors' non-public class playlists work, not just public ones.
- Verified via Python esprima (0 errors) and headless Playwright: confirmed
  the local-file guard toast fires when opened via `file://` (real behavior
  today, since Pages hasn't re-deployed this version yet at the time of
  writing); confirmed `spotifyImportSupported()` correctly returns `false` on
  `file://`; simulated a signed-in session (token in `sessionStorage`) and
  intercepted both `accounts.spotify.com`/`api.spotify.com` calls via
  Playwright route mocks to verify, without hitting the real Spotify API: a
  2-track playlist imports correctly (name/artist-join/duration-from-ms/link
  all correct, track count and autosave both advance), and pagination across
  a mocked 2-page response (`next` followed correctly) merges both pages'
  tracks before showing the preview — all with zero console errors.
- **Same-session follow-up**: user was confused by the pre-existing
  "🟢 Spotify Class Playlist Link" button after seeing the new import button
  next to it, asking whether it pushed the class's tracklist out to Spotify.
  It doesn't and never did — `exportSpotifyPlaylistModal()` is one-directional
  *from* Spotify only (saves/opens a playlist URL you already made yourself,
  launches individual already-linked tracks, copies a plain-text tracklist to
  the clipboard) — no API call of any kind. The modal's own heading calling
  itself "🟢 Spotify Class Playlist & **Exporter**" (mismatched with the
  button's own "Link" wording) was the real source of the confusion, so
  renamed rather than just explained: button → "🟢 Spotify Playlist Link &
  Tracklist", modal heading → "🟢 Spotify Class Playlist & Tracklist", tooltip
  reworded to describe linking/launching/copying, not exporting. Re-verified
  esprima (0 errors) and Playwright (renamed button opens the modal, new
  heading text confirmed present, "Exporter" confirmed gone from the whole
  page, zero console errors).
- **Second same-session follow-up**: user noticed 3 separate "➕ Add New
  Track" buttons once the new import button made the top action row more
  crowded — top action bar (next to Save/Load/Clear), a second one in the
  "🛠️ Movement Transitions & Spotify Tracks" section header, and a third
  auto-appended at the bottom of the rendered track list. Agreed bottom-of-
  list is the right single location (add-more-once-you've-seen-what's-there
  is the more standard pattern); removed the top-bar and section-header
  buttons, kept only the bottom one. The separate empty-state "➕ Add First
  Track" prompt (shown only when `classTracks.length === 0`) is unrelated and
  was left alone. `addNewSpotifyTrack` (alias of `addNewTrack`) still has a
  live call site there, so it wasn't removed as dead code. Re-verified esprima
  (0 errors) and Playwright: confirmed exactly one "Add New Track" button
  renders with tracks present (previously 3), confirmed clearing all tracks
  still shows the empty-state "Add First Track" button, zero console errors.
- **Not yet done**: `git push` to actually publish this version to GitHub
  Pages (the redirect URI won't resolve to *this* code until that happens),
  and adding instructors' Spotify accounts to the app's Development Mode
  allowlist (max 5 total, user's own account already occupies 1 of them) so
  login doesn't fail with access denied.
- Snapshot: `Backups/spinning_spotify_builder_v4.9.19_SpotifyPlaylistImportPKCE_20260905_092724.html`.

---

**spinning_singlemix_builder.html v0.4.0 (2026-09-02) — Lightweight Export With On-Phone Attach Page**
- User asked (after discussing where a SingleMix mix file needs to live to
  play on a phone) whether the mix MP3 could be re-attached from inside the
  exported standalone Cockpit HUD itself, rather than only from the full
  builder. Answer: not by rewriting the exported file (a static HTML file
  can't save back to itself), but a picker inside the export that loads the
  file into memory for that session works fine — approved and built.
- `exportCockpitForPhone(embedAudio)` (still defaults to `true`, unchanged
  behavior/output for that path) now always generates **two pages** in the
  exported HTML, toggled by plain `style.display`: `#attachPage` (a
  centered "📎 Choose Mix MP3" file picker, shown only when the owner
  track has no baked-in audio) and `#workoutPage` (the existing Cockpit
  HUD, unchanged markup/logic). A new `ownerHasAudio()` check on load
  picks which one shows first — an `embedAudio=true` export still opens
  straight to the workout page exactly as before.
- Picking a file on the attach page (`handleAttachFile`) does **not**
  round-trip through base64 — it wires the native `File` directly via
  `URL.createObjectURL(file)` into a new `owner.__liveBlobUrl`, which
  `getPlayableAudioSrc()` now checks ahead of `audioDataUrl`. The four
  existing "is this track really playable" gates
  (`loadTrackAudio`/`nudgeTime`/`togglePlay`/`seekAudio`, all previously
  `t.audioDataUrl || t.mixSourceId`) were extended to
  `|| t.__liveBlobUrl` so the owner track is recognized as playable once
  attached.
- **No persistence** — deliberate, first-pass scope confirmed with the
  user: re-opening the exported file always shows the attach page again if
  it wasn't exported with audio embedded. `file://` storage behavior
  (`localStorage`/IndexedDB) is inconsistent enough across mobile browsers
  (iOS Safari especially) that promising "attach once, remembers next
  time" wasn't worth the risk without dedicated testing — flagged as a
  possible follow-up, not built.
- Added a second export button next to the existing "⚡ Export Mobile
  Cockpit HTML" (now explicitly `exportCockpitForPhone(true)`): "📎 Export
  Lightweight (Attach MP3 on Phone)" → `exportCockpitForPhone(false)`. This
  is the first UI path that ever called the export with `embedAudio =
  false` — previously that branch of the function existed but was
  unreachable from any button.
- Verified via Python esprima (0 errors on both the live builder's script
  and each of the two exported HTML variants' generated scripts) and
  headless Playwright: seeded a 2-track mix class, triggered both export
  variants (blobs intercepted via `expect_download`, not saved to the
  repo), confirmed the embedded export opens straight to the workout page
  with zero console errors, confirmed the lightweight export opens on the
  attach page, and confirmed simulating a real file pick (synthetic
  `File`+`DataTransfer`+`change` event) switches to the workout page with
  `audio.src` set to a genuine `blob:` URL and zero console errors.
- Snapshot: `Backups/spinning_singlemix_builder_v0.4.0_LightweightExportAttachPage_20260902_071021.html`.

---

## 1. Active file (the one that matters)

| File | Role | Version |
|---|---|---|
| `spinning_local_builder.html` | **ACTIVE** — Local Version (100% Local MP3 Only, Zero SoundCloud), the reference lineage new features land on first | v5.0.50 (Local) |
| `spinning_singlemix_builder.html` | **ACTIVE** — SingleMix Version, forked from Local. For Karen-style classes premixed by the instructor into one continuous audio file: Track 1 is the sole audio owner, every other track is auto-linked and plays through segment boundaries without reloading/restarting audio, driven by one shared "🎵 Mix Audio" player panel (shows whole-file position, not per-song). Movement timestamps are absolute mix-time; slot 1 is locked (not editable) to the previous track's start + duration, self-healing via `enforceSingleMixLinks()`/`recomputeMixOffsets()` on every load. Adds a per-movement %Effort field (defaulted from `Docs & Guides/Class Design Quick Reference.jpg`, overridable, always displayed with a trailing "%"). BPM is deliberately reference-only here (speed always 1.0x for mix-linked tracks), so it was excluded from the BPM wall-clock display work below. Export offers two modes: the default self-contained "⚡ Export Mobile Cockpit HTML" (audio baked in) and a new "📎 Export Lightweight" variant whose exported HUD opens on an in-file Attach page to pick the mix MP3 from the phone itself (in-memory only, not persisted). | v0.4.0 (SingleMix) |
| `spinning_multisource_builder.html` | **ACTIVE** — Multi-Source Class Builder (Local MP3 + SoundCloud) | v5.0.48 |
| `spinning_spotify_builder.html` | **ACTIVE** — Spotify Class Builder (Spotify as dedicated music source). Hosted copy at `https://simonstokes7.github.io/Spinning/spinning_spotify_builder.html` is the one usable for "🟢 Import Spotify Playlist" / "💾 Save to Spotify" (PKCE login needs a real redirect URI, won't work opened as a local file) — must stay pushed/in sync with this file. | v4.9.23 |
| `8n12_builder.html` | **ACTIVE** — 8n12 Version (spin, 100% Local MP3, 8n12 Branding) | v5.0.59 (8n12) |
| `8n12_weights_builder.html` | **ACTIVE** — 8n12 Weights variant (Gear+RPM replaced with a single Weight field) | v0.5.3 (8n12-Weights) |
| `Backups/` | One timestamped snapshot per released version, **plus** (as of 2026-08-31) the retired root duplicates below | — |
| `Backups/builder.html` | **ARCHIVED** — was a byte-identical mirror of `spinning_local_builder.html`; consolidated out of root 2026-08-31, no longer maintained/synced | v5.0.48 (Local) at archive time |
| `Backups/builder_spotify.html`, `Backups/Spinning Class Builder Spotify Edition.html` | **ARCHIVED** — both were byte-identical duplicates of `spinning_spotify_builder.html`; consolidated out of root 2026-08-31 | v4.9.17 at archive time |
| `Backups/index.html` | **ARCHIVED** — a separate, unrelated tool ("Spinning® Class Profile Builder"), not a version of any of the 5 builders above; moved out of root 2026-08-31 per explicit user confirmation | — |

**Naming note (2026-08-31):** the in-app title/header text "Course Designer" was renamed to "Class Builder" across all 5 active files (title tag + header `<h1>`). "Course Designer" should not reappear in any active file going forward.

Single-file app: all HTML + CSS + one ~3,100-line inline `<script>` block.
A single top-level `SyntaxError` kills the whole app, so syntax verification is mandatory.

## 2. Current version & what shipped

**All 6 active files (2026-09-01) — Screen Wake Lock API in the Exported Mobile Cockpit HUD**
- User asked: in "the export for mobile use process," keep the phone/tablet
  screen from dimming or sleeping during a workout — annoying when the
  display disappears mid-class. Confirmed scope via `AskUserQuestion`: all 6
  active builders (`spinning_local_builder.html`, `spinning_multisource_builder.html`,
  `spinning_spotify_builder.html`, `spinning_singlemix_builder.html`,
  `8n12_builder.html`, `8n12_weights_builder.html`), including the two 8n12
  files even though they weren't named up front.
- **Scoped to the exported standalone Mobile Cockpit HUD only** (the
  `exportCockpitForPhone()` generated script), per the user's explicit "export
  process" wording — the live builder's own Cockpit tab was left untouched,
  unlike the earlier Media Session/Bluetooth pass which touched both.
- Added `requestWakeLock()`/`releaseWakeLock()` (feature-detected via
  `"wakeLock" in navigator`, silent no-op where unsupported) to each file's
  generated script, plus a `visibilitychange` listener that reacquires the
  lock if the tab regains visibility mid-workout — the OS releases a wake
  lock automatically whenever the tab is hidden (e.g. briefly switching
  apps), so without this the lock wouldn't resume after the user came back.
  Wired `requestWakeLock()` into `togglePlay()`'s play branch and
  `releaseWakeLock()` into its pause branch, plus the class-completion
  branches of `nextTrack()` and the `audio` `"ended"` listener (same pattern
  in every file: `isPlaying = false; ... audio.pause(); releaseWakeLock();`).
  `spinning_spotify_builder.html` had no prior Media Session block to key
  off (out of scope for that earlier pass) — wake lock was added standalone
  there, same helper functions, same call sites.
- Verified via Python esprima (0 errors, all 6 files' main script) and
  headless Playwright: triggered the real `exportCockpitForPhone(false)`
  export in every file (intercepted via Playwright's download event, not
  saved to disk by the app), confirmed the generated HTML's script parses
  with 0 esprima errors and contains both `requestWakeLock`/`releaseWakeLock`,
  and confirmed zero console errors loading each exported file fresh.
- Snapshot: one `Backups/*_ScreenWakeLock_*.html` per file, all timestamped
  together (`20260901_205338`).

**spinning_local_builder.html v5.0.49 / 8n12_builder.html v5.0.58 / spinning_multisource_builder.html v5.0.47 (2026-09-01) — BPM Changes Now Rescale Duration, Timestamps, and Class Length Everywhere They're Displayed**
- User asked: for every active builder with a BPM editor, changing a
  track's BPM should change the track's length, its movement/cue
  timestamps, and the total class duration accordingly. Investigation
  found the app already had half of this: `getTrackPlaybackSpeed(track)`
  (target BPM ÷ `originalBpm`, clamped 0.5x–2.0x) already drove real
  `audioPlayer.playbackRate`, and `spinning_local_builder.html` alone
  already divided nominal durations by that ratio for the class total
  (`updateStats()`) and the Cockpit HUD's elapsed/remaining clocks +
  next-movement countdown — `8n12_builder.html` and
  `spinning_multisource_builder.html` had the same speed machinery but
  never got that division ported. **No file** adjusted the Duration input
  or individual movement/cue timestamp inputs themselves.
- **Explicitly out of scope, confirmed with the user along the way**:
  `spinning_spotify_builder.html` ("Don't do Spotify" — not touched this
  pass). `spinning_singlemix_builder.html` is correctly excluded by
  design — its `getTrackPlaybackSpeed()` deliberately forces 1.0x for
  every mix-linked track (BPM is reference-only there; Karen's shared
  recording can't be resped per segment). `8n12_weights_builder.html` is
  correctly excluded — its BPM/tempo UI was fully removed in v0.2.0 (no
  rendered BPM input anywhere).
- **Key design constraint surfaced during planning**: `track.duration`
  and each movement's `.time` aren't cosmetic labels — they're live,
  user-editable data also used as the content-time denominator for the
  progress bar, the audio-fallback duration, and cue-firing comparisons
  against `audioPlayer.currentTime` (always native/content time
  regardless of `playbackRate`). Overwriting them with wall-clock numbers
  would silently break that math everywhere they're read back in. Per
  user's explicit direction: **stored values stay original content-time**
  (unchanged) — **every displayed** time value converts to wall-clock via
  new `formatSecAsTime()`/`wallClockTimeStr()`/`contentTimeStrFromWallClock()`
  helpers (added next to `getTrackPlaybackSpeed()` in each file, plus a
  matching trio inside each file's `exportCockpitForPhone()` generated
  script). The Duration input and each movement/cue timestamp input now
  display wall-clock, converting back to content-time on write
  (`updateTrackDurationDisplay()`, rewritten `updateSlotTime()`); every
  read-only display (Overview table, Cockpit metric badge, playhead
  "0:00 / mm:ss" caption, movement-grid time badges, exported HUD) got the
  same swap. `updateBpm()` now also refreshes these boxes in place (same
  pattern it already used for the BPM input/cadence label) so they update
  live without a full re-render.
- **New "↺" reinstate-original-BPM button** added next to each track's BPM
  controls, shown only when `bpm != originalBpm`. Wired to
  `resetTrackBpm()` — which already existed correctly in all 3 files but
  had zero call sites (pure dead code, no button anywhere) before this
  pass.
- `8n12_builder.html`'s data model differs from Local/Multisource (2 fixed
  "Cue 1 / Cue 6" timed-cue slots rather than 6 free movement slots, Cue 1
  locked to 0:00, BPM shown as a plain `bpmVal_` readout rather than a
  typed input) — same conversion pattern applied, adapted to that shape.
  Its `renderCockpit()` uses `buildCuePoints()`/`findActiveCuePoint()`
  instead of a movement array walk, but the same content-time-for-firing /
  wall-clock-for-display split applies identically.
- Verified via Python esprima (0 errors, all 3 files) and headless
  Playwright: seeded a 4:00 track at BPM 120→150 (1.25x), confirmed the
  Duration box, movement/cue timestamp box, and class total all showed the
  divided wall-clock value while `classTracks[].duration`/`.time` stayed
  the original content-time strings; confirmed the reset button appears
  only once BPM changes and clicking it restores every display; triggered
  the real `exportCockpitForPhone()` export (blob intercepted, not
  downloaded), loaded the generated HTML fresh, and confirmed matching
  wall-clock numbers with zero console errors in both the live builder and
  the export, across all 3 files.
- Snapshot: one `Backups/*_BpmWallClockDisplay_*.html` per file.
- Found and left alone (pre-existing, unrelated): a handful of malformed
  CSS rule fragments around `spinning_local_builder.html` line 928-936
  (IDE reports `{ expected` errors there) — present before this session's
  edits, doesn't affect the inline `<script>` block this pass touched, out
  of scope for a BPM-focused change.

**spinning_singlemix_builder.html v0.3.0 (2026-09-01) — Fourth Pass: Real Root Cause of "0:00" Start Times, a Self-Inflicted Crash, Whole-Mix Player Time**
- **Root cause found for a bug that survived several earlier attempted
  fixes**: user kept seeing every track's slot-1 start time read "0:00"
  after loading a real class. Added a "Start Time" column to the Overview
  table (between `#` and `Track & Artist`) to make this diagnosable, which
  revealed the loaded tracks had **no `mixSourceId` at all** — they were
  independent, unlinked tracks (from an older save, or one never fully
  migrated to this builder's model), so each correctly computed its own
  offset as zero rather than actually being broken. New
  `enforceSingleMixLinks()` repairs this on every load path (`loadAutoSave`
  and the Load button): any track after Track 1 missing a `mixSourceId`
  (or pointing at an id that no longer exists) gets linked to Track 1, then
  offsets are recomputed from there. This is now the single call both load
  paths make, replacing the narrower "just recompute offsets" fix from the
  previous pass, which only fixed already-linked-but-stale data.
- **Slot 1 is now locked** (previous pass added the field; this pass closed
  the remaining gaps): `applyTimestampToSlot()` can no longer target index
  0 via any fallback path (last-focused-slot, first-empty-slot, or the
  ultimate default), and `selectSymbol()` always recomputes slot 1's time
  from the track's real `mixOffsetSec` rather than trusting whatever was
  there before — closes a hole where clearing and re-picking a movement on
  slot 1 could reset it to 0:00. `openSymbolModal()` also now recomputes
  and redraws slot 1 the instant its icon is clicked, so the modal always
  opens on the true current value.
- **Self-inflicted regression, found and fixed same pass**: de-duplicating
  the slot-render code in the previous pass accidentally deleted the
  `zoneColor` variable declaration used by the card's left-edge color
  stripe, so `renderTracks()` threw on the very first track and silently
  rendered zero cards (while the track-count stat, read independently,
  still showed the correct number) — exactly what the user hit after a
  real mp3 import. Restored the declaration; this class of bug (a
  behavioral regression a syntax-only check can't catch) is why every pass
  now re-runs the full Playwright regression immediately after any
  structural edit, not just an esprima pass.
- **Mix Audio panel now shows whole-mix time**, not per-song: its time
  readout, progress fill, and a new dedicated `seekMixAudio()` handler
  (separate from `seekTrackAudio()`, which the Cockpit's own per-song scrub
  bar still uses intentionally) all use `audioPlayer.currentTime`/
  `.duration` directly. Each track's own "Duration" field is unrelated and
  stays per-song.
- **Track 1's Name/Artist no longer get overwritten by the imported mix
  file's ID3/filename** — that identity now only flows to the Profile
  Title (unconditionally, on every attach/replace, per the prior pass).
  Track 1's Name/Artist are the first song's own fields, typed in by hand
  like every other track's.
- Verified via Python esprima and headless Playwright throughout,
  including a synthetic "9 independent tracks, no mixSourceId" JSON file
  built to match the user's actual reported data shape.

**spinning_singlemix_builder.html v0.2.0 (2026-09-01) — Third Feedback Pass: Absolute Timestamps, Field Cleanup, Title-Level Audio dB**
- **Timestamps are now absolute mix-time everywhere**, not segment-relative:
  slot 1's default is the cumulative sum of all prior tracks' durations
  (Track 1 → 0:00, Track 2 → 5:00, Track 3 → 10:00...), staying in sync via
  `recomputeMixOffsets()` as durations change — but only while a slot is
  still at its auto-assigned value; a manually-typed timestamp is never
  overwritten. "⏱️ Use Timestamp" now captures the player's raw
  `audioPlayer.currentTime` with no offset subtraction. Live builder
  (`updateBuilderSlotHighlights`), Cockpit HUD (`renderCockpit`, via a new
  `movMatchSec` kept separate from the segment-relative `curSec` used for
  the progress bar/clock), and the exported standalone player's duplicated
  logic were all updated in tandem. The per-segment progress bar/duration
  readout is unaffected — that's a separate, still-relative display concern.
- **Defaults**: BPM → 140, Cadence (RPM) re-added as a plain editable field
  (no more auto-derived "N RPM (Terrain)" text — `updateBpm()` no longer
  touches cadence at all) defaulting to 70. Attaching/replacing the mix file
  backfills detected BPM onto tracks still at blank or the untouched 140
  default, leaving customized ones alone. Slot 1 defaults to Warm Up/RPE 2
  on Track 1, Recovery/RPE 2 elsewhere; Track 1's default cue is "Steady
  warmup". `classTitle` now defaults blank and auto-fills from the mix
  file's ID3 title/filename on attach (only if not already typed).
- **Removed as redundant**: track-level Cadence/Zone/RPE dropdowns (Zone/RPE
  are fully handled per-movement now; the fields still exist as inert
  fallback data, just not editable at the track level), the "SPINNING®
  MOVEMENTS & TRANSITIONS (UP TO 6)" label, the stale "Cadence Rule: BPM >
  110 → Half-Time RPM" hint box, the Overview table's Audio dB/Energy
  Zone/Target RPE columns, and the "🔗 Mix Segment" chip (true for every
  row by design, so it stopped being informative).
- **Audio dB moved to the title level**: a single `#overviewAudioDbBox`
  next to "Print Overview" now shows Track 1's peak loudness (the one real
  audio file), auto-populated on import — no more per-row column or manual
  "Scan dB" button (both removed in the prior pass).
- **Layout**: coaching cues moved into the same row as the track title
  (cutting each card from 3 rows to 2); RPE and %Effort now sit side by
  side in each slot box instead of stacked.
- **%Effort always displays with a trailing "%"** (`resolveEffortPct()`
  and the exported player's inline equivalent both append one if a
  manually-typed override omits it) — confirmed it was already surviving
  `loadAutoSave()`'s normalizer and `saveClassJson()`'s export untouched,
  since movement objects are passed through those wholesale rather than
  reconstructed field-by-field.
- Fixed two stale toast messages still referencing the removed bulk "🎵
  Select Music Files" button (from the prior pass) with the current
  "📎 Attach Mix MP3" panel control.
- Default track count bumped to 9 (previously 2) to match a typical class
  song count; "➕ Add Track" always appends at the true end of the list,
  fixed alongside removing a duplicate header-level Add Track button.
- Verified via Python esprima (main script + a triggered export's
  generated script, 0 errors each run) and headless Playwright throughout.

**spinning_singlemix_builder.html v0.1.0 (2026-08-31) — New 6th Builder for Premixed Continuous-Audio Classes**
- User's instructor mixes her own classes into one continuous ~45-minute
  audio file (loudness/BPM already handled in her mix creation — out of
  scope here). Forked from `spinning_local_builder.html` rather than
  touching any of the 3 canonical builders, per user's explicit choice.
- **Data model**: track objects gain two optional fields — `mixSourceId`
  (the `id` of the track that actually owns the shared `audioDataUrl`; a
  follower has none of its own) and `mixOffsetSec` (this segment's start
  offset into the shared file). Referenced by `id`, not array index, so the
  link survives `deleteTrack()`/`moveTrack()` reordering. New helpers
  `mixOwnerIndex()`, `isSameMixGroup()`, `isMixLinkedTrack()` (~line 3045).
- **UI, revised after first-pass feedback ("looks too much like Local, only
  need one mp3 load")**: this builder now enforces exactly one audio file
  for the whole class — Track 1 is always the mix owner; every other track
  is automatically a segment (no per-track "Attach MP3"/file picker exists
  below Track 1 at all). A single shared "🎵 Mix Audio" panel sits above the
  track list (`renderMixAudioPanel()`) with one Play/Pause, scrubber,
  active-segment label, "⏱️ Use Timestamp", and Attach/Replace control —
  `attachMixAudio()` auto-creates Track 1 if the list is empty. The header's
  old bulk "🎵 Select Music" (multi-file → multi-track) and "🔊 Scan dB"
  buttons were removed, and whole-window audio drag-and-drop now routes
  through `attachMixAudio()` too, since both bypassed the single-file model.
  Track cards were stripped of BPM nudge/Tap-Tempo/dB-gain controls (BPM is
  now a plain reference field — `getTrackPlaybackSpeed()` and the exported
  player's `getTrackSpeed()` both force `1.0` for any mix-linked track, since
  the shared file can't actually be sped up per segment) and of per-row
  play/progress bars. One unified `addTrackOrSegment()` backs every "Add
  Track" button (header, section, empty-state, bottom) — first track via
  `addNewTrack()`, every one after via `addMixSegmentTrack(0)`, which no
  longer requires the owner to already have audio attached. `DEFAULT_TRACKS`
  was cut from 7 sample songs down to 2 blank "Track 1"/"Track 2" rows to
  match the "Karen fills it in by hand" workflow.
- **Bug caught during this pass**: `loadAutoSave()`'s track-normalizer
  whitelisted a fixed set of fields and silently dropped everything else —
  including `id`, so `mixSourceId` references broke on every single reload,
  even a fresh page load with no saved data. Fixed by adding `id`,
  `mixSourceId`, `mixOffsetSec`, and (for parity with already-existing
  features whose UI is now hidden) `audioFileName`/`peakDb`/`volumeGain`/
  `originalBpm`/`detectedBpm`/`customSpeedMultiplier` to what it preserves.
- `addMixSegmentTrack()` creates a new track after the group with no file
  picker, just name/duration; offsets auto-recompute
  (`recomputeMixOffsets()`) whenever a duration in the group changes.
  `deleteTrack()` promotes the next segment to owner instead of orphaning
  the group's audio if the owner is deleted.
- **Playback engine**: `getPlayableAudioSrc()`, `toggleTrackAudio()`,
  `onAudioTimeUpdate()` (new `maybeAdvanceMixSegment()`),
  `updateBuilderSlotHighlights()`, `seekTrackAudio()`, and `renderCockpit()`
  all made mix-aware so a shared file plays through segment boundaries
  without `audio.src` ever being reassigned — the active track index
  advances purely from `audioPlayer.currentTime` crossing the next
  segment's offset, mirroring the pattern the app already used for
  movement-slot cues within one track. The exported standalone player
  (`exportCockpitForPhone()`) carries an equivalent hand-rolled copy of the
  same logic in its generated `<script>` string.
- **%Effort field**: new `MOVEMENT_DEFAULT_EFFORT_PCT` table sourced from
  `Docs & Guides/Class Design Quick Reference.jpg`'s Heart Rate Range
  column, auto-filling a movement-slot's %Effort (editable override) in the
  Select Movement/Zone/RPE modal; shown in slot cards, the Cockpit HUD
  movement grid, the Class Overview tooltip, and the exported player.
- **Known limitation**: mix groups are assumed contiguous in `classTracks`;
  `moveTrack()` doesn't guard against reordering a segment out of its
  group. Not fixed — flagged for follow-up if it comes up in practice.
- **Second feedback pass, same day**: removed the duplicate header-level
  "Add Track" button (kept the one above the track list + the one at its
  bottom); `addMixSegmentTrack()` now always inserts at `classTracks.length`
  instead of walking for the end of the owner's contiguous run, so a new
  track can never land mid-list if that run is ever broken (and
  `recomputeMixOffsets()` now walks the whole tail with `continue` instead
  of stopping at the first non-member track, for the same reason). Removed
  the track-level Cadence (RPM), Energy Zone, and Target RPE fields — all
  three are now handled per-movement (the modal already sets Zone/RPE per
  slot, cadence is implied by the movement chosen); `track.zone`/`track.rpe`
  still exist as inert fallback data for movements without their own
  override, just no longer editable at the track level. Removed the
  "SPINNING® MOVEMENTS & TRANSITIONS (UP TO 6)" label above the slot grid.
  BPM stays per-track and editable (user's explicit call, not moved to the
  Mix Audio panel), but attaching/replacing the mix file now backfills that
  same detected BPM onto every other track in the group whose BPM is still
  blank, so they start in sync without clobbering any track already
  customized by hand. `classTitle`'s hardcoded sample default ("Spin 001 -
  High Energy Endurance") was replaced with a blank field that auto-fills
  from the mix file's ID3 title/filename on attach — only when the user
  hasn't already typed a title.
- Own autosave key (`spinning_singlemix_autosave_v1`) and export filename
  prefix (`Spinning_SingleMix_`) so it doesn't collide with Local's saves.
- Verified via Python esprima (both the live builder's script and a
  triggered export's generated script, 0 errors) and headless Playwright:
  attached a real audio file, added 2 linked segments, confirmed
  `audio.src` never changes while `playingAudioTrackIdx`/`activeIdx`
  advances across both segment boundaries (live builder and the exported
  HTML both checked), confirmed the Cockpit HUD shows segment-relative
  time, confirmed the %Effort override/default flow, confirmed the Class
  Overview table's 🔗 chip.

**spinning_multisource_builder.html v5.0.46 / spinning_spotify_builder.html v4.9.17 (2026-08-31) — Movement/Zone/RPE Validation Strategy Ported From Local; 5-Builder Consolidation; "Course Designer" → "Class Builder" Rename**
- Three related asks in one session, recorded together. No in-app version
  badges were bumped (not requested) — git commits `486c810` and `1f159cf`
  are the record of what changed instead of a new `Backups/` snapshot set.
- **Rename**: "Course Designer" → "Class Builder" in the `<title>` and
  header `<h1>` of all files that had it — `spinning_local_builder.html`,
  `spinning_multisource_builder.html`, `spinning_spotify_builder.html`,
  `8n12_builder.html`, `8n12_weights_builder.html`, plus the 3 files later
  archived this session (`builder.html`, `builder_spotify.html`, `Spinning
  Class Builder Spotify Edition.html`). `LESSONS_LEARNED.md`'s historical
  changelog entries were deliberately left saying "Course Designer" since
  they're a record of past state, not live UI text.
- **Consolidation to 5 active builders**: user said there were too many
  root-level versions. Confirmed via `md5sum` that `builder.html` was a
  byte-identical twin of `spinning_local_builder.html`, and that
  `builder_spotify.html` + `Spinning Class Builder Spotify Edition.html`
  were both byte-identical twins of `spinning_spotify_builder.html` — all
  3 moved into `Backups/` (git-tracked renames/adds, not deletions).
  `index.html` turned out to be a wholly separate, unrelated tool ("Spinning®
  Class Profile Builder", 2803 lines, no relation to any of the 5 builders)
  — confirmed via `AskUserQuestion` before archiving it too, since it
  wasn't one of the 5 the user named and wasn't a duplicate either.
- **Movement/Zone/RPE port**: `spinning_local_builder.html` had accumulated
  a materially more advanced validation architecture than the SoundCloud
  (`spinning_multisource_builder.html`) and Spotify
  (`spinning_spotify_builder.html`) editions — a 3-way preview/commit split
  (`previewSymbol()` for movement-tile clicks vs. `selectSymbol()` +
  `applyModalSelection()` as the sole commit path via the Apply-to-Slot
  button), a "dead-end" grey downgrade for Movement+Zone+RPE combinations
  that are structurally impossible (vs. an amber "pick a different RPE"
  warning when a valid choice does exist), an Apply-button hard-disable on
  a genuinely broken rule, and user-facing toasts whenever the app
  auto-corrects a Zone/RPE choice instead of silently overriding it
  ("Lesson 121"). Spotify was further behind than Multisource: it had a
  stale `MOVEMENT_ALLOWED_ZONES` table, no `MOVEMENT_ALLOWED_RPES` table at
  all, and no Apply-to-Slot button/commit-bar in its modal whatsoever
  (every tile click committed instantly, no preview step).
- Confirmed via line-by-line diff (after isolating the exact function
  boundaries in each file) that **none** of this logic touches
  `soundcloudUrl`/`spotifyUrl`/iframe/widget code anywhere in any of the
  three files — the only adjacency is positional, not a data dependency —
  so the entire `MOVEMENT_ALLOWED_ZONES` → `applyModalSelection()` block
  was ported from `spinning_local_builder.html` into both target files via
  an exact line-range splice (`scratch/splice_multisource_block.py`,
  `scratch/splice_spotify_block.py`), rather than hand-patching each gap
  separately — safer for an exact, byte-for-byte match on 1.4MB+ files.
  Spotify additionally needed: the commit-bar HTML added to its modal, and
  the standalone mobile-cockpit export's `ZONE_RPE_BADGES` fallback added
  (it had none, so a movement with no explicit per-movement RPE rendered no
  badge at all on the exported HUD).
- Verified via esprima (0 errors, both files' main script) and headless
  Playwright: opened the movement modal, confirmed a tile click previews
  without closing the modal or committing, confirmed the Apply button's
  disabled state follows the zone/movement rule correctly (including the
  "allowed but not recommended" dead-end case), confirmed Apply commits and
  closes the modal. Also triggered the real `exportCockpitForPhone()`
  export (blob intercepted, not downloaded) for both files, confirmed the
  generated standalone HTML contains `ZONE_RPE_BADGES` and parses + renders
  with zero console errors when loaded fresh.
- `spinning_local_builder.html` itself was **not modified** — it was the
  read-only reference source for this port.

**spinning_local_builder.html v5.0.48 / builder.html v5.0.48 / spinning_multisource_builder.html v5.0.46 (2026-08-29) — Exported HUD Top-Bar Spacing Fix**
- User opened a real exported Mobile Cockpit HTML file from Downloads and
  reported the top bar (class title + version badge on the left, total
  timer on the right) "looks a bit cramped".
- Root cause: a genuine, pre-existing inconsistency between the live
  builder's Cockpit tab and the exported standalone HUD's CSS, not just
  perception. The live `.cockpit-hud-topbar`/`.cockpit-total-timer` rules
  use `padding: 8px 16px` / `font-size: 0.88rem` and `padding: 3px 10px`
  respectively — but the `exportCockpitForPhone()` generator in
  `spinning_local_builder.html` and `spinning_multisource_builder.html`
  pushed tighter values (`padding: 6px 12px` / `font-size: 0.82rem` and
  `padding: 3px 8px` / `font-size: 0.8rem`). Cross-checked all 5 files:
  `8n12_builder.html` and `8n12_weights_builder.html` already used the
  roomier values, so only these two files (plus their `builder.html`
  mirror) had the tighter, cramped ones.
- Fixed by bringing the tight files' exported CSS up to match the
  already-correct roomier standard, rather than guessing at new numbers.
- Verified via esprima (0 errors) and a real export-then-screenshot pass
  (triggered `exportCockpitForPhone()`, fetched the generated blob,
  rendered it in a fresh page) confirming visibly more breathing room in
  the top bar.
- `builder.html` re-synced from `spinning_local_builder.html`; confirmed
  identical via `md5sum`.
- Snapshot: `*_ExportTopbarSpacingFix_*.html` for all 3 files.

**All 5 active files (2026-08-29) — Cockpit Scrubber-Row Text-Wrap Fix**
- User reported audio "glitchiness" on `spinning_local_builder.html` that
  visually correlated with the scrubber row (the `-5s`/current-time/status/
  remaining-time/`+5s` row above the progress bar) flicking to a taller,
  wrapped layout whenever the elapsed/remaining time values grew a digit
  (e.g. `-9:36` → `-13:15`). Root cause: `.cockpit-hud-scrubber-row` is a
  `display:flex` row with no `white-space:nowrap` on its child spans —
  when total content width got tight, an individual span's text (most
  often `#cockpitStatusText`, the longest/most variable piece — things
  like "⚡ Cue active until track end (1m 23s)") would wrap internally,
  growing that flex item's height and visibly reflowing the whole HUD on
  every `timeupdate` tick while a value hovered near the wrap threshold.
- Confirmed via a worst-case Playwright test (forcing `123:45` /
  `-123:45` / a long status string into the DOM) that the row's rendered
  height jumped from a single line to a wrapped, taller box before the
  fix, and stayed single-line after it.
- Fix: added `white-space:nowrap; flex-shrink:0;` to the two nudge
  buttons and the two time spans (so they never wrap and never get
  squeezed below their natural width), and — only on the two files that
  have a `#cockpitStatusText` span (`spinning_local_builder.html` /
  `builder.html` and `spinning_multisource_builder.html`) —
  `white-space:nowrap; overflow:hidden; text-overflow:ellipsis; flex:1;`
  so that span truncates with an ellipsis instead of wrapping when it's
  the one running out of room. `8n12_builder.html` and
  `8n12_weights_builder.html` don't have a status span in this row at all
  (just the two buttons + two time spans), so only needed the nowrap/
  flex-shrink half of the fix. Per the user's "remove icons if you have
  to" — simplified the nudge buttons from "⏪ -5s"/"⏩ +5s" to plain
  "-5s"/"+5s" across all 5 files to free up horizontal room, since the
  emoji weren't load-bearing for meaning.
- **Confirmed by the user after shipping**: playback is smooth now — the
  scrubber-row reflow (triggered every `timeupdate` tick whenever a
  countdown value sat near the wrap threshold) really was causing the
  audible glitching, not just a visually-correlated coincidence. Worth
  remembering for future perf reports on this codebase: layout thrashing
  in the Cockpit HUD's per-tick render path is apparently frequent/heavy
  enough here to cause audible audio stutter, so don't assume audio
  decode is safely isolated from main-thread layout work in this app —
  see [[spinning-blob-url-audio-caching]] for the other validated audio
  perf fix from earlier this session.
- `builder.html` re-synced from `spinning_local_builder.html` (mirror
  obligation) both before and after the version bump; confirmed identical
  via `md5sum` each time.
- Verified via esprima (0 errors, all 5 files) and headless Playwright
  screenshots confirming single-line layout under worst-case wide values
  in every file.
- Snapshot: one `*_ScrubberRowWrapFix_*.html` per file, timestamped
  together.

**spinning_local_builder.html v5.0.46 / builder.html v5.0.46 / 8n12_builder.html v5.0.56 / spinning_multisource_builder.html v5.0.44 (2026-08-29) — ID3 Artist/Title Tag Reading Ported From 8n12_weights_builder.html**
- User attached a real track ("09 - Hallowed Be Thy Name.mp3", confirmed
  via a VLC screenshot to carry real ID3 tags — Artist: Iron Maiden,
  Album: The Number Of The Beast) to `spinning_local_builder.html` and the
  artist still didn't populate. Root cause: the `parseID3TagsFromArrayBuffer`
  fix built for `8n12_weights_builder.html` earlier this session was never
  ported to the other 4 active files — each still only ever parsed the
  *filename* (`parseArtistAndTitleFromFileName`), which fails here because
  "09 - Hallowed Be Thy Name.mp3" has no further `" - "` to split into
  artist/title once the leading track-number prefix is stripped.
- Ported the identical `parseID3TagsFromArrayBuffer(buf)` function (reads
  `TPE1`/`TPE2` artist and `TIT2` title frames from the file's real ID3v2
  tag) into `spinning_local_builder.html`, `8n12_builder.html`, and
  `spinning_multisource_builder.html`, then rewired each file's
  `handleSingleTrackAudioImport` the same way: fetch `arrayBuf` first,
  resolve `id3Tags.title || parsed.title || targetTrack.name` for the name
  and `id3Tags.artist || parsed.artist` for the artist (ID3 wins when
  present, filename-guess is the fallback). Unlike the weights variant,
  `track.name` genuinely *is* the song title in these 3 files (never
  repurposed as an exercise/movement name), so ID3 is allowed to update it
  too — no name-preservation guard needed here.
- Bundled in the same pass: `8n12_builder.html` and
  `spinning_multisource_builder.html` still had the old, already-fixed-
  elsewhere stale-artist bug (`if (parsed.artist) targetTrack.artist = ...`
  — only wrote artist when filename parsing found one, so replacing a file
  with no parseable artist silently kept the *previous* track's artist).
  Fixed alongside the ID3 port since it's the exact same lines being
  touched; `spinning_local_builder.html` already had this fixed from
  earlier in the session.
- **`builder.html` mirror maintenance**: per the mirror discovery earlier
  this session, `builder.html` must stay byte-identical to
  `spinning_local_builder.html`. Confirmed via `md5sum` they'd diverged
  (only `spinning_local_builder.html` had been edited), re-synced by
  copying the whole file over rather than hand-applying the diff twice
  (safe here since the only difference before this session's edit was
  nothing — they were fully identical), and reconfirmed identical
  `md5sum` after the version bump too.
- Used a small shared Python port script
  (`scratch/port_id3_tags.py`, since removed) rather than hand-editing
  each file, to guarantee byte-identical function bodies across all 4
  files and avoid manually retyping the NUL-byte-sensitive escape
  sequences a fourth time.
- Verified via esprima (0 errors, all 4 files) and headless Playwright
  against real ID3-tagged files (`audio/track4.mp3`, ID3 artist "Madonna",
  title "Hung Up (SDP's Extended Dub)") in each of the 4 files: confirmed
  both name and artist update correctly from the real tag data, with zero
  console errors.
- Snapshot: one `*_ID3ArtistTagReading_*.html` per file, timestamped
  together.
- **Not yet ported**: nothing — this closes the gap across every active
  file. `8n12_weights_builder.html` keeps its own variant (ID3 artist only
  feeds `track.artist`; title feeds the separate `track.songTitle`
  caption, never `track.name`, since that field means something different
  there).

**8n12_weights_builder.html v0.5.1 (2026-08-29) — Inline Artist + Song Title**
- `8n12_weights_builder.html` only. The artist input and the real-song-title
  caption (added in v0.4.2) were stacked on separate lines in the Track &
  Artist cell. Wrapped both in a `display:flex` row (artist input at
  `flex:1`, caption as a `white-space:nowrap` + `text-overflow:ellipsis`
  span) so they sit side by side on one line instead.
- Verified via esprima (0 errors) and a Playwright screenshot of a real
  attach (track4.mp3 → "Madonna" | "🎵 Hung Up (SDP's Extended Dub)" on
  one line).
- Snapshot: `Backups/8n12_weights_builder_v0.5.1_InlineArtistSongTitle_*.html`.

**All 5 active files (2026-08-29) — Bluetooth / Lock-Screen Media Controls (Media Session API)**
- User asked for this across "all versions": `spinning_local_builder.html`
  (v5.0.45), `8n12_builder.html` (v5.0.55), `8n12_weights_builder.html`
  (v0.5.0), `spinning_multisource_builder.html` (v5.0.43), and `builder.html`
  (v5.0.45) — the same "all but Spotify" scope established earlier this
  session. Applied to **both** the live Cockpit tab and the standalone
  exported Mobile Cockpit HUD in every file, since the exported HUD is the
  actual artifact played on a phone during a workout — the primary use
  case for Bluetooth headset controls.
- Discovery made while scoping this: `builder.html` is not a separate
  "older lineage" file as the table above previously said — a recent
  commit (`6671778 Publish spinning_local_builder as both builder.html and
  spinning_local_builder.html`) made it a byte-identical republish of
  `spinning_local_builder.html`. Confirmed via `md5sum` before and after
  editing both — they matched going in and still matched after applying
  the identical diff to each. Table above updated to reflect this; **both
  files must keep receiving the same edits going forward** or they'll
  silently diverge.
- Implementation, applied identically to all 5 (function names for
  play/pause/next/prev turned out to be identical across every file —
  `toggleCockpitAudio()`, `prevTrack()`, `nextTrack()`, and a shadowed/dead
  duplicate `toggleTrackAudio()` inherited from the same root cause found
  earlier in `spinning_local_builder.html`):
  - **Live Cockpit**: added `updateMediaSessionMetadata(track)` (sets
    `navigator.mediaSession.metadata` — title/artist/album) and
    `setupMediaSessionHandlers()` (registers `play`/`pause`/`previoustrack`/
    `nexttrack` action handlers, wired to the existing `audioPlayer`/
    `prevTrack`/`nextTrack`). Rather than scattering metadata-update calls
    through every function that can start/stop playback, hooked the
    native `audioPlayer` `'play'`/`'pause'` DOM events instead — one place,
    stays correct regardless of which code path (button click, OS
    Bluetooth button, `nextTrack` auto-advance) changed playback state.
  - **Exported HUD**: mirrored the identical pattern into the
    `parts.push(...)`-generated script inside `exportCockpitForPhone`,
    using the export's own `togglePlay()`/`prevTrack()`/`nextTrack()` and
    a `CLASS_TITLE` constant baked in at export time via
    `JSON.stringify(title)`.
  - `spinning_multisource_builder.html`/`builder.html`'s SoundCloud-embed
    branch is a known, accepted gap: Media Session only reflects the
    local-`<audio>`-element path, since a SoundCloud iframe never fires
    `audioPlayer` events. Noted in a code comment rather than solved —
    SoundCloud tracks simply won't expose Bluetooth transport controls.
- **Real, pre-existing bug found and fixed while verifying** (unrelated to
  Media Session, but blocked testing it): `spinning_multisource_builder.html`'s
  exported HUD had a `SyntaxError` in the generated script — the
  SoundCloud-iframe-markup line built its HTML attributes with unescaped
  double quotes inside a double-quoted JS string (`"<div style="width:100%;
  ...`), so the string terminated after `style=` and `width:100%` became
  bare, invalid JS. Because this is one giant script block, **the entire
  exported HUD was non-functional for every export from this file** —
  not just the SoundCloud path — Play/Pause/Next/Prev, all of it, dead on
  arrival. Confirmed via esprima against the actual exported output (not
  just the source file, which looked fine at a glance) and by browser
  console errors (`"Unexpected identifier 'width'"`,
  `"togglePlay is not defined"`). Fixed by rebuilding the line
  programmatically in Python (constructing the correctly-escaped source
  string via `.replace('\\', '\\\\').replace("'", "\\'")` rather than
  hand-typing nested backslashes) and confirming the *target* generated JS
  parsed standalone before touching the real file, then confirming the
  actual re-exported HTML parses and runs end-to-end.
- Verified via esprima (0 errors, all 5 files) and headless Playwright
  against all 5 files' live Cockpit *and* exported HUD: for files whose
  `DEFAULT_TRACKS[0]` ships with embedded sample audio (`8n12_builder.html`,
  `8n12_weights_builder.html`), played the real default track. For the
  other 3 (whose default track 0 has no embedded audio), injected a real
  MP3 via `classTracks[0].audioDataUrl` first so the test proves actual
  playback, not just "no error was thrown." In every case: confirmed all
  four actions (`play`/`pause`/`previoustrack`/`nexttrack`) registered
  with `navigator.mediaSession.setActionHandler` (verified by patching
  `setActionHandler` before page load to record calls), confirmed
  `navigator.mediaSession.metadata.title` and `.playbackState` update
  correctly on real play, and confirmed `audio.currentTime`/
  `audioPlayer.currentTime` actually advances — proving genuine playback,
  not a mocked/stubbed check.
- Snapshot: one `*_MediaSessionBluetooth_*.html` (or
  `*_MediaSessionAndSoundCloudFix_*.html` for the multisource file) per
  file, all timestamped together.

**8n12_weights_builder.html v0.4.2 (2026-08-29) — Real Song Title Caption**
- `8n12_weights_builder.html` only, follow-up to v0.4.1 in the same
  session. User pointed out that once Artist started being pulled in
  correctly (v0.4.1), the file's real Title tag/filename info was *still*
  going nowhere — `track.name` is protected (holds the exercise), and
  nothing ever captured the actual song title at all, so it was
  effectively discarded on every attach.
- Generalized `parseID3ArtistFromArrayBuffer` into
  `parseID3TagsFromArrayBuffer(buf)`, extracting both `TPE1`/`TPE2`
  (artist) and `TIT2` (title) frames in a single pass over the same ID3v2
  tag (shared frame-walking loop, one `decodeFrameText` helper for both).
  `handleSingleTrackAudioImport` now resolves
  `id3Tags.title || parsed.title` into a new `track.songTitle` field —
  separate from `track.name`, so the exercise name is never touched.
- Added a small muted caption under the artist input in the Track & Artist
  cell — "🎵 <real song title>" — shown only when `songTitle` exists and
  differs from the exercise name, so bookend tracks (where name already
  *is* the real title) don't show a redundant duplicate.
- **Caught and fixed my own bug while refactoring**: rebuilding the ID3
  parser function via a Python one-off script hit the exact same NUL-byte
  trap as v0.4.1 — twice. First, editing the file through the Edit tool
  failed silently-safe (its exact-string match rejected the change because
  the file uses CRLF line endings, so no bytes were touched — verified via
  a byte-level `grep`/diff before assuming anything landed). Then a
  Python heredoc replacement did apply, but a naive ` ` inside a
  Python string literal got interpreted as an actual NUL character
  (again) rather than the literal 4-character escape text intended for
  the JS source — caught immediately via the same byte-level NUL-count
  check used in v0.4.1, and fixed properly by constructing the replacement
  bytes from explicit `bytes([0x5c]) + b'u0000'` rather than typing
  backslash-escapes through three nested layers of string interpretation
  (JSON tool-call → bash heredoc → Python string literal). Confirmed zero
  NUL bytes in the file both times before moving on.
- Verified via esprima (0 errors) and headless Playwright against the same
  real ID3-tagged file (`track4.mp3`): `track.name` stays "Lat Pull Down",
  `track.artist` becomes "Madonna", `track.songTitle` becomes "Hung Up
  (SDP's Extended Dub)" exactly matching the file's real ID3 tags, and the
  caption renders correctly in the cell (screenshot-confirmed). Re-ran the
  v0.4.0 and v0.4.1 regression scripts afterward to confirm the rename
  from `parseID3ArtistFromArrayBuffer` didn't break either earlier fix —
  both still pass.
- Snapshot: `Backups/8n12_weights_builder_v0.4.2_ID3TitleCaption_*.html`.

**8n12_weights_builder.html v0.4.1 (2026-08-29) — Real ID3 Artist Tag Reading**
- `8n12_weights_builder.html` only, follow-up to v0.4.0's Attach-MP3 fix in
  the same session. User reported that after the fix stopped clobbering
  the exercise name, Artist still never got filled in on attach/replace.
  Root cause: `parseArtistAndTitleFromFileName()` has only ever parsed the
  **filename** string ("Artist - Title.mp3") — it has no way to see a
  file's actual embedded ID3 metadata, and most real MP3 filenames don't
  follow that pattern. Confirmed with `mutagen` against the local sample
  files: `audio/track3.mp3` carries a real `TPE1` tag "Lange feat. Skye"
  and `audio/track4.mp3` carries "Madonna", neither recoverable from the
  filename.
- Added `parseID3ArtistFromArrayBuffer(buf)`: a small hand-rolled ID3v2
  parser (right after `parseArtistAndTitleFromFileName`) that walks the
  tag header, iterates frames looking for `TPE1`/`TPE2`, and decodes the
  frame's text per its ID3 encoding byte (ISO-8859-1, UTF-16 with BOM,
  UTF-16BE, or UTF-8). No library — everything's read directly off the
  `ArrayBuffer` already available in `handleSingleTrackAudioImport`
  (previously only used for BPM detection/loudness). Returns `''`
  gracefully for files with no ID3v2 header, no artist frame, or anything
  unparseable.
- Wired into `handleSingleTrackAudioImport`: artist now resolves as
  `parseID3ArtistFromArrayBuffer(arrayBuf) || parsed.artist` — ID3 tag
  wins when present (more reliable than a filename guess), falling back to
  the existing filename parser otherwise. `track.name` is still never
  touched by either path, preserving the v0.4.0 fix.
- **Self-caught bug during implementation**: the first draft of the ID3
  parser's null-byte checks (the frame-padding sentinel and the
  trailing-null trim on decoded text) accidentally wrote 5 literal NUL
  bytes into the HTML file itself instead of the intended ` ` escape
  sequences — caught immediately via a byte-level `grep`/Python check
  before ever running it, and fixed by replacing the raw bytes with proper
  escape sequences (confirmed zero NUL bytes remain anywhere in the file
  afterward).
- Verified via esprima (0 errors) and headless Playwright against real
  files: `track4.mp3` (ID3 artist "Madonna") and `track3.mp3` (ID3 artist
  "Lange feat. Skye") both correctly populate `track.artist` with the
  exact tag value (no stray trailing characters) while `track.name` stays
  the exercise name; `track1.mp3` (no ID3 header at all) leaves the
  existing artist untouched with zero console errors, confirming the
  graceful-failure path.
- Snapshot: `Backups/8n12_weights_builder_v0.4.1_ID3ArtistTagReading_*.html`.

**8n12_weights_builder.html v0.4.0 (2026-08-29) — Page 1/Page 2 Merge + Print Button**
- `8n12_weights_builder.html` only, follow-up to v0.3.1 in the same
  session. User asked to make the Track Builder (Page 1) look like the
  Class Overview table (Page 2), add a Print button, and retire Page 2 —
  confirmed via `AskUserQuestion`: real `<table>` rows (not just slimmer
  cards), and remove the Page 2 tab entirely rather than leave it in
  place.
- Rewrote `renderTracks()` to build one `<tr>` per track (via
  `document.createElement('tr')`, matching the old `renderSummaryTable()`
  pattern) inside a `<table class="summary-table">` — reusing that
  existing CSS class so the new Page 1 genuinely inherits Page 2's look —
  instead of a `<div class="track-card">` per track. Columns: # | Track
  & Artist (editable inputs, unlike Page 2's read-only text) | Duration
  (read-only) | Weight+kg (editable) | Audio (Play/pause + time + scrub +
  Add/Replace MP3, compacted into one cell) | Order (▲▼🗑️, right-justified).
  Dropped the Power column/badge and the BPM speed badge from the merged
  view — both are dead/unused now that nothing in this file edits them,
  consistent with earlier cleanup passes this session.
- Added a "🖨️ Print" button to Page 1's header (next to "➕ Add New
  Track"), reusing the same `onclick="window.print()"` Page 2 used — no
  dedicated print stylesheet exists in this file, so printing relies on
  `.view-section:not(.active) { display:none }` already hiding whichever
  tab isn't open, same mechanism Page 2's print relied on.
- Removed Page 2 entirely: the `tabBtnOverview` tab button, the
  `#viewOverviewSection`/`#overviewTableBody` markup, `renderSummaryTable()`,
  `editTrackSlots()` (only ever called from Page 2's now-gone "Edit"
  button), and the `'overview'` branch in `switchViewMode()`. Also found
  and fixed two now-stale `document.querySelectorAll('.track-card')`
  auto-scroll calls (in the "track finished, jump to next" and "track
  added, scroll to it" flows) that would have silently no-op'd since
  `.track-card` no longer exists anywhere — repointed both at
  `#tracksList tr`.
- **Bug fix bundled into this version**: user reported that replacing a
  track's MP3 via "Add/Replace MP3" overwrote the exercise name (e.g.
  "Lat Pull Down" reverted to "Do you know", the new file's parsed
  filename) while the weight stayed correct. Root cause:
  `handleSingleTrackAudioImport()` unconditionally did
  `targetTrack.name = parsed.title` on every attach/replace — correct
  behavior in the other builder editions where `name` holds the song
  title, but wrong here where `name` holds the movement/exercise
  (renamed away from song titles back in v0.2.0). Fixed by dropping that
  one line in this file only, leaving the artist-parsing line untouched
  (not reported as broken, and out of scope for a single-line surgical
  fix per the user's explicit ask).
- Verified via esprima (0 errors) and headless Playwright: confirmed the
  Overview tab/section are gone from the DOM, 12 rows render, editing
  title/weight writes back to `classTracks`, Play/Move/Delete/Add all
  work end-to-end, the Print button exists and is wired correctly, the
  Cockpit tab still switches fine, and — for the MP3-replace fix
  specifically — replaced a real track's audio file and confirmed
  `track.name` and the weight are both unchanged afterward. Also took a
  screenshot of the merged table to visually confirm the layout.
- Snapshot: `Backups/8n12_weights_builder_v0.4.0_Page1Page2MergePrintButton_*.html`.

**8n12_weights_builder.html v0.3.1 (2026-08-29) — Header Row Layout**
- `8n12_weights_builder.html` only, follow-up to v0.3.0 in the same
  session. Moved the Weight+kg box from the audio-controls row up into the
  top `track-main-row`, right beside the title/artist fields (the
  "movement"), and right-justified the ▲ ▼ 🗑️ move/delete button group
  after it (`justify-content:flex-end` added alongside the existing
  `margin-left:auto`). Confirmed via screenshot: Weight box sits
  immediately after the title, buttons pushed to the far right.
- User then asked where the *real* song name/artist should now be shown,
  since the title field displays the exercise name — offered to add it to
  the Track Builder card, the Cockpit HUD, or both via `AskUserQuestion`.
  User's answer: Page 2 (Class Overview & Plan)'s existing "Track & Artist"
  column already covers this, so no new UI was added anywhere.
- Renamed the "🎵 Attach MP3" button to "🎵 Add/Replace MP3" (and its
  tooltip) per user feedback that "Attach" doesn't read as covering the
  common case of swapping out an already-attached file.
- Verified via esprima (0 errors) after each change and a Playwright
  screenshot of the final card layout.
- Snapshot: `Backups/8n12_weights_builder_v0.3.1_HeaderRowLayout_*.html`.

**8n12_weights_builder.html v0.3.0 (2026-08-29) — Inline Weight Box + Cockpit/Overview Cleanup**
- `8n12_weights_builder.html` only, follow-up to v0.2.0 in the same
  session. Three rounds of user feedback from live screenshots:
  1. Moved the Weight input from its own row up into the audio-controls
     row next to the Play/progress/Attach MP3 controls, and added a "kg"
     unit suffix. `weightBoxHtml` (renamed from `slotBannerHtml`) is now
     `display:inline-flex` and appended directly into that row instead of
     being appended as a separate block below it.
  2. Page 2 (Class Overview & Plan) table still had "Song BPM" and "Audio
     dB" columns — removed both (header `<th>`s and their `<td>`s in
     `renderSummaryTable()`). Also caught and fixed a real bug while in
     there: the table's "Weight" column was still reading the old
     `eightN12.s2Weight` (Blast/slot-2, no longer editable anywhere) instead
     of `s1Weight` (the one field the inline box actually writes to via
     `update8n12Field(tIdx, 1, 'weight', v)`) — would have silently frozen
     at the seeded default and never reflected edits. Now reads `s1Weight`.
  3. Instructor Cockpit HUD: removed the instructor cue box entirely
     (`#cockpitCueBox`, which showed spin-style auto-text like "You need
     weight 40, power target is 300"), removed the Power metric card
     (kept Weight, now reading `s1Weight` instead of the dead `s2Weight`),
     and removed a redundant metric card that duplicated the exercise name
     a second time right below the title — that card used to show the
     movement type (Seated Flat/Standing Climb), which is meaningless now
     that the movement-type selector is gone, so it was just repeating
     "Lat Pull Down" twice on screen. Confirmed via `AskUserQuestion`
     before deleting it outright rather than repurposing it. Also, while
     diagnosing a "no track song name or artist?" question: confirmed via
     the exported JSON that these tracks have always had an empty `artist`
     field (pre-existing data, not a bug) and that the hero title now
     intentionally shows the exercise name (`track.name`) rather than the
     original song title, per the v0.2.0 rename — same root cause pattern
     as the `spinning_local_builder.html` "Instructor Track" question
     answered earlier this session.
- Left the SONG BPM metric card in the Cockpit HUD, and the entire export
  HUD generator, untouched — not requested in this pass. Both are known
  pending cleanup items (still spin-flavored) if the user wants them
  addressed later.
- Verified via esprima (0 errors) after each change and headless Playwright
  screenshots of both the Track Builder card (inline Weight+kg box next to
  play controls) and the Cockpit HUD (confirmed `#cockpitCueBox` and
  `#cockpitTargetPower` no longer exist in the DOM, zero console errors).
- Snapshot: `Backups/8n12_weights_builder_v0.3.0_InlineWeightAndCockpitCleanup_*.html`.

**8n12_weights_builder.html v0.2.0 (2026-08-29) — Weights-Only Card Simplification**
- `8n12_weights_builder.html` only. User flagged (via 4 screenshots) that
  the track cards still carried spin-class concepts that don't apply to a
  weights class: SONG BPM/Tap-tempo, CADENCE (RPM), DURATION, the "⏱️ Use
  Timestamp" button, the 6-slot (bookend) / 2-slot (regular) instructor-cue
  timeline, and the dual Recovery(blue)/Blast(red) interval banner with
  movement-type + Weight + Power. Confirmed exact scope via
  `AskUserQuestion` before touching the card: remove Duration along with
  BPM/Cadence (not just the two purely-spin fields), delete the whole
  Blast(red) box and relabel the surviving box from "RECOVERY" to plain
  "Weight", and remove the cue-slot timeline entirely rather than reducing
  it further.
- Track cards now show: name, artist, play/pause + progress bar + Attach
  MP3 (audio itself is untouched — still real background music per track),
  and a single "Weight" number input. Warm-up/cool-down tracks (track 1 &
  the last track) show no banner at all, since they carry no exercise
  weight.
- Implementation: `slotBannerHtml` rewritten to drop the red box, the
  bookend 6-slot cue grid, and `movTypeLabel`/`s2Weight`/`s2Pow` entirely,
  keeping only `s1Weight` bound to `update8n12Field(tIdx, 1, 'weight', v)`.
  Removed the `movements-section` (Cues C1 & C6) block and the
  `VISIBLE_SLOT_INDICES`-driven slot rendering from `renderTracks()`, the
  SONG BPM/DURATION/CADENCE `form-group`s from the track main-row, and the
  "Use Timestamp" button from the audio-controls row. Left the now-unused
  function definitions (`cycleMovementType`, `useTimestamp`,
  `renderSingleSlotWrapperHtml`, `ensureSlot1DefaultCue`, etc.) in place as
  dead code rather than deleting them — they're still called from
  `ensureCueDefaultsForAllTracks()` (startup/pre-export) and are harmless
  now that nothing reads `track.movements` in the Editor tab; the Cockpit
  tab, Overview table, and export HUD were explicitly left untouched
  (out of scope — the user's screenshots were all from the Track Builder
  editor tab specifically), so those views may still show old-style spin
  cue text/badges sourced from `track.eightN12`/`movements` until a
  follow-up pass covers them too.
- Set new default exercise names + weights for tracks 2-11 in both
  `DEFAULT_TRACKS` (`name` field, via id-anchored string edits since that
  array is a single ~54MB line with embedded audio) and `SLOT2_DEFS` inside
  `init8n12TrackDefaults()` (the `weight` value that seeds `s1Weight`):
  Lat Pull Down (40), Bench Press (58), Squat (30), Bench Row (36), Tricep
  Ext (18), Upright Row (30), Butterfly (18), Leg Ext (31), Bicep (30),
  Plank (0). Track 1 ("Do you know [START]") and track 12 ("Cool Down
  [END]") were left as the existing warm-up/cool-down tracks.
- Verified via esprima (0 errors) and headless Playwright
  (`scratch/verify_weights_simplification.py`): confirmed the 10 default
  names/weights, confirmed none of the removed UI text
  (SONG BPM/CADENCE/DURATION-label/Use Timestamp/INSTRUCTOR CUES/BLAST/
  RECOVERY) appears anywhere in the Editor tab's DOM, and confirmed exactly
  10 Weight input boxes render (one per non-bookend track). Also took a
  screenshot of the rendered cards to visually confirm the simplified
  layout.
- Snapshot: `Backups/8n12_weights_builder_v0.2.0_WeightsOnlySimplification_*.html`.

**spinning_local_builder.html v5.0.44 (2026-08-29) — Blob/ObjectURL Audio Caching (Live + Export)**
- `spinning_local_builder.html` only. User reported the live cockpit felt
  sluggish and audio "struggles" once it starts playing, especially on
  replay/track-switch — tracks are 50-80MB MP3s stored as raw base64
  `data:` URIs on `track.audioDataUrl`, and every time that string is
  handed to `audio.src` the browser has to re-decode the whole thing.
- Added `getPlayableAudioSrc(track)` (right before `toggleTrackAudio`,
  ~L2967): converts `audioDataUrl` to a `Blob` → `URL.createObjectURL()`
  once, caches it on the track (invalidating/rebuilding if the audio is
  ever replaced), and returns the cached `blob:` URL on subsequent calls.
  Wired into the one live playback assignment site inside `toggleTrackAudio`
  (there's a second, dead/shadowed copy of that function earlier in the
  file from a pre-existing duplicate-function-name bug — left untouched,
  out of scope for this change).
- Benchmarked before extending further (`scratch/benchmark_audio_src.py`,
  real ~57MB test file built by concatenating sample tracks): first play is
  roughly the same cost either way (both must decode once), but every
  subsequent play/resume/track-switch drops from ~191ms to ~2.7ms
  "ready-to-play" latency, and ~216ms to ~28ms until audio is actually
  audible — a ~70x improvement on repeats, which is exactly the "struggles
  once it starts" symptom reported.
- Extended the same pattern into `exportCockpitForPhone`'s generated
  standalone HUD script (the `parts.push(...)` string-building around
  L2306-2362): added an equivalent `getPlayableAudioSrc(t)` inside the
  generated JS (stashing `__blobUrl`/`__blobSrc` directly on the plain
  track objects, since the exported HUD has no need for a `WeakMap` — it's
  a standalone, read-only viewer), and pointed the generated
  `loadTrackAudio(idx)` at it instead of the raw `t.audioDataUrl`.
- Verified via `scratch/verify_export_blob_url.py`: triggered the real
  export from a live page (intercepted the anchor `.click()` to capture the
  blob without actually downloading), esprima-checked the generated inline
  script (0 errors), confirmed `getPlayableAudioSrc` is present in the
  output, then loaded the exported HUD itself in a fresh page, clicked
  "Play Workout", and confirmed `audio.src` became a `blob:` URL and
  `audio.currentTime` actually advanced (1.4s after ~1.5s of real
  playback) — proving the exported file plays real audio via the cache,
  not just that it parses.
- Bug fix bundled into this version: removed a misleading `(Auto-Synced)`
  suffix from the `'⚡ Workout Timer & Audio Started!'` toast
  (`startCockpitTimer`, ~L2562) — user flagged it as a leftover from
  earlier Spotify lead-in-sync experimentation (there's a comment a few
  lines above explaining the old 10s BBC-pip Spotify sync lead-in was
  intentionally removed from this edition). Confirmed via code trace that
  `startCockpitTimer` only ever runs on the *no-audio-attached* fallback
  branch of `toggleCockpitAudio` — so even "& Audio Started" is arguably
  inaccurate there, but that wording wasn't what was flagged, so it was
  left as-is pending a decision.
- Same toast wording (`'⚡ Workout Timer & Audio Started! (Auto-Synced)'`)
  turned out to be copy-pasted identically into `8n12_builder.html`,
  `8n12_weights_builder.html`, `spinning_multisource_builder.html`, and
  `builder.html` — fixed identically in all of them per the user's "amend
  all but the spotify version" request. Checked all three Spotify-named
  files (`Spinning Class Builder Spotify Edition.html`, `builder_spotify.html`,
  `spinning_spotify_builder.html`) and none of them contain this string at
  all, so nothing needed preserving there. Each file bumped one patch
  version and snapshotted individually (see version table above) — the
  Blob-URL caching work itself is `spinning_local_builder.html` only.
- Snapshot: `Backups/spinning_local_builder_v5.0.44_BlobUrlAudioCache_*.html`
  (+ one `*_ToastFix_*.html` snapshot per other file listed above).

**8n12_builder.html v5.0.53 (2026-08-29) — Default Profile Auto-Load (Fallback Only)**
- `8n12_builder.html` **only** — confirmed `8n12_weights_builder.html` and
  `spinning_local_builder.html` have zero references to `DEFAULT_PROFILE_DATA`
  or `8n12_default_profile`, per the user's explicit "8n12 ONLY" request.
- User created `Default/v5.0.52_8n12_default_Class_Profile.json` (a full
  12-track 8n12 class profile with embedded audio) and asked for it to
  auto-load into the builder on refresh. Confirmed via `AskUserQuestion`
  that this should be **fallback-only**: it seeds a brand-new session, but
  must never overwrite an in-progress autosaved session.
- Key finding: a `file://`-loaded page's `fetch()` of a local JSON file is
  blocked by CORS ("Failed to fetch"), but `<script src="local.js">` tag
  loading of a local file works fine — confirmed empirically with a minimal
  Playwright repro in `scratch/filetest/` before choosing an approach.
- Implementation: wrapped the JSON as `Default/8n12_default_profile.js`
  (`const DEFAULT_PROFILE_DATA = {...};`) and loads it via a blocking
  `<script src="Default/8n12_default_profile.js">` tag in `<head>` — by the
  time the app's own inline script runs, `DEFAULT_PROFILE_DATA` is
  guaranteed defined (or simply `undefined` if the file is missing/renamed,
  which degrades gracefully to the old built-in `DEFAULT_TRACKS`).
- Root-cause bug hit along the way: `classTracks` was pre-seeded at module
  scope with `DEFAULT_TRACKS` *before* `loadAutoSave()` ever ran, making
  `loadAutoSave()`'s `if (!classTracks...)` empty-check permanently
  unreachable dead code — so the new fallback logic never actually executed
  despite `DEFAULT_PROFILE_DATA` loading correctly. Diagnosed via repeated
  Playwright runs (ruled out timing/race and duplicate handlers first).
  Fixed by making the seed line itself prefer `DEFAULT_PROFILE_DATA` when
  present, and rewriting `loadAutoSave()` to track a `loadedFromAutosave`
  flag so title/instructor/energy-zone fields are only set from the Default
  profile when an autosave did *not* win.
- `resetSampleTracks()` (toolbar "🔄 Reset" button) also updated to prefer
  `DEFAULT_PROFILE_DATA.tracks` over `DEFAULT_TRACKS` for consistency —
  it only ever touched track data, not title/instructor/zone, so no change
  needed there beyond the data-source swap.
- Verified via esprima (0 errors) and headless Playwright: (a) fresh
  context, no autosave → `classTitle` = "8n12 default", 12 tracks, 0 console
  errors; (b) autosave present with audio → autosave wins, Default profile
  ignored entirely, 0 console errors.
- Snapshot: `Backups/8n12_builder_v5.0.53_DefaultProfileFallback_*.html`.

**spinning_local_builder.html v5.0.43 (2026-08-29) — Wall-Clock-Accurate Timing**
- Follow-up to v5.0.42, `spinning_local_builder.html` only.
- Resolves the open question from v5.0.42: displayed durations/elapsed/
  remaining time now account for each track's playback speed, instead of
  showing the nominal/content duration a sped-up or slowed-down track no
  longer actually takes.
- Root cause: `audioPlayer.currentTime`/`.duration` (and the stored
  `track.duration` string) are always **content time** — position within
  the file's own natural timeline, unaffected by `playbackRate`. That's
  exactly right for the progress-bar fill (`curSec/durSec` is a ratio, so
  it's correct either way) and for movement-cue matching (cues are stored
  in content time too, so they already fire at the correct musical moment
  regardless of speed — confirmed via code read, deliberately left
  unchanged). But every place that converted content-time straight to a
  clock string was wrong once a track's speed ≠ 1.0×.
- Fixed by dividing by `getTrackPlaybackSpeed(track)` (live builder) /
  the new `getTrackSpeed(t)` helper (mirrored into the export, replacing
  a duplicated inline formula in `loadTrackAudio`) at each display point:
  `renderCockpit()`'s current-track elapsed/remaining time, the "next
  movement in Xs" / "until track end" countdowns, the running total
  elapsed-vs-total-class-time badge, and `updateStats()`'s "Workout Time"
  total. Mirrored identically in the exported HUD's `render()`.
- Checked project history before touching this: a backup named
  `..._v4.7.13_WallClockRemoved.html` exists, and `LESSONS_LEARNED.md`
  rule #10 says "no wall clock" in the cockpit top bar — turned out to be
  unrelated (that rule is about a real-world *time-of-day* clock like
  "🕒 07:42", not playback-speed-corrected elapsed/remaining durations),
  so no conflict with past decisions.
- Verified via esprima (0 errors) and headless Playwright with a synthetic
  2-track class (one at 1.25× speed): confirmed exact wall-clock math in
  both the live cockpit and a freshly exported HUD (2:00 content @ 1.25×
  → 1:36 real duration; 30 content-seconds played → 0:24 real elapsed;
  total workout time 2:36 for the two tracks combined) — matching
  independently in both places. Re-confirmed the v5.0.42 Reset button and
  artist-fix still work after these changes.
- Snapshot: `Backups/spinning_local_builder_v5.0.43_WallClockTime_*.html`.

**spinning_local_builder.html v5.0.42 (2026-08-29) — Reset Buttons + Stale Artist Fix**
- `spinning_local_builder.html` only (a different lineage from the 8n12
  files above — not touched by any of the 8n12 work in this log).
- Added a per-track **"↺ Reset"** button (only shown once a track's BPM or
  volume gain has actually been adjusted) that reverts both back to how
  the file arrived: BPM to `originalBpm`/`detectedBpm` (via the existing
  `updateBpm()`), volume gain to 1.0/0dB (via the existing
  `setTrackVolumeGain()`), and clears `customSpeedMultiplier` so it can't
  keep overriding the BPM-ratio speed calculation after reset. New
  function: `resetTrackAdjustments(tIdx)`.
- **Bug fix**: `handleSingleTrackAudioImport()` (the per-track "🎵 Attach
  MP3" button) only overwrote `track.artist` when
  `parseArtistAndTitleFromFileName()` found an `Artist - Title` separator
  in the new filename. A replacement file named without that pattern (e.g.
  `"06 Say Something.mp3"`) left the *previous* track's artist in place
  instead of clearing it — reported by the user after replacing an MP3 and
  seeing the old artist still attached to the new song. Fixed by writing
  `parsed.artist` unconditionally (empty string included) instead of only
  when truthy. Reproduced the exact scenario and confirmed fixed via a
  synthetic `File`/`DataTransfer` in headless Chromium (not just a code
  read) — and confirmed the normal `Artist - Title.mp3` case still parses
  correctly.
- Investigated (not yet acted on) a separate question raised in
  conversation: BPM-driven playback speed and volume gain are both
  whole-track values (`audio.playbackRate` / `audio.volume` set once per
  track, no per-timeline-segment control) — confirmed cue/movement
  timestamps are stored and compared in *content time*
  (`audioPlayer.currentTime`, unaffected by `playbackRate`), so they
  already trigger at the correct musical moment regardless of speed and
  need no adjustment. What *is* currently inaccurate: `updateStats()`'s
  "Workout Time" total and the cockpit's remaining-time countdown both sum
  `track.duration` / `audioPlayer.duration` directly (content-time), so a
  sped-up track's real-world wall-clock duration is shorter than what's
  displayed. Not fixed yet — flagged for the user to decide whether
  displayed times should be corrected for playback speed.
- Noted (not fixed, out of scope, pre-existing, unrelated to this
  session's edits): the IDE's CSS linter flagged a broken rule around line
  928 — a selector went missing at some earlier point, leaving orphaned
  property declarations after the `@keyframes slowRedGlow` block. Browsers
  silently skip malformed CSS like this, so nothing is visually broken,
  but whatever selector was meant to own those properties currently has no
  styling applied.
- Verified via esprima (0 errors) and headless Playwright: Reset button
  appears/disappears correctly and reverts BPM+gain+customSpeedMultiplier;
  stale-artist bug reproduced and confirmed fixed via a real (synthetic)
  file attach, with the normal filename-parsing path re-confirmed intact.
- Snapshot: `Backups/spinning_local_builder_v5.0.42_ResetButtonsAndArtistFix_*.html`.

**v5.0.52 (2026-08-29) — 8n12: Editable Warm-Up/Cool-Down Cues + Stronger Bookend Colors**
- Follow-up to v5.0.51, `8n12_builder.html` only.
- The static "Track N — Warm Up/Cool Down (no metrics required)" banner is
  now also an editable **6-slot instructor-cue grid**, rendered *inside*
  that same banner box (not the regular movements-section other tracks
  use) via `renderSingleSlotWrapperHtml()` — same underlying slot
  components as Cue 1/6 elsewhere, just all 6 exposed since warm-up/cool-
  down narration needs more than 2 beats. Feeds the cockpit cue box exactly
  like regular cues do (`buildCuePoints()` already read all 6 slots
  generically — no changes needed there).
- Baked the user's actual class content into `DEFAULT_TRACKS` (edited via
  the same careful Python json.loads/dumps approach as the cooldown-track
  addition, given the array is one ~51MB line): warm-up gets a welcome cue
  @0:00 and an 8n12-protocol explainer @1:00; cool-down gets three cues
  (@0:00, @1:00, @2:00) walking the flywheel/legs/breathing wind-down.
  `autoCue: false` on all of them so they're never touched by the
  gear-based auto-default logic.
- **Bug caught by the test suite**: `ensureCueDefaultsForAllTracks()` (the
  function that guarantees Cue 1/6 defaults regardless of which tab was
  opened — see v5.0.46) only special-cased index 0, not the last-track
  cool-down convention added in v5.0.51. It was silently overwriting the
  hand-written cool-down cues with the gear-based "You need gear 12..."
  default and the generic "Last one coming up" text. Fixed by adding the
  same `isCooldown` check already used everywhere else.
- **Stronger 3-way color distinction** (user feedback: bookend tint was
  too subtle, and warm-up/cool-down looked identical to each other):
  split `.bookend-track` into `.bookend-warmup` (cyan, alpha upped
  0.05→0.1 background / 0.3→0.5 border) and `.bookend-cooldown` (new
  violet `#7c4dff`, same intensities) — applied to the card, its `.track-
  num` badge, the banner box itself, and the Overview table row tint.
  Regular (middle) tracks are unaffected.
- Verified via esprima (0 errors) and a substantially rewritten
  `scratch/runtime_check_cooldown_track.py`: asserts the exact cue text
  and times for both bookend tracks, that the separate movements-section
  is absent for them, distinct bookend classes on first vs. last card, and
  drives `cockpitElapsedSec` through both tracks confirming the right cue
  text surfaces at the right moment. Also fixed two now-stale test fixtures
  (`runtime_check_export_hud.py`, and noted `runtime_check_8n12_v3.py` as
  obsolete) that used 2-track arrays where the "sample" track was
  ambiguously both first-not and last — now always add a 3rd track so a
  genuine middle/regular track is under test.
- Snapshot: `Backups/8n12_builder_v5.0.52_WarmupCooldownCues_*.html`.

**v5.0.51 (2026-08-29) — 8n12: Cool Down Track + Fullscreen Toggle**
- Follow-up to v5.0.50, `8n12_builder.html` only.
- **12th default track added**: `DEFAULT_TRACKS` now ends with `"Cool Down
  [END]"` (no embedded audio — user attaches their own MP3), edited
  directly in the file's single-line JSON array via a Python script
  (`json.loads` → append → `json.dumps`) rather than the Edit tool, since
  the array line is ~51MB of embedded base64 audio. **Caught and fixed a
  bug from that edit**: the rebuild appended `"];\n"` after `json.dumps()`
  output that already ended in `]`, producing a stray `}]];` — esprima
  caught it immediately (0 errors is mandatory before calling anything
  done), fixed with a second targeted script pass.
- The **last track is now treated exactly like the first (warm-up) track**
  — same "bookend" concept, purely positional (`tIdx === 0` /
  `tIdx === length-1`), matching how warm-up already worked: no cue slots
  or Recovery/Blast pills, "Track N — Cool Down (no metrics required)"
  banner, same Gear 12/RPM 70/Power 150 default
  (`init8n12TrackDefaults()`'s `WARM_COOL_DEF` now applies to both ends),
  blank TRACK metric and "Cool Down" workout type in the Cockpit, mirrored
  in the exported HUD. Applies to *any* class (not just the 12-track
  default) — the last track of any class is now a cool-down by this same
  convention, symmetric with the existing warm-up rule.
- **Bookend styling**: first/last track cards get a `.bookend-track` class
  (cyan-tinted background/border, tinted number badge) in the Editor, and
  a matching tinted row background in the Overview table, so they're
  visually obvious in the list without reading the banner text.
- **Fullscreen toggle**: added a ⛶ button next to the version badge in the
  Cockpit topbar (live + exported HUD). Live builder: toggles the
  `standalone-mobile-body` CSS (pre-existing but previously unreachable —
  hides the app's own header/toolbar, fills the viewport) plus requests
  real browser fullscreen where supported; a `fullscreenchange` listener
  keeps the button in sync if fullscreen is exited via Escape/back gesture.
  Exported HUD: same real-fullscreen request only (no extra app chrome to
  hide there). Icon is an inline SVG, not a Unicode glyph — the ⛶
  character (U+26F6) rendered as a missing-glyph box in testing, so both
  contexts use hand-written SVG paths (expand / compress corner arrows)
  that render identically everywhere regardless of font/emoji support.
- Verified via esprima (0 errors) and two new scripts:
  `scratch/runtime_check_cooldown_track.py` (12 tracks, cool-down track
  behavior parity with warm-up, bookend styling, unaffected workout-track
  numbering) and manual SVG-render checks for the fullscreen button in
  both live and exported contexts.
- Snapshot: `Backups/8n12_builder_v5.0.51_CooldownTrackAndFullscreen_*.html`.

**v5.0.50 (2026-08-29) — 8n12: Cockpit Blast Targets Row**
- Follow-up to v5.0.49, `8n12_builder.html` only.
- User noted a lot of empty space below the cue box once the movement
  grid/duration card/status text had all been stripped out. Added a third
  metric row — Gear / RPM / Power — sourced from the same
  `track.eightN12.s2Gear/s2Rpm/s2Power` values already baked into the
  Cue 1 sentence, styled with the existing `.cockpit-metric-card` tiles
  (3-column variant of `.cockpit-hud-metrics`) so it fills the space with
  something actually useful mid-ride instead of a sentence the instructor
  has to parse. Mirrored in both the live cockpit (`renderCockpit()`) and
  the exported HUD's generated markup/script.
- Verified via esprima (0 errors) and updated
  `scratch/runtime_check_8n12_v4.py` (now scopes its "3 metric cards, no
  Duration" checks to the *first* `.cockpit-hud-metrics` grid specifically,
  since there are two on the page now, and asserts the new Gear/RPM/Power
  row's values for both the warm-up track and a real track — live and
  exported, zero errors either way).
- Snapshot: `Backups/8n12_builder_v5.0.50_CockpitBlastTargets_*.html`.

**v5.0.49 (2026-08-29) — 8n12: Exported HUD ↔ Live Cockpit CSS Parity**
- Follow-up to v5.0.48, `8n12_builder.html` only.
- The exported phone HUD (`exportCockpitForPhone()`'s generated `<style>`)
  had drifted from the live builder's Cockpit tab CSS over several rounds
  of "make it bigger" edits that only updated one side — user compared a
  real phone screenshot of an exported file against the live builder's
  Cockpit tab and asked for the two to match.
- Brought every shared cockpit CSS rule to exact parity, property-for-
  property: `.cockpit-hud-topbar`, `.cockpit-hud-classtitle`,
  `.cockpit-total-timer`, `.cockpit-hud-tracktitle` (now 2-line clamp
  instead of single-line ellipsis), `.cockpit-hud-artist`,
  `.cockpit-hud-metrics`, `.cockpit-metric-card`, `.cockpit-metric-label`,
  `.cockpit-metric-val`, `.cockpit-hud-controls`, `.cockpit-hud-btn` /
  `.main-play`, `.cockpit-hud-scrubber-row`, `.cockpit-hud-progress-bg` /
  `-fill`, `.cockpit-hud-cuebox`, and `.cockpit-hud-wrap`'s gap.
- No markup or behavior changes — CSS values only. Verified via esprima
  (0 errors), `scratch/runtime_check_8n12_v4.py` (no regressions), and a
  side-by-side screenshot of the live Cockpit tab vs. a freshly exported
  HUD loaded fresh (`scratch/parity_live.png` / `scratch/parity_export.png`)
  confirming the two now look the same.
- Snapshot: `Backups/8n12_builder_v5.0.49_ExportCssParity_*.html`.

**v5.0.47-v5.0.48 (2026-08-29) — 8n12: Cockpit Metrics Grid Rework**
- Follow-up to v5.0.46, `8n12_builder.html` only.
- Track counter now excludes the warm-up track from the count: track 1's
  TRACK metric is blank (was "1 / 11"), and the first real track reads
  "1 / N" where N = `classTracks.length - 1` (was "2 / 11"). Same fix
  mirrored in the exported HUD.
- Track-subtitle fallback text (shown when `track.artist` is empty) changed
  from generic "Instructor Track" to "Warmup Track" (track 1) / "Workout
  Track" (everything else).
- WORKOUT TYPE always reads "Warm Up" for track 1 regardless of its
  `eightN12` data state (previously showed "--" since the warm-up track's
  `eightN12.movement` used to default to `null`).
- Cockpit metrics grid: removed the DURATION card entirely and the
  WORKOUT TYPE label text — WORKOUT TYPE now spans the full row width as a
  single value, restyled to match the instructor cue box (left cyan accent
  stripe) instead of a plain metric tile. Removing the DURATION card meant
  deleting the *unguarded* `document.getElementById("mMetricDuration").
  textContent = ...` line in the export script — same
  null-deref-in-the-exported-HUD class of bug as the earlier status-span
  fix, caught the same way (loading the actual exported file, not just
  eyeballing the generator code).
- `init8n12TrackDefaults()`'s `SLOT2_DEFS[0]` (the warm-up track) changed
  from all-null to real defaults: `movement: 'Warm Up / Recovery', gear:
  12, rpm: 70, power: 150` — so the Overview table's Gear/RPM/Power columns
  show real numbers for track 1 too instead of "--".
- Verified via esprima (0 errors) and `scratch/runtime_check_8n12_v4.py`
  (grid card count/labels, warm-up vs. real-track TRACK/WORKOUT TYPE/
  artist text, Overview row values, all mirrored in the exported HUD with
  zero errors).
- Snapshot: `Backups/8n12_builder_v5.0.48_CockpitMetricsCleanup_*.html`.

**v5.0.46 (2026-08-29) — 8n12: Cockpit Polish + a Real Cue-Default Bug Fix**
- Follow-up to v5.0.45, `8n12_builder.html` only.
- **Bug fix (the important one):** Cue 1/Cue 6 defaults were only ever
  computed as a side effect of rendering the Editor tab
  (`renderTracks()`), but the app opens on the **Cockpit** tab by default
  (`activeViewMode = 'cockpit'`). A track never visited in the Editor —
  including anything exported straight from the Cockpit tab — showed the
  generic fallback cue instead of its real Cue 1 text at the start of
  playback. Fixed with `ensureCueDefaultsForAllTracks()`, called at
  startup (`init()`), on every `renderCockpit()` for the active track, and
  at the top of `exportCockpitForPhone()` before serializing — so the
  defaults are guaranteed regardless of which tab was ever opened.
  Caught by `scratch/runtime_check_export_hud.py`, which loads the
  *exported* file (not just the live builder) and drives it.
- Removed the Recovery/Blast timestamp fields entirely — a single fixed
  instant doesn't mean anything for an interval that repeats throughout
  the track, so `buildCuePoints()`/`expCuePoints()` no longer read
  `eightN12.s1Time`/`s2Time` at all; Recovery/Blast are reference-only
  info in the builder now (Gear/RPM/Power, and workout type), not part of
  the cockpit's cue timeline. `update8n12Time()` removed.
- Blast's workout-type `<select>` (badly-styled native dropdown, see
  screenshot in session) replaced with a plain clickable box matching the
  cockpit's metric-card look (`cycleMovementType()` cycles the 4 options).
- Cockpit's CADENCE metric replaced with **WORKOUT TYPE**, showing
  `eightN12.movement` — mirrored in the exported HUD.
- Cue 6 now defaults to `"Last one coming up"` at **(track duration -
  25s)** instead of a fixed `"Last one..."` @ 0:00 — still respects a
  manual edit to either the time or the text (`autoCue` flips false on
  either `updateSlotTime`/`updateSlotCue` for slot 5, and on
  `applyTimestampToSlot`).
- Cockpit scrubber row / progress bar / cue box sized up considerably
  (bigger font, thicker bar); the redundant per-cue chip strip
  (`#cockpitMovGrid` / `#mMovGrid`) is now hidden and unpopulated in both
  the live cockpit and the export — the single quoted cue box is the only
  cue display now. Removed the in-between status-message span
  (`#cockpitStatusText` / `#mStatusText`) per feedback that it broke up
  the two timestamps; this also fixed a latent bug where the exported
  HUD's script still wrote to the now-missing `#mStatusText` unconditionally
  (`statusEl.textContent = ...` with no null check) — would have thrown on
  every render() call in any HUD exported after the span was removed.
- Overview (Page 2): removed the SPINPOWER ZONES legend bar (Editor +
  Overview), softened the Gear/RPM/Power text color (was `#ff1744`, now
  `#ff8a80` — same for the Blast pill's label) for readability, put the
  Audio dB cell on one row instead of three (was three stacked `<div>`s,
  now one flex row), and added a per-row ▶/⏸ button (`toggleTrackAudio`)
  to preview a track's audio straight from the table.
- Recovery/Blast pills also got bigger fonts, explicit Gear/RPM/Power text
  labels (not just tooltips), `justify-content:space-between` to use their
  full box width, and wider number inputs so 3-digit RPM/Power values
  don't get clipped.
- Verified via esprima (0 errors) and three headless Playwright scripts:
  `scratch/runtime_check_8n12_v3.py` (pill sizing/labels, cockpit
  chip-strip removal, Cue 1/6 behavior), `scratch/runtime_check_export_hud.py`
  (exported HUD loads and shows Cue 1's default with zero JS errors).
- Snapshot: `Backups/8n12_builder_v5.0.46_CockpitAndPillCleanup_*.html`.

**v5.0.45 (2026-08-29) — 8n12: C1/C6-only Cues, Compact Pills, Overview Cleanup**
- Follow-up to v5.0.44, `8n12_builder.html` only.
- Cues 2-5 dropped from the UI entirely — only Cue 1 (Blast target, always
  0:00) and Cue 6 (wrap-up) render, via `VISIBLE_SLOT_INDICES = [0, 5]`.
  `movements[1..4]` are left untouched in the data model so nothing
  downstream needs special-casing.
- Cue 6 defaults to `"Last one..."` (`SLOT6_DEFAULT_CUE` /
  `ensureSlot6DefaultCue()`), same autoCue-respects-manual-edit rule as
  Cue 1.
- Cue 1's time is now permanently locked to `0:00`: the input is
  `readonly`, `ensureSlot1DefaultCue()` re-forces `time: '0:00'` on every
  render, and `updateSlotTime()` no-ops for slot 0. `applyTimestampToSlot()`
  (the "⏱️ Use Timestamp" button) no longer searches for a target slot — it
  always writes into Cue 6.
- The Recovery (blue) / Blast (red) pills now show visible "Gear"/"RPM"/
  "Power" text labels next to each value (not just tooltips), and Recovery
  is sized to its content (`flex:0 0 auto`) instead of matching Blast's
  width, since it has fewer fields.
- Overview (Page 2) table: dropped the "Ride Cadence (RPM)", "Energy Zone",
  "Target RPE", and "Movements Sequence (Up to 6)" columns; replaced the
  latter two with **Gear / RPM / Power** columns sourced from each track's
  red Blast (slot 2) values.
- Verified via esprima syntax audit (0 errors) and headless Playwright:
  exactly 2 slot boxes render, Cue 1 is locked/readonly at 0:00, Cue 6
  defaults correctly, `applyTimestampToSlot` only ever touches Cue 6, both
  pills show labels and stay single-row with Recovery narrower than Blast,
  and the Overview header/row match the new column set.
- Snapshot saved to
  `Backups/8n12_builder_v5.0.45_CuesC1C6OverviewCleanup_*.html`.
- Reusable script: `scratch/runtime_check_8n12_cue_slots_v2.py`.

**v5.0.44 (2026-08-29) — 8n12: Cue-Slots Refinement**
- Follow-up to v5.0.43, `8n12_builder.html` only.
- Track 1 (warm-up) no longer renders the 6 cue slots at all — it already
  skipped the Recovery/Blast banner; now the whole "INSTRUCTOR CUES"
  section is hidden for that track too (`isWarmupTrack` guard around both
  `slotsHtml` and the `.movements-section` markup).
- Slots 1-6 and the blue Recovery / red Blast boxes are now each a single
  row tall: the per-slot cue textarea became a single-line `.slot-cue-input`
  laid out inline with its time field and clear button, and the banner
  boxes dropped their stacked label/subtitle/field rows for one `flex;
  flex-wrap:nowrap` row per box (`overflow-x:auto` as a width safety valve,
  not a height one).
- Slot 1's cue now **defaults** from the red Blast slot's gear/RPM/power:
  `"You need gear G, speed at R, power target is P"`
  (`computeSlot1DefaultCue()` / `ensureSlot1DefaultCue()`), and stays live
  in sync as those fields change (`update8n12Field` re-derives it for
  slot 2's gear/rpm/power edits). Typing directly into Cue 1 sets
  `movements[0].autoCue = false` so the auto-default stops overwriting it
  — same never-overrule-the-user rule as the pre-existing Lesson 121
  comment in `selectSymbol()`.
- Verified via esprima syntax audit (0 errors) and headless Playwright:
  Track 1 has no slots-grid, slot/banner box heights are single-row (~34px),
  Slot 1 auto-populates and live-syncs until manually edited, and manual
  edits are preserved across further gear/RPM/power changes.
- Snapshot saved to `Backups/8n12_builder_v5.0.44_CueSlotsRefinement_*.html`.

**v5.0.43 (2026-08-29) — 8n12: Cue-Driven Slots Redesign**
- `8n12_builder.html` only (other editions untouched this round).
- Slots 1-6 on each track card are no longer a Spinning movement-symbol
  picker (modal + zone/RPE) — they're now 6 independently-timed instructor
  cue boxes (`{time, cue}`), edited inline (no modal).
- The 8n12 interval banner (blue "RECOVERY (12s)" / red "BLAST (8s)") moved
  from below the slot grid to **above** it, laid out side by side, and each
  box now carries its own timestamp so it participates in the same
  time-driven cockpit cue system as slots 1-6.
- Removed the static per-track "coaching cues" textarea and the
  `cockpitCueBox`'s dependence on `track.cues` — the cockpit cue box (live
  builder + exported phone HUD) now shows whichever of the 8 timed cue
  points (6 slots + Recovery/Blast) is currently active by elapsed playback
  time. Shared logic lives in `buildCuePoints()` / `findActiveCuePoint()`
  (mirrored in the phone-HUD export script as `expCuePoints()` /
  `expActiveCue()`).
- Legacy saves (old `{name,zone,rpe,time}` movement shape) are normalized
  on load via `normalizeMovementsToCueSlots()` — timestamps are kept, old
  movement symbols are dropped (instructor re-enters cue text).
- Verified via esprima syntax audit (0 errors) and headless Playwright
  (slot/banner layout + time-driven cue box text, 0 page errors).
- Snapshot saved to `Backups/8n12_builder_PreCueSlotsRedesign_*.html`.
- Reusable scripts: `scratch/verify_8n12_cue_slots.py`,
  `scratch/runtime_check_8n12_cue_slots.py`.

**v5.0.41 (2026-08-28) — 8n12 Dedicated Edition Pre-Populated Startup**
- Configured [8n12_builder.html](file:///c:/Data_Projects/Spinning/8n12_builder.html) with all **11 8n12 MP3 audio tracks embedded directly into default startup state**:
  1. *Do you know [START]* (132 BPM, 03:08)
  2. *Do you know* (138 BPM, 02:03)
  3. *Airwave* (132 BPM, 02:04)
  4. *Destiny* (150 BPM, 01:58)
  5. *Independence* (137 BPM, 02:09)
  6. *Krystal* (138 BPM, 02:10)
  7. *Let It Rain* (137 BPM, 02:11)
  8. *Sandstorm* (150 BPM, 01:59)
  9. *Symbols* (138 BPM, 02:08)
  10. *Take me to the Clouds* (150 BPM, 02:20)
  11. *Xit2* (140 BPM, 02:07)
- Embedded with full Base64 audio, movements, cues, target BPMs, and loudness gains. When `8n12_builder.html` opens on any device/browser, it starts up immediately with all 11 MP3 tracks loaded and ready to play in the Cockpit or export to Phone HUD.
- Verified via AST parser and Headless Playwright (11/11 audio tracks loaded, 0 errors).
- Snapshot saved to `Backups/8n12_builder_v5.0.41_PrePopulatedMP3s_*.html`.

**v5.0.41 & v5.0.41-Local (2026-08-28) — Mobile HUD Export Audio Engine Fix**
- Fixed silent playback bug in exported Mobile Cockpit HUD (`exportCockpitForPhone`):
  - In previous exports, `classTracks` embedded the Base64 audio correctly (hence large file sizes), but the generated HUD script lacked `loadTrackAudio(activeIdx)` and `audio.src = t.audioDataUrl` assignment in `togglePlay()`, causing the HUD to default to a silent timer fallback with no audio output.
  - Added complete standalone HTML audio playback engine inside exported HUDs: automatic track loading, `audio.src = t.audioDataUrl`, pitch-preserving tempo stretching (`playbackRate`), track volume gain, interactive scrubber seeking, `⏪ -5s` / `⏩ +5s` nudge, track auto-advance on track end, and graceful fallback timer.
- Both files syntax verified with AST auditor (`check_js.py` → **CLEAN**).
- Timestamped backups created in `Backups/`.

**v5.0.39-Local (2026-08-28) — Spinning® Local Course Designer (Local Version)**
- Created `spinning_local_builder.html` branched from stable v5.0.39 designer.
- 100% purged all SoundCloud code: removed external SDK script, modals, streaming badges, embed widgets, and streaming fallbacks.
- Retained full Local MP3 suite: batch `Select Music`, single-track `Attach MP3`, peak dB loudness analyzer, `-4dB` to `+4dB` GainNode volume boosting, pitch-locked tempo stretching (`playbackRate`), tap tempo, BPM override, 3-page navigation, and mobile standalone HUD export with Base64 embedded audio.
- AST validated with `esprima`; runtime tested via Playwright (0 errors across all 3 pages). Snapshot saved in `Backups/`.

**v5.0.39 (2026-08-27) — Overview: all movement icons in one shared box**
- `.summary-mov-wrap` is now a single bordered `inline-flex` box (`nowrap`);
  `.summary-mov-badge` lost its own border/background/padding so it is just the icon.
- Per-icon `margin-right:4px` removed in `renderSummaryTable()` — the wrap's `gap` spaces them.
- Result: the 3×2 grid of six separate boxes collapsed to one 195×36px box on a single
  row; Overview row height 60px (was ~2 rows). Zone colour still shown per icon tile;
  movement name + hand position remain in the `title` tooltip.
- Verified in headless Chromium: 1 box, 6 icons, 1 row, no page errors.

Preceding releases (from `Backups/`): v5.0.38 Overview dB column · v5.0.37 modal apply
& transparency · v5.0.36 cockpit parity · v5.0.35 remove Spotify lead-in ·
v5.0.34 gain boost fix · v5.0.33 per-page zone legend · v5.0.32 controls moved to top.

## 3. Working rules (see `AGENTS.md`, `CLAUDE.md`, `LESSONS_LEARNED.md`)

1. Bump the `v5.0.XX` version badge on every change — it busts the browser's script cache.
2. Snapshot to `Backups/Spinning_MultiSource_v5.0.XX_<Reason>_<YYYYMMDD>.html`.
3. Run an automated JS syntax audit before declaring anything done.
4. Prove it at runtime — never declare a layout fixed from an edit alone.
5. Minimal, targeted changes; don't refactor untouched files.

## 4. Toolchain facts (verified 2026-08-27)

- **`node` is NOT installed** on this machine — `node --check` is unavailable.
- Python `esprima` **is** available → use it for JS syntax auditing.
- Python `playwright` **is** available (headless Chromium) → use it for runtime proof;
  `file://` loading of the builder works and the page throws no errors on load.
- Reusable scripts for this change:
  - `scratch/verify_v5039_icon_box.py` — esprima syntax audit + CSS/version assertions.
  - `scratch/runtime_check_v5039_icon_box.py` — headless render, geometry assertions, row screenshot.

## 5. Open items / known state

- `builder.html` and `spinning_multisource_builder.html` are **out of parity** (different
  lineages, ~1.46MB vs ~292KB). AGENTS.md Rule 3 assumes mirrored editions — decide whether
  `builder.html` is retired or should be re-synced before applying changes to both.
- Working tree has many untracked scratch/backup files and deletions staged from an earlier
  reorganisation; nothing committed for v5.0.39 yet.
