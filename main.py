import hashlib
import json
import os
import re
import urllib.request
from pathlib import Path

URL_ARM = "https://work.weixin.qq.com/wework_admin/commdownload?platform=mac_arm64&from=wwindex"
URL_INTEL = "https://work.weixin.qq.com/wework_admin/commdownload?platform=mac&from=wwindex"

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return fp

def resolve_redirect(url):
    opener = urllib.request.build_opener(NoRedirectHandler)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    resp = opener.open(req)
    loc = resp.headers.get("Location")
    if not loc:
        raise RuntimeError(f"Failed to resolve location for {url}")
    return loc

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
    print(f"Downloading from {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as resp, open(dest_path, "wb") as f:
        while chunk := resp.read(1024 * 1024):
            hasher.update(chunk)
            f.write(chunk)
    return hasher.hexdigest()

def main():
    repo = os.getenv("GITHUB_REPOSITORY", "meteor-ioi/wecom-mac-versions")
    arm_url = resolve_redirect(URL_ARM)
    intel_url = resolve_redirect(URL_INTEL)

    m_arm = re.search(r"WeCom_([0-9\.]+)_Apple\.dmg", arm_url)
    m_intel = re.search(r"WeCom_([0-9\.]+)_Intel\.dmg", intel_url)

    arm_ver = m_arm.group(1) if m_arm else ""
    intel_ver = m_intel.group(1) if m_intel else ""

    print(f"Official latest Mac versions -> Apple Silicon: {arm_ver}, Intel: {intel_ver}")
    tag = f"v{arm_ver}"

    exists = check_release_exists(repo, tag)
    updated = not exists

    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)
    artifacts = []

    if updated:
        print(f"New Mac version detected! Preparing release for {tag}...")
        arm_path = build_dir / f"WeCom_{arm_ver}_Apple.dmg"
        arm_sha = download_and_hash(arm_url, arm_path)
        artifacts.append(str(arm_path))

        intel_path = build_dir / f"WeCom_{intel_ver}_Intel.dmg"
        intel_sha = download_and_hash(intel_url, intel_path)
        artifacts.append(str(intel_path))

        release_note = (
            f"## WeCom Mac Version {arm_ver}\n\n"
            f"### 🍏 Apple Silicon (M1/M2/M3/M4)\n"
            f"- **Version**: `{arm_ver}`\n"
            f"- **Download URL**: [{arm_url}]({arm_url})\n"
            f"- **SHA-256**: `{arm_sha}`\n\n"
            f"### 💻 Intel x86_64\n"
            f"- **Version**: `{intel_ver}`\n"
            f"- **Download URL**: [{intel_url}]({intel_url})\n"
            f"- **SHA-256**: `{intel_sha}`\n"
        )
        (build_dir / "releaseNote.md").write_text(release_note, encoding="utf-8")
        print("Release note generated.")
    else:
        print(f"Release {tag} already exists. No update required.")

    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"updated={str(updated).lower()}\n")
            f.write(f"version={arm_ver}\n")
            f.write(f"tag={tag}\n")
            f.write(f"artifacts={' '.join(artifacts)}\n")

if __name__ == "__main__":
    main()
