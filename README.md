You have to put your Accesstokens in a config.ini File like example.ini.
Copy the whole file and put in your Accesstokens

Make sure the port of your local gitlab-installation is correct.
You can change this in 

LOCAL_GITLAB_URL

Make sure you have Python verion 3.5 or newer installed.

You have to install pip packages:

prometheus_client

PyGithub

python-gitlab

docker

If you start this it will show metrics on port 9999 on your localhost, to change this you can change the SERVER_PORT variable.

You have to start this on the machine where the gitlab-instance runs.

User python check.py to start the server or something like pthon3 check.py if your standard python has version 2.7