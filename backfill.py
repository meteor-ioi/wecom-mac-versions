import argparse
import hashlib
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

def check_release_exists(repo, tag):
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    api_url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
    req = urllib.request.Request(api_url)
    req.add_header("User-Agent", "WeCom-Mac-Archiver")
    if token:
        req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise

def download_and_hash(url, dest_path):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    hasher = hashlib.sha256()
    print(f"Downloading {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as resp, open(dest_path, "wb") as f:
        while chunk := resp.read(1024 * 1024):
            hasher.update(chunk)
            f.write(chunk)
    return hasher.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Backfill historical WeCom Mac releases from oldest to newest.")
    parser.add_argument("--start", type=int, default=0, help="Start index (0-based)")
    parser.add_argument("--limit", type=int, default=0, help="Max versions to process (0 = all)")
    parser.add_argument("--versions-file", type=str, default="versions.json", help="Path to versions JSON file")
    args = parser.parse_args()

    repo = os.getenv("GITHUB_REPOSITORY", "meteor-ioi/wecom-mac-versions")
    with open(args.versions_file, "r", encoding="utf-8") as f:
        items = json.load(f)

    # Ensure strictly sorted from oldest to newest
    def ver_key(item):
        return [int(x) for x in item["version"].split(".")]

    items.sort(key=ver_key)

    total = len(items)
    selected = items[args.start:]
    if args.limit > 0:
        selected = selected[:args.limit]

    print(f"Total available Mac versions: {total}. Processing {len(selected)} starting from index {args.start}...")

    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)

    for idx, item in enumerate(selected, start=args.start + 1):
        ver = item["version"]
        intel_ver = item.get("intel_version", ver)
        tag = f"v{ver}"
        arm_url = item.get("arm_url")
        intel_url = item.get("intel_url")

        print(f"\n[{idx}/{total}] Checking {tag} ...")
        if check_release_exists(repo, tag):
            print(f"Tag {tag} already exists. Skipping.")
            continue

        artifacts = []
        notes = [f"## WeCom Mac Version {ver}\n\n- **Release Date**: `{item.get('date', '')}`\n"]

        try:
            if arm_url:
                arm_path = build_dir / f"WeCom_{ver}_Apple.dmg"
                arm_sha = download_and_hash(arm_url, arm_path)
                artifacts.append(str(arm_path))
                notes.append(
                    f"### 🍏 Apple Silicon (M1/M2/M3/M4)\n"
                    f"- **Version**: `{ver}`\n"
                    f"- **Download URL**: [{arm_url}]({arm_url})\n"
                    f"- **SHA-256**: `{arm_sha}`\n\n"
                )

            if intel_url and intel_url != arm_url:
                intel_path = build_dir / f"WeCom_{intel_ver}_Intel.dmg"
                intel_sha = download_and_hash(intel_url, intel_path)
                artifacts.append(str(intel_path))
                notes.append(
                    f"### 💻 Intel x86_64\n"
                    f"- **Version**: `{intel_ver}`\n"
                    f"- **Download URL**: [{intel_url}]({intel_url})\n"
                    f"- **SHA-256**: `{intel_sha}`\n\n"
                )

            if not artifacts:
                print(f"No artifacts available for {tag}. Skipping.")
                continue

            note_file = build_dir / "releaseNote.md"
            note_file.write_text("".join(notes), encoding="utf-8")

            print(f"Publishing release for {tag} with {len(artifacts)} assets...")
            cmd = [
                "gh", "release", "create", tag, *artifacts,
                "--repo", repo,
                "--title", f"WeCom Mac Version {ver}",
                "--notes-file", str(note_file)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                print(f"Error publishing {tag}: {res.stderr}")
            else:
                print(f"Successfully published release {tag}: {res.stdout.strip()}")

        except Exception as e:
            print(f"Failed processing {ver}: {e}")
        finally:
            for art in artifacts:
                p = Path(art)
                if p.exists():
                    p.unlink()

        time.sleep(2)

    print("\nMac backfill process completed.")

if __name__ == "__main__":
    main()
