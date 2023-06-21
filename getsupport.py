import ctypes
import zipfile
from time import sleep
import sys
from tqdm import tqdm
import os
import urllib.request
import subprocess
import requests

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

url = "https://github.com/rustdesk/rustdesk/releases/download/1.1.9/rustdesk-1.1.9-windows_x64.zip"
destination_file = "rustdesk.zip"
extract_folder = "rustdesk"
config_path = os.path.join(os.getenv('APPDATA'), 'RustDesk', 'config', 'RustDesk.toml')

if not is_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            " ".join(sys.argv),
            None,
            1
        )
        pass
    except:
        print("Krever administrator rettigheter")
        sys.exit()

def progress_hook(count, block_size, total_size):
    progress_bar_download.update(block_size)

file_size = int(urllib.request.urlopen(url).headers['Content-Length'])
progress_bar_download = tqdm(total=file_size, unit='B', unit_scale=True, desc="Laster ned fil")
urllib.request.urlretrieve(url, destination_file, reporthook=progress_hook)
progress_bar_download.close()
zip_file_size = os.path.getsize(destination_file)
progress_bar_unzip = tqdm(total=zip_file_size, unit='B', unit_scale=True, desc="Pakker ut fil")

with zipfile.ZipFile(destination_file, 'r') as zip_ref:
    for file in zip_ref.namelist():
        zip_ref.extract(file, extract_folder)
progress_bar_unzip.close()

exe_files = [file for file in os.listdir(extract_folder) if file.endswith(".exe")]
if exe_files:
    installer_path = os.path.join(extract_folder, exe_files[0])

# Launch RustDesk client in a separate process
subprocess.Popen(installer_path)

input("Trykk ENTER her ETTER du har fullført installasjonen av programmet")

# Rest of the script
if os.path.exists(config_path):
    with open(config_path, "r") as file:
        lines = [file.readline().strip() for _ in range(2)]

        if len(lines) >= 2:
            id = lines[0].split("=")[-1].strip()
            password = lines[1].split("=")[-1].strip()

text = 'ID:' +  str(id) + " | " + "Password: " + password

mailurl = "https://send-mail-serverless.p.rapidapi.com/send"

payload = {
	"personalizations": [{ "to": [
				{
					"email": "recipient@mail",
					"name": "recipient"
				}
			] }],
	"from": {
		"email": "me@mail",
		"name": "me"
	},
	"reply_to": {
		"email": "replyto@example.com",
		"name": "Reply to name"
	},
	"subject": "Example subject",
	"content": [
		{
			"type": "text/html",
			"value": text
		},
		{
			"type": "text/plan",
			"value": text
		}
	],
	"headers": { "List-Unsubscribe": "<mailto: unsubscribe@example.com?subject=unsubscribe>, <https://example.com/unsubscribe/id>" }
}

headers = {
	"content-type": "application/json",
	"Content-Type": "application/json",
	"X-RapidAPI-Key": "API KEY HERE :)",
	"X-RapidAPI-Host": "send-mail-serverless.p.rapidapi.com"
}

response = requests.post(mailurl, json=payload, headers=headers)

if response.status_code >= 400:
    print("Email couldnt not be sent. Status code:", response.status_code)
    print(response.text)
    print("ID:" + id)
    print("")
    print("Passord: " + password)
    print("")
else:
    print("Email sent!")
    print("Success!")

input("Press ENTER to quit")
