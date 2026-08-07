"""
Build script to compile ZeroClaw Commerce into a single-file standalone executable
for Windows (.exe), Apple macOS, and Linux.
"""

import os
import sys
import subprocess

def main():
    print("=" * 70)
    print("Building ZeroClaw Commerce Single-File Standalone Executable")
    print("=" * 70)

    is_win = sys.platform.startswith("win")
    is_mac = sys.platform == "darwin"
    
    sep = ";" if is_win else ":"
    ext = ".exe" if is_win else ""
    
    if is_win:
        platform_tag = "windows-x86_64"
    elif is_mac:
        platform_tag = "macos-aarch64"
    else:
        platform_tag = "linux-x86_64"

    binary_name = f"zeroclaw-commerce-{platform_tag}{ext}"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--clean",
        "--name", binary_name,
        "--add-data", f"fastapi-gateway/app/static{sep}app/static",
        "zeroclaw_launcher.py"
    ]

    print(f"Executing: {' '.join(cmd)}\n")
    res = subprocess.run(cmd)

    if res.returncode != 0:
        print(f"❌ Error: PyInstaller build failed with exit code {res.returncode}")
        sys.exit(res.returncode)

    dist_path = os.path.join("dist", binary_name)
    if os.path.exists(dist_path):
        size_mb = os.path.getsize(dist_path) / (1024 * 1024)
        print("\n" + "=" * 70)
        print(f" SUCCESS: Single-file executable generated at:")
        print(f" {os.path.abspath(dist_path)} ({size_mb:.2f} MB)")
        print("=" * 70 + "\n")
    else:
        print(f"❌ Error: Target binary not found at {dist_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
