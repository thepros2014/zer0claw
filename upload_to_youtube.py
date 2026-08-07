import os
import sys
import argparse
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def upload_video(video_path, title, description, category_id="28", privacy_status="public"):
    print(f"=== ZeroClaw YouTube Uploader ===")
    print(f"Target Video: {video_path}")
    print(f"Title: {title}")
    
    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' not found!")
        sys.exit(1)
        
    client_secrets_file = "client_secrets.json"
    token_file = "youtube_token.json"
    
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
    if not creds or not creds.valid:
        if os.path.exists(client_secrets_file):
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        else:
            print("\n[NOTE] Google OAuth credentials ('client_secrets.json') not found in root directory.")
            print("To complete YouTube upload via API:")
            print("1. Download client_secrets.json from Google Cloud Console (YouTube Data API v3).")
            print("2. Run: python upload_to_youtube.py")
            print("\nAlternatively, upload 'docs/Zeroclaw_video_voiceover.mp4' directly via YouTube Studio (https://studio.youtube.com).")
            return

    youtube = build('youtube', 'v3', credentials=creds)
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['Solana', 'AI', 'ZeroClaw', 'WASM', 'Crypto', 'WhatsApp', 'Phantom'],
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )

    print("Uploading video to YouTube...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    print("\n✅ Upload Complete!")
    print(f"Video ID: {response.get('id')}")
    print(f"YouTube Link: https://youtu.be/{response.get('id')}")

if __name__ == "__main__":
    video_file = r"docs/Zeroclaw_video_voiceover.mp4"
    if not os.path.exists(video_file):
        video_file = r"docs/Zeroclaw_video_submission.mp4"
        
    title = "ZeroClaw Commerce — Fail-Closed Solana AI Cashier (Narrated Video Demo)"
    description = (
        "ZeroClaw Commerce: A Solana Payment Terminal for Family Shops 🇧🇷\n\n"
        "Demo video narrated by AI voiceover team.\n"
        "GitHub Repository: https://github.com/thepros2014/zer0claw\n\n"
        "Features:\n"
        "- Zero-key custody AI cashier for WhatsApp & Telegram\n"
        "- Native Solana Pay QR code generation & Phantom wallet scanning\n"
        "- Fail-closed Tier 3 WASM risk engine (wasm32-wasip2)\n"
        "- Multi-currency IRS Form 8849 & Receita Federal BRL tracking\n"
        "- Kraken AI autonomous margin trading integration"
    )
    
    upload_video(video_file, title, description)
