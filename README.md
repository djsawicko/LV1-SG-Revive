# eMotion LV1 | SG Connect Revive

[![Windows](https://img.shields.io/badge/Windows-10+-blue?logo=windows)](https://)
[![Python](https://img.shields.io/badge/Python-3.13+-blue?logo=python)](https://)

Utility for restoring Local Device (SoundGrid Connect) support in eMotion LV1 sessions (dropped in v15). 
Pre-built Windows executables available in [Releases](https://github.com/djsawicko/LV1-SG-Revive/releases).

> [!CAUTION]
> Only works with drivers up to v15.6, as on v16 Waves completely removed the SoundGrid Connect tab from the control panel and it's functionality. Unfortunately this means that there is no known way of using Local IO on LV1 v16, as that also require v16 drivers. See more in https://github.com/djsawicko/LV1-SG-Revive/issues/2

**Use Cases:**
- Dante Virtual Soundcard integration
- FOH talkback/headphone feeds  
- Timecode distribution  
- Custom audio routing configurations

<p align="center">
  <img src="https://github.com/user-attachments/assets/b13fdc24-49c3-489c-bf31-2ba18456e4ff" alt="SG Connect Revive Interface">
</p>

<video src="https://github.com/user-attachments/assets/6cd72004-b64d-483d-b0a0-ba1e058bba53" autoplay loop muted playsinline></video>


## Technical Implementation

Modifies `.emo` session files (SQLite databases) by injecting proper SoundGrid Connect configuration values.  
Windows-only (requires WMI for network interface detection).

**Tested Environment:**
- ✔ Windows 10/11
- ✔ LV1 15.6.223.414 Build R
- ✔ SoundGrid 15.6.22
- ✔ ASIO4All v2.16

## Contributing

We welcome contributions to:
- 🐛 Report issues with different LV1 versions/device configurations
- ⚠ Fix LV1 v16 compatibility
- 🍎 Add macOS support (needs alternative to WMI)  
- 📚 Document discovered SQL schema values  
- ✨ Suggest improvements

---

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)  
*Not affiliated with or endorsed by Waves Audio*
