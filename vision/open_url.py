# open_url.py
import webbrowser
import sys

# URL to open is passed as a command line argument
url = sys.argv[1]
webbrowser.open_new_tab(url)