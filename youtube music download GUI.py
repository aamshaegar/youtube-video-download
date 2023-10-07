from pytube.exceptions import RegexMatchError
from multiprocessing import Queue
from lib.interface_lib import *
import PySimpleGUI as sg
import urllib.request
from PIL import Image
import threading
import io


__name__ = "__MAIN__"

def main():
    
    notify_queue = Queue()
    notify_queue2 = Queue()
    search_text = ""
    videos_list = []
    get_video_value = []
    actual_image = ""
    rename_text = ""
    number_bar = 0


    file_list_column = [

        [sg.Text("Type here!"),
            sg.In(size=(40, 1), enable_events=True, key="FIND_TEXT"),
            sg.Button("Find", size=(5, 1), enable_events=True, key="FIND_BUTTON")],

        [sg.Listbox(values=[], enable_events=True, size=(50, 20),  font=(
            'Calibri Bold', 12), expand_y=True, horizontal_scroll=True,  key="FILE_LIST")],

    ]

    image_viewer_column = [

        [sg.Multiline("Type a content (press Enter), then select a music to download.", size=(42, 22), disabled=True,  font=('Calibri Bold', 12), enable_events=True, key="TEXT_RIGHT")],
        [sg.Button("Download audio", size=(20, 1), enable_events=True, key="DOWNLOAD_AUDIO"),
            sg.Button("Download video", size=(20, 1), enable_events=True, key="DOWNLOAD_VIDEO")]

    ]

    image_menu = [
        
        [sg.Text(text="All images shown are saved under the './temp' directory and deleted automatically after 30 requests", key="TEXT", size=(38, 4), justification="center", font=('Calibri Bold', 12))],
        [sg.Image(source=actual_image, enable_events=True, key="IMAGE",size=(38, 50))],
        [sg.Text("Would you like to store the .mp3 file on the server?", justification="center", visible=False, size=(38, 2))],
        
        [sg.Text("Rename file?", size=(10,1)),
            sg.In(size=(26, 1), enable_events=True, key="RENAME_TEXT", font=('Calibri Bold', 12))],
        
        [sg.Radio('Download Video 360p', 1, default=True, enable_events=True, key="RADIO1"),
        sg.Radio('Download Video 720p', 1, enable_events=True, key="RADIO2"),],
        #,[sg.ProgressBar(100, orientation='h', size=(26, 1), border_width=4, key='progbar',bar_color=['Green','Blue'])],
        [sg.Multiline("", size=(36, 4), text_color="Azure", background_color="Black", disabled=True,  font=('Calibri Bold', 12), enable_events=True, key="LOG")]
    ]

    # ----- Full layout -----

    layout = [

        [sg.Column(file_list_column),
            sg.VSeperator(),
            sg.Column(image_viewer_column, key="COLUMN1"),
            sg.VSeperator(),
            sg.Column(image_menu, visible=False, key= "COLUMN")]
    ]


    check_temp_size()
    window = sg.Window(title="Youtube music download!", layout=layout, finalize=True)
    window['FIND_TEXT'].bind("<Return>", "_Enter")


    while True:
        event, values = window.read(timeout=2000)      
    
    
        if not notify_queue2.empty():
            val = notify_queue2.get_nowait()
            if val is not None: 
                window['LOG'].update(val[:36] + '\n', append=True)


        if not notify_queue.empty():
            val = notify_queue.get_nowait()
            if val is not None: 
                sg.popup_notify(val + " has been successfully downloaded!")
       
        
        if event == "Exit" or event == sg.WIN_CLOSED:
            os._exit(0)

        elif (event == "FIND_TEXT"):
            search_text = values['FIND_TEXT']

        elif (event == "FIND_BUTTON") or (event == "FIND_TEXT" + "_Enter"):
            if search_text == "":
                window['TEXT_RIGHT'].update("TYPE A CONTENT, FIRST!")
                
            else:
                try:
                    videos_list = three_params(search_text, 20, "audio")
                except Exception:
                    sg.popup("No connection. Please, connect to internet!\nRetry?", title="Info", button_type=sg.POPUP_BUTTONS_OK)
                lista = [el['title'] for el in videos_list]
                window['FILE_LIST'].update(lista)

        elif event == "FILE_LIST":
            if len(values['FILE_LIST']) > 0:
                get_value = values['FILE_LIST'][0]
                for el in videos_list:
                    if el['title'] == get_value:
                        get_video_value = el


                text = "Title: " + get_video_value['title'] + "\n" + "Link: " + \
                    get_video_value['link'] + "\n" + \
                    "Duration: " + get_video_value['duration'] + "\n" + \
                    "Total Views: " + get_video_value['total_views'] + "\n" + \
                    "Published time: " + get_video_value['publishedTime'] + "\n" + \
                    "Published by: " + get_video_value['publishedBy'] + "\n\n" + \
                    "Description: " + get_video_value['description'] + "\n\n" + \
                    "Image Link: " + get_video_value['image_url'] 

                if get_video_value['image_url'] != "NONE": 
                    actual_image = "./temp/" + get_video_value['title'][:10] + "_" + get_video_value['total_views'] + '.png'
                    if os.path.exists(actual_image):
                        window["IMAGE"].update(actual_image)
                    else:    
                        try:
                            with urllib.request.urlopen(get_video_value['image_url']) as url:
                                f = io.BytesIO(url.read())
                            img = Image.open(f)
                            img = img.resize((300,200))
                            img.save(actual_image)
                            window["IMAGE"].update(actual_image)
                        except Exception as e:
                            print(e)
                            sg.popup_notify("No image downlodable! :( ")

                window['COLUMN'].update(visible = True)                
                window['TEXT_RIGHT'].update(text)
            else:
                window['TEXT_RIGHT'].update("TYPE A CONTENT, FIRST!")
        
        elif event == "RENAME_TEXT":
            rename_text = values['RENAME_TEXT']  





        elif event == "DOWNLOAD_AUDIO":
            if get_video_value == []:
                window['TEXT_RIGHT'].update("TYPE A CONTENT, FIRST!")
            else:
                popup_wait()
                try:
                    number_bar += 1
                    if rename_text != "": t = threading.Thread(target=download_thread, args = (number_bar,notify_queue, notify_queue2, get_video_value, "audio", values['RADIO1'], rename_text))
                    else: t = threading.Thread(target=download_thread, args = (number_bar,notify_queue, notify_queue2, get_video_value, "audio", values['RADIO1'], None))
                    t.start()             
             
                
                except RegexMatchError as reg:
                    regex_error()   
                    
                except Exception as e:
                    print(e)
                    print()
                    sg.popup_error("This content cannot be downloaded!... :( ")             
                    
                    

        elif event == "DOWNLOAD_VIDEO":
            if get_video_value == []:
                window['TEXT_RIGHT'].update("TYPE A CONTENT, FIRST!")
            else:
                
                popup_wait()
                try:
                    number_bar += 1
                    resolution = values['RADIO1']
                    if rename_text != "": t = threading.Thread(target=download_thread, args = (number_bar,notify_queue, notify_queue2, get_video_value, "video", resolution, rename_text))
                    else: t = threading.Thread(target=download_thread, args = (number_bar,notify_queue, notify_queue2,  get_video_value, "video", resolution ,None))
                    t.start()
            
            
                except RegexMatchError as reg:
                    regex_error()   
                    
                except Exception as e:
                    print(e)
                    print()
                    sg.popup_error("This content cannot be downloaded!... :( ")


main()