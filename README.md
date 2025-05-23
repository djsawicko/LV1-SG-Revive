# eMotion LV1 | SG Connect Revive

[![Windows](https://img.shields.io/badge/Windows-10+-blue?logo=windows)](https://)
[![Python](https://img.shields.io/badge/Python-3.13+-blue?logo=python)](https://)

Utility for restoring Local Device (SoundGrid Connect) support in eMotion LV1 sessions (dropped in v15). 
Pre-built Windows executables available in [Releases](https://github.com/djsawicko/LV1-SG-Revive/releases).

**Key Features:**
- Dante Virtual Soundcard integration
- FOH talkback/headphone feeds  
- Timecode distribution  
- Custom audio routing configurations

<p align="center">
  <img src="https://github.com/user-attachments/assets/b13fdc24-49c3-489c-bf31-2ba18456e4ff" alt="SG Connect Revive Interface">
</p>

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
- 🍎 Add macOS support (needs alternative to WMI)  
- 📚 Document discovered SQL schema values  
- ✨ Suggest improvements

---

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)  
*Not affiliated with or endorsed by Waves Audio*
