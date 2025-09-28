# 🎬 Advanced YouTube Downloader

**Professional YouTube Content Downloader with Interactive Quality Selection**

## 🚀 About This Project

A powerful, feature-rich YouTube downloader that puts you in complete control of your downloads. Choose your exact video quality, download entire playlists or channels, and enjoy lightning-fast concurrent processing.

**Built on the foundation of:** [Download-Simply-Videos-From-YouTube](https://github.com/pH-7/Download-Simply-Videos-From-YouTube) by Pierre-Henry Soria, extensively enhanced and modernized.

## ✨ Key Features
- 🎯 **Interactive Quality Selection** - Choose from 144p to 4K with real-time detection
- 📊 **Smart Download Info** - See file sizes, FPS, and quality before downloading
- ⚡ **Concurrent Processing** - Download multiple content simultaneously
- 🗂️ **Smart Organization** - Auto-organized folders for playlists and channels
- 📺 **Full Channel Support** - Download entire YouTube channels
- 🎵 **Audio-Only Mode** - High-quality MP3 extraction for educational content
- 🛡️ **Robust Error Handling** - Resilient to network issues and failed downloads

## 📑 Table of Contents
- [⚙️ Requirements](#requirements)
- [📦 Installation](#installation) 
- [🚀 Quick Start](#quick-start)
- [🎯 Interactive Quality Selection](#interactive-quality-selection)
- [📋 Playlist & Channel Downloads](#playlist--channel-downloads)
- [🎵 Audio Downloads](#audio-downloads)
- [⚡ Advanced Features](#advanced-features)
- [🛠️ Configuration](#configuration)
- [🧹 Maintenance](#maintenance)
- [📄 License](#license)
- [🙏 Attribution](#attribution)

## ⚙️ Requirements
- **Python 3.7+** 🐍
- **FFmpeg** (for video processing) 🎬
- Internet connection for downloads 🌐

## 📦 Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/AdemCE-eng/youtube-downloader-pro.git
   cd youtube-downloader-pro
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux  
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg** (Required for video processing)
   
   **Windows:**
   1. Download FFmpeg from [FFmpeg.org](https://ffmpeg.org/download.html)
   2. Extract to any folder (e.g., `C:\ffmpeg` or `D:\tools\ffmpeg`)
   3. Add the `bin` folder to your system PATH:
      - Open System Properties → Environment Variables
      - Edit PATH variable and add: `C:\your-path-to-ffmpeg\bin`
      - Or run: `setx PATH "%PATH%;C:\your-path-to-ffmpeg\bin"`
   4. Verify installation: `ffmpeg -version`
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt install ffmpeg
   ```
   
   **Note:** FFmpeg path configuration is handled automatically by the script, but ensure FFmpeg is accessible from your command line.

## 🚀 Quick Start

**Basic Usage:**
```bash
python download.py
```

**Example Download Session:**
```
📥 YouTube Multi-Content Downloader
Enter YouTube URL(s): https://www.youtube.com/watch?v=EXAMPLE_ID

Choose format:
  1. MP4 Video (default)
  2. MP3 Audio only  
  3. Interactive resolution choice
Enter choice (1-3): 3

📺 Available Video Resolutions:
  1. 4K (2160p) (~342MB)
  2. 1080p (Full HD) (~76MB) 
  3. 720p (HD) (~25MB)
  4. 480p (~13MB)
Choose resolution (1-4): 2
```

## 🎯 Interactive Quality Selection

Take control of your download quality with real-time resolution detection:

**Features:**
- 🔍 **Auto-Detection** - Scans available qualities
- 📊 **Detailed Info** - Shows resolution, FPS, file size estimates  
- 🎯 **Precise Control** - Download exactly what you want
- 🚀 **4K Support** - Full Ultra HD when available
- ⚡ **Smart Fallback** - Handles unavailable qualities

**Quality Options:**
- **4K (2160p)** - Ultra HD quality
- **1440p (2K)** - High definition
- **1080p** - Full HD standard
- **720p** - HD quality
- **Lower resolutions** - 480p, 360p, 240p, 144p
- **Audio Only** - High-quality MP3

## 📋 Playlist & Channel Downloads

Download entire collections with smart organization:

**Playlist Support:**
- ✅ Standard playlists: `https://www.youtube.com/playlist?list=PLAYLIST_ID`
- ✅ Mixed URLs: `https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID`
- ✅ Multiple playlists simultaneously

**Channel Support:**  
- ✅ Handle format: `https://www.youtube.com/@channelname`
- ✅ Channel ID: `https://www.youtube.com/channel/CHANNEL_ID`
- ✅ Custom URL: `https://www.youtube.com/c/channelname`
- ✅ Legacy: `https://www.youtube.com/user/username`

**Organization:**
```
downloads/
├── Educational Playlist/
│   ├── 01-Tutorial Video.mp4
│   ├── 02-Learning Content.mp4
└── Tech Channel/
    ├── 20240101-Latest Tutorial.mp4
    └── 20231215-Programming Guide.mp4
```

## 🎵 Audio Downloads

High-quality audio extraction for educational and informational content:

**Features:**
- 🎵 **192kbps MP3** quality
- 📁 **Smart organization** for playlists
- ⚡ **Fast processing** with FFmpeg
- 🎯 **Clean output** without video data

Perfect for:
- Educational lectures and tutorials
- Podcasts and interviews  
- Documentary content
- Language learning materials

## ⚡ Advanced Features

**Concurrent Downloads:**
- Download multiple videos/playlists simultaneously
- Configurable workers (1-5, default: 3)
- Independent error handling per download

**Smart Input Parsing:**
- Comma-separated URLs: `url1, url2, url3`
- Space-separated URLs: `url1 url2 url3`
- Mixed formats: `url1, url2 url3, url4`
- Multi-line input for bulk operations

**Error Resilience:**
- Failed downloads don't stop others
- Automatic retries for network issues
- Detailed error reporting and summaries

## 🛠️ Configuration

**Debug Mode:**
```bash
python download.py --list-formats
```

**Customizable Options:**
- Resolution preferences and limits
- Concurrent download workers (1-5)
- Output directory structure
- Audio quality settings
- Retry logic for failed downloads

### FFmpeg Troubleshooting

The script automatically detects FFmpeg installation. If you encounter FFmpeg-related errors:

1. **Verify FFmpeg is installed:**
   ```bash
   ffmpeg -version
   ```

2. **If FFmpeg is not in PATH:**
   - Windows: Add FFmpeg bin folder to system PATH
   - macOS: `brew install ffmpeg` 
   - Linux: `sudo apt install ffmpeg`

3. **Common FFmpeg locations the script checks:**
   - **Windows:** `C:\ffmpeg\bin`, `C:\Program Files\ffmpeg\bin`
   - **macOS:** `/usr/local/bin`, `/opt/homebrew/bin`
   - **Linux:** `/usr/bin`, `/usr/local/bin`

4. **Manual FFmpeg installation verification:**
   - Ensure FFmpeg executable is accessible from command line
   - The script will automatically detect and use your FFmpeg installation

## 🧹 Maintenance

**Clean Up Incomplete Downloads:**
```bash
python cleanup_downloads.py
```
Removes `.part` and `.ytdl` files from interrupted downloads.

**Format Debugging:**
If you encounter format issues, use the format listing feature to see what's available for any video.

## 📄 License

This project is licensed under the MIT License - see the [license.md](license.md) file for details.

## 🙏 Attribution

This project builds upon the excellent foundation of [Download-Simply-Videos-From-YouTube](https://github.com/pH-7/Download-Simply-Videos-From-YouTube) by Pierre-Henry Soria. 

**Original Creator:** Pierre-Henry Soria  
**Original License:** MIT License  
**This Enhanced Version:** Extensively modified with new features while maintaining the same permissive license.

---

## ⚠️ Disclaimer

**Legal Usage Only:** This tool is for educational and personal use. Please:
- ✅ Ensure you have permission to download content
- ✅ Respect copyright and intellectual property rights  
- ✅ Comply with YouTube's Terms of Service
- ✅ Use responsibly for personal, educational, or fair use purposes

**Not affiliated with YouTube.** This is an independent tool that uses publicly available APIs.