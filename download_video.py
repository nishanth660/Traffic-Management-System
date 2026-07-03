import requests
import os
from urllib.parse import urlparse

def download_video(url, filename="real_traffic.mp4"):
    """Download video from URL"""
    try:
        print(f"Downloading video from {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Video downloaded successfully as {filename}")
        return True
    except Exception as e:
        print(f"Error downloading video: {e}")
        return False

if __name__ == "__main__":
    # Note: Direct download from Pexels may not work due to their terms of service
    # You may need to manually download the video and place it in the directory
    print("Please manually download the video from:")
    print("https://www.pexels.com/video/busy-urban-highway-traffic-flow-31115066/")
    print("Save it as 'real_traffic.mp4' in the current directory")
