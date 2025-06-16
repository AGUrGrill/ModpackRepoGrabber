import os
import requests
import base64
import shutil
import stat
import tkinter
import threading
from git import Repo
from os import path
from tkinter import *
import tkinter.font as tkFont

has_info = True
has_token = False
modpack_number = None
name = None
repo = None
token = None

def main():
    global has_token
    global name

    if os.path.exists("gitfo.txt"):
        print("Info found.")
        with open("gitfo.txt", "r") as f:
            info = f.readlines()
            try:
                info[2].strip().find("github")
                has_token = True
                print("Token found.")
            except Exception as e:
                print("No token found.")
    else:
        with open("gitfo.txt", "w") as file:
            file.write("Example")
            print("Created new info file.")
        
    ui()

# Main UI
def ui():
    global modpack_number
    global name
    global repo
    global token

    root = tkinter.Tk()
    root.title("Modopack Repo Grabber")

    header_custom_font = tkFont.Font(family="Monocraft", size=18)
    custom_font = tkFont.Font(family="Monocraft", size=12)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{int(screen_width/3)}x{int(screen_height/2)}")
    root.configure(bg="lightgray")

    root.size

    info_label = Label(root, text=f"GitHub Source: {get_github_name()}", font=header_custom_font, bg="lightgray")
    info_label.pack()

    # View Modpacks
    view_modpacks = Label(root, text=f"Modpacks\n{get_existing_repos()}", font=header_custom_font, bg="lightgray")
    view_modpacks.pack(padx=2, pady=5)

    # Choose Modpack
    choose_modpack = Label(root, text="Enter Modpack #:", font=custom_font, bg="lightgray")
    modpack_number = Entry(root, width=50)
    choose_modpack.pack(padx=2, pady=5)
    modpack_number.pack(padx=2, pady=5)

    # Download Modpacks
    download_button = tkinter.Button(root, text="Download Modpacks", width=25, command=clone_repo, font=custom_font)
    download_button.pack(padx=2, pady=2)

    # Info Entry
    name_label = Label(root, text="GitHub Name:", font=custom_font, bg="lightgray")
    name = Entry(root, width=50)
    repo_label = Label(root, text="Repo Name for Uploads:", font=custom_font, bg="lightgray")
    repo = Entry(root, width=50)
    token_label = Label(root, text="GitHub Token for Uploads:", font=custom_font, bg="lightgray")
    token = Entry(root, width=50)
    name_label.pack(padx=2, pady=5)
    name.pack(padx=2, pady=5)
    repo_label.pack(padx=2, pady=5)
    repo.pack(padx=2, pady=5)
    token_label.pack(padx=2, pady=5)
    token.pack(padx=2, pady=5)

    # Save Information
    save_button = tkinter.Button(root, text="Save Information", width=25, command=lambda: save_info(root, info_label, view_modpacks), font=custom_font)
    save_button.pack(padx=2, pady=5)

    # Upload Files
    #upload_button = tkinter.Button(root, text="Upload Files", width=25, command=upload_file)
    #upload_button.pack()

    # Quit Button
    quit_button = tkinter.Button(root, text="Quit", width=25, command=root.destroy, font=custom_font)
    quit_button.pack()

    root.mainloop()

# Update vital UI labels
def update_ui(root, info, packs):
    info.config(text=f"GitHub Source: {get_github_name()}")
    packs.config(text=f"Modpacks\n{get_existing_repos()}")
    
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

    repo_number = int(modpack_number.get())
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

# Allows the user to upload files to their GitHub account (shit code)
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

# Saves user information locally for easier reuse
def save_info(root, info_label, view_modpacks):
    info = f"{name.get()}\n{repo.get()}\n{token.get()}"

    with open("gitfo.txt", "w") as f:
        f.write(info)

    update_ui(root, info_label, view_modpacks)

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
            if "modpack" in line.lower():
                packs.append(line)
    else:
        print(f"Failed to aquire response. {response.status_code}")
    
    return packs

# Get GitHub name
def get_github_name():
    with open("gitfo.txt", "r") as f:
        info = f.readlines()

    return info[0]

# Call Main
if __name__ == "__main__":
    main()