from lib.youtube_lib import *
import PySimpleGUI as sg
import subprocess
import os.path
from pytube.exceptions import RegexMatchError
# from pytube.exceptions import AgeRestrictedError




def popup(text, title='Message', modal=True, text_color=None, background_color=None,font=('Courier New', 12)):
    
    lines = text.split('\n')
    width = max(map(len, lines))
    height = len(lines)
    layout = [
        [sg.Image(data=sg.EMOJI_BASE64_WEARY, background_color=background_color),
         sg.Multiline(text, size=(width, height), no_scrollbar=True, disabled=True,
            text_color=text_color, background_color=background_color, expand_x=True,
            font=font, border_width=0)],
        [sg.Push(background_color=background_color), sg.Button('OK')],
    ]
    sg.Window(title, layout, background_color=background_color, modal=modal).read(close=True)


def popup_wait():
    message = "\n\n ..... Downloading content!  PLEASE WAITING ..... \n\n"
    sg.popup_quick_message(message, 
                            auto_close_duration=1, 
                            text_color='white', 
                            background_color='black',
                            keep_on_top=True, 
                            line_width=50,
                            non_blocking=True)

def regex_error():
    
    message = """
            
    ERROR: There are some library not up to date!!!
    
    - ERROR ON : C:..../Programs/Python/Python310/Lib/site-packages/pytube/cipher.py 
    - ON LINUX: /home/USER/.local/lib/python3.10/site-packages/pytube/cipher.py
    - ERROR_TYPE: RegexMatchError: __init__: could not find match for ^\w+\W
    
    To solve this issue, check on https://github.com/pytube/pytube/issues/1326 
    Or follow these istructions:
    
    1) go on .../pytube/cipher.py
    2) go on line 30
    3) replace 'var_regex = re.compile(r"^\w+\W")' with var_regex = re.compile(r"^\$*\w+\W")
    4) save...
    
    """.strip()              
    popup(message, title='Library Not Up to Date', text_color='white', background_color='green')




def yt_error():
    
    message = """
            
    ERROR: There are some library not installed!!!
    
    Please install yt-dlp.
    Visit https://github.com/yt-dlp/yt-dlp for major detail.
    
    """.strip()              
    popup(message, title='Library Not Up to Date', text_color='white', background_color='green')





def three_params(video_name, limit, videoSearch = None):
    """ Three params Select! """

    if not videoSearch:
        video, search = find_videos_per_name(video_name, limit)
        videos_list = list_of_all_content_found(video)
        return videos_list, search
    else:
        videoSearch.next()
        json_result = videoSearch.result()
        video = json_result['result']
        videos_list = list_of_all_content_found(video)
        return videos_list, videoSearch
        


def check_temp_size():
    """ Check temp size """
    
    dir_list = os.listdir("./temp")
    if len(dir_list) >= 30:    
        for file in dir_list:
            os.remove("./temp/" + file)


def download_thread(sg, number, notify_queue, notify_queue2, link, type, low_resolution, rename_text, output="default"):
    """Download content in a separate thread"""

    try:
        new_text = str(number)  + ") Downloading " + link['title'] + "..."
        notify_queue2.put(new_text)
        print("starting downloading", link['title'])
        if type == "audio": select_download_format_type(link['link'], type, output = output, rename=rename_text)
        else: select_download_format_type(link['link'], type, low_resolution=low_resolution, output=output, rename=rename_text)
        notify_queue.put(str(number)  + ") " + link['title'])
    # except AgeRestrictedError as age:
    #     print(e)
    #     print()
    #     sg.popup_quick_message(" \n\n This content is age restricted, so cannot be downloaded!... :( \n\n ", text_color='red', auto_close=True, auto_close_duration=2, background_color='black') 

    except RegexMatchError as reg:
        regex_error()   
        
    except Exception as e:
        print(e)
        print()
        sg.popup_quick_message("\n\n This content cannot be downloaded!... :( \n\n", text_color='red', auto_close=True, auto_close_duration=2, background_color='black')
    



def check_yt_dlp_installed():
    """Check if yt-dlp is available"""
    try: 
        subprocess.run(["yt-dlp", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False




def download_audio_yt(sg, number, notify_queue, notify_queue2, link, download_type, low_resolution, rename_text, output="default"):
    """Download audio content from YouTube in a separate thread."""

    if not check_yt_dlp_installed():
        yt_error()
    else:
        try:
            new_text = f"{number}) Downloading {link['title']}..."
            notify_queue2.put(new_text)
            print("Starting download:", link['title'])
            resolution = "height:480" if low_resolution else "height:720"
            if rename_text: file_name = f"./audio_output/{rename_text}.mp3"
            else: file_name = f"./audio_output/{link['title']}.mp3"

            command = [
                "yt-dlp",
                "--preset-alias", "mp3",
                link['link'],
                "-S", resolution,
                "-o", file_name
            ]

            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                print("Download successful!")
                print(result.stdout)
                notify_queue.put(f"{number}) {link['title']} downloaded successfully.")
            else:
                print("Download failed!")
                print(result.stderr)

        except RegexMatchError:
            print("Regex match error occurred.")
            sg.popup_quick_message("\n\n This content cannot be downloaded due to a regex match error!... :( \n\n", 
                                text_color='red', auto_close=True, auto_close_duration=2, background_color='black')

        except Exception as e:
            print(f"An error occurred: {e}")
            sg.popup_quick_message("\n\n This content cannot be downloaded!... :( \n\n", 
                                text_color='red', auto_close=True, auto_close_duration=2, background_color='black')




def download_video_yt(sg, number, notify_queue, notify_queue2, link, download_type, low_resolution, rename_text, output="default"):
    """Download audio content from YouTube in a separate thread."""

    if not check_yt_dlp_installed():
        yt_error()
    else:
        try:
            new_text = f"{number}) Downloading {link['title']}..."
            notify_queue2.put(new_text)
            print("Starting download:", link['title'])
            resolution = "height:480" if low_resolution else "height:720"
            if rename_text: file_name = f"./video_output/{rename_text}.mp4"
            else: file_name = f"./video_output/{link['title']}.mp4"

            command = [
                "yt-dlp",
                "--preset-alias", "mp4",
                link['link'],
                "-S", resolution,
                "-o", file_name
            ]

            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                print("Download successful!")
                print(result.stdout)
                notify_queue.put(f"{number}) {link['title']} downloaded successfully.")
            else:
                print("Download failed!")
                print(result.stderr)

        except RegexMatchError:
            print("Regex match error occurred.")
            sg.popup_quick_message("\n\n This content cannot be downloaded due to a regex match error!... :( \n\n", 
                                text_color='red', auto_close=True, auto_close_duration=2, background_color='black')

        except Exception as e:
            print(f"An error occurred: {e}")
            sg.popup_quick_message("\n\n This content cannot be downloaded!... :( \n\n", 
                                text_color='red', auto_close=True, auto_close_duration=2, background_color='black')

