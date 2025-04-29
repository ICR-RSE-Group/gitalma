"""-------------------------------------
GITLAB PULL SCRIPT FOR BCR-DataScienceTeam
This module downloads dynamically all the projects from gitlab and clones if absent or pulls if present.
Example inputs (all default to standard options):
gitlab.py -path /path/for/repo/bcrbioinformatics -include Team,Manuscripts,General,Projects -exclude Utils -source target --static
--help returns this message
--version returns the version
-source target is the production repo, test is the repo that is being tested and not updated
-path is the path to the root of the gitlab projects
-include: Only get whitelisted folders (comma delim)
-exclude: Exclude blacklisted folders (comma delim)
--static: does not dynamically get the projects, but updates from those existing or those included
--protocol: override default ssh clone behaviour with https
--history: report history instead of diff
--debug: outputs extra logs for debugging
--dry: report what would be done (mkdir, clone and pull) but don't do it
--status: report the status on each project, forces dry
--single: override multithreaded behaviour, stay in single thread.
-------------------------------------
"""
import argparse
import os
import datetime


thisversion = "0.0.0"
gversion = "0.0.0"

def main():
    parser = argparse.ArgumentParser(description="GitLab pull or clone", 
        epilog="""
        GITLAB PULL SCRIPT FOR BCR-DataScienceTeam
        This module downloads dynamically all the projects from gitlab and clones if absent or pulls if present.
        Example inputs (all default to standard options):          
        git-alma --status
        """)
    parser.add_argument("--version", help="returns the version", action="store_true")
    # The main commands    
    actions_help = "actions = [init, info, pull, update, clean, status, history,change,upgrade]"
    parser.add_argument("action", nargs=1, help=actions_help)    
    # The paramaters that need values
    parser.add_argument("-source", help="target is the production repo, test is the repo that is being tested and not updated", type=str)
    parser.add_argument("-path", help="is the path to the root of the gitlab projects", type=str)
    parser.add_argument("-server", help="The url to gitlab or github", type=str)
    parser.add_argument("-subgroup", help="the gitlab subgroup number which is the root of the gitlab projects", type=int)    
    parser.add_argument("-protocol", help="override default https clone behaviour with ssh", type=str)    
    parser.add_argument("-autoupgrade", help="Always automatically update to latest main version", type=str)
    
    # The flags        
    parser.add_argument("--debug", help="outputs extra logs for debugging", action="store_true")
    parser.add_argument("--dry", help="report what would be done (mkdir, clone and pull) but don't do it", action="store_true")    
    parser.add_argument("--single", help="override multithreaded behaviour, stay in single thread.", action="store_true")
    parser.add_argument("--root", help="run from home path no matter where in the repo you are.", action="store_true")
        
    args = parser.parse_args()
    thisversion = get_gitalma_version()
    gversion = get_github_version()
    if args.version:        
        print("GitAlma version:", thisversion)
        print("Github version:", gversion)
        exit()
    
    start_time = datetime.datetime.now()            
    cwd = os.getcwd()        
    scrch = Scratch(cwd)
    if not scrch.gitalma:
        scrch.home = str(scrch.path)
    new_params = init_args(scrch, args)
    repo_params = init_check_get(scrch,new_params)
    #########################################################################################
    if args.action[0] == "init":        
        changed_params = init_save(new_params, repo_params)                
        init_print(changed_params, init=True)
        exit()
    #########################################################################################
    if not scrch.gitalma:
        print("Not in a gitalma repository")
        exit()    
    new_params = init_args(scrch, args)
    cmd_params = cmd_args(args)
    repo_params = init_check_get(scrch,new_params)
    clone_params = clone_args(args,cmd_params)
    params = {}
    for key in cmd_params:
        params[key] = cmd_params[key]
    for key in repo_params:
        params[key] = repo_params[key]
    for key in clone_params:
        params[key] = clone_params[key]
    if args.debug:
        print("===========================================")
        print("===== GIT-ALMA from the ICR RSE Team =====")
        print("===========================================")
        print("-Config repo params-")    
        for key in repo_params:        
            print(f"\t{key}: {repo_params[key]}")    
        print("-Params entered-")    
        for key in clone_params:
            print(f"\t{key}: {clone_params[key]}")
        print("=====================================")
    else: #less verbose logging        
        print("\n===== GITALMA from the ICR RSE Team =====")                
        if "repo" in repo_params:        
            print(f"repo: {repo_params['repo']}")    
        elif "server" in repo_params:        
            print(f"server: {repo_params['server']}")
        if "path" in repo_params:        
            print(f"path: {repo_params['path']}")            
        print("Local/latest versions:", thisversion, "/", gversion)        
        print("=====================================")

    #########################################################################################
    if "autoupgrade" in params:
        if params["autoupgrade"].upper() == "Y":
            auto_update()
    
    if args.root:
        params["path"] = params["home"]
        scrch = Scratch(params["path"])
    if args.action[0] == "info":        
        init_print(repo_params, init=False)
    elif args.action[0] == "update":        
        if params["source"] in ["gitlab","icr"]:
            print(f">> Check projects to delete --- ")
            all_projects,archived = clone_clean(params, args.dry)
            to_clone, to_pull = clone_projects(params, args.dry, args.debug, all_projects)                
        else:
            to_clone, to_pull = gh_clone_projects(params, args.dry, args.debug)
        if to_clone != []:
            print(f">> Cloning {len(to_clone)} projects --- ")
            git_clone_all(params, args.dry, args.debug, to_clone)
        if to_pull != []:
            print(f">> Pulling {len(to_pull)} projects --- ")
            git_pull_all(params, "pull", args.dry, args.debug, to_pull)
    elif args.action[0] == "pull":                
        print(f">> Pull projects---")
        git_pull_all(params, "pull", args.dry, args.debug,None)
    elif args.action[0] == "clean":                     
        clone_clean(params, args.dry)
    elif args.action[0] == "status":                    
        print(f">> Status projects---")
        git_pull_all(params, "status", args.dry, args.debug,None)
    elif args.action[0] == "history":                   
        print(f">> History projects---")
        git_pull_all(params, "history", args.dry, args.debug, None)
    elif args.action[0] == "change":
        if args.protocol:
            print(f">> Changing to {args.protocol}")
            token = None
            if args.protocol == "pat":
                api = GitLabAPI(params["subgroup"], params["server"])
                token = api.token
            git_change_protocol(params, args.protocol, args.dry, args.debug,token)
            
        else:
            print(f">> No change supplied, exiting")                                        
    elif args.action[0] == "upgrade":
        print("auto-upgrade")
        if not auto_update():
            print("No update needed")
                        
    #----------------------------------------------------
    end_time = datetime.datetime.now()    
    print("Completed in ", end_time-start_time)
    print("=====================================")

