import os
os.environ["REPLICATE_API_TOKEN"] = "r8_O5TeEzAygKdZEBEGF3RwLX9Be8xub3z4GnKXo"

import replicate
import requests

video = r"D:\hoctap\Python\video-restoration\resources\input\vid1.mp4"
result = r"D:\hoctap\Python\video-restoration\resources\output\vid1.mp4"

def enhanceVideo(input_path, output_path):
    api = replicate.Client(api_token='r8_O5TeEzAygKdZEBEGF3RwLX9Be8xub3z4GnKXo')
    
    output_url = replicate.run(
        "lucataco/real-esrgan-video:c23768236472c41b7a121ee735c8073e29080c01b32907740cfada61bff75320",
        input={"video_path": open(input_path, "rb")}
    )
    
    response = requests.get(output_url)
    
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print("Download Video Success")
    else:
        print("Download Failed")
    
    return output_path
