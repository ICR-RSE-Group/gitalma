import os
from pathlib import Path
import requests

class GitHubAPI:
    def __init__(self, repos, server):
        self.projects = []
        for repo in repos:
            for key,val in repo.items():
                print(key,val)
                pr_nm = val.split("/")[-1].replace(".git","")
                self.projects.append((val,0,key + "/" + pr_nm))
                
                
    def list_projects(self):
        return self.projects
            
        
    ##################################################################################
    