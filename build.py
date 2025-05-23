import PyInstaller.__main__
import os

# Configuration
app_name = "eMotion_LV1_SG_Connect_Revive"
script_path = "main.py"
upx_path = None
icon_path = "app_icon.ico" 
additional_files = []

# PyInstaller arguments
args = [
    script_path,
    "--onedir",
    "--windowed",
    f"--name={app_name}",
    "--clean",
    "--noconfirm",
    "--add-data=assets;assets" if os.path.exists("assets") else "",
    f"--icon={icon_path}" if os.path.exists(icon_path) else "",
    f"--upx-dir={upx_path}" if upx_path else ""
]

# Remove empty arguments
args = [arg for arg in args if arg]
PyInstaller.__main__.run(args)