#################################################################
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
                # but if it doesn;t exist tghen use default python
                if not os.path.exists(exe_python):
                    exe_python = "python3"
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
    
###############################################################
import os
from pathlib import Path


class Scratch:
    def __init__(self, path):                
        self.path = path
        self.gitalma = False
        self.get_home()
        self.gits = self.get_gits()        
    ##################################################################################
    def get_home(self):
        """Find the parent gitalma home."""        
        #Check if the given path is a Git repository or its child."""
        gitlabpath = Path(self.path).resolve()
        
        for gitlab_path in [gitlabpath, *gitlabpath.parents]:                        
            if os.path.exists(os.path.join(gitlab_path, ".gitalma")):                
                self.gitalma = True
                self.home = gitlab_path
                break
    ##################################################################################
    def get_gits(self):
        """Find all the gitalma homes in the parent directory."""
        gitlabpath = Path(self.path).resolve()        
        gits = []
        # find all the child folders that have a .git direcrorty        
        subfolders = [f for f in gitlabpath.iterdir() if f.is_dir()]
        while len(subfolders) > 0:        
            subfolder = subfolders.pop()
            if os.path.exists(os.path.join(subfolder, ".git")):
                gits.append(str(subfolder))
            else:
                subfolders.extend([f for f in subfolder.iterdir() if f.is_dir()])
        for g in range(len(gits)):
            gits[g] = str(gits[g])
        return gits
    ##################################################################################
    def get_subgroups(self, groups, repo_len):
        sgps = []
        for gp in groups:
            gpath = f"{self.home}/{'/'.join(gp.split('/')[repo_len:])}"               
            sgps.append(gpath)
        return sgps        
    ##################################################################################
    def get_child_projects(self, projects, repo_len):
        child_projects = []
        for project in projects:            
            gpath = f"{self.home}/{'/'.join(project[2].split('/')[repo_len:])}"            
            if gpath.startswith(self.path):
                child_projects.append(project)                
        return child_projects
    ##################################################################################
