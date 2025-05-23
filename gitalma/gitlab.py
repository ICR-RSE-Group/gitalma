#Author: Rachel Alcraft
#Edit: 15-03-2025 - RA: Initial version

import subprocess
import os
from .api_gl import GitLabAPI
from .scratch import Scratch

##################################################################################      
### Command line parsing ###
def gl_clone_args(args,params):    
    params["path"] = os.getcwd() if not args.path else args.path    
    params["multi"] = False if args.single else True
    params["root"] = True if args.root else False    
    return params
##################################################################################
def gl_clone_projects(params, dry,debug, all_projects=[]):
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
def gl_clone_clean(params, dry, all_projects=[]):    
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
            # check the status of the project
            process = subprocess.run(["git", "-C", gpath, "status"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            outstr = process.stdout.decode("utf-8").strip()
            errstr = process.stderr.decode("utf-8").strip()
            print(f"\t---Candidate to delete: {gpath}---")
            if errstr != "":
                print(f"\t!!!Error in git status for {gpath}: {errstr}")                
            elif "nothing to commit" in outstr:
                count += 1                
                if dry:
                    print(f"\tDry: would delete {gpath}")
                else:
                    print(f"\tDeleting {gpath}/*")
                    subprocess.run(["rm", "-rf", gpath],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                print(f"\t!!!Project {gpath} has uncommitted changes, not deleting!!!")

            
    if count > 0:
        print()
    print(f"\tDeleted {count} projects")
    print("=====================================")
    return all_projects,archived
##################################################################################
