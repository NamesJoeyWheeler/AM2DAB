# import_to_dab_library_with_tracks_robust.py
import requests
import csv
import time
import sys
import re

API_BASE = "https://dab.yeet.su/api"
EMAIL = "EMAIL"        # <-- replace
PASSWORD = "PASSWORD"       # <-- replace
CSV_PATH = "music.csv"  # <-- path to your playlists.cloud CSV
LIB_NAME = "Imported Playlist"

session = requests.Session()
session.headers.update({"Accept": "application/json"})

def bad_exit(msg, resp=None):
    print(msg)
    if resp is not None:
        print("status:", resp.status_code)
        try:
            print("body:", resp.json())
        except Exception:
            print("body:", resp.text)
    sys.exit(1)

def normalize_title(title):
    """Lowercase and remove parentheses/brackets and remix/feat info"""
    title = re.sub(r"[\(\[].*?[\)\]]", "", title)
    title = title.replace("’", "'")  # normalize quotes
    return title.strip().lower()

# --- Step 1: Login ---
print("Logging in...")
login_resp = session.post(f"{API_BASE}/auth/login", json={"email": EMAIL, "password": PASSWORD})
if not login_resp.ok:
    bad_exit("Login failed — check credentials and payload.", login_resp)
print("Login OK — cookies:", session.cookies.get_dict())

# --- Step 2: Create library ---
print("Creating library...")
lib_payload = {"name": LIB_NAME, "isPublic": False}
lib_resp = session.post(f"{API_BASE}/libraries", json=lib_payload)
if not lib_resp.ok:
    bad_exit("Failed to create library.", lib_resp)

lib_json = lib_resp.json()
library = lib_json.get("library") or lib_json.get("data") or lib_json
library_id = library.get("id") if isinstance(library, dict) else None
if not library_id:
    bad_exit("Could not find library id in response:", lib_resp)
print("Created library id:", library_id)

# --- Step 3: Import tracks from CSV ---
not_found = []
added_count = 0
skipped_count = 0
row_count = 0

with open(CSV_PATH, newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        row_count += 1
        artist = (row.get("artist") or "").strip()
        track_name = (row.get("track_name") or row.get("Title") or "").strip()
        album_name = (row.get("album_name") or "").strip()
        isrc = (row.get("isrc") or "").strip()

        if not track_name:
            print("Skipping incomplete row:", row)
            continue

        # --- Step 3a: Prepare dual search queries ---
        search_queries = []
        if artist:
            search_queries.append(f"{track_name} - {artist}")  # first try with artist
        search_queries.append(track_name)  # fallback without artist

        found = None
        for search_query in search_queries:
            search_url = f"{API_BASE}/search?q={requests.utils.quote(search_query)}&offset=0&type=track"
            try:
                response = session.get(search_url)
                if response.status_code != 200:
                    continue

                data = response.json()
                tracks = data.get("tracks", [])

                # --- Step 3b: Relaxed exact matches ---
                exact_matches = [
                    t for t in tracks
                    if normalize_title(t.get("title","")) == normalize_title(track_name)
                    and (not album_name or t.get("albumTitle","").strip().lower() == album_name.lower())
                ]

                if exact_matches:
                    found = exact_matches[0]
                    break  # stop after first successful search

            except Exception as e:
                print(f"Search failed for {search_query} — {e}")

        # --- Step 3c: ISRC fallback if still not found ---
        if not found and isrc:
            try:
                r = session.get(f"{API_BASE}/search?q={isrc}&offset=0&type=track")
                r.raise_for_status()
                results = r.json().get("tracks", [])
                if results:
                    found = results[0]
                    print(f"✅ Found via ISRC fallback: {found.get('title')} — {found.get('artist')}")
            except Exception as e:
                print(f"ISRC search failed for {track_name} — {e}")

        if not found:
            print(f"❌ Not found: {track_name} — {artist}")
            not_found.append((track_name, artist, album_name, isrc))
            continue

        track_id = found.get("id")
        if not track_id:
            print(f"⚠️ Track missing ID, skipping: {track_name}")
            skipped_count += 1
            continue

        # --- Step 3d: Add track to library ---
        add_payload = {"track": found}
        add_resp = session.post(f"{API_BASE}/libraries/{library_id}/tracks", json=add_payload)
        if add_resp.ok or add_resp.status_code in (200, 201):
            added_count += 1
            print(f"✅ Added ({added_count}) {found.get('title','?')} — {found.get('artist','?')}")
        else:
            try:
                print("⚠️ Add failed:", add_resp.status_code, add_resp.json())
            except Exception:
                print("⚠️ Add failed:", add_resp.status_code, add_resp.text)
            skipped_count += 1

        time.sleep(0.3)  # small delay to avoid hammering API

# --- Step 4: Summary ---
print("Done.")
print(f"Rows processed: {row_count}, added: {added_count}, skipped/failed: {skipped_count}, not found: {len(not_found)}")
if not_found:
    print("Not found list (first 20):")
    for t, a in not_found[:20]:
        print("-", t, "—", a)
