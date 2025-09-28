import os
import sys
import re
from typing import Optional, List, Dict, Tuple
from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import ffmpeg
import platform
import subprocess
import shutil


def detect_ffmpeg_location():
    """
    Automatically detect FFmpeg location on the system.
    Returns the path to FFmpeg executable or None if not found.
    """
    # First try to find FFmpeg in PATH
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return os.path.dirname(ffmpeg_path)
    
    # Common Windows locations
    if platform.system() == 'Windows':
        common_paths = [
            'C:\\ffmpeg\\bin',
            'C:\\Program Files\\ffmpeg\\bin',
            'C:\\Program Files (x86)\\ffmpeg\\bin',
            'D:\\ffmpeg\\bin',
            os.path.join(os.path.expanduser('~'), 'ffmpeg', 'bin'),
        ]
        
        for path in common_paths:
            ffmpeg_exe = os.path.join(path, 'ffmpeg.exe')
            if os.path.exists(ffmpeg_exe):
                return path
    
    # Common macOS/Linux locations
    else:
        common_paths = [
            '/usr/bin',
            '/usr/local/bin',
            '/opt/homebrew/bin',  # macOS with Apple Silicon
            '/home/linuxbrew/.linuxbrew/bin',  # Linux with Homebrew
        ]
        
        for path in common_paths:
            ffmpeg_exe = os.path.join(path, 'ffmpeg')
            if os.path.exists(ffmpeg_exe):
                return path
    
    # If not found, return None (will rely on PATH)
    return None


@lru_cache(maxsize=128)
def get_url_info(url: str) -> Tuple[str, Dict]:
    """
    Get URL information with caching to avoid duplicate yt-dlp calls.
    Returns (content_type, info_dict) for efficient reuse.

    Args:
        url (str): YouTube URL to analyze

    Returns:
        Tuple[str, Dict]: (content_type, info_dict) where content_type is 'video', 'playlist', or 'channel'
    """
    try:
        # Use yt-dlp to extract info without downloading
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # Only extract basic info, faster
            'no_warnings': True,
            'skip_download': True,
            'playlist_items': '1',  # Only check first item for speed
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Check if info extraction was successful
            if info is None:
                # Fallback to URL parsing if yt-dlp fails
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)

                # Check for channel patterns
                if '/@' in url or '/channel/' in url or '/c/' in url or '/user/' in url:
                    return 'channel', {}
                elif 'list' in query_params:
                    return 'playlist', {}
                else:
                    return 'video', {}

            # Determine content type based on yt-dlp info
            content_type = info.get('_type', 'video')

            # Handle special case: URLs with both video and playlist (type 'url')
            if content_type == 'url':
                # Check if URL has playlist parameter - treat as playlist
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                if 'list' in query_params:
                    return 'playlist', info
                else:
                    return 'video', info

            # Handle channel detection
            if content_type == 'playlist':
                # Check if it's actually a channel (uploader_id indicates channel content)
                if info.get('uploader_id') and ('/@' in url or '/channel/' in url or '/c/' in url or '/user/' in url):
                    return 'channel', info
                else:
                    return 'playlist', info

            return content_type, info

    except Exception:
        # Simple fallback: check URL patterns
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        if '/@' in url or '/channel/' in url or '/c/' in url or '/user/' in url:
            return 'channel', {}
        elif 'list' in query_params:
            return 'playlist', {}
        else:
            return 'video', {}


def is_playlist_url(url: str) -> bool:
    """
    Check if the provided URL is a playlist or a single video using cached detection.
    Uses yt-dlp's native detection with simple URL parsing fallback.

    Args:
        url (str): YouTube URL to check

    Returns:
        bool: True if URL is a playlist, False if single video
    """
    content_type, _ = get_url_info(url)
    return content_type == 'playlist'


def get_content_type(url: str) -> str:
    """
    Get the content type of a YouTube URL.

    Args:
        url (str): YouTube URL to analyze

    Returns:
        str: 'video', 'playlist', or 'channel'
    """
    content_type, _ = get_url_info(url)
    return content_type


