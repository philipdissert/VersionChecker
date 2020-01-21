from github import Github
from prometheus_client import start_http_server, Info, Gauge
import time
import docker
import re
import json
import subprocess
import requests 
import gitlab
import configparser

client = docker.from_env()

PRIVATE_TOKEN_GITLAB = ''
PRIVATE_TOKEN_GITHUB = ''
PRIVATE_TOKEN_GITLABCOM = ''

LOCAL_GITLAB_URL = 'http://localhost:8000'
SERVER_PORT = 9999

try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    PRIVATE_TOKEN_GITLAB = str(config['KEYS']['PRIVATE_TOKEN_GITLAB'])
    PRIVATE_TOKEN_GITHUB = str(config['KEYS']['PRIVATE_TOKEN_GITHUB'])
    PRIVATE_TOKEN_GITLABCOM = str(config['KEYS']['PRIVATE_TOKEN_GITLABCOM'])
except:
    print("Config config.ini could not get parsed")
    exit()

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

def isDockerLatest():
    gitHubVersion = ''
    try:
        github = Github(PRIVATE_TOKEN_GITHUB)
        gitHubVersion = github.get_repo("docker/docker-ce").get_releases()[0].title    
    except:
        print("Error while checking docker-repo. Do you have internet? Is your github.com key valid?")
        raise

    clientVersion = ''
    try:
        clientVersionWithTag = client.version()["Version"]
        clientVersionRegex = re.search("[0-9\.]*",clientVersionWithTag)
        clientVersion = clientVersionRegex.group(0)
    except:
        print("Error while checking lokal docker, does it run? Does the libary work?")
        raise

    if clientVersion.__eq__(gitHubVersion):
        return True
    else:
        return False
    

def isGitlabLatest():
    r = requests.get(LOCAL_GITLAB_URL+'/api/v4/version', headers=headerGitLab)
    gitlabLocalVersionString = ''
    requestServer = ''
    try:
        gitlabLocalVersionString = json.loads(r.text)["version"]
    except:
        print("Local gitlab error does it run? Is the key valid?")
        raise
            
    requestServer = json.loads(requests.get('https://api.github.com/repos/gitlabhq/gitlabhq/tags').text)
    return isVersionEqual(gitlabLocalVersionString, requestServer, isJson=True)

def isGitlabRunnerLatest():
    localVersions = []

    allRunners = json.loads(requests.get(LOCAL_GITLAB_URL+'/api/v4/runners', headers=headerGitLab).text)
    gl = gitlab.Gitlab('http://gitlab.com', private_token=PRIVATE_TOKEN_GITLABCOM)            
    for runnerFromAll in allRunners:
        runner = {}
        try:
            runner = json.loads(requests.get(LOCAL_GITLAB_URL+'/api/v4/runners/'+str(runnerFromAll["id"]), headers=headerGitLab).text)
        except:
            print("Local gitlab error does it run? Is the key valid?")
            raise
        try:
            localVersions.append(isVersionEqual(runner["version"], gl.projects.get(250833).releases.list(), isJson=False))
        except:
            print("GitLab.com error do you have internet? Is the key valid?")
            raise

    
    return localVersions

if __name__ == '__main__':

    # Start up the server to expose the metrics.
    start_http_server(SERVER_PORT)
    # Generate some requests.
    while True:
        try:
            g = Gauge("toolcheck_is_gitlab_latest", "0 if gitlab needs to be updated else 1")
            g.set(isGitlabLatest())
        except:
            print("toolcheck_is_gitlab_latest will not get shown")

        try:
            g = Gauge("toolcheck_is_docker_latest", "0 if docker needs to be updated else 1")
            g.set(isDockerLatest())
        except:
            print("toolcheck_is_docker_latest will not get shown")
        
        try:
            runnercount = 0
            for runnerBoolean in isGitlabRunnerLatest():
                g = Gauge("toolcheck_is_gitlab_runner_latest_"+ str(runnercount), "0 if gitlab-runner needs to be updated else 1")
                g.set(runnerBoolean)
                runnercount = runnercount + 1
        except:            
            print("toolcheck_is_gitlabrunner_latest will not get shown")

        time.sleep(60*10)
