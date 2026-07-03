import cv2
import numpy as np
import matplotlib.pyplot as plt
import urllib.request
import os

# Create a simple script to save the traffic image
def main():
    # URL for a sample traffic image (similar to the one in the conversation)
    url = "https://media.istockphoto.com/id/1295254559/photo/traffic-jam-in-bangkok-city-thailand.jpg?s=612x612&w=0&k=20&c=ybE_rAjqV8-e-V76a8WYYiKJlKlKZQoRxVA_dwKlGJY="
    
    try:
        # Download the image
        print(f"Downloading traffic image...")
        urllib.request.urlretrieve(url, "real_traffic.jpg")
        print(f"Image saved as real_traffic.jpg")
        
        # Verify the image was saved
        if os.path.exists("real_traffic.jpg"):
            img = cv2.imread("real_traffic.jpg")
            if img is not None:
                print(f"Image loaded successfully. Size: {img.shape}")
                return True
            else:
                print("Failed to load the saved image")
        else:
            print("Image file not found")
    except Exception as e:
        print(f"Error downloading image: {e}")
    
    return False

if __name__ == "__main__":
    main()