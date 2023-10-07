from lib.youtube_lib import *
import PySimpleGUI as sg
import os.path



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
    - ERROR_TYPE: RegexMatchError: __init__: could not find match for ^\w+\W
    
    To solve this issue, check on https://github.com/pytube/pytube/issues/1326 
    Or follow these istructions:
    
    1) go on .../pytube/cipher.py
    2) go on line 30
    3) replace 'var_regex = re.compile(r"^\w+\W")' with var_regex = re.compile(r"^\$*\w+\W")
    4) save...
    
    """.strip()              
    popup(message, title='Library Not Up to Date', text_color='white', background_color='green')
 



def three_params(video_name, limit, file_type):
    """ Three params Select! """

    video = find_videos_per_name(video_name, limit)
    videos_list = list_of_all_content_found(video)
    return videos_list


def check_temp_size():
    """ Check temp size """
    
    dir_list = os.listdir("./temp")
    if len(dir_list) >= 30:    
        for file in dir_list:
            os.remove("./temp/" + file)


def download_thread(number, notify_queue, notify_queue2, link, type, low_resolution, rename_text):
    """Download content in a separate thread"""

    new_text = str(number)  + ") Downloading " + link['title'] + "..."
    notify_queue2.put(new_text)
    print("starting downloading", link['title'])
    if type == "audio": select_download_format_type(link['link'], type, rename=rename_text)
    else: select_download_format_type(link['link'], type, low_resolution=low_resolution, rename=rename_text)
    notify_queue.put(str(number)  + ") " + link['title'])
    