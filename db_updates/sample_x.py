# tweet_sample.py
import os
import sys
import tweepy

# Add parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Load the X (Twitter) credentials
from python_api.get_secrets import (
    x_app_api_key,
    x_app_api_key_secret,
    x_app_access_token,
    x_app_access_token_secret
)

# Path to generated_cards folder
GC_DIR = os.path.join(parent_dir, "generated_cards")
IMAGE_PATH = os.path.join(GC_DIR, "sample.jpg")

import tweepy

def create_media_api():
    # OAuth1 handler for media upload
    auth = tweepy.OAuth1UserHandler(
        x_app_api_key,
        x_app_api_key_secret,
        x_app_access_token,
        x_app_access_token_secret
    )
    return tweepy.API(auth)

def create_v2_client():
    # OAuth1 user context for v2 tweeting
    return tweepy.Client(
        consumer_key=x_app_api_key,
        consumer_secret=x_app_api_key_secret,
        access_token=x_app_access_token,
        access_token_secret=x_app_access_token_secret
    )



def post_tweet_with_image(image_path, tweet_text):

    # 1. Upload media using v1.1 (allowed)
    media_api = create_media_api()
    media = media_api.media_upload(image_path)
    media_id = media.media_id_string

    # 2. Post tweet using v2
    client = create_v2_client()

    client.create_tweet(
        text=tweet_text,
        media_ids=[media_id]
    )

    print("Tweet posted successfully.")



if __name__ == "__main__":
    tweet_message = (
        "Data-led. No noise. Telegram Link in Bio.\n\n"
        "Full stat pack 👇"
    )

    print(f"Using image: {IMAGE_PATH}")
    post_tweet_with_image(IMAGE_PATH, tweet_message)


# # tweet_text_only.py
# import os
# import sys
# import tweepy

# # Add parent dir so python_api works
# parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(parent_dir)

# # Load Twitter/X credentials from your secrets module
# from python_api.get_secrets import (
#     x_app_api_key,
#     x_app_api_key_secret,
#     x_app_access_token,
#     x_app_access_token_secret,
#     x_app_bearer_token
# )


# import requests
# import json

# url = "https://api.x.com/2/tweets"

# headers = {
#     "Authorization": f"Bearer {x_app_bearer_token}",   # <-- MUST BE USER TOKEN WITH WRITE ACCESS
#     "Content-Type": "application/json"
# }

# payload = {
#     "text": "Testing API v2 tweet from DataPitch."
# }

# response = requests.post(url, json=payload, headers=headers)

# print("Status:", response.status_code)
# print(response.json())
