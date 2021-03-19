# LWCYouTubeUploader
A command-line application that works specifically for **Living Word Church** (located in Union, NJ).

### Disclamer!
**Before running this application the user must run the following in their terminal:**
```
pip install -r requirements.txt
```
**The user will also be prompted to authenticate their Google account to the application.**

## How It Works:
This is a fairly simple application that uses the **YouTube Data API v3** to upload any video.
This application does the following:
* Titles the video
* Adds a description
* Adds the video to a user-specified playlist
* Sets the privacy status (unlisted, public, or private)
* Alerts subscribers of the video

When the user runs the application, they will be prompted with the following question:
```
For this script to properly upload videos, please make sure the '/Upload' folder contains only one video file (.mp4) and one thumbnail file (.jpg).
```

This prompt is in place because the application only uploads a single video at a time. This will ensure that the correct video is uploaded along with the correct thumbnail image.

The user is also prompted with a question about which playlist the video will be uploaded to:
```
Enter which playlist to upload to (e.g. Sermons, Worship, or leave blank for none):
```

Currently there are three options: _Sermons_, _Worship_, and _no playlist (i.e. no response)_. The chosen playlist determines how the video will be titled and how the description box will be filled out.

## WIP:
There are some additional changes I want to make to this project which I have listed below (as of March 17th, 2021):
- [ ] Create a UI
- [ ] Allow for multiple videos to be uploaded