#Author: Rachel Alcraft
#Edit: 15-03-2025 - RA: Initial version

import os
import yaml


##################################################################################      
### Command line parsing ###
def init_args(scrch, args):
    params = {}    
    params["path"] = os.getcwd() if not args.path else args.path
    if not scrch.gitalma:    
        scrch.home = str(params["path"])
    params["home"] = scrch.home    
    params["source"] = "icr" if not args.source else args.source
    if params["source"] == "icr":        
        params["server"] = "https://git.icr.ac.uk" if not args.server else args.server    
    elif params["source"] == "gitlab":
        params["server"] = "https://gitlab.com" if not args.server else args.server
    elif params["source"] == "github":
        params["server"] = "https://github.com" if not args.server else args.server
    else:
        params["server"] = "https://git.icr.ac.uk" if not args.server else args.server    
    if params["source"] == "gitlab" or params["source"] == "icr":
        params["protocol"] = "pat" if not args.protocol else args.protocol
    else:
        params["protocol"] = "https" if not args.protocol else args.protocol
    params["subgroup"] = -1 if not args.subgroup else args.subgroup    
    params["autoupgrade"] = "Y" if not args.autoupgrade else args.autoupgrade
    return params
##################################################################################
def cmd_args(args):
    params = {}    
    params["path"] = os.getcwd() if not args.path else args.path
    if args.protocol:
        params["protocol"] = args.protocol
    return params
##################################################################################
def init_check_get(scrch,params):
    init_params = {}    
    init_path = f"{scrch.home}/.gitalma/init.yaml"
    if os.path.exists(init_path):    
        with open(init_path, "r") as yaml_file:
            init_params = yaml.safe_load(yaml_file)#, Loader=yaml.FullLoader)                                
    return init_params
##################################################################################
def init_save(new_params, orig_params):
    init_path = f"{new_params['path']}/.gitalma"
    os.makedirs(init_path, exist_ok=True)
    init_file = f"{new_params['path']}/.gitalma/init.yaml"
    changed_params = {}
    # put orig params in first then any overwrites
    for key in orig_params:
        changed_params[key] = orig_params[key]
    for key in new_params:                
        if key in changed_params:
            print(f"Changing {key} from {orig_params[key]} to {new_params[key]}")
        changed_params[key] = str(new_params[key])
    # now do a sanity check on the matching names of the path and groupip
    if changed_params["source"] in ["gitlab","icr"]:
        api = GitLabAPI(changed_params["subgroup"],changed_params["server"])
        gp, rp = api.get_id_repo()
        changed_params["subgroup"] = gp
        changed_params["repo"] = rp
                
    with open(init_file, "w") as yaml_file:
        yaml.dump(changed_params, yaml_file, default_flow_style=False, indent=4, width=80, sort_keys=False)
    
    return changed_params
##################################################################################
def init_print(params,init):
    print("-------------------------------------")
    if init:
        print("Initialised the settings for gitlab or github")
    else:
        print("The existing settings for gitlab or github")
    print("-------------------------------------")
    for key in params:
        num_tabs = 2 - len(key)//8
        print(key, num_tabs*"\t",params[key])
##################################################################################
        
    
import os
from pathlib import Path
import requests