def parse_multiple_urls(input_string: str) -> List[str]:
    """
    Parse multiple URLs from input string separated by commas, spaces, newlines, or mixed formats.
    Handles complex mixed separators like "url1, url2 url3\nurl4".

    Args:
        input_string (str): String containing one or more URLs

    Returns:
        List[str]: List of cleaned URLs
    """
    # Use regex to split by multiple separators: comma, space, newline, tab
    urls = re.split(r'[,\s\n\t]+', input_string.strip())
    urls = [url.strip() for url in urls if url.strip()]

    # Validate URLs (basic YouTube URL check)
    valid_urls = []
    invalid_count = 0
    for url in urls:
        if ('youtube.com' in url or 'youtu.be' in url) and (
            '/watch?' in url or
            '/playlist?' in url or
            '/@' in url or
            '/channel/' in url or
            '/c/' in url or
            '/user/' in url or
            'youtu.be/' in url
        ):
            valid_urls.append(url)
        elif url:  # Only show warning for non-empty strings
            print(f"⚠️  Skipping invalid URL: {url}")
            invalid_count += 1

    if invalid_count > 0:
        print(
            f"💡 Found {len(valid_urls)} valid YouTube URLs, skipped {invalid_count} invalid entries")

    return valid_urls


def get_available_resolutions(url: str) -> dict:
    """
    Get available video resolutions for a YouTube URL.
    
    Args:
        url (str): YouTube URL to check
        
    Returns:
        dict: Available resolutions with format info
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info or 'formats' not in info:
                return {}
                
            # Extract video formats with resolution info
            resolutions = {}
            for fmt in info['formats']:
                if fmt.get('vcodec') != 'none' and fmt.get('height'):  # Video formats only
                    height = fmt['height']
                    width = fmt.get('width', 'unknown')
                    fps = fmt.get('fps', 'unknown')
                    ext = fmt.get('ext', 'unknown')
                    filesize = fmt.get('filesize', 0)
                    
                    # Create resolution key
                    res_key = f"{height}p"
                    if height >= 2160:
                        res_key = "4K (2160p)"
                    elif height >= 1440:
                        res_key = "1440p (2K)"
                    elif height >= 1080:
                        res_key = "1080p (Full HD)"
                    elif height >= 720:
                        res_key = "720p (HD)"
                    elif height >= 480:
                        res_key = "480p"
                    elif height >= 360:
                        res_key = "360p"
                    elif height >= 240:
                        res_key = "240p"
                    
                    if res_key not in resolutions or (filesize and filesize > resolutions[res_key].get('filesize', 0)):
                        resolutions[res_key] = {
                            'height': height,
                            'width': width,
                            'fps': fps,
                            'ext': ext,
                            'filesize': filesize,
                            'format_id': fmt['format_id']
                        }
            
            return resolutions
            
    except Exception as e:
        print(f"⚠️ Error getting resolutions: {str(e)}")
        return {}


def choose_resolution(url: str) -> str:
    """
    Let user choose video resolution from available options.
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: Format selector string
    """
    print("🔍 Detecting available video resolutions...")
    resolutions = get_available_resolutions(url)
    
    if not resolutions:
        print("⚠️ Could not detect available resolutions, using default (1080p max)")
        return 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
    
    # Sort resolutions by height (descending)
    sorted_resolutions = sorted(resolutions.items(), key=lambda x: x[1]['height'], reverse=True)
    
    print("\n📺 Available Video Resolutions:")
    print("=" * 50)
    
    choices = []
    for i, (res_name, info) in enumerate(sorted_resolutions, 1):
        filesize_mb = info['filesize'] / (1024*1024) if info['filesize'] else 0
        size_info = f" (~{filesize_mb:.1f}MB)" if filesize_mb > 0 else ""
        fps_info = f" @ {info['fps']}fps" if info['fps'] != 'unknown' else ""
        
        print(f"  {i}. {res_name} ({info['width']}x{info['height']}){fps_info}{size_info}")
        choices.append((res_name, info))
    
    # Add option for audio-only
    print(f"  {len(choices)+1}. Audio Only (MP3)")
    
    print("=" * 50)
    
    while True:
        try:
            choice = input(f"Choose resolution (1-{len(choices)+1}, default=1): ").strip()
            
            if not choice:
                choice = "1"
                
            choice_num = int(choice)
            
            if choice_num == len(choices) + 1:
                # Audio only
                return 'audio_only'
            elif 1 <= choice_num <= len(choices):
                selected_res = choices[choice_num - 1]
                height = selected_res[1]['height']
                
                print(f"✅ Selected: {selected_res[0]} ({selected_res[1]['width']}x{height})")
                
                # Return format selector based on chosen resolution
                return f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best'
            else:
                print(f"❌ Please enter a number between 1 and {len(choices)+1}")
                
        except ValueError:
            print("❌ Please enter a valid number")


def choose_resolution_for_collection(url: str, content_type: str) -> str:
    """
    Let user choose resolution for playlists or channels.
    
    Args:
        url (str): YouTube URL (playlist or channel)
        content_type (str): 'playlist' or 'channel'
        
    Returns:
        str: Format selector string
    """
    print(f"\n🔍 Interactive resolution for {content_type}...")
    print(f"📋 Note: This resolution preference will be applied to all videos in this {content_type}")
    print("🎯 Some videos may not have all resolutions available - the script will use the best available match")
    
    # Show common resolution options without specific file sizes (since they vary per video)
    print(f"\n📺 Choose Resolution Preference for {content_type.title()}:")
    print("=" * 60)
    
    resolution_options = [
        ("4K (2160p) - Ultra HD Quality", "bestvideo[height<=2160]+bestaudio/best[height<=2160]/best"),
        ("1440p (2K) - High Quality", "bestvideo[height<=1440]+bestaudio/best[height<=1440]/best"),
        ("1080p (Full HD) - Standard HD", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"),
        ("720p (HD) - Basic HD", "bestvideo[height<=720]+bestaudio/best[height<=720]/best"),
        ("480p - Standard Quality", "bestvideo[height<=480]+bestaudio/best[height<=480]/best"),
        ("360p - Lower Quality", "bestvideo[height<=360]+bestaudio/best[height<=360]/best"),
        ("Best Available (No Limit)", "bestvideo+bestaudio/best"),
        ("Audio Only (MP3)", "audio_only")
    ]
    
    for i, (desc, _) in enumerate(resolution_options, 1):
        print(f"  {i}. {desc}")
    
    print("=" * 60)
    
    while True:
        try:
            choice = input(f"Choose resolution preference (1-{len(resolution_options)}, default=3 for 1080p): ").strip()
            
            if not choice:
                choice = "3"  # Default to 1080p
                
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(resolution_options):
                selected_option = resolution_options[choice_num - 1]
                print(f"✅ Selected: {selected_option[0]}")
                
                if selected_option[1] == "audio_only":
                    return 'audio_only'
                else:
                    return selected_option[1]
            else:
                print(f"❌ Please enter a number between 1 and {len(resolution_options)}")
                
        except ValueError:
            print("❌ Please enter a valid number")


def choose_general_resolution() -> str:
    """
    Let user choose general resolution preference for multiple URLs.
    
    Returns:
        str: Format selector string
    """
    print("\n🔍 Choose general resolution preference for all downloads...")
    print("📋 Note: This preference will be applied to all videos, playlists, and channels")
    print("🎯 Individual videos may not have all resolutions - the script will use the best available match")
    
    resolution_options = [
        ("4K (2160p) - Ultra HD Quality", "bestvideo[height<=2160]+bestaudio/best[height<=2160]/best"),
        ("1440p (2K) - High Quality", "bestvideo[height<=1440]+bestaudio/best[height<=1440]/best"),
        ("1080p (Full HD) - Standard HD (Recommended)", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"),
        ("720p (HD) - Basic HD", "bestvideo[height<=720]+bestaudio/best[height<=720]/best"),
        ("480p - Standard Quality", "bestvideo[height<=480]+bestaudio/best[height<=480]/best"),
        ("360p - Lower Quality", "bestvideo[height<=360]+bestaudio/best[height<=360]/best"),
        ("Best Available (No Limit)", "bestvideo+bestaudio/best"),
        ("Audio Only (MP3)", "audio_only")
    ]
    
    print(f"\n📺 Choose General Resolution Preference:")
    print("=" * 60)
    
    for i, (desc, _) in enumerate(resolution_options, 1):
        print(f"  {i}. {desc}")
    
    print("=" * 60)
    
    while True:
        try:
            choice = input(f"Choose resolution preference (1-{len(resolution_options)}, default=3 for 1080p): ").strip()
            
            if not choice:
                choice = "3"  # Default to 1080p
                
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(resolution_options):
                selected_option = resolution_options[choice_num - 1]
                print(f"✅ Selected: {selected_option[0]}")
                
                if selected_option[1] == "audio_only":
                    return 'audio_only'
                else:
                    return selected_option[1]
            else:
                print(f"❌ Please enter a number between 1 and {len(resolution_options)}")
                
        except ValueError:
            print("❌ Please enter a valid number")


def get_available_formats(url: str) -> None:
    """
    List available formats for debugging purposes.

    Args:
        url (str): YouTube URL to check formats for
    """
    ydl_opts = {
        'listformats': True,
        'quiet': False
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=False)
    except Exception as e:
        print(f"Error listing formats: {str(e)}")


def download_single_video(url: str, output_path: str, thread_id: int = 0, audio_only: bool = False, format_selector: Optional[str] = None) -> dict:
    """
    Download a single YouTube video, playlist, or channel.

    Args:
        url (str): YouTube URL to download (video, playlist, or channel)
        output_path (str): Directory to save the download
        thread_id (int): Thread identifier for logging
        audio_only (bool): If True, download audio only in MP3 format
        format_selector (str): Custom format selector string

    Returns:
        dict: Result status with success/failure info
    """
    if audio_only or format_selector == 'audio_only':
        # Configure for audio-only MP3 downloads
        format_selector = 'bestaudio/best'
        file_extension = 'mp3'
        postprocessors = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        print(f"🎵 [Thread {thread_id}] Audio-only mode: Downloading MP3...")
        audio_only = True
    else:
        # Configure for video downloads with AAC audio (Windows Media Player compatible)
        if format_selector is None:
            format_selector = (
                # Try best video+audio combination first
                'bestvideo[height<=1080]+bestaudio/best[height<=1080]/'
                # Fallback to best available quality
                'best'
            )
        file_extension = 'mp4'
        postprocessors = [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]

    # Configure yt-dlp options
    ydl_opts = {
        'format': format_selector,
        'ignoreerrors': True,
        'no_warnings': False,
        'extract_flat': False,
        # Disable additional downloads for clean output
        'writesubtitles': False,
        'writethumbnail': False,
        'writeautomaticsub': False,
        'postprocessors': postprocessors,
        # Clean up options
        'keepvideo': False,
        'clean_infojson': True,
        'retries': 3,
        'fragment_retries': 3,
        # Ensure playlists are fully downloaded
        'noplaylist': False,  # Allow playlist downloads
    }

    # Detect and set FFmpeg location automatically
    ffmpeg_location = detect_ffmpeg_location()
    if ffmpeg_location:
        ydl_opts['ffmpeg_location'] = ffmpeg_location

    # Add merge format for video downloads only
    if not audio_only:
        ydl_opts['merge_output_format'] = 'mp4'
        # Add FFmpeg postprocessor to convert audio to AAC for compatibility
        ydl_opts['postprocessor_args'] = {
            'ffmpeg': ['-c:a', 'aac', '-b:a', '192k']
        }

    # Set different output templates for playlists, channels and single videos
    content_type, cached_info = get_url_info(url)

    # Debug: Print detection result
    if thread_id == 1:  # Only print for first thread to avoid spam
        print(f"🔍 [Debug] URL analysis: {content_type.title()}")

    if content_type == 'playlist':
        ydl_opts['outtmpl'] = os.path.join(
            output_path, '%(playlist_title)s', f'%(playlist_index)s-%(title)s.{file_extension}')
        print(
            f"📋 [Thread {thread_id}] Detected playlist URL. Downloading entire playlist...")
    elif content_type == 'channel':
        ydl_opts['outtmpl'] = os.path.join(
            output_path, '%(uploader)s', f'%(upload_date)s-%(title)s.{file_extension}')
        print(
            f"📺 [Thread {thread_id}] Detected channel URL. Downloading entire channel...")
    else:  # single video
        ydl_opts['outtmpl'] = os.path.join(
            output_path, f'%(title)s.{file_extension}')
        print(
            f"🎥 [Thread {thread_id}] Detected single video URL. Downloading {'audio' if audio_only else 'video'}...")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Extract fresh info for download (cached info is only for detection)
            info = ydl.extract_info(url, download=False)

            # Check if info extraction was successful
            if info is None:
                return {
                    'url': url,
                    'success': False,
                    'message': f"❌ [Thread {thread_id}] Failed to extract video information. Video may be private or unavailable."
                }

            if info.get('_type') == 'playlist':
                title = info.get('title', 'Unknown Playlist')
                video_count = len(info.get('entries', []))
                print(
                    f"📋 [Thread {thread_id}] {content_type.title()}: '{title}' ({video_count} videos)")

                # Ensure we have entries to download
                if video_count == 0:
                    return {
                        'url': url,
                        'success': False,
                        'message': f"❌ [Thread {thread_id}] {content_type.title()} appears to be empty or private"
                    }

            # Download content
            ydl.download([url])

            if info.get('_type') == 'playlist':
                title = info.get('title', f'Unknown {content_type.title()}')
                video_count = len(info.get('entries', []))
                return {
                    'url': url,
                    'success': True,
                    'message': f"✅ [Thread {thread_id}] {content_type.title()} '{title}' download completed! ({video_count} {'MP3s' if audio_only else 'videos'})"
                }
            else:
                return {
                    'url': url,
                    'success': True,
                    'message': f"✅ [Thread {thread_id}] {'Audio' if audio_only else 'Video'} download completed successfully!"
                }

    except Exception as e:
        return {
            'url': url,
            'success': False,
            'message': f"❌ [Thread {thread_id}] Error: {str(e)}"
        }


def download_youtube_content(urls: List[str], output_path: Optional[str] = None,
                             list_formats: bool = False, max_workers: int = 3, audio_only: bool = False, 
                             interactive_resolution: bool = False) -> None:
    """
    Download YouTube content (single videos, playlists, or channels) in MP4 format or MP3 audio only.
    Supports multiple URLs for simultaneous downloading.

    Args:
        urls (List[str]): List of YouTube URLs to download (videos, playlists, or channels)
        output_path (str, optional): Directory to save the downloads. Defaults to './downloads'
        list_formats (bool): If True, only list available formats without downloading
        max_workers (int): Maximum number of concurrent downloads
        audio_only (bool): If True, download audio only in MP3 format
        interactive_resolution (bool): If True, let user choose resolution for each video
    """
    # Set default output path if none provided
    if output_path is None:
        output_path = os.path.join(os.getcwd(), 'downloads')

    # If user wants to list formats, do that for the first URL and return
    if list_formats:
        print("Available formats for the first provided URL:")
        get_available_formats(urls[0])
        return

    # Interactive resolution selection
    format_selector = None
    if interactive_resolution and not audio_only:
        print("\n🎯 Interactive Resolution Mode Activated!")
        
        # Check content types
        video_count = sum(1 for url in urls if get_content_type(url) == 'video')
        playlist_count = sum(1 for url in urls if get_content_type(url) == 'playlist')
        channel_count = sum(1 for url in urls if get_content_type(url) == 'channel')
        
        if len(urls) == 1:
            # Single URL - check what type it is
            content_type = get_content_type(urls[0])
            if content_type == 'video':
                format_selector = choose_resolution(urls[0])
            elif content_type in ['playlist', 'channel']:
                format_selector = choose_resolution_for_collection(urls[0], content_type)
        else:
            # Multiple URLs - ask for general resolution preference
            format_selector = choose_general_resolution()
        
        if format_selector == 'audio_only':
            audio_only = True
            format_selector = None

    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)

    print(
        f"\n🚀 Starting download of {len(urls)} URL(s) with {max_workers} concurrent workers...")
    print(f"📁 Output directory: {output_path}")
    print(f"🎧 Format: {'MP3 Audio Only' if audio_only else 'MP4 Video'}")

    # Show what types of content we're downloading
    playlist_count = sum(
        1 for url in urls if get_content_type(url) == 'playlist')
    channel_count = sum(
        1 for url in urls if get_content_type(url) == 'channel')
    video_count = len(urls) - playlist_count - channel_count

    content_summary = []
    if playlist_count > 0:
        content_summary.append(f"{playlist_count} playlist(s)")
    if channel_count > 0:
        content_summary.append(f"{channel_count} channel(s)")
    if video_count > 0:
        content_summary.append(f"{video_count} video(s)")

    if content_summary:
        print(f"📋 Content: {' + '.join(content_summary)}")
    else:
        print("🎥 Content: Unknown content type")

    print("-" * 60)

    # Concurrent downloads
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(download_single_video, url, output_path, i+1, audio_only, format_selector): url
            for i, url in enumerate(urls)
        }

        # Collect results
        for future in as_completed(future_to_url):
            result = future.result()
            results.append(result)
            print(result['message'])

    print("\n" + "=" * 60)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 60)

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f"✅ Successful downloads: {len(successful)}")
    print(f"❌ Failed downloads: {len(failed)}")

    if failed:
        print("\n❌ Failed URLs:")
        for result in failed:
            print(f"   • {result['url']}")
            print(f"     Reason: {result['message']}")

    if successful:
        print(f"\n🎉 All files saved to: {output_path}")


if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--list-formats':
        url = input("Enter the YouTube URL to list formats: ")
        download_youtube_content([url], list_formats=True)
    else:
        # Normal download flow
        print("📥 YouTube Multi-Content Downloader")
        print("=" * 50)
        print("💡 SUPPORTED INPUT FORMATS:")
        print("   🔸 Single URL: Just paste one YouTube URL")
        print("   🔸 Comma-separated: url1, url2, url3")
        print("   🔸 Space-separated: url1 url2 url3")
        print("   🔸 Mixed format: url1, url2 url3, url4")
        print("   🔸 Multi-line: Press Enter without typing, then one URL per line")
        print()
        print("🎯 SUPPORTED CONTENT TYPES:")
        print("   📹 Single Videos: https://www.youtube.com/watch?v=...")
        print("   📋 Playlists: https://www.youtube.com/playlist?list=...")
        print("   📺 Channels: https://www.youtube.com/@channelname")
        print("   📺 Channels: https://www.youtube.com/channel/UC...")
        print("   📺 Channels: https://www.youtube.com/c/channelname")
        print("   📺 Channels: https://www.youtube.com/user/username")
        print("-" * 50)

        urls_input = input("Enter YouTube URL(s): ")

        # Handle multi-line input
        if not urls_input.strip():
            print("📝 Multi-line mode activated!")
            print("💡 Enter one URL per line, press Enter twice when finished:")
            urls_list = []
            line_count = 1
            while True:
                line = input(f"   URL {line_count}: ")
                if line.strip() == "":
                    break
                urls_list.append(line)
                line_count += 1
            urls_input = '\n'.join(urls_list)

        if not urls_input.strip():
            print("❌ No URLs entered. Exiting...")
            exit(1)

        urls = parse_multiple_urls(urls_input)

        if not urls:
            print("❌ No valid YouTube URLs found. Please try again.")
            exit(1)

        print(f"\n✅ Found {len(urls)} valid URL(s)")
        for i, url in enumerate(urls, 1):
            print(f"   {i}. {url}")

        output_dir = input(
            "\nEnter output directory (press Enter for default): "
        ).strip()

        # Ask for format preference
        format_choice = input(
            "\nChoose format:\n"
            "  1. MP4 Video (default)\n"
            "  2. MP3 Audio only\n"
            "  3. Interactive resolution choice\n"
            "Enter choice (1-3, default=1): ").strip()

        audio_only = False
        interactive_resolution = False
        
        if format_choice == '2':
            audio_only = True
            print("🎵 Selected: MP3 Audio only")
        elif format_choice == '3':
            interactive_resolution = True
            print("🎯 Selected: Interactive resolution choice")
        else:
            print("🎥 Selected: MP4 Video")

        # Only ask for concurrent workers if there are multiple URLs
        max_workers = 1  # Default for single URL
        if len(urls) > 1:
            workers_input = input(
                "Number of concurrent downloads (1-5, default=3): ").strip()
            try:
                max_workers = int(workers_input) if workers_input else 3
                max_workers = max(1, min(5, max_workers))  # Clamp between 1-5
            except ValueError:
                max_workers = 3

        print(f"\n🎬 Starting downloads...")
        print(f"📊 URLs to download: {len(urls)}")
        print(f"🎧 Format: {'MP3 Audio' if audio_only else ('Interactive Resolution' if interactive_resolution else 'MP4 Video')}")
        if len(urls) > 1:
            print(f"⚡ Concurrent workers: {max_workers}")
        print(
            f"📁 Output: {output_dir if output_dir else 'default (./downloads)'}")

        if output_dir:
            download_youtube_content(
                urls, output_dir, max_workers=max_workers, audio_only=audio_only, 
                interactive_resolution=interactive_resolution)
        else:
            download_youtube_content(
                urls, max_workers=max_workers, audio_only=audio_only, 
                interactive_resolution=interactive_resolution)
