from pathlib import Path
import json
import lz4.block
from typing import Optional, List, Tuple, Set

profiles_dir = Path.home() / "Library/Application Support/Firefox/Profiles"


def read_jsonlz4(path: Path) -> Optional[dict]:
    try:
        raw = path.read_bytes()
        if not raw.startswith(b"mozLz40\0"):
            print(f"⚠️  Warning: Not a valid Firefox jsonlz4 file: {path}")
            return None

        return json.loads(lz4.block.decompress(raw[8:]).decode("utf-8"))

    except Exception as e:
        print(f"❌ Error reading {path}: {e}")
        return None


def get_live_tabs(profile: Path) -> Optional[Set[str]]:
    path = profile / "sessionstore-backups" / "recovery.jsonlz4"

    if not path.exists():
        return None

    data = read_jsonlz4(path)
    if data is None:
        return None

    urls: Set[str] = set()

    try:
        for window in data.get("windows", []):
            for tab in window.get("tabs", []):
                entries = tab.get("entries", [])
                if not entries:
                    continue

                idx = tab.get("index", len(entries)) - 1

                if 0 <= idx < len(entries):
                    url = entries[idx].get("url", "")

                    if url and not url.startswith(
                        ("about:", "moz-extension:", "data:", "chrome:", "blob:")
                    ):
                        urls.add(url)

    except Exception as e:
        print(f"❌ Error processing tabs in {profile.name}: {e}")
        return None

    return urls


def get_profiles() -> List[Tuple[Path, Set[str]]]:
    profiles: List[Tuple[Path, Set[str]]] = []

    if not profiles_dir.exists():
        print(f"❌ Firefox profiles directory not found: {profiles_dir}")
        return profiles

    try:
        for profile in sorted(profiles_dir.iterdir()):
            if profile.is_dir():
                tabs = get_live_tabs(profile)

                # Keep profiles even if they have zero visible tabs,
                # as long as a live recovery file exists.
                if tabs is not None:
                    profiles.append((profile, tabs))

    except Exception as e:
        print(f"❌ Error scanning profiles directory: {e}")

    return profiles


def select_profiles(profiles: List[Tuple[Path, Set[str]]]) -> List[int]:
    if not profiles:
        print("❌ No Firefox profiles with live recovery files found.")
        return []

    print("\n" + "=" * 60)
    print("Available Firefox Profiles:")
    print("=" * 60)

    for i, (path, tabs) in enumerate(profiles):
        print(f"  [{i}] {path.name} ({len(tabs)} tabs)")
        print(f"      {path}")

    print("\n" + "=" * 60)
    print("Enter profile numbers to compare, comma-separated")
    print("Example: 0,1 or 0,1,2")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nProfile numbers: ").strip()
            indices = [int(x.strip()) for x in user_input.split(",")]

            if len(indices) < 2:
                print("❌ Please select at least 2 profiles.")
                continue

            if any(idx < 0 or idx >= len(profiles) for idx in indices):
                print(f"❌ Invalid profile number. Choose between 0 and {len(profiles) - 1}.")
                continue

            if len(indices) != len(set(indices)):
                print("❌ Duplicate profile numbers detected.")
                continue

            return indices

        except ValueError:
            print("❌ Invalid input. Enter comma-separated numbers, for example: 0,1,2")


def print_common_tabs(profiles: List[Tuple[Path, Set[str]]], indices: List[int]) -> None:
    selected = [profiles[i] for i in indices]

    common = set.intersection(*(tabs for _, tabs in selected))

    print("\n" + "=" * 60)
    print("SELECTED PROFILES")
    print("=" * 60)

    for path, tabs in selected:
        print(f"{path.name}: {len(tabs)} tabs")
        print(path)

    print("\n" + "=" * 60)
    print(f"COMMON TABS ({len(common)})")
    print("=" * 60)

    if not common:
        print("No common tabs.")
        return

    for url in sorted(common):
        print(url)


def main() -> None:
    print("\n" + "=" * 60)
    print("Firefox Live Tabs Comparison Tool")
    print("=" * 60)

    print("\n🔍 Scanning Firefox profiles...")
    profiles = get_profiles()

    if not profiles:
        print("❌ No Firefox profiles found with live recovery files.")
        return

    print(f"✅ Found {len(profiles)} profile(s).\n")

    indices = select_profiles(profiles)
    if not indices:
        return

    print_common_tabs(profiles, indices)
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