class GitLabAPI:
    def __init__(self, group_id, server):
        self.repo = ""
        self.group_id = int(group_id)
        self.repo_len = 0
        self.url = server
        home = str(Path.home())
    
        if "icr.ac.uk" in server:
            token_path = home + "/gitlab_token.txt"
        else:
            token_path = f"{home}/{server.replace('/','').replace('https','').replace(':','').replace('.','')}_gitalma_token.txt"
                
        if not os.path.exists(token_path):
            print("You need to generate a gitlab personal token and save it to:")
            print("Toekn path=", token_path)
            print("See here for how to generate a token:")
            print("https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html")
            self.ok = False
            exit()
        else:            
            with open(token_path, 'r') as f:
                self.token = f.read().strip()
            self.headers = {
                "PRIVATE-TOKEN": self.token
            }                                                                        
            self.repo = ""
            self.repo_len = 0
            if int(group_id) != -1:
                self.repo = self.get_repo_from_id(group_id)
                if self.repo == None:
                    print("Group ID not found")
                    exit()
                self.repo_len = len(self.repo.split("/"))            
    ##################################################################################
    def get_id_repo(self):
        return self.group_id, self.repo
    ##################################################################################
    def list_projects(self,):
        """List all projects in the GitLab instance."""        
        projects = []
        arch_projects = []        
        try:        
            gitlab_url = f"{self.url}/api/v4/groups/{self.group_id}/projects"            
            page_int = 0            
            got_pages = True
            print("Fetching projects for", gitlab_url, end=" ", flush=True)
            while got_pages:                
                got_pages = False
                page_int += 1
                print("...", end="", flush=True)
                response = requests.get(gitlab_url, headers=self.headers, data={"per_page":100,"page": page_int, "include_subgroups" : True})                
                response.raise_for_status()
                current_path = ""
                if response.status_code == 200:
                    if len(response.json()) == 0:
                        print("")
                    for val in response.json():                                                
                        proj_id = val["id"]
                        http_url_to_repo = val["http_url_to_repo"]
                        path_with_namespace = val["path_with_namespace"]
                        archived = val["archived"]                        
                        if archived:                                                        
                            arch_projects.append((http_url_to_repo, proj_id,path_with_namespace))
                        else:                            
                            projects.append((http_url_to_repo, proj_id,path_with_namespace))
                        got_pages = True                
                else:
                    print("Failed to fetch projects: ",response.status_code)                                    
            return projects, arch_projects
        except Exception as e:
            print("!!! Failed to fetch projects: ",e)
            if e.response.status_code == 401:
                print("!!! Your Gitlab API token might be expired !!!")
            print("!!! Not safe to continue, exiting !!!")            
            exit()
    ##################################################################################        
    def get_repo_from_id(self, group_id):
        gitlab_url = f"{self.url}/api/v4/groups/{group_id}"        
        response = requests.get(gitlab_url, headers=self.headers, data={"include_subgroups" : False, "with_projects" : False})
        if response.status_code == 200:
            print("Group ID:",group_id,"is",response.json()["full_path"])    
            return response.json()["full_path"]
        else:
            return None
    ##################################################################################                
    def list_groups(self):
        """List all groups in the GitLab instance."""        
        groups = []     
        gitlab_url = f"{self.url}/api/v4/groups/{self.group_id}/subgroups"
        page_int = 0
        got_pages = True
        print("Fetching groups for", gitlab_url, end=" ", flush=True)
        while got_pages:                            
            page_int += 1
            print("...", end="", flush=True)
            response = requests.get(gitlab_url, headers=self.headers, data={"page":page_int, "include_subgroups" : True})
            if response.status_code == 200:
                if len(response.json()) == 0:
                    got_pages = False
                for val in response.json():                                                    
                    full_path = val["full_path"]                    
                    groups.append(full_path)                                                        
            else:
                print(f"Failed to fetch projects: {response.status_code}")
                got_pages = False
        print("")
        return groups        
    ##################################################################################
    def tokenise_server(self, server):
        git_server = server.replace("https://",f"https://oauth2:{self.token}@")
        return git_server
    
    
          
    
    #Author: Rachel Alcraft
#Edit: 15-03-2025 - RA: Initial version

import subprocess
import os


##################################################################################      
### Command line parsing ###
def clone_args(args,params):    
    params["path"] = os.getcwd() if not args.path else args.path    
    params["multi"] = False if args.single else True
    params["root"] = True if args.root else False    
    return params
##################################################################################
def create_subgroups(params, dry):
    print(f"---Creating subgroups--- ")
    sgs = 0
    api = GitLabAPI(params["subgroup"], params["server"])
    full_groups = api.list_groups()
    sctch = Scratch(params["path"])
    groups = sctch.get_subgroups(full_groups, api.repo_len)
    count = 0
    for group in groups:
        count += 1
        if not os.path.exists(group):
            sgs += 1
            msg = f"{count}/{len(groups)}:"
            msg += f"Creating {group}"
            if dry:
                print(f"Dry: would create group {group}")
            else:                
                print(msg)
                os.makedirs(group, exist_ok=True)
    if sgs > 0:
        print()
    print(f"\tCreated {sgs} subgroups")
    print("=====================================")
