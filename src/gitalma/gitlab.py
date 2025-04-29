#Author: Rachel Alcraft
#Edit: 15-03-2025 - RA: Initial version

import subprocess
import os
from .api_gl import GitLabAPI
from .scratch import Scratch

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
