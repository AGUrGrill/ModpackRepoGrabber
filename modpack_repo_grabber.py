import os
import requests
import shutil
import stat
import tkinter as tk
from git import Repo
from os import path
from tkinter import *
import tkinter.font as tkFont
from io import BytesIO
from PIL import Image, ImageTk

important_image_url="https://static.wikia.nocookie.net/videogaming/images/b/b7/Deltarune_-_Sprite_-_Ralsei_-_Splat.png/revision/latest?cb=20230425002225"
image = None
saved_image = None
has_info = True
modpack_number = None
name = None
#repo = None
#token = None
#has_token = False

if os.path.exists("gitfo.txt"):
    print("File found.")
    with open("gitfo.txt", "r") as f:
        info = f.readlines()
        try: # Look for username
            name = info[0]
            has_token = True
            print("Username found.")
        except:
            print("No username found.")
        #try: # Look for designated repo
        #    token = info[2]
        #    has_token = True
        #    print("Token found.")
        #except:
        #    print("No token found.")
        #try: # Look for github token
        #    info[2].strip().find("github")
        #    token = info[2]
        #    has_token = True
        #    print("Token found.")
        #except:
        #    print("No token found.")
else:
    print("File not found. Creating...")
    with open("gitfo.txt", "w") as file:
        file.write("Example")
        print("Created new info file.")  

# Update vital UI labels
def update_ui():
    username_entry.config(text=get_github_name())
    view_modpacks.config(text=f"Modpacks\n{get_modpack_names()}")
    
# Allows user to download repos
def clone_repo():
    modpacks = get_existing_repos()
    # Checks if info is saved
    if has_info: # Read info
        with open("gitfo.txt", "r") as f:
            info = f.readlines()
            name = info[0].strip()
    else: # Get Input
        return

    repo_number = int(modpack_entry.get())
    repo = modpacks[repo_number-1]

    curseforge_dir_path = os.path.expanduser(f"~\\curseforge\\minecraft\\Instances\\{repo}")
    temp_curseforge_dir_path = os.path.expanduser("~\\curseforge\\minecraft\\Instances\\dir_temp")

    # Make Directory and Clone Repo
    if not os.path.exists(curseforge_dir_path):
        os.mkdir(curseforge_dir_path)
        print("Directory made successfully!")

        # Grab Repo
        if Repo.clone_from(f"https://github.com/{name}/{repo}.git", curseforge_dir_path):
            print("Clone successful!")
        else:
            print("Clone failed.")
    # If file exists, create temp and transfer
    else:
        print("Directory already exists! Removing old files.")

        # Make temp directory
        try:
            os.mkdir(temp_curseforge_dir_path)
            print("Making temp directory.")
        except Exception as e:
            print(f"Temp directory creation error. {e}" )

        # Remove mods and config
        try:
            shutil.rmtree(f"{curseforge_dir_path}\\mods")
            print("Removed mods.")
        except Exception as e:
            print(f"No mod files exist. {e}")
        try:
            shutil.rmtree(f"{curseforge_dir_path}\\config")
            print("Removed config.")
        except Exception as e:
            print(f"No config files exist. {e}")

        # Grab repo and copy to temp
        if Repo.clone_from(f"https://github.com/{name}/{repo}.git", temp_curseforge_dir_path):
            print("Clone successful!")
        else:
            print("Clone failed.")

        # Move files from temp to main
        try:
            shutil.move(f"{temp_curseforge_dir_path}/mods", curseforge_dir_path)
            print("Mods copied successfully!")
        except Exception as e:
            print(f"Mods copy error. {e}")
        try:
            shutil.move(f"{temp_curseforge_dir_path}/config", curseforge_dir_path)
            print("Config copied successfully!")
        except Exception as e:
            print(f"Config copy error. {e}")

        # Remove temp directory
        try:
            print("Removed temp directory.")
            for root, dirs, files, in os.walk(temp_curseforge_dir_path):
                for dir in dirs:
                    os.chmod(path.join(root, dir), stat.S_IRWXU)
                for file in files:
                    os.chmod(path.join(root, file), stat.S_IRWXU)
            shutil.rmtree(temp_curseforge_dir_path)
        except Exception as e:
            print(f"Error removing temp directory. {e}" )
    
    print("Cloning completed.")

# Saves user information locally for easier reuse
def save_info():
    info = f"{username_entry.get()}"
    #\n{repo.get()}\n{token.get()}"

    with open("gitfo.txt", "w") as f:
        f.write(info)

    update_ui()

# Gets a list of avaliable GitHub repos with the term 'modpack'
def get_existing_repos():
    packs = []
    # Checks if info is saved
    if has_info: # Read info
        with open("gitfo.txt", "r") as f:
            info = f.readlines()
            name = info[0].strip()
    else:
        return packs

    # Sends request for user GitHub repos
    url = f"https://api.github.com/users/{name}/repos"
    response = requests.get(url)

    if response.status_code == 200:
        # print("Successfully aquired response!")
        data = response.json()
        for repo in data:
            line = repo["name"]
            if "modpack" in line.lower() and line != "ModpackRepoGrabber":
                packs.append(line)
    else:
        print(f"Failed to aquire response. {response.status_code}")
    
    return packs

def get_modpack_names():
    modpack_list = get_existing_repos()
    if modpack_list == []:
        return "No Packs Found"
    formatted_list = ""
    counter = 1
    #modpack_list = json.dumps(modpack_list)
    # Format Modpack List
    for element in modpack_list:
        element = element.replace("modpack-", "")
        formatted_list += f"{counter}: {element}\n"
        counter+=1

    return formatted_list