##################################################################################
def clone_projects(params, dry,debug, all_projects=[]):
    print(f"---Gathering projects--- ")    
    api = GitLabAPI(params["subgroup"], params["server"])
    repo_len = api.repo_len    
    if all_projects == []:
        all_projects,archived = api.list_projects()    
    root_path = params["path"]
    home_path = params["home"]    
    scrch = Scratch(root_path)    
    projects = scrch.get_child_projects(all_projects,repo_len)    
    count = 0
    cloned = 0
    to_clone = []
    to_pull = []
    for project in projects:
        count += 1        
        phttps = project[0]        
        ppath = project[2]        
        spath = f"{home_path}/{'/'.join(ppath.split('/')[repo_len:-1])}"               
        gpath = f"{home_path}/{'/'.join(ppath.split('/')[repo_len:])}"       
        if params["protocol"] == "ssh":            
            phttps = phttps.replace("https://","git@")   
        elif params["protocol"] == "pat":
            phttps = api.tokenise_server(phttps)        
        if not os.path.exists(gpath):                  
            os.makedirs(spath, exist_ok=True)
            to_clone.append((phttps, gpath))
        else:            
            to_pull.append(gpath)    
    return to_clone, to_pull
##################################################################################
def clone_clean(params, dry, all_projects=[]):    
    api = GitLabAPI(params["subgroup"], params["server"])
    repo_len = api.repo_len
    scrch = Scratch(params["path"])    
    if all_projects == []:
        all_projects,archived = api.list_projects()          
    projects = scrch.get_child_projects(all_projects,repo_len)      
    projects_paths = []
    for project in projects:
        ppath = project[2]        
        gpath = f"{params['home']}/{'/'.join(ppath.split('/')[repo_len:])}"
        projects_paths.append(str(gpath))            
    count = 0    
    for gpath in scrch.gits:
        if str(gpath) not in projects_paths:
            count += 1
            if dry:
                print(f"Dry: would delete {gpath}")
            else:
                print(f"Deleting {gpath}")
                # TODO check if there are any files that need updating
                subprocess.run(["rm", "-rf", gpath],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if count > 0:
        print()
    print(f"\tDeleted {count} projects")
    print("=====================================")
    return all_projects,archived
##################################################################################

    
 #Author: Rachel Alcraft
#Edit: 15-03-2025 - RA: Initial version


import os


##################################################################################      
### Command line parsing ###
def gh_args(args,params):    
    params["path"] = os.getcwd() if not args.path else args.path    
    params["multi"] = False if args.single else True
    params["root"] = True if args.root else False    
    return params
##################################################################################
def gh_clone_projects(params, dry,debug, all_projects=[]):
    print(f"---Gathering projects--- ")    
    api = GitHubAPI(params["repos"], params["server"])    
    to_clone = []
    to_pull = []
    if all_projects == []:
        all_projects = api.list_projects()    
    root_path = params["path"]
    home_path = params["home"]    
    scrch = Scratch(root_path)    
    repo_len = 0
    projects = scrch.get_child_projects(all_projects,repo_len)
    count = 0
    cloned = 0
    for project in projects:
        count += 1        
        phttps = project[0]        
        ppath = project[2]        
        gpath = f"{home_path}/{'/'.join(ppath.split('/')[repo_len:])}"         
        spath = f"{home_path}/{'/'.join(ppath.split('/')[repo_len:-1])}"                       
        if params["protocol"] == "ssh":            
            phttps = phttps.replace("https://","git@")           
        if not os.path.exists(gpath):                  
            os.makedirs(spath, exist_ok=True)              
            to_clone.append((phttps, gpath))            
        else:            
            to_pull.append(gpath)                
    return to_clone, to_pull
##################################################################################
   
    
    
    
    #Author: Rachel Alcraft
#Edit: 15-03-2025 - RA: Initial version

import subprocess
import os
import time
from pathlib import Path
import threading


THROTTLE_CLONE = 0.05
THROTTLE_PULL = 0.01
KEEPS = 10


##################################################################################
def git_pull_all(params, action, dry,debug, to_pull):    
    threads_to_pull = list()    
    scrch = Scratch(params["path"])            
    count = 0
    if to_pull == None:
        to_pull = scrch.gits    
    for gpath in to_pull:                
        count += 1
        msg = f"{count}/{len(to_pull)}:"                
        if not os.path.exists(gpath):
            print(f"Path {gpath} does not exist")
            continue
        else:            
            msg += f"{action} from {gpath}"
            if dry:
                print(f"Dry: would {action} {gpath}")
            else:
                if params["multi"]:
                    time.sleep(THROTTLE_PULL)                    
                    x = None
                    if action == "pull":
                        x = threading.Thread(target=git_pull, args=(gpath, msg,debug))
                    elif action == "status":
                        x = threading.Thread(target=git_status, args=(gpath, msg,debug))
                    elif action == "history":
                        x = threading.Thread(target=git_history, args=(gpath, msg,debug))
                    if x != None:
                        threads_to_pull.append(x)
                        x.start()
                else:
                    if action == "pull":
                        git_pull(gpath, msg,debug)
                    elif action == "status":
                        git_status(gpath, msg,debug)                
                    elif action == "history":
                        git_status(gpath, msg,debug)                
    if params["multi"]:        
        for index, thread in enumerate(threads_to_pull):
            thread.join()        
    if count > 0:
        print()
    print(f"{action}ed {count} projects")
    print("=====================================")
##################################################################################
def git_clone_all(params, dry,debug, to_clone):    
    threads_to_pull = list()    
    scrch = Scratch(params["path"])            
    count = 0    
    for phttps, gpath in to_clone:
        count += 1
        msg = f"{count}/{len(to_clone)}:"                        
        msg += f"clone from {gpath}"
        if dry:
            print(f"Dry: would 'git clone {phttps} {gpath}'")
        else:
            if params["multi"]:
                    time.sleep(THROTTLE_PULL)                    
                    x = None                        
                    x = threading.Thread(target=git_clone, args=(phttps, gpath, msg, debug))
                    if x != None:
                        threads_to_pull.append(x)
                        x.start()
            else:                    
                git_clone(phttps, gpath, msg, debug)                
    if params["multi"]:
        progress = 0
        for index, thread in enumerate(threads_to_pull):
            progress += 1
            thread.join()
            #print(f"Cloned: {progress}/{len(threads_to_pull)}")
    if count > 0:
        print()
    print(f"cloned {count} projects")
    print("=====================================")
##################################################################################
def git_clone(phttps, spath, msg, debug):        
    keep_going = True
    count = 0
    while keep_going and count < KEEPS:
        count += 1        
        process = subprocess.run(["git", "clone", phttps, spath],stdout=subprocess.PIPE, stderr=subprocess.PIPE)        
        if debug:
            print(f"git clone {phttps} {spath}")
        keep_going = git_message(process, msg,True, count == KEEPS)
        if keep_going:
            #if count%20 == 0:
            #    print("Retrying", phttps, count, "/" , KEEPS)
            time.sleep(1)
    if keep_going:
        print(f"\nFailed to clone {phttps} to {spath}")
        return False
    elif count > 1:
        print(f"\n{phttps} succeeded after {count} times")
    return True
##################################################################################
def git_pull(gpath, msg, debug):           
    keep_going = True
    count = 0
    while keep_going and count < KEEPS:
        count += 1
        #process = subprocess.run(["git", "-C", gpath, "pull","--rebase"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)            
        process = subprocess.run(["git", "-C", gpath, "pull"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)            
        keep_going = git_message(process, msg, debug, count == KEEPS)
        if keep_going:
            #if count%20 == 0:
            #    print("Retrying", gpath, count)
            time.sleep(0.05)
    if keep_going:
        print(f"\nFailed to pull {gpath}")    
        return False
    elif count > 10:
        print(f"\n{gpath} succeeded after {count} times")
    return True
##################################################################################
def git_status(gpath, msg, debug):    
    process = subprocess.run(["git", "-C", gpath, "status"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)    
    git_message(process, msg, debug)    
##################################################################################
def git_history(gpath, msg, debug):    
    process = subprocess.run(["git", "-C", gpath, "log", "-2", "--pretty=format:'%h%x09%an%x09%ad%x09%s'"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    git_message(process, msg, debug)    
##################################################################################
def git_message(process, msg, debug, force_msg=False):            
    connection_error = False
    out = process.stdout.decode("utf-8").strip()    
    err = process.stderr.decode("utf-8").strip()

    # strip out err msg from ssh key
    err = err.replace('\\220',"").replace('\\230',"").replace('\\342',"").replace('\\225',"")
    err = err.replace('\\224',"").replace('\\202',"").replace('\\233',"").replace('\\222',"")
    err = err.replace("UNAUTHORISED ACCESS TO THIS APPLIANCE IS PROHIBITED!","")
    err = err.replace("This appliance, and associated systems, are for ICR authorised users only.","")
    err = err.replace("Unauthorised or improper use may result in disciplinary action, and/or","")
    err = err.replace("civil or criminal prosecution under the Computer Misuse Act (1990). By","")
    err = err.replace("continuing, you agree to abide by the terms of the ICR Acceptable Use","")
    err = err.replace("Policy (published on NEXUS). All use is monitored, and users have no","")
    err = err.replace("implicit or explicit expectation of privacy. Please contact ICR","") 
    err = err.replace("Information Security (infosec@icr.ac.uk) for more information.","")                    
    #err = err.replace(" ","")
    err = err.replace("\n","")
    #err = err.replace("\t","")
    if "Connection reset by peer" in err and not force_msg:
        connection_error = True        
        print("-", end="", flush=True)
    elif "fatal: Could not read from remote repository" in err and not force_msg:        
        connection_error = True
        print("-", end="", flush=True)
    else:
        out = out.replace("Already up to date.","")
        out = out.replace("On branch main","")
        out = out.replace("Your branch is up to date with 'origin/main'.","")
        out = out.replace("nothing to commit, working tree clean","")
        out = out.strip()                                                
        outs = out.split("\n")
        out2 = "\n\t".join(outs).strip()    
        errs = err.split("\n") 
        if len(errs) > 2:#skip the security message
            if "UNAUTHORISED ACCESS" in err:
                errs = errs[11:]
        err2 = "\n\t".join(errs).strip()
        if out2 == "" and err2 == "" and not debug:
            print(".", end="", flush=True)
        else:
            if out2 != "":            
                msg += f"\n\t{out2}"
            if err2 != "":                        
                if err2 != "":  
                    msg += f"\n\t{err2}"        
            print("\n",msg, end="", flush=True)
    return connection_error
##################################################################################
def git_change_protocol(params, new_protocol, dry, debug,token):
    scrch = Scratch(params["path"])            
    to_change = scrch.gits        
    count = 0
    for ch in to_change:        
        git_config_file = Path(ch) / ".git" / "config"        
        if not git_config_file.exists():
            print(f"Path {git_config_file} does not exist")
            continue
        else:            
            with open(git_config_file, "r") as f:
                lines = f.readlines()                
            
            new_lines = []
            for line in lines:
                if "url =" in line:
                    would_change = False
                    if "oauth2" in line:
                        if new_protocol == "https":
                            line = pat_to_https(line)
                            would_change = True
                        elif new_protocol == "ssh":
                            line = pat_to_ssh(line)
                            would_change = True
                        elif new_protocol == "pat":
                            line = pat_to_pat(line,token)
                            would_change = True
                    elif "https://" in line:
                        if new_protocol == "pat":                            
                            line = https_to_pat(line,token)
                            would_change = True
                        elif new_protocol == "ssh":
                            line = https_to_ssh(line)
                            would_change = True                        
                    elif "git@" in line:
                        if new_protocol == "pat":
                            line = ssh_to_pat(line,token)
                            would_change = True
                        elif new_protocol == "https":
                            line = ssh_to_https(line)                                                                
                            would_change = True
                    if would_change:
                        count += 1
                        if dry:
                            print("would replace:", line)
                        elif debug:
                            print("replacing:", line)
                                                    
                new_lines.append(line)
                    
            if not dry:
                with open(git_config_file, "w") as f:
                    for line in new_lines:                                                                        
                        f.write(line)                                                                            
    
    print(f"\nchanged {count} repo protocols")
    return True
##################################################################################
def ssh_to_pat(line, token):
    line = line.replace("git@",f"https://oauth2:{token}@")
    return line
##################################################################################
def https_to_pat(line,token):
    line = line.replace("https://",f"https://oauth2:{token}@")
    return line
##################################################################################
def https_to_ssh(line):
    line = line.replace("https://","git@")    
    return line
##################################################################################
def ssh_to_https(line):
    line = line.replace("git@","https://")
    return line
##################################################################################
def pat_to_ssh(line):
    lineA = line.split("https://")[0]
    lineB = line.split("@")[1]    
    line = lineA + "git@" + lineB    
    return line
##################################################################################
def pat_to_https(line):
    lineA = line.split("https://")[0]
    lineB = line.split("@")[1]    
    line = lineA + "https://" + lineB    
    return line
##################################################################################
def pat_to_pat(line,token):    
    lineA = line.split("https://")[0]
    lineB = line.split("@")[1]            
    line =  lineA + f"https://oauth2:{token}@" + lineB
    return line
##################################################################################
        
    
        



##############################################################
if __name__ == "__main__":
    # calling the main function
    main()
    
