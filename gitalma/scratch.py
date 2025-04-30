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
        subfolders = [f for f in gitlabpath.iterdir() if f.is_dir()] + [gitlabpath]
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
        
        
    
        