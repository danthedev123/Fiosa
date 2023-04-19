# Update checking program

import requests



def check_updates(curr_version):
    content = None

    url = "http://fiosaupdateserver.dtd-123.repl.co/"
    response = requests.get(url)

    if response.status_code == 200:
        content = response.content
        print(content)
    else:
        print("Error retrieving content from", url)

    if (not curr_version == content):
        return True # There are updates available
    else:
        return False # No updates = False