# Get GitHub name
def get_github_name():
    with open("gitfo.txt", "r") as f:
        info = f.readlines()

    return info[0]

# Allows the user to upload files to their GitHub account (shit code)
'''''
def upload_file():
    # Checks if info is saved
    if has_info: # Read info
        with open("gitfo.txt", "r") as f:
            info = f.readlines()
            name = info[0].strip()
            repo = info[1].strip()
            token = info[2].strip()
        if not has_token: # If choosen not to save token, input it
            token = input("Enter your GitHub Personal Access Token: ").strip()
    else: # Get Input
        token = input("Enter your GitHub Personal Access Token: ").strip()
        name = input("Enter GitHub Name: ").strip()
        repo = input("Enter Repo Name: ").strip()

    branch = "main" # Could be changed but prob main for most
    file_path = input("Enter the file path of the file: ").strip()
    repo_file = input("Enter name of file with extension (.zip, .rar): ").strip()
    commit_message = input("Enter a commit message: ").strip()
    repo_file_path = f"{file_path}/{repo_file}"

    # Read and encode the file
    with open(repo_file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    url = f"https://api.github.com/repos/{name}/{repo}/contents/{repo_file_path}"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "message": commit_message,
        "content": content,
        "branch": branch
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 201 or response.status_code == 200:
        print("File uploaded successfully!")
    else:
        print(f"Upload failed. {response.status_code}: {response.json()}")

# Upload Files
#upload_button = tkinter.Button(root, text="Upload Files", width=25, command=upload_file)
#upload_button.pack()
'''''

# Aquire Glorious Image
def get_image():
    url_response = requests.get(important_image_url)
    image = Image.open(BytesIO(url_response.content))
    height = int(image.height/3)
    width = int(image.width/3)
    image = image.resize((height, width), Image.LANCZOS)
    image = ImageTk.PhotoImage(image)
    important_image.config(image=image)
    important_image.image = image

# UI
root = tk.Tk()
root.title("Modopack Repo Grabber")

# Fonts
header_custom_font = tkFont.Font(family="Monocraft", size=12)
custom_font = tkFont.Font(family="Monocraft", size=10)

# Screen Settings
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
adjusted_screen_width = int(screen_width/4)
adjusted_screen_height = int(screen_height/2.75)
root.geometry(f"{adjusted_screen_width}x{adjusted_screen_height}")
root.configure(bg="lightgray")
padding_y = 2
root.resizable(False, False)

# Username Frame
name_frame = tk.Frame(root, bg="lightgray", pady=padding_y*4)
name_frame.grid(row=0, column=0, sticky=NSEW)
username_label = tk.Label(name_frame, text="Username:", font=header_custom_font, bg="lightgray")
username_label.place(relx=0.05, rely=0.5, anchor=W)
username_entry = tk.Entry(name_frame, font=header_custom_font)
username_entry.insert(0, name)
username_entry.grid(row=0, column=1, sticky=NSEW)

# Modpack Frame
#pack_frame = tk.Frame(root, bg="lightgray", pady=padding_y*4)
#pack_frame.grid(row=1, column=0, sticky=NSEW, pady=padding_y)
view_modpacks = tk.Label(root, text=f"Modpacks\n{get_modpack_names()}", font=header_custom_font, bg="lightgray")
view_modpacks.grid(row=1, column=0, sticky=NSEW, pady=padding_y)
important_image = tk.Label(root, bg="lightgray")
important_image.place(relx=0.2, rely=0.3, anchor=CENTER)

# Modpack Options Frame
pack_options_frame = tk.Frame(root, bg="lightgray")
pack_options_frame.grid(row=2, column=0, sticky=NSEW)
modpack_label = tk.Label(pack_options_frame, text="Modpack #:", font=header_custom_font, bg="lightgray")
modpack_label.place(relx=0.05, rely=0.35, anchor=W)
modpack_entry = tk.Entry(pack_options_frame, font=header_custom_font)
modpack_entry.grid(row=0, column=1, sticky=NSEW)

# Button Frame
button_frame = tk.Frame(root, bg="lightgray")
button_frame.grid(row=3, column=0, sticky=NSEW)
download_button = tk.Button(button_frame, text="Download/Update Modpack", command=clone_repo, font=custom_font)
download_button.grid(row=0, column=0, sticky=NSEW, pady=padding_y)
save_button = tk.Button(button_frame, text="Change User", command=lambda: save_info(), font=custom_font)
save_button.grid(row=1, column=0, sticky=NSEW, pady=padding_y)
quit_button = tk.Button(button_frame, text="Quit", command=root.destroy, font=custom_font)
quit_button.grid(row=2, column=0, sticky=NSEW, pady=padding_y)

# Configure Grid
# Main Frame
for i in range(4): 
    root.rowconfigure(i, weight=1)
root.columnconfigure(0, weight=1)

# Name Frame
name_frame.rowconfigure(0, weight=1)
name_frame.columnconfigure(0, weight=1)
name_frame.columnconfigure(1, weight=1)

# Modpack Options Frame
pack_options_frame.rowconfigure(0, weight=1)
pack_options_frame.rowconfigure(1, weight=1)
pack_options_frame.columnconfigure(0, weight=1)
pack_options_frame.columnconfigure(1, weight=1)

# Button Frame
for i in range(3):
    button_frame.rowconfigure(i, weight=1)
button_frame.columnconfigure(0, weight=1)

get_image()

root.mainloop()
