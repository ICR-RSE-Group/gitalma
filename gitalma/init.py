#Author: Rachel Alcraft
#Edit: 15-03-2025 - RA: Initial version

import os
import yaml
from .api_gl import GitLabAPI

##################################################################################      
### Command line parsing ###
def init_args(scrch, args):
    params = {}    
    params["path"] = os.getcwd() if not args.path else args.path
    if not scrch.gitalma:    
        scrch.home = str(params["path"])
    params["home"] = scrch.home    
    params["source"] = "icr" if not args.source else args.source
    params["wikis"] = False if not args.wikis else args.wikis
    if str(params["wikis"]).lower() == "true":
        params["wikis"] = True
    elif str(params["wikis"]).lower() == "false":
        params["wikis"] = False
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
def init_save(new_params, orig_params, api=None):
    init_path = f"{new_params['home']}/.gitalma"
    os.makedirs(init_path, exist_ok=True)
    init_file = f"{new_params['home']}/.gitalma/init.yaml"
    changed_params = {}
    # put orig params in first then any overwrites
    for key in orig_params:
        changed_params[key] = orig_params[key]
    for key in new_params:                        
        if key in changed_params:
            if orig_params[key] != new_params[key]:
                print(f"Changing {key} from {orig_params[key]} to {new_params[key]}")
        if key == "home":
            changed_params[key] = str(new_params[key])
        elif key == "wikis" or key == "multi" or key == "root":
            if str(new_params[key]).lower() == "true":
                changed_params[key] = True
            elif str(new_params[key]).lower() == "false":
                changed_params[key] = False
            else:
                changed_params[key] = new_params[key]
        else:
            changed_params[key] = new_params[key]
    # now do a sanity check on the matching names of the path and groupip
    if changed_params["source"] in ["gitlab","icr"] and api is not None:
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
        
    

    
    
          
    
    
    
    
    
    
    
    