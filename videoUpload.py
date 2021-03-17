import os
import pickle

import google.auth.transport.requests
import requests
import google_auth_oauthlib.flow
# import googleapiclient.discovery
import googleapiclient.errors
# from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def CreateRequest(clientSecretFile, apiName, apiVersion, *scopes):
    client_secrets_file = clientSecretFile
    api_service_name = apiName
    api_version = apiVersion
    scopes = [scope for scope in scopes[0]]
    # print(CLIENT_SECRET_FILE, API_SERVICE_NAME, API_VERSION, SCOPES, sep = ' | ')
    # print(scopes)

    pickleFile = f'token_{api_service_name}_{api_version}.pickle'
    # print(pickleFile)

    credentials = None
    request = google.auth.transport.requests.Request()
    # print(request)

    if os.path.exists(pickleFile):
        with open(pickleFile, 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(request)
        else:
            # flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            credentials = flow.run_local_server()

        with open(pickleFile, 'wb') as token:
            pickle.dump(credentials, token)

    try:
        youtube = build(api_service_name, api_version, credentials = credentials)
        # print('Video successfully uploaded to YouTube!')
        print("Uploading video to YouTube...")
        return youtube
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Confirms with the user if the directory is holding the proper files.
    print("For this script to properly upload videos, please make sure the '/Upload' folder contains only one video file (.mp4) and one thumbnail file (.jpg).")
    answer = input("Would you like to continue (Y/N)? ")
    if answer.lower().startswith("n"):
        exit()

    # YouTube Data V3 API variables.
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"
    scopes = [
                "https://www.googleapis.com/auth/youtube.upload", 
                "https://www.googleapis.com/auth/youtube.force-ssl"
    ]
    
    # Pulls the files from the directory for upload.
    path = "/Users/thiago/Developer/Projects/youtube-uploader/Upload/"
    dir_files = os.scandir(path)
    video_file_extension = ".mp4"
    image_file_extension = ".jpg"
    for entry in dir_files:
        if entry.is_file():
            if video_file_extension in entry.name:
                media_file = entry.name
            if image_file_extension in entry.name:
                thumbnail_file = entry.name
    dir_files.close()

    # Based on the playlist, choose how to title the video & which description to add.
    playlist = input("Enter which playlist to upload to (e.g. Sermons, Worship, or leave blank for none):\n")
    
    # Determine title, which description file to read from, and the ID of the playlist.
    if playlist.lower().startswith("w"):
        title = media_file[:len(media_file) - 4] + " | Living Word Worship"
        description_doc = open(path + "worship.txt", "r+")
        playlist_id = "PLY1fHcEkLB4Z1CE4_7EfH20_fvj64qdkM"
    elif playlist.lower().startswith("s"):
        sermon_speaker = input("Please list the speaker(s) of this sermon:\n")
        title = media_file[:len(media_file) - 4] + " | Sunday Service - " + sermon_speaker
        description_doc = open(path + "sermon.txt", "r+")
        playlist_id = "PLY1fHcEkLB4Y1WnyNOec4QyUfIyR13jb7"
    else:
        title = media_file[:len(media_file) - 4]
        description_doc = open(path + "sermon.txt", "r+")
        playlist_id = None

    # Add description file to variable and close.
    description = description_doc.read()
    description_doc.close()

    # print(title)
    # print(description)

    # Get credentials and create an API client
    request = CreateRequest(client_secrets_file, api_service_name, api_version, scopes)

    videos_response = request.videos().insert(
        part = "snippet, status",
        notifySubscribers = False,
        body = {
            "snippet": {
                "categoryId": "29",
                "title": title,
                "description": description,
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        },
        # Pointer to the media file being uploaded.
        media_body = MediaFileUpload(path + media_file)
    ).execute()
    print("The video has been uploaded successfully!")

    request.thumbnails().set(
        videoId = videos_response.get('id'),
        media_body = MediaFileUpload(path + thumbnail_file)
    ).execute()

    if playlist_id is not None:
        playlists_response = request.playlistItems().insert(
            part = "snippet,contentDetails",
            body = {
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": videos_response.get('id')
                    }
                }
            }
        ).execute()
        print("Video has been added to the '%s' playlist." % (playlist.title()))

if __name__ == "__main__":
  main()