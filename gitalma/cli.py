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
from .init import *
from .gitlab import *
from .git import *
from .github import *
from .scratch import Scratch
from .versions import *

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
    parser.add_argument("-wikis", help="Whether to look for wikis too", type=bool)
        
    # The flags        
    parser.add_argument("--debug", help="outputs extra logs for debugging", action="store_true")
    parser.add_argument("--dry", help="report what would be done (mkdir, clone and pull) but don't do it", action="store_true")    
    parser.add_argument("--single", help="override multithreaded behaviour, stay in single thread.", action="store_true")
    parser.add_argument("--root", help="run from home path no matter where in the repo you are.", action="store_true")
    parser.add_argument("--minimal", help="choose to reduce output messages", action="store_true")
        
    args = parser.parse_args()
    thisversion = get_local_version()
    gversion = get_github_version()
    if args.version:        
        print("Local version:", thisversion)
        print("Github version:", gversion)
        exit()

    minimal = False
    if args.minimal:
        minimal = True                
    
    start_time = datetime.datetime.now()            
    cwd = os.getcwd()        
    scrch = Scratch(cwd)
    if not scrch.gitalma:
        scrch.home = str(scrch.path)
    new_params = init_args(scrch, args)
    repo_params = init_check_get(scrch,new_params)
    #########################################################################################
    if args.action[0] == "init":        
        if scrch.gitalma:
            print("Already initialised in", scrch.home)
            exit()
        elif scrch.gitalmaparent:            
            print("Can't init parent - there are child gitalma repositories below this")
            exit()
        else:            
            changed_params = init_save(new_params, repo_params)
            init_print(changed_params, init=True)
            exit()
    #########################################################################################
    if not scrch.gitalma:
        print("Not in a gitalma repository")
        if scrch.working.endswith("/bcrbioinformatics"):
            print("Initialising gitalma repository")
            params = {"path": scrch.working,
                      "home": scrch.working,
                      "subgroup":2879,
                      "source":"icr",
                      "server":"https://git.icr.ac.uk",
                      "protocol":"pat"}            
            params = init_save(params, params)
            init_print(params, init=True)
            exit()
        else:
            exit()    
    new_params = init_args(scrch, args)
    cmd_params = cmd_args(args)
    repo_params = init_check_get(scrch,new_params)
    clone_params = gl_clone_args(args,cmd_params)
    params = {}
    for key in cmd_params:
        params[key] = cmd_params[key]
    for key in repo_params:
        params[key] = repo_params[key]
    for key in clone_params:
        params[key] = clone_params[key]
    if "wikis" not in params:
        params["wikis"] = False
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
    elif not minimal:
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
    if args.root:
        params["path"] = params["home"]
        scrch = Scratch(params["path"])
    if args.action[0] == "info":        
        init_print(repo_params, init=False)
    elif args.action[0] == "update":        
        if params["source"] in ["gitlab","icr"]:
            print(f">> Check projects to delete --- ")
            all_projects,archived = gl_clone_clean(params, args.dry)
            to_clone, to_pull = gl_clone_projects(params, args.dry, args.debug, all_projects)                
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
        gl_clone_clean(params, args.dry)
    elif args.action[0] == "status":                    
        print(f">> Status projects---")
        git_pull_all(params, "status", args.dry, args.debug,None)
    elif args.action[0] == "history":                   
        print(f">> History projects---")
        git_pull_all(params, "history", args.dry, args.debug, None)
    elif args.action[0] == "change":
        if args.protocol:
            if not minimal:
                print(f">> Changing to {args.protocol}")
            token = None
            api = None
            if args.protocol == "pat" or params["source"] in ["gitlab","icr"]:                
                api = GitLabAPI(params["subgroup"], params["server"], params["wikis"], minimal)
                token = api.token
            git_change_protocol(params, args.protocol, args.dry, args.debug,token, minimal=minimal)
            changed_params = init_save(params, params, minimal, api)
            
        else:
            if not minimal:
                print(f">> No change supplied, exiting")                                        
                            
    #----------------------------------------------------
    end_time = datetime.datetime.now()    
    if not minimal:
        print("=====================================")
        print("Completed in ", end_time-start_time)
    
    
