import os

def install_all_requirements():

    try: import youtubesearchpython
    except ImportError as error:
        os.system('pip install youtube-search-python')
        
    try: import pytube
    except ImportError as error:
        os.system('pip install pytube')

    try: import PySimpleGUI
    except ImportError as error:
        os.system('pip install PySimpleGUI')
        
    try: import PIL
    except ImportError as error:
        os.system('pip install pillow')
    #os.system("pip install -r ./requirements.txt")