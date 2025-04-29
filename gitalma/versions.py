import requests
import subprocess
import os


def auto_update():        
    try:
        gh_v = get_github_version()
        a_v = get_gitalma_version()
        process = subprocess.run(["which","gitlab"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exe_gitlab = process.stdout.decode('utf-8').strip()
        if gh_v != a_v:
            if not exe_gitlab:            
                exe_gitlab = "python3"
            else:                
                exe_python = "/".join(exe_gitlab.split("/")[:-1]) + "/python3"   
            print("github version: ", gh_v)
            print("Current version: ", a_v)
            update_cmd = f"{exe_python} -m pip install git+https://github.com/ICR-RSE-Group/gitalma.git" #--break-system-packages
            print(update_cmd)
            process = subprocess.run(update_cmd.split(" "), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            outstr = process.stdout.decode('utf-8').strip()
            errstr = process.stderr.decode('utf-8').strip()
            if outstr:
                print("Output: ", outstr)
            if errstr:
                print("Error: ", errstr)
            return True        
    except Exception as e:
        print("Upgrade error: ", e)
        return False
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
    process = subprocess.run(["python3","-m","pip", "show","gitalma","|","grep","Version"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = process.stdout.decode('utf-8').strip().split('\n')
    for line in lines:
        if "Version" in line:
            version = line.split(":")[1].strip()
            return version
    return version
    