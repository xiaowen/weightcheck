# Some pre-reqs:
# pip install --user --upgrade google-api-python-client httplib2 oauth2client
# Go to https://console.developers.google.com/apis/credentials and download client_secret.json

# References:
# https://developers.google.com/api-client-library/python/start/get_started#installed
# https://stackoverflow.com/questions/53328101/python-google-photos-api-list-items-in-album

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file as ocfile, client, tools
import os
from pdb import set_trace as st
import urllib

# Get credentials
SCOPES = 'https://www.googleapis.com/auth/photoslibrary.readonly'
store = ocfile.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store, tools.argparser.parse_args(['--noauth_local_webserver']))

service = build('photoslibrary', 'v1', http=creds.authorize(Http()))

# Get metadata for all images
pageToken = ''
images = []
while True:
    results = service.mediaItems().search(body={
        'pageSize': 100,
        'pageToken': pageToken,
        'filters': { 'mediaTypeFilter': { 'mediaTypes': [ "PHOTO" ] } }
    }).execute()

    items = results['mediaItems']
    for item in items:
        # If you only want images with a keyword in the description, check item.get('description')
        if u'image/jpeg' == item['mimeType']:
            mmeta = item['mediaMetadata']
            images.append({
                'pid': item['id'],
                'ctime': mmeta['creationTime'],
                'baseUrl': item['baseUrl'],
                'height': int(mmeta['height']),
                'width': int(mmeta['width']),
            })

    pageToken = results['nextPageToken']
    if not pageToken or items[-1]['mediaMetadata']['creationTime'][:7] < '2019-02':
        break

# Download the images
imgdir = 'images'
if not os.path.exists(imgdir):
    os.makedirs(imgdir)

for img in images:
    imgpath = '%s/%s.jpg' % (imgdir, img['ctime'])
    print(img['ctime'])
    if not os.path.exists(imgpath):
        urllib.urlretrieve('%s=w%s-h%s' % (img['baseUrl'], img['width'], img['height']), imgpath)
