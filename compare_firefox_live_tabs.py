from pathlib import Path
import json
import lz4.block

profiles_dir = Path.home() / "Library/Application Support/Firefox/Profiles"

def read_jsonlz4(path):
    raw = path.read_bytes()
    if not raw.startswith(b"mozLz40\0"):
        raise ValueError(f"Not a Firefox jsonlz4 file: {path}")
    return json.loads(lz4.block.decompress(raw[8:]).decode("utf-8"))

def get_live_tabs(profile):
    path = profile / "sessionstore-backups" / "recovery.jsonlz4"
    if not path.exists():
        return None

    data = read_jsonlz4(path)
    urls = set()

    for window in data.get("windows", []):
        for tab in window.get("tabs", []):
            entries = tab.get("entries", [])
            if not entries:
                continue

            idx = tab.get("index", len(entries)) - 1
            if 0 <= idx < len(entries):
                url = entries[idx].get("url", "")
                if url and not url.startswith(("about:", "moz-extension:")):
                    urls.add(url)

    return urls

profiles = []

for profile in profiles_dir.iterdir():
    if profile.is_dir():
        tabs = get_live_tabs(profile)
        if tabs is not None:
            profiles.append((profile.name, tabs))

print("Live Firefox profiles found:\n")
for i, (name, tabs) in enumerate(profiles):
    print(f"[{i}] {name}: {len(tabs)} tabs")

a = int(input("\nFirefox profile number: "))
b = int(input("Firefox Developer Edition profile number: "))

tabs_a = profiles[a][1]
tabs_b = profiles[b][1]

common = tabs_a & tabs_b

print("\nFirefox tabs:", len(tabs_a))
print("Firefox Developer Edition tabs:", len(tabs_b))
print("Common tabs:", len(common))

print("\nCommon URLs:")
for url in sorted(common):
    print(url)
