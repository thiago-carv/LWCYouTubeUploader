import os
import pickle

import google.auth.transport.requests
import requests
import google_auth_oauthlib.flow
import googleapiclient.errors
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def CreateRequest(clientSecretFile, apiName, apiVersion, *scopes):
    client_secrets_file = clientSecretFile
    api_service_name = apiName
    api_version = apiVersion
    scopes = [scope for scope in scopes[0]]

    pickleFile = f'token_{api_service_name}_{api_version}.pickle'

    credentials = None
    request = google.auth.transport.requests.Request()

    if os.path.exists(pickleFile):
        with open(pickleFile, 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(request)
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            credentials = flow.run_local_server()

        with open(pickleFile, 'wb') as token:
            pickle.dump(credentials, token)

    try:
        youtube = build(api_service_name, api_version, credentials = credentials)
        print("Uploading video to YouTube...")
        return youtube
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None

def CreateVideoData(path, playlistChoice, speaker):
    # Pulls the files
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

    # Creates title, description, and assigns playlistID
    if playlistChoice.lower().startswith("w"):
        title = media_file[:len(media_file) - 4] + " | Living Word Worship"
        description_doc = open(path + "worship.txt", "r+")
        playlist_id = "PLY1fHcEkLB4Z1CE4_7EfH20_fvj64qdkM"
    elif playlistChoice.lower().startswith("s"):
        title = media_file[:len(media_file) - 4] + " | Sunday Service - " + speaker
        description_doc = open(path + "sermon.txt", "r+")
        playlist_id = "PLY1fHcEkLB4Y1WnyNOec4QyUfIyR13jb7"
    else:
        title = media_file[:len(media_file) - 4]
        description_doc = open(path + "sermon.txt", "r+")
        playlist_id = None

    # Add description file to variable and close.
    description = description_doc.read()
    description_doc.close()

    return {
                "video": media_file,
                "thumbnail": thumbnail_file,
                "title": title, 
                "description": description + " #" + media_file[:len(media_file) - 4].replace(' ', ''), 
                "playlist": playlist_id
            }

def main():
    # YouTube Data API v3 Auth variables.
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"
    scopes = [
                "https://www.googleapis.com/auth/youtube.upload", 
                "https://www.googleapis.com/auth/youtube.force-ssl"
    ]

    while (True):
        # Confirms with the user if directory is holding proper files.
        print("For this script to properly upload videos, please make sure the '/Upload' folder contains only one video file (.mp4) and one thumbnail file (.jpg).")
        answer = input("Would you like to continue (Y/N)? ")
        if answer.lower().startswith("n"):
            exit()
        
        # Based on the playlist, choose how to title the video & which description to add.
        playlist = input("Enter which playlist to upload to (e.g. Sermons, Worship, or leave blank for none):\n")
        sermon_speaker = None
        if playlist.lower().startswith("s"):
            sermon_speaker = input("Please list the speaker(s) of this sermon:\n")

        # Pulls the files from the directory for upload.
        # Based on the playlist, choose how to title the video & which description to add.
        # Determine title, which description file to read from, and the ID of the playlist.
        path = "/Users/thiago/Developer/Projects/youtube-uploader/Upload/"
        video_data = CreateVideoData(path, playlist, sermon_speaker)

        # Get credentials and create an API client
        request = CreateRequest(client_secrets_file, api_service_name, api_version, scopes)

        videos_response = request.videos().insert(
            part = "snippet, status",
            notifySubscribers = False,
            body = {
                "snippet": {
                    "categoryId": "29",
                    "title": video_data["title"],
                    "description": video_data["description"],
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False
                }
            },
            # Pointer to the media file being uploaded.
            media_body = MediaFileUpload(path + video_data["video"])
        ).execute()
        print("The video has been uploaded successfully!")

        # Thumbnail to add to the video.
        request.thumbnails().set(
            videoId = videos_response.get('id'),
            media_body = MediaFileUpload(path + video_data["thumbnail"])
        ).execute()

        # Uploads video to selected playlist.
        if video_data["playlist"] is not None:
            playlists_response = request.playlistItems().insert(
                part = "snippet,contentDetails",
                body = {
                    "snippet": {
                        "playlistId": video_data["playlist"],
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": videos_response.get('id')
                        }
                    }
                }
            ).execute()
            print("Video has been added to the '%s' playlist." % (playlist.title()))

        # Gives user the option to restart the program.
        answer = input("Would you like to upload another video (Y/N)? ")
        if answer.lower().startswith("n"):
            exit()

if __name__ == "__main__":
  main()