from youtubesearchpython import VideosSearch
from pytube import YouTube
import datetime
import os


def get_content_size(url_video):
    """ Return all content informations"""

    try:
        youtube = YouTube(url_video)
    except ConnectionError:
        print("Error: No internet!")

    video_found = youtube.streams.filter(only_audio=True).first()
    actual_file_size = video_found.filesize
    return actual_file_size



def estimate_download_time(url_video):
    """ Try to estimate the download time of a specific content """
    
    global connection_speed
    size = get_content_size(url_video)
    return size, connection_speed, size / connection_speed
    



def download_audio(url_video, rename = None):
    """ Convert single video found in mp3 format.
    :param url_video: str """

    try:
        youtube = YouTube(url_video)
    except ConnectionError:
        print("Error: No internet!")

    video_found = youtube.streams.filter(only_audio=True).first()
    destination = "./audio_output"

    x = datetime.datetime.now()
    format = "_" + x.strftime("%H") + " " + x.strftime("%M") + " " + x.strftime("%S")
    
    out_file = video_found.download(destination)
    base, ext = os.path.splitext(out_file)
    if rename: new_file = "./audio_output/" + rename + format + ".mp3"
    else: new_file = base + format + '.mp3'
    
    print(new_file)
    os.rename(out_file, new_file)
    print(video_found.title + " has been successfully downloaded.")
    return new_file



def download_video(url_video, low_resolution, rename = None):
    """ Convert single video found in mp4 format.
    :param url_video: str """

    destination = "./video_output"
    try:
        youtube = YouTube(url_video)
    except ConnectionError:
        print("Error: No internet!")
    videos = youtube.streams.all()
    vid = list(enumerate(videos))
    
    video_selected = [(vid[i],i) for i in range(0,len(vid)) 
        if 'acodec=' in str(vid[i]) and 
        'mp4' in str(vid[i]) and 
        '3gpp' not in str(vid[i]) and 
        'mime_type="audio' not in str(vid[i])]
    
    # we are using enumerate to get the index number
    for video in video_selected: print(str(video[1]) + ")", video[0])
    
    if low_resolution: 
        selected = video_selected[0]
        plus_name = "(360p) "
    else: 
        selected = video_selected[-1]
        plus_name = "(720p) "
    
    #resolution = int(input("Enter the index number of the video : "))
    destination = "./video_output"
    out_file = selected[0][1].download(destination)
    
    x = datetime.datetime.now()
    format = "_" + x.strftime("%H") + " " + x.strftime("%M") + " " + x.strftime("%S")
    
    
    if rename: new_file = "./video_output/" + rename + format + ".mp4"
    else: new_file = out_file.split(".mp4")[0] + plus_name + format + ".mp4"
        
    os.rename(out_file, new_file)
    print('your video is downloaded successfully')




def select_download_format_type(url_video, file_type, low_resolution=False, rename = None):
    """ Select what format do you like! """
    
    #rename = input("If you want, type a new name for the file, otherwise blank\n")
    #if rename == "": rename = None 

    file_path = ""
    if file_type == 'audio': 
        file_path = download_audio(url_video, rename)
        
        #response = input("\nWould you like to store music on server? (Y/N)")
        #if(response.lower() in ['y', 'yes']):
        #    store_music(file_path)
        #else:
        #    print("Session closed!")
            
    else: 
        file_path = download_video(url_video, low_resolution, rename)

    return file_path
    



def find_videos_per_name(video_search_name, limit_search):
    """ find a set of limit_search max video from youtube. 
    The search is based on Youtube queries, so could change 
    every time is called
    :param video_search_name: str 
    :param limit_search: number 
    :return: array of video """

    videosSearch = VideosSearch(video_search_name, limit = limit_search)
    json_result = videosSearch.result()
    return json_result['result']



def list_of_all_content_found(json_result_list):
    """ List all video info found """

    list_returned = []
    for video in json_result_list:

        single_video = {}
        single_video['title'] = video['title'] if video['title'] else "NONE"
        single_video['link'] = video['link'] if video['link'] else "NONE"
        single_video['duration'] = video['duration'] if video['duration'] else "NONE"
        single_video['total_views'] = video['viewCount']['short'] if video['viewCount'] else "NONE"
        single_video['publishedTime'] = video['publishedTime'] if video['publishedTime'] else "NONE"
        single_video['publishedBy'] = video['channel']['name'] if video['channel'] else "NONE"
        single_video['image_url'] = video['thumbnails'][0]['url'] if video['thumbnails'] else "NONE"
        single_video['description'] = video['descriptionSnippet'][0]['text'] if video['descriptionSnippet'] else "NONE"
        
        list_returned.append(single_video)
        
    return list_returned


