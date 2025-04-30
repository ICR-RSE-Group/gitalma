import requests
import subprocess
import os

LVERSION = ""
        
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

def get_local_version():
    if LVERSION == "":
        return get_gitalma_version()
    else:
        return LVERSION
    
def get_gitalma_version():    
    version = ""    
    process = subprocess.run(["python3","-m","pip", "show","gitalma","|","grep","Version"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = process.stdout.decode('utf-8').strip().split('\n')
    for line in lines:
        if "Version" in line:
            version = line.split(":")[1].strip()
            return version
    return version
    