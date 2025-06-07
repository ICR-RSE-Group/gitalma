import os
from pathlib import Path
import requests

class GitLabAPI:
    def __init__(self, group_id, server, iswikis):
        self.repo = ""
        self.group_id = int(group_id)
        self.repo_len = 0
        self.url = server
        self.iswikis = iswikis
        home = str(Path.home())
    
        if "icr.ac.uk" in server:
            token_path = home + "/gitlab_token.txt"
        else:
            token_path = f"{home}/{server.replace('/','').replace('https','').replace(':','').replace('.','')}_gitalma_token.txt"
                
        if not os.path.exists(token_path):
            print("You need to generate a gitlab personal token and save it to:")
            print("Toekn path=", token_path)
            print("See here for how to generate a token:")
            print("https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html")
            self.ok = False
            exit()
        else:            
            with open(token_path, 'r') as f:
                self.token = f.read().strip()
            self.headers = {
                "PRIVATE-TOKEN": self.token
            }                                                                        
            self.repo = ""
            self.repo_len = 0
            if int(group_id) != -1:
                self.repo = self.get_repo_from_id(group_id)
                if self.repo == None:
                    print("Group ID not found")
                    exit()
                self.repo_len = len(self.repo.split("/"))            
    ##################################################################################
    def get_id_repo(self):
        return self.group_id, self.repo
    ##################################################################################
    def list_projects(self,):
        """List all projects in the GitLab instance."""        
        projects = []
        arch_projects = []        
        urls = [f"{self.url}/api/v4/groups/{self.group_id}/projects"]        
        #if self.iswikis:
        #    urls.append(f"{self.url}/api/v4/groups/{self.group_id}/wikis")
        try:        
            for gitlab_url in urls:            
                page_int = 0            
                got_pages = True
                print("Fetching projects for", gitlab_url, end=" ", flush=True)
                while got_pages:                
                    got_pages = False
                    page_int += 1
                    print("...", end="", flush=True)
                    response = requests.get(gitlab_url, headers=self.headers, data={"per_page":100,"page": page_int, "include_subgroups" : True})                
                    response.raise_for_status()
                    current_path = ""
                    if response.status_code == 200:
                        if len(response.json()) == 0:
                            print("")
                        for val in response.json():                                                
                            proj_id = val["id"]
                            http_url_to_repo = val["http_url_to_repo"]
                            path_with_namespace = val["path_with_namespace"]
                            archived = val["archived"]                        
                            if archived:                                                        
                                arch_projects.append((http_url_to_repo, proj_id,path_with_namespace))
                            else:                            
                                projects.append((http_url_to_repo, proj_id,path_with_namespace))
                            got_pages = True                
                    else:
                        print("Failed to fetch projects: ",response.status_code)                                    
            
            # Try adding wikis if requested
            if self.iswikis:
                print("Fetching wikis for", gitlab_url, flush=True)
                wiki_projects = []
                for project in projects:
                    url = project[0]
                    proj_id = project[1]
                    ppath = project[2]
                    gitlab_url = f"{self.url}/api/v4/projects/{proj_id}/wikis"
                    pages = 0
                    response = requests.get(gitlab_url, headers=self.headers, data={"per_page":100,"page": 1})
                    if response.status_code == 200:                                                
                        for val in response.json():
                            pages += 1
                    if pages > 0:                            
                        #print("wiki for project ID:", proj_id, project[2])                        
                        gpath_wiki = f"{ppath}.wiki"
                        wiki_url = url.replace(".git", ".wiki.git")
                        wiki_projects.append((wiki_url, proj_id, gpath_wiki))
                                            
                for wp in wiki_projects:                
                    projects.append(wp)
            return projects, arch_projects
        except Exception as e:
            print("!!! Failed to fetch projects: ",e)
            if e.response.status_code == 401:
                print("!!! Your Gitlab API token might be expired !!!")
            print("!!! Not safe to continue, exiting !!!")            
            exit()
    ##################################################################################        
    def get_repo_from_id(self, group_id):
        gitlab_url = f"{self.url}/api/v4/groups/{group_id}"        
        response = requests.get(gitlab_url, headers=self.headers, data={"include_subgroups" : False, "with_projects" : False})
        if response.status_code == 200:
            print("Group ID:",group_id,"is",response.json()["full_path"])    
            return response.json()["full_path"]
        else:
            return None
    ##################################################################################                
    def list_groups(self):
        """List all groups in the GitLab instance."""        
        groups = []     
        gitlab_url = f"{self.url}/api/v4/groups/{self.group_id}/subgroups"
        page_int = 0
        got_pages = True
        print("Fetching groups for", gitlab_url, end=" ", flush=True)
        while got_pages:                            
            page_int += 1
            print("...", end="", flush=True)
            response = requests.get(gitlab_url, headers=self.headers, data={"page":page_int, "include_subgroups" : True})
            if response.status_code == 200:
                if len(response.json()) == 0:
                    got_pages = False
                for val in response.json():                                                    
                    full_path = val["full_path"]                    
                    groups.append(full_path)                                                        
            else:
                print(f"Failed to fetch projects: {response.status_code}")
                got_pages = False
        print("")
        return groups        
    ##################################################################################
    def tokenise_server(self, server):
        git_server = server.replace("https://",f"https://oauth2:{self.token}@")
        return git_server