from lib.install_lib import install_all_requirements
install_all_requirements()


from lib.interface_lib import *
from pytube.exceptions import RegexMatchError
from pytube.exceptions import AgeRestrictedError
from multiprocessing import Queue
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
    old_serach_text = ""
    videos_list = []
    get_video_value = []
    actual_image = ""
    rename_text = ""
    number_bar = 0
    search = None
    output_folder = "default"


    file_list_column = [

        [sg.Text("Type here!"),
            sg.In(size=(40, 1), enable_events=True, key="FIND_TEXT"),
            sg.Button("Find", size=(5, 1), enable_events=True, key="FIND_BUTTON")],

        [sg.Listbox(values=[], enable_events=True, size=(41, 19),  font=(
            'Calibri Bold', 12), expand_y=True, horizontal_scroll=True,  key="FILE_LIST")],


        [sg.Button("Next page", size=(15, 1), enable_events=True, key="NEXT_BUTTON", visible=False)]
        #sg.Button("Previous page", size=(10, 1), enable_events=True, key="PREVIOUS_BUTTON", visible=False), 

    ]

    image_viewer_column = [

        [sg.Multiline("Type a content (press Enter), then select a music to download.", size=(40, 22), disabled=True,  font=('Calibri Bold', 12), enable_events=True, key="TEXT_RIGHT")],
        [sg.Button("Download audio", size=(20, 1), enable_events=True, key="DOWNLOAD_AUDIO"),
            sg.Button("Download video", size=(20, 1), enable_events=True, key="DOWNLOAD_VIDEO")]

    ]

    image_menu = [
        
        [sg.Text(text="All images shown are saved under the './temp' directory and deleted automatically after 30 requests", key="TEXT", size=(38, 4), justification="center", font=('Calibri Bold', 12))],
        [sg.Image(source=actual_image, enable_events=True, key="IMAGE",size=(38, 50))],
        [sg.Text("Would you like to store the .mp3 file on the server?", justification="center", visible=False, size=(38, 2))],
        
        [sg.T("")],
        [sg.Text("Rename file?", size=(12,1)), sg.In(size=(27, 1), enable_events=True, key="RENAME_TEXT", font=('Calibri Bold', 12))],


        [sg.Text("Output folder?", size=(12,1)), sg.In("default", key="INPUT_BROWSE", size=(23,1),font=('Calibri Bold', 10)), sg.FolderBrowse(key="BROWSE")],
        
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
    window = sg.Window(title="Youtube music download!", layout=layout, finalize=True, resizable=True)
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
            old_serach_text = search_text

        elif (event == "FIND_BUTTON") or (event == "FIND_TEXT" + "_Enter"):
            if search_text == "":
                window['TEXT_RIGHT'].update("TYPE A CONTENT, FIRST!")
        
            else:
                try:
                    videos_list, s = three_params(search_text, 19, videoSearch=None)
                    search = s
                    #window['PREVIOUS_BUTTON'].update(visible = True)
                    window['NEXT_BUTTON'].update(visible = True)
                    
                    
                except Exception as e:
                    import traceback
                    traceback.print_exc() 
                    print(e)
                    sg.popup("No connection. Please, connect to internet!\nRetry?", title="Info", button_type=sg.POPUP_BUTTONS_OK)
                lista = [el['title'] for el in videos_list]
                window['FILE_LIST'].update(lista)

        
        elif event == "NEXT_BUTTON":
            if search_text != "":
                try:
                    videos_list, s = three_params(search_text, 19, videoSearch=search)
                    
                except Exception as e:
                    import traceback
                    traceback.print_exc() 
                    print(e)
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
                number_bar += 1
                
                if not os.path.exists(values['INPUT_BROWSE']): output_folder = "default"
                else: output_folder = values['INPUT_BROWSE']
                if rename_text != "": t = threading.Thread(target=download_thread, args = (sg, number_bar,notify_queue, notify_queue2, get_video_value, "audio", values['RADIO1'], rename_text, output_folder))
                else: t = threading.Thread(target=download_thread, args = (sg, number_bar,notify_queue, notify_queue2, get_video_value, "audio", values['RADIO1'], None, output_folder))
                t.start()                    
                    

        elif event == "DOWNLOAD_VIDEO":
            if get_video_value == []:
                window['TEXT_RIGHT'].update("TYPE A CONTENT, FIRST!")
            else:
                
                popup_wait()            
                number_bar += 1
                
                if not os.path.exists(values['INPUT_BROWSE']): output_folder = "default"
                else: output_folder = values['INPUT_BROWSE']
                resolution = values['RADIO1']
                if rename_text != "": t = threading.Thread(target=download_thread, args = (sg, number_bar,notify_queue, notify_queue2, get_video_value, "video", resolution, rename_text, output_folder))
                else: t = threading.Thread(target=download_thread, args = (sg, number_bar,notify_queue, notify_queue2,  get_video_value, "video", resolution ,None, output_folder))
                t.start()

main()