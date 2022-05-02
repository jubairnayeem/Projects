import csv
import json
import requests

chanel_id = 'XXXXXXXXX'
channel_id2 = 'XXXXXXXXX'
youtube_api_key = 'XXXXXXXXX'

def make_csv(page_id):
    base = 'https://www.googleapis.com/youtube/v3/search?'
    fields = '&part=snippet&channelId='
    api_key = '&key=' + youtube_api_key
    api_url = base + fields + page_id + api_key
    api_response = requests.get(api_url)
    videos = json.loads(api_response.text)
    with open("%syoutube_videos.csv" % page_id, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['publishedAt',
                            'title',
                            'description',
                            'thumbnailurl'])
        has_another_page = True
        while has_another_page:
            if videos.get('items') is not None:
                for video in videos.get('items'):
                    video_data_row = [
                        video['snippet']['publishedAt'],
                        video['snippet']['title']#.encode('utf-8'),
                        video['snippet']['description']#.encode('utf-8'),
                        video['snippet']['thumbnails']['default']['url']#.encode('utf-8')
                        ]
                        csv_writer.writerow(video_data_row)
            if 'nextPageToken' in videos.keys():
                next_page_url = api_url + '&pageToken=' + videos['nextPageToken']
                next_page_posts = requests.get(next_page_posts.text)
            else:
                print('No More Videos!')
                has_another_page = False

make_csv(channel_id)
make_csv(channel_id2)

## https://github.com/lamthuyvo/social-media-data-scripts
