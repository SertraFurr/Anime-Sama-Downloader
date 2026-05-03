<div align="center">

# 🎌 Anime-Sama Downloader
  
<img src="https://img.shields.io/badge/Python-3.6+-blue.svg?style=for-the-badge&logo=python" alt="Python Version">
<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux_(mostly_windows)-lightgrey.svg?style=for-the-badge" alt="Platform">
<img src="https://img.shields.io/badge/License-GPL_3-green.svg?style=for-the-badge" alt="License">
 
**A powerful, beautiful and simple CLI tool to download anime episodes from anime-sama.(any)**

(✨27 STARS✨! Thanks!)

*Enhanced with colorful interface, smart source detection, and robust error handling*

*Questions? Unworking urls? Open an issue, will be added fastly (hopefully)*

It also works on unreleased episodes ! (Where it says 'This content does not exist.' sometimes it still exist.) 

### 🌟 Star this repo if it helped you!

Looking for projects to do ! feel free to request in issue !

![Website Support](https://img.shields.io/badge/Website%20Support-100%25-brightgreen)

## ✨ Features

### Supports videos/scans

<table>
<tr>
<td width="50%">

###  **Smart & Intuitive**
-  **Beautiful CLI Interface** with colors and emojis
-  **Auto URL Validation** with helpful error messages
-  **Built-in Tutorial** for first-time users
-  **Multi-threaded Downloads** for blazing fast performance
</td>
<td width="50%">

###  **Powerful & Reliable**  
-  **Multiple Player Support** (Player 1, 2, 3...)
-  **Smart Source Detection** (SendVid, Sibnet and others)
-  **Real-time Progress** with download speeds
-  **Robust Error Handling** with retry logic
-  **Multiple Episode Selection** with threads supports
-  **FFmpeg support** choose between 2 converters

</td>
</tr>
</table>

---

## Quick Start
</div>

### 📋 Prerequisites

<details>
<summary>🐍 <strong> <align="center">Python Requirements</strong></summary>

Make sure you have **Python 3.6+** installed:

```bash
# Check Python version
python --version

# Install required packages
pip install requests beautifulsoup4 tqdm
```

**Required Libraries:**
- `requests` - HTTP requests handling
- `beautifulsoup4` - HTML parsing
- `tqdm` - Progress bar display

</details>


### ⚡ Installation & Usage

```bash
# 1. Clone the repository.
git clone https://github.com/SertraFurr/Anime-Sama-Downloader.git

# 2. Navigate into the project directory.
cd Anime-Sama-Downloader

# 3. Run it.
python3 main.py

# Or use the CLI arguments.
python3 main.py --help
```

---

## 📖 CLI Arguments & Usage

You can use the script entirely from the command line without interactive prompts.

| Argument | Description | Example | Default |
| :--- | :--- | :--- | :--- |
| `--search` | Search for an anime by name | `--search "naruto"` | `None` |
| `--url` | Direct URL to anime season/page | `--url "https://..."` | `None` |
| `--episodes` | Select episodes to download | `--episodes "1,2"` | `None` |
| `--player` | Select specific player (fuzzy match) | `--player "Sibnet"` | `None` |
| `--dest` | Base download directory (auto-creates folders) | `--dest "C:/X"` | `Config Folder` |
| `--threads` | Enable threaded episode downloads | `--threads` | `False` |
| `--fast` | Enable multi-threaded .ts download (10x faster) | `--fast` | `False` |
| `--mp4` | Auto-convert .ts to .mp4 | `--mp4` | `False` |
| `--tool` | Select conversion tool (av/ffmpeg) | `--tool av` | `av` |
| `--latest` | Download only the latest episode | `--latest` | `False` |
| `--no-mal` | Disable MyAnimeList research | `--no-mal` | `False` |


### ⚡ User Examples

**1. Search and Download Interactively:**
```bash
python main.py --search "roshidere"
```

**2. Download Specific Episodes from URL (Fast Mode):**
```bash
python main.py --url "https://anime-sama.tv/catalogue/roshidere/saison1/vostfr/" --episodes "1,2" --fast --mp4
```

**3. Download ALL episodes from a specific player:**
```bash
python main.py --search "one piece" --player "Sibnet" --episodes "all" --threads
```

---

<div align="center">


## 📖 Complete Interactive Usage Guide


<h3>Three Simple Steps</h3>


<table>
<tr>
<td width="33%" align="center">

### 1️⃣ Find Anime
<img src="https://img.shields.io/badge/Step-1-blue?style=for-the-badge">

Visit **[anime-sama](https://anime-sama.(DOMAIN)/catalogue/)**

- Search your anime  
- Select season & language  
-  Copy the complete URL

</td>
<td width="33%" align="center">

### 2️⃣ Run Script  
<img src="https://img.shields.io/badge/Step-2-green?style=for-the-badge">

Launch the downloader

- Paste the URL  
- Choose player & episode  
- Set download folder

</td>
<td width="33%" align="center">

### 3️⃣ Enjoy!
<img src="https://img.shields.io/badge/Step-3-purple?style=for-the-badge">

Watch the magic happen

- Auto-download starts  
- Real-time progress  
- Episode ready to watch!

</td>
</tr>
</table>

</div>

<details>
<summary>🔗 Example URLs</summary>

**✅ Works**
```
- https://anime-sama.fr/catalogue/roshidere/saison1/vostfr/
- https://anime-sama.fr/catalogue/demon-slayer/saison1/vf/
- https://anime-sama.fr/catalogue/attack-on-titan/saison3/vostfr/
- https://anime-sama.fr/catalogue/one-piece/saison1/vostfr/
```


**❌ Won’t work**
```
- https://anime-sama.fr/catalogue/roshidere/
- https://anime-sama.fr/
```
</details>


## 🛠️ Video Source Support

| Platform | Status | Performance | Notes |
|:--------:|:------:|:-----------:|:------|
| **⚠️ READ BEFORE DOING ANYTHING** | Threaded mode is only suitable for strong Wi-Fi connections that won't crash when handling multiple downloads simultaneously. |||
| 📹 **SendVid** | ![Working](https://img.shields.io/badge/Status-✅_Working-brightgreen) | ✅ Good | Primary recommended source |
| 🎬 **Sibnet** | ![Working](https://img.shields.io/badge/Status-✅_Working-brightgreen) | ✅ Good | Reliable backup source |
| 🎬 **Vidmoly** | ![Working](https://img.shields.io/badge/Status-✅_Working-brightgreen) | ✅ SLOW if not threaded. FASTEST if | Download .ts file then make them into an mp4 back. |
| 🎬 **ONEUPLOAD** | ![Working](https://img.shields.io/badge/Status-✅_Working-brightgreen) | ✅ SLOW if not threaded. Very fast if | Download .ts file then make them into an mp4 back. |
| 🎬 **EMBED4ME** | ![Working](https://img.shields.io/badge/Status-✅_Working-brightgreen) | ✅ SLOW if not threaded. Very fast if | Download .ts file then make them into an mp4 back. |
| 🎬 **MOVEARNPRE** | ![Working](https://img.shields.io/badge/Status-➖_Working_Inconsistent-orange) | ✅ SLOW if not threaded. Very fast if  | Download .ts file then make them into an mp4 back. INCONSISTENT |
| 🎬 **SMOOTHPRE** | ![Working](https://img.shields.io/badge/Status-➖_Working_Inconsistent-orange) | ✅ SLOW if not threaded. Very fast if | Download .ts file then make them into an mp4 back. INCONSISTENT |
| 🎬 **MIVALYO** | ![Working](https://img.shields.io/badge/Status-➖_Working_Inconsistent-orange) | ✅ SLOW if not threaded. Faster if | Download .ts file then make them into an mp4 back. INCONSISTENT |
| 🎬 **DINGTEZUNI** | ![Working](https://img.shields.io/badge/Status-➖_Working_Inconsistent-orange) | ✅ SLOW if not threaded. Faster if | Download .ts file then make them into an mp4 back. INCONSISTENT |
| 🚫 **MYVI** | ![Deprecated](https://img.shields.io/badge/Status-❌_Deprecated-red) | ❌ None | Malicious website, only redirect to advertisement. |
| 🚫 **MINOCHINOS** | ![Deprecated](https://img.shields.io/badge/Status-❌_Unsupported-red) | ❌ None | Does not work in some countries, useless to implement. |
| 🤔 **VK.com** | ![Deprecated](https://img.shields.io/badge/Status-❌_Unsupported-red) | ❌ None | Could try, but did not find any working URL. |

---


## 📸 Screenshots

<details>
<summary>🖼️ <strong>View CLI Interface Screenshots</strong></summary>

###  Main Interface
```
╔══════════════════════════════════════════════════════════════╗
║                 ANIME-SAMA VIDEO DOWNLOADER                  ║
║                       Enhanced CLI v2.0                      ║
╚══════════════════════════════════════════════════════════════╝

📺 Download anime episodes from anime-sama.fr easily!
```

###  Player Selection
```
🎮 SELECT PLAYER
─────────────────────────────────────────────────────────────────
  1. Player 1 (12/15 working episodes)
  2. Player 2 (8/15 working episodes)  
  3. Player 3 (15/15 working episodes)

Enter player number (1-3) or type player name:
```

###  Download Progress
```
⬇️ DOWNLOADING
─────────────────────────────────────────────────────────────────
📥 roshidere_episode_1.mp4: 100%|████████| 145M/145M [02:15<00:00, 1.07MB/s]
✅ Download completed successfully!
```

</details>

---


## ⚙️ Configuration



<details>
<summary>🔧 <strong>Customization Options</strong></summary>


### 📁 Default Settings

**Download Directory**: `./videos/`

**Video Format**: `.mp4`

**Naming Convention**: `{anime_name}_episode_{number}.mp4`


###  Color Themes
The script uses a beautiful color scheme:

🔵 **Info**: Cyan messages

✅ **Success**: Green confirmations  

⚠️ **Warning**: Yellow alerts

❌ **Error**: Red error messages

💜 **Headers**: Purple titles


</details>

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

[![Issues](https://img.shields.io/badge/Issues-Welcome-blue?style=for-the-badge)](https://github.com/sertrafurr/Anime-Sama-Downloader/issues)
[![Pull Requests](https://img.shields.io/badge/PRs-Welcome-green?style=for-the-badge)](https://github.com/sertrafurr/Anime-Sama-Downloader/pulls)
[![Discussions](https://img.shields.io/badge/Discussions-Join-purple?style=for-the-badge)](https://github.com/sertrafurr/Anime-Sama-Downloader/discussions)


### 🐛 Found a Bug?
 Check existing [issues](https://github.com/sertrafurr/issues)
 Create a new issue with:
   📝 Clear description
   🔄 Steps to reproduce
   💻 System information

### 💡 Feature Request?
 Open a [discussion](https://github.com/sertrafurr/discussions)
 Explain your idea
 Community feedback welcome!


---


## 📄 License

This project is licensed under the **GPL v3 License**

[![License: GPL](https://img.shields.io/badge/License-GPL_V3-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

*Feel free to use, modify, and distribute!*


---


## ⚠️ Disclaimer

**📢 Important Notice**

 🎯 This tool is for **educational purposes** only

 📺 Respect **copyright laws** in your jurisdiction  

 🔒 Use responsibly and in compliance with anime-sama.fr's terms


---


## 🙏 Acknowledgments

<img src="https://img.shields.io/badge/Made_with-❤️-red?style=for-the-badge">

** Core algorithms and video extraction logic: Human-developed**  
** Code restructuring and user interface enhancements: AI-assisted**

---

### 🌟 Star this repo if it helped you!

[![Stars](https://img.shields.io/github/stars/sertrafurr/anime-sama-downloader?style=for-the-badge&logo=github)](https://github.com/sertrafurr/anime-sama-downloader/stargazers)

You wish for something/a service to get removed/added, open an issue.
