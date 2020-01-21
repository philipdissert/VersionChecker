You have to put your Accesstokens to those variables.

PRIVATE_TOKEN_GITLAB = ''
PRIVATE_TOKEN_GITHUB = ''
PRIVATE_TOKEN_GITLABCOM = ''

Make sure the port of your local gitlab-installation is correct.
You can change this in 

LOCAL_GITLAB_URL

If you start this it will show metrics on port 9999 on your localhost, to change this you can change the SERVER_PORT variable.

You have to start this on the machine where the gitlab-instance runs.

Install pip packages:
configparse
prometheus_client
PyGithub
python-gitlab
docker