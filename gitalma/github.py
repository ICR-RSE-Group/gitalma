#Author: Rachel Alcraft
#Edit: 15-03-2025 - RA: Initial version


import os
from .scratch import Scratch
from .api_gh import GitHubAPI

from .git import *

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
