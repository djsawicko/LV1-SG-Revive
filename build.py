import PyInstaller.__main__
import os
import platform

# Configuration
app_name = "eMotion_LV1_SG_Connect_Revive"
script_path = "main.py"
upx_path = None
icon_path = "app_icon.icns" if platform.system() == "Darwin" else "app_icon.ico"

# Handle macOS vs Windows deployment types
# macOS requires directory mode for GUI windowed bundles; Windows prefers a clean single .exe
is_mac = platform.system() == "Darwin"
mode_flag = "--onedir" if is_mac else "--onefile"

# PyInstaller arguments
args = [
    script_path,
    mode_flag,
    "--windowed",
    f"--name={app_name}",
    "--clean",
    "--noconfirm",
]

# Safely check if assets folder exists before attempting to bundle it
if os.path.exists("assets"):
    data_sep = ":" if is_mac else ";"
    args.append(f"--add-data=assets{data_sep}assets")

# Append icon if it exists
if os.path.exists(icon_path):
    args.append(f"--icon={icon_path}")

# Append UPX compression if configured
if upx_path:
    args.append(f"--upx-dir={upx_path}")

print(f"Building for {platform.system()} using flags: {args}")
PyInstaller.__main__.run(args)