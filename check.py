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

PRIVATE_TOKEN_GITLAB = 'HBkPMVNTR3EGqGyKJ3JJ'
PRIVATE_TOKEN_GITHUB = '5e6816a03b3feb4e1a1dab668a79db351447cd70'
PRIVATE_TOKEN_GITLABCOM = 'B6aqZ4C7Gv8tNUKQ1oBx'

LOCAL_GITLAB_URL = 'http://localhost:8000'
SERVER_PORT = 9999

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
    r = requests.get(LOCAL_GITLAB_URL+'/api/v4/version', headers=headerGitLab)
    gitlabLocalVersionString = json.loads(r.text)["version"]

    requestServer = json.loads(requests.get('https://api.github.com/repos/gitlabhq/gitlabhq/tags').text)    
    return isVersionEqual(gitlabLocalVersionString, requestServer, isJson=True)

#def isGitlabRunnerLatest():
#    allRunners = json.loads(requests.get(LOCAL_GITLAB_URL+'/api/v4/runners', headers=headerGitLab).text)
#    gl = gitlab.Gitlab('http://gitlab.com', private_token=PRIVATE_TOKEN_GITLABCOM)
#    for runnerFromAll in allRunners:
#        runner = json.loads(requests.get(LOCAL_GITLAB_URL+'/api/v4/runners/'+str(runnerFromAll["id"]), headers=headerGitLab).text)
#        return isVersionEqual(runner["version"], gl.projects.get(250833).releases.list(), isJson=False)

#print(isGitlabLatest())
#print(isDockerLatest())
#print(isGitlabRunnerLatest())



if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(SERVER_PORT)
    # Generate some requests.
    while True:
        g = Gauge("toolcheck_is_gitlab_latest", "0 if gitlab needs to be updated else 1")
        g.set(isGitlabLatest())

        g = Gauge("toolcheck_is_docker_latest", "0 if docker needs to be updated else 1")
        g.set(isDockerLatest())

        #g = Gauge("toolcheck_is_gitlab_runner_latest", "0 if gitlab-runner needs to be updated else 1")
        #g.set(isGitlabRunnerLatest())

        time.sleep(60*10)
