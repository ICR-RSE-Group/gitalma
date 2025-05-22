#Author: Rachel Alcraft
#Edit: 15-03-2025 - RA: Initial version

import subprocess
import os
import time
from pathlib import Path
from .scratch import Scratch
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
    if err.upper() == err.lower():
        err = ""
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
        if out.upper() == out.lower():
            out = ""
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
    server = params["server"]          
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
                        line = line.replace(f"{server.replace('https://','')}:",
                                            f"{server.replace('https://','')}/")
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