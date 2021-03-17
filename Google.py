import os
import pickle
import datetime
import google.auth.transport.requests
import requests
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

def CreateRequest(clientSecretFile, apiName, apiVersion, *scopes):
    CLIENT_SECRET_FILE = clientSecretFile
    API_SERVICE_NAME = apiName
    API_VERSION = apiVersion
    SCOPES = [scope for scope in scopes[0]]
    # print(CLIENT_SECRET_FILE, API_SERVICE_NAME, API_VERSION, SCOPES, sep = ' | ')
    # print(SCOPES)

    pickleFile = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'
    print(pickleFile)

    cred = None
    request = google.auth.transport.requests.Request()
    print(request)

    if os.path.exists(pickleFile):
        with open(pickleFile, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(request)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickleFile, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials = cred)
        print(API_SERVICE_NAME, 'Service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None

# def convertToRFCDatetime(year = 1900, month = 1, day = 1, hour = 0, minute = 0):
#     dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
#     return dt