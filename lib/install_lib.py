import os

def install_all_requirements():

    try: import pipreqs
    except ImportError as error:
        os.system('pip install pipreqs')

    os.system("pip install -r ./requirements.txt")

