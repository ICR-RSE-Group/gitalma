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

__version__ = "0.1.0"

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
    __version__ = get_gitalma_version()
    if args.version:        
        print("GitAlma version:", __version__)
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
        print("===== GITALMA from the ICR RSE Team =====")        
        print("-Config repo params-")    
        if "repo" in repo_params:        
            print(f"\trepo: {repo_params['repo']}")    
        if "path" in repo_params:        
            print(f"\tpath: {repo_params['path']}")    
        if "server" in repo_params:        
            print(f"\tserver: {repo_params['server']}")
        print("GitAlma version:", __version__)        
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
    
