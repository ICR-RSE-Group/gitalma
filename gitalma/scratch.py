import os
from pathlib import Path
import glob


class Scratch:
    def __init__(self, path):                
        self.path = path
        self.gitalma = False
        self.gitalmaparent = False
        self.get_home()
        self.gits = self.get_gits()        
    ##################################################################################
    def get_home(self):
        """Find the parent gitalma home."""                
        #Check if the given path is a Git repository or its child."""
        gitlabpath = Path(self.path).resolve()
        self.working = os.getcwd()
        self.home = None

        all_gitalmas = []
        child_gitalmas = []
        
        for gitlab_path in [gitlabpath, *gitlabpath.parents]:                        
            if os.path.exists(os.path.join(gitlab_path, ".gitalma")):                
                self.gitalma = True                      
                all_gitalmas.append(str(gitlab_path))                
        #remove home        
        if self.gitalma:
            self.home =  all_gitalmas[-1]                    
            x_alma = [x for x in all_gitalmas if str(x) != str(self.home)]            
            if len(x_alma) > 0 and self.gitalma:
                print(f"\tfound {len(x_alma)} sub gitalma homes in {self.home}")
                for xa in x_alma:
                    full_path = xa + "/.gitalma"                    
                    if os.path.exists(full_path):
                        print("\t\tdeleting sub gitalma home", full_path)
                        os.system(f"rm -rf {full_path}")
        else:
            # look for a child gitalma, use a recursive path to find a chhild gitalma
            gitalmas = glob.glob(f"{self.path}/**/.gitalma", recursive=True)            
            if len(gitalmas) > 0:
                print(f"\tfound {len(gitalmas)} gitalma repos beneath {self.path}")
                self.gitalmaparent = True
                child_gitalmas = [str(gitalmas[0])]
    ##################################################################################
    def get_gits(self, root = None):
        """Find all the gitalma homes in the parent directory."""
        if not root:
            gitlabpath = Path(self.path).resolve()        
        else:
            gitlabpath = Path(root).resolve()
        gits = []
        # find all the child folders that have a .git direcrorty        
        subfolders = [f for f in gitlabpath.iterdir() if f.is_dir()] + [gitlabpath]
        while len(subfolders) > 0:        
            subfolder = subfolders.pop()
            if os.path.exists(os.path.join(subfolder, ".git")):
                gits.append(str(subfolder))
            else:
                subfolders.extend([f for f in subfolder.iterdir() if f.is_dir()])
        for g in range(len(gits)):
            gits[g] = str(gits[g])
        # make sure this is a unique list
        gits = list(set(gits))
        # sort the list
        gits.sort()
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
        
        
    
        