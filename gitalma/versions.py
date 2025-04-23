import requests
import subprocess
import os


def auto_update():        
    gh_v = get_github_version()
    a_v = get_gitalma_version()
    if gh_v != a_v:
        print("github version: ", gh_v)
        print("Current version: ", a_v)        
        process = subprocess.run(["python","-m","pip", "install", "git+https://git.icr.ac.uk/sc-rse/group/resources/gitalma.git@main#egg=gitalma"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        strout = process.stdout.decode('utf-8').strip().split('\n')
        changed = False
        for line in strout:
            if "Successfully installed" in line:
                print(line)                
                changed = True
        if changed:
            print("Updated gitalma")
            os.system("python -m pip show gitalma | grep Version")
            return True        
    return False
        


def get_github_version():
    # get the file contents of the github file
    version = ""
    url = "https://raw.githubusercontent.com/ICR-RSE-Group/gitalma/refs/heads/main/pyproject.toml"
    response = requests.get(url)
    if response.status_code == 200:
        lines = response.content.decode("utf-8").split("\n")
        for line in lines:
            if "version" in line:
                version = line.split("=")[1].strip().replace('"','')
                return version
    else:
        print("Failed to download cli.py")
    return version

def get_gitalma_version():    
    version = ""    
    process = subprocess.run(["python","-m","pip", "show","gitalma","|","grep","Version"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = process.stdout.decode('utf-8').strip().split('\n')
    for line in lines:
        if "Version" in line:
            version = line.split(":")[1].strip()
            return version
    return version
    