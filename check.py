from github import Github
from prometheus_client import start_http_server, Info, Gauge
import time
import docker
import re
import json
import pprint
import subprocess
import requests 
import gitlab

pp = pprint.PrettyPrinter(indent=4)
client = docker.from_env()

PRIVATE_TOKEN_GITLAB = ''
PRIVATE_TOKEN_GITHUB = ''
PRIVATE_TOKEN_GITLABCOM = ''

headerGitLab = {
        'PRIVATE-TOKEN': PRIVATE_TOKEN_GITLAB
    }

def isVersionEqual(yourVersionString, otherVerionStringJsonList, isJson): 
    if(isJson):       
        result = filter(lambda x: not "pre" in x["name"] and not "rc" in x["name"],otherVerionStringJsonList)
        otherVersionString = result.__next__()["name"]
    else:
        result = filter(lambda x: not "pre" in x.name and not "rc" in x.name, otherVerionStringJsonList)
        otherVersionString = result.__next__().name    
    return ("v"+yourVersionString).__eq__(otherVersionString)

def isVersionEqual2(yourVersionString, otherVerionStringJsonList): 
    result = filter(lambda x: not "pre" in x["name"] and not "rc" in x["name"],otherVerionStringJsonList)   
    otherVersionString = result.__next__()["name"]
    return ("v"+yourVersionString).__eq__(otherVersionString)

def isDockerLatest():    
    github = Github(PRIVATE_TOKEN_GITHUB)
    gitHubVersion = github.get_repo("docker/docker-ce").get_releases()[0].title    
    clientVersionWithTag = client.version()["Version"]
    clientVersionRegex = re.search("[0-9\.]*",clientVersionWithTag)
    clientVersion = clientVersionRegex.group(0)
    if clientVersion.__eq__(gitHubVersion):
        return True
    else:
        return False

def isGitlabLatest():
    r = requests.get('http://localhost:8000/api/v4/version', headers=headerGitLab)
    gitlabLocalVersionString = json.loads(r.text)["version"]

    requestServer = json.loads(requests.get('https://api.github.com/repos/gitlabhq/gitlabhq/tags').text)    
    return isVersionEqual(gitlabLocalVersionString, requestServer, isJson=True)

def isGitlabRunnerLatest():
    allRunners = json.loads(requests.get('http://localhost:8000/api/v4/runners', headers=headerGitLab).text)
    gl = gitlab.Gitlab('http://gitlab.com', private_token=PRIVATE_TOKEN_GITLABCOM)
    for runnerFromAll in allRunners:
        runner = json.loads(requests.get('http://localhost:8000/api/v4/runners/'+str(runnerFromAll["id"]), headers=headerGitLab).text)
        return isVersionEqual(runner["version"], gl.projects.get(250833).releases.list(), isJson=False)

#print(isGitlabLatest())
#print(isDockerLatest())
#print(isGitlabRunnerLatest())



if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(9999)
    # Generate some requests.
    while True:
        g = Gauge("is_gitlab_latest", "0 if gitlab needs to be updated else 1")
        g.set(isGitlabLatest())

        g = Gauge("is_docker_latest", "0 if docker needs to be updated else 1")
        g.set(isDockerLatest())

        g = Gauge("is_gitlab_runner_latest", "0 if gitlab-runner needs to be updated else 1")
        g.set(isGitlabRunnerLatest())

        print("asgssag")

        time.sleep(60*10)
    
    








