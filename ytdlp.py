#!/usr/bin/env python3
import os
import sys
import re
import json
import requests
import subprocess
from pathlib import Path
from urllib.parse import quote
import argparse
from typing import List, Dict, Optional
import time

class UniversalVideoDownloader:
    def __init__(self):
        script_dir = Path(__file__).parent.absolute()
        self.output_dir = script_dir / "Video Downloads"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.check_ytdlp_installed():
            print("[*] yt-dlp is not installed. Please install it with: pip install yt-dlp")
            sys.exit(1)
    
    def check_ytdlp_installed(self) -> bool:
        try:
            subprocess.run(["yt-dlp", "--version"], 
                          capture_output=True, check=True, text=True, timeout=10)
            return True
        except subprocess.TimeoutExpired:
            print("[*] Timeout checking yt-dlp version")
            return False
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
        except Exception as e:
            print(f"[*] Unexpected error checking yt-dlp: {e}")
            return False
    
    def clear_screen(self):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.show_header()
        except Exception as e:
            print(f"[*] Error clearing screen: {e}")
    
    def show_header(self):
        try:
            print(r"       _      _ _       ")
            print(r"      | |    | | |      ")
            print(r" _   _| |_ __| | |_ __  ")
            print(r"| | | | __/ _` | | '_ \ ")
            print(r"| |_| | || (_| | | |_) |")
            print(r" \__, |\__\__,_|_| .__/ ")
            print(r"  __/ |          | |    ")
            print(r" |___/           |_|    ")
            print("     Developed by: @Finnapple")
            print()
            print("[*] Universal Video Downloader - HIGHEST QUALITY WITH AUDIO")
            print("[*] Download videos in highest quality with proper audio")
            print("[*] Supports: YouTube, Facebook, TikTok, Instagram, Twitter, etc.")
            print("[*] Paste any video URL. Type 'exit' to quit.")
            print("[*] Type 'clear' to clear the screen.")
            print(f"[*] Downloading to: {self.output_dir}")
            print("-" * 60)
        except Exception as e:
            print(f"[*] Error displaying header: {e}")
    
    def sanitize_filename(self, name: str) -> str:
        try:
            if not name:
                return "video"
            name = re.sub(r'[<>:"/\\|?*]', '', name)
            if len(name) > 150:
                name = name[:150]
            return name.strip()
        except Exception as e:
            print(f"[*] Error sanitizing filename: {e}")
            return "video"
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"[*] Getting video information (attempt {attempt + 1}/{max_retries})...")
                result = subprocess.run([
                    "yt-dlp", "--dump-json", "--no-warnings", url
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    return {
                        'title': info.get('title', 'Unknown Title'),
                        'uploader': info.get('uploader', 'Unknown Uploader'),
                        'duration': info.get('duration', 0),
                        'view_count': info.get('view_count', 0),
                        'upload_date': info.get('upload_date', ''),
                        'description': info.get('description', '')[:200],
                        'webpage_url': info.get('webpage_url', url),
                        'extractor': info.get('extractor', 'Unknown Platform')
                    }
                else:
                    print(f"[*] yt-dlp returned error code: {result.returncode}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        
            except subprocess.TimeoutExpired:
                print(f"[*] Timeout getting video info (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    time.sleep(2)
            except json.JSONDecodeError as e:
                print(f"[*] Failed to parse video info JSON: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
            except Exception as e:
                print(f"[*] Error getting video info (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        print("[*] Failed to get video information after all retries")
        return None
    
    def download_with_ytdlp(self, url: str, output_path: Path, timeout: int = 900) -> bool:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # HIGHEST QUALITY WITH AUDIO - best video + best audio, merged to MP4
                format_spec = "bestvideo+bestaudio/best"
                
                cmd = [
                    "yt-dlp",
                    "-f", format_spec,
                    "--merge-output-format", "mp4",
                    "-o", str(output_path / "%(title)s.%(ext)s"),
                    "--no-warnings",
                    "--newline",
                    url
                ]
                
                print(f"[*] Download attempt {attempt + 1}/{max_retries}")
                print(f"[*] Downloading HIGHEST QUALITY with audio...")
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                start_time = time.time()
                merging = False
                
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        if '[download]' in line:
                            print(f"\r{line}", end='', flush=True)
                        elif 'ETA' in line or '%' in line:
                            print(f"\r{line}", end='', flush=True)
                        elif 'Merging' in line and not merging:
                            print(f"\n[*] Merging video and audio streams...")
                            merging = True
                        elif 'ERROR' in line:
                            print(f"\nError: {line}")
                        elif 'WARNING' in line:
                            if 'already been downloaded' not in line:
                                print(f"\nWarning: {line}")
                    
                    if time.time() - start_time > timeout:
                        process.kill()
                        print(f"\n[*] Download timed out after {timeout} seconds!")
                        if attempt < max_retries - 1:
                            print(f"[*] Retrying...")
                            time.sleep(3)
                        break
                
                else:
                    process.wait()
                    
                    if process.returncode == 0:
                        print(f"\n[+] Download completed successfully!")
                        print(f"[+] Highest quality video with audio ready!")
                        return True
                    else:
                        print(f"\n[!] Download failed with exit code: {process.returncode}")
                        if attempt < max_retries - 1:
                            print(f"[*] Retrying in 3 seconds...")
                            time.sleep(3)
                
                continue
                
            except Exception as e:
                print(f"[*] Error downloading with yt-dlp (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"[*] Retrying in 3 seconds...")
                    time.sleep(3)
        
        print(f"[!] Download failed after {max_retries} attempts")
        return False
    
    def find_downloaded_file(self, video_info: Dict, output_path: Path) -> Optional[Path]:
        try:
            video_files = list(output_path.glob("*.mp4"))
            
            if not video_files:
                print("[*] No MP4 files found in download directory")
                return None
            
            video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            sanitized_title = self.sanitize_filename(video_info['title'])
            for file in video_files:
                if sanitized_title.lower() in file.stem.lower():
                    print(f"[*] Found matching file: {file.name}")
                    return file
            
            newest_file = video_files[0]
            print(f"[*] No exact title match, using newest file: {newest_file.name}")
            return newest_file
            
        except Exception as e:
            print(f"[*] Error finding downloaded file: {e}")
            return None
    
    def download_video(self, url: str) -> bool:
        try:
            print(f"[*] Processing URL: {url}")
            
            video_info = self.get_video_info(url)
            
            if video_info:
                print(f"[*] Title: {video_info['title']}")
                print(f"[*] Uploader: {video_info['uploader']}")
                print(f"[*] Platform: {video_info['extractor']}")
                if video_info['duration']:
                    minutes = int(video_info['duration']) // 60
                    seconds = int(video_info['duration']) % 60
                    print(f"[*] Duration: {minutes}:{seconds:02d}")
                if video_info['view_count']:
                    view_count = video_info['view_count']
                    if isinstance(view_count, (int, float)):
                        print(f"[*] Views: {view_count:,}")
                    else:
                        print(f"[*] Views: {view_count}")
            else:
                print("[*] Could not get video information, proceeding with download...")
                video_info = {'title': 'Unknown Video', 'uploader': 'Unknown', 'extractor': 'Unknown'}
            
            platform_dir = self.output_dir / self.sanitize_filename(video_info['extractor'])
            try:
                platform_dir.mkdir(exist_ok=True)
            except Exception as e:
                print(f"[*] Error creating directory {platform_dir}: {e}")
                platform_dir = self.output_dir
            
            print(f"[*] Downloading to: {platform_dir}")
            
            success = self.download_with_ytdlp(url, platform_dir)
            
            if success:
                downloaded_file = self.find_downloaded_file(video_info, platform_dir)
                if downloaded_file:
                    try:
                        file_size = downloaded_file.stat().st_size / (1024 * 1024)
                        print(f"[+] Download complete: {downloaded_file.name}")
                        print(f"[+] File size: {file_size:.2f} MB")
                        print(f"[+] Location: {downloaded_file}")
                        
                        # Verify file has audio
                        try:
                            result = subprocess.run([
                                "ffprobe", "-v", "quiet", "-select_streams", "a",
                                "-show_entries", "stream=codec_type", 
                                "-of", "csv=p=0", str(downloaded_file)
                            ], capture_output=True, text=True, timeout=10)
                            
                            if result.returncode == 0 and 'audio' in result.stdout:
                                print(f"[+] Audio: Present")
                            else:
                                print(f"[!] Audio: Not detected")
                        except:
                            print(f"[*] Could not verify audio stream")
                            
                    except Exception as e:
                        print(f"[*] Error getting file info: {e}")
                        print(f"[+] Download complete: {downloaded_file.name}")
                else:
                    print("[+] Download completed but could not locate the specific file")
                    print(f"[*] Check directory: {platform_dir}")
                
                return True
            else:
                print("[!] Download failed after all retries")
                return False
                
        except Exception as e:
            print(f"[*] Error in download_video: {e}")
            return False
    
    def download_playlist(self, url: str) -> bool:
        try:
            print(f"[*] Processing playlist: {url}")
            
            playlist_dir = self.output_dir / "Playlists" / f"Playlist_{int(time.time())}"
            try:
                playlist_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"[*] Error creating playlist directory: {e}")
                playlist_dir = self.output_dir / "Playlists"
                playlist_dir.mkdir(exist_ok=True)
            
            print(f"[*] Downloading playlist to: {playlist_dir}")
            
            cmd = [
                "yt-dlp",
                "-f", "bestvideo+bestaudio/best",
                "--merge-output-format", "mp4",
                "-o", str(playlist_dir / "%(playlist_title)s/%(title)s.%(ext)s"),
                "--no-warnings",
                "--newline",
                url
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            video_count = 0
            success_count = 0
            for line in process.stdout:
                line = line.strip()
                if line:
                    if '[download]' in line and 'Downloading video' not in line:
                        print(f"\r{line}", end='', flush=True)
                        if '100%' in line:
                            success_count += 1
                    elif 'Downloading video' in line:
                        video_count += 1
                        print(f"\n[*] Downloading video {video_count}: {line.split(' of ')[-1]}")
                    elif 'ETA' in line or '%' in line:
                        print(f"\r{line}", end='', flush=True)
                    elif 'Merging' in line:
                        print(f"\n[*] Merging audio and video...")
                    elif 'ERROR' in line:
                        print(f"\nError: {line}")
                    elif 'WARNING' in line:
                        print(f"\nWarning: {line}")
            
            process.wait()
            
            if process.returncode == 0:
                print(f"\n[+] Playlist download completed! Downloaded {success_count}/{video_count} videos successfully.")
                return True
            else:
                print(f"\n[!] Playlist download completed with errors. Exit code: {process.returncode}")
                print(f"[*] Successfully downloaded: {success_count}/{video_count} videos")
                return False
                
        except Exception as e:
            print(f"[*] Error downloading playlist: {e}")
            return False
    
    def process_url(self, url: str) -> bool:
        try:
            if not url.startswith(('http://', 'https://')):
                print("[!] Invalid URL format. Please include http:// or https://")
                return False
            
            if 'playlist' in url.lower() or 'list=' in url:
                print("[*] Detected playlist, downloading all videos...")
                return self.download_playlist(url)
            else:
                print("[*] Detected single video, downloading...")
                return self.download_video(url)
                
        except Exception as e:
            print(f"[*] Error processing URL: {e}")
            return False

def main():
    try:
        parser = argparse.ArgumentParser(description='Universal Video Downloader - HIGHEST QUALITY WITH AUDIO')
        parser.add_argument('url', nargs='?', help='Video URL (YouTube, Facebook, TikTok, Instagram, etc.)')
        parser.add_argument('--file', '-f', help='Text file containing multiple video URLs')
        parser.add_argument('--playlist', '-p', action='store_true', help='Force treat as playlist')
        
        args = parser.parse_args()
        
        downloader = UniversalVideoDownloader()
        
        if args.file:
            try:
                if not os.path.exists(args.file):
                    print(f"[!] File not found: {args.file}")
                    return
                
                with open(args.file, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
                if not urls:
                    print("[!] No URLs found in the file")
                    return
                
                print(f"[*] Found {len(urls)} URLs in file")
                success_count = 0
                
                for i, url in enumerate(urls, 1):
                    print(f"\n{'='*60}")
                    print(f"[*] Processing URL {i}/{len(urls)}: {url}")
                    print(f"{'='*60}")
                    
                    if downloader.process_url(url):
                        success_count += 1
                    
                    if i < len(urls):
                        print(f"[*] Waiting 3 seconds before next download...")
                        time.sleep(3)
                
                print(f"\n[*] Completed: {success_count}/{len(urls)} downloads successful")
                    
            except FileNotFoundError:
                print(f"[!] File not found: {args.file}")
            except PermissionError:
                print(f"[!] Permission denied accessing file: {args.file}")
            except UnicodeDecodeError:
                print(f"[!] File encoding error. Please use UTF-8 encoding: {args.file}")
            except Exception as e:
                print(f"[!] Error processing file: {e}")
        
        elif args.url:
            if args.playlist:
                downloader.download_playlist(args.url)
            else:
                downloader.process_url(args.url)
        
        else:
            downloader.show_header()
            
            while True:
                try:
                    url = input("\n[*] Enter Video URL: ").strip()
                    
                    if url.lower() in ['exit', 'quit', 'q']:
                        print("[*] Goodbye!")
                        break
                    
                    if url.lower() in ['clear', 'cls']:
                        downloader.clear_screen()
                        continue
                    
                    if not url:
                        continue
                    
                    downloader.process_url(url)
                    
                except KeyboardInterrupt:
                    print("\n[*] Exiting...")
                    break
                except EOFError:
                    print("\n[*] Exiting...")
                    break
                except Exception as e:
                    print(f"[!] Error: {e}")
    
    except KeyboardInterrupt:
        print("\n[*] Program interrupted by user")
    except Exception as e:
        print(f"[!] Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()