### Overview
Purpose of the application is run a sample web service with two endpoints:

1. **/messages**  takes a message as a POST and returns the SHA256 hash digest
of that message (in hexadecimal format)
2. **/messages/\<hash\>**  takes a GET request that returns the original message. A request to a non-existent <hash> returns a 404 error.

It utilizes python 3 and the [flask](http://flask.pocoo.org/) module.
#### SSL Note
By default the application will utilize SSL to serve it's' endpoints. If you want you can generate your own private key and cert (there are some defaults ones in the repo):

	openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

#### Building a Docker Image
To run the test app, just clone this repo:

	git clone http://github.com/elatov/simple-flask-app

and go inside the checked out repo:

	<> cd test-flask-app

Then on a machine that has **docker** installed (install instructions for docker are available [here](https://docs.docker.com/install/linux/docker-ce/ubuntu/)), you can build a docker image. It will look similar to this:

	<> docker build -t test-flask .
	Sending build context to Docker daemon 26.62 kB
	Step 1/5 : FROM python:3
	 ---> d21927554614
	Step 2/5 : COPY app app
	 ---> 9fa33963cb79
	Removing intermediate container 7628cd3f530c
	Step 3/5 : WORKDIR app
	 ---> c85b8edc8151
	Removing intermediate container 0e3e905ec706
	Step 4/5 : RUN pip install -r requirements.txt
	 ---> Running in b3dc807b1b79
	Collecting flask (from -r requirements.txt (line 1))
	  Downloading Flask-0.12.2-py2.py3-none-any.whl (83kB)
	Collecting Werkzeug>=0.7 (from flask->-r requirements.txt (line 1))
	  Downloading Werkzeug-0.14.1-py2.py3-none-any.whl (322kB)
	Collecting Jinja2>=2.4 (from flask->-r requirements.txt (line 1))
	  Downloading Jinja2-2.10-py2.py3-none-any.whl (126kB)
	Collecting click>=2.0 (from flask->-r requirements.txt (line 1))
	  Downloading click-6.7-py2.py3-none-any.whl (71kB)
	Collecting itsdangerous>=0.21 (from flask->-r requirements.txt (line 1))
	  Downloading itsdangerous-0.24.tar.gz (46kB)
	Collecting MarkupSafe>=0.23 (from Jinja2>=2.4->flask->-r requirements.txt (line 1))
	  Downloading MarkupSafe-1.0.tar.gz
	Building wheels for collected packages: itsdangerous, MarkupSafe
	  Running setup.py bdist_wheel for itsdangerous: started
	  Running setup.py bdist_wheel for itsdangerous: finished with status 'done'
	  Stored in directory: /root/.cache/pip/wheels/fc/a8/66/24d655233c757e178d45dea2de22a04c6d92766abfb741129a
	  Running setup.py bdist_wheel for MarkupSafe: started
	  Running setup.py bdist_wheel for MarkupSafe: finished with status 'done'
	  Stored in directory: /root/.cache/pip/wheels/88/a7/30/e39a54a87bcbe25308fa3ca64e8ddc75d9b3e5afa21ee32d57
	Successfully built itsdangerous MarkupSafe
	Installing collected packages: Werkzeug, MarkupSafe, Jinja2, click, itsdangerous, flask
	Successfully installed Jinja2-2.10 MarkupSafe-1.0 Werkzeug-0.14.1 click-6.7 flask-0.12.2 itsdangerous-0.24
	 ---> b419eef3d10e
	Removing intermediate container b3dc807b1b79
	Step 5/5 : CMD python app.py
	 ---> Running in 3ea08f7df4ba
	 ---> 51441f73c8c3
	Removing intermediate container 3ea08f7df4ba
	Successfully built 51441f73c8c3

And you will see the newly created image on your docker host:

	<> docker images test-flask
	REPOSITORY     TAG      IMAGE ID       CREATED              SIZE
	test-flask     latest   19a1cf8cdf3b   About a minute ago   698 MB

### Launch the Docker Image with Docker-Compose
Then lastly you can use **docker-compose** (install instructions for docker-compose are [here](https://docs.docker.com/compose/install/)) to start the image/container

	<> docker-compose up -d
	Creating flask-app

You can confirm it's running by running the following:

	<> docker-compose ps
	  Name         Command      State                Ports
	--------------------------------------------------------------------
	flask-app   python app.py   Up      0.0.0.0:5000->5000/tcp, 8000/tcp

### Testing Out the Application
At this point you can send sample commands to the application with [curl](https://curl.haxx.se/docs/manpage.html):

	<> curl --cacert app/cert.pem  -X POST -H "Content-Type: application/json" -d '{"message": "foo"}' https://localhost:5000/messages
	{"digest": "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"}

And you can query by the digest to find the message:

	<> curl --cacert app/cert.pem  -X GET  https://localhost:5000/messages/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae
	{"message": "foo"}

Quering a non-existent digest will return a 404:

	<> curl -i --cacert app/cert.pem  -X GET  https://localhost:5000/messages/2c26b46b68ffc68ff
	HTTP/1.0 404 NOT FOUND
	Content-Type: application/json
	Content-Length: 32
	Server: Werkzeug/0.14.1 Python/3.6.4
	Date: Sat, 17 Mar 2018 15:10:32 GMT
	
	{"err_msg": "Message not found"}%

And you can checkout the logs from the application like so:

	<> docker-compose logs -f
	Attaching to flask-app
	flask-app     |  * Running on https://0.0.0.0:5000/ (Press CTRL+C to quit)
	flask-app     | 172.17.0.1 - - [17/Mar/2018 15:09:40] "POST /messages HTTP/1.1" 201 -
	flask-app     | 172.17.0.1 - - [17/Mar/2018 15:09:51] "GET /messages/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae HTTP/1.1" 200 -
	flask-app     | 172.17.0.1 - - [17/Mar/2018 15:09:59] "GET /messages/2c26b46b68ffc68ff HTTP/1.1" 404 -
	flask-app     | 172.17.0.1 - - [17/Mar/2018 15:10:07] "GET /messages/2c26b46b68ffc68ff HTTP/1.1" 404 -
	flask-app     | 172.17.0.1 - - [17/Mar/2018 15:10:32] "GET /messages/2c26b46b68ffc68ff HTTP/1.1" 404 -
	flask-app     | 172.17.0.1 - - [17/Mar/2018 15:12:03] "GET /messages/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa HTTP/1.1" 404 -
	flask-app     | 172.17.0.1 - - [17/Mar/2018 15:12:03] "POST /messages HTTP/1.1" 201 -
	flask-app     | 172.17.0.1 - - [17/Mar/2018 15:12:03] "GET /messages/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae HTTP/1.1" 200 -
	flask-app     | 172.17.0.1 - - [17/Mar/2018 15:12:03] "POST /messages HTTP/1.1" 201 -
	flask-app     | 172.17.0.1 - - [17/Mar/2018 15:12:03] "GET /messages/fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9 HTTP/1.1" 200 -
	flask-app     | 172.17.0.1 - - [17/Mar/2018 15:12:03] "GET /messages/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae HTTP/1.1" 200 -

#### Docker-compose logging
In the **docker-compose.yml** file, I have the following section:

	logging:
	      driver: "json-file"
	      options:
	        max-size: "12m"
	        max-file: "5"

This will rotate the logs after they reach 12m and it will keep 5 of those logs. You can check out where all the log files are for that container, by running `docker inspect`:

	<> docker inspect flask-app | grep LogPath
	        "LogPath": "/var/lib/docker/containers/b224b578dc500a0715957e0ffdbec960fe8588d45a5e595dc3d42f6b1fd6ce04/b224b578dc500a0715957e0ffdbec960fe8588d45a5e595dc3d42f6b1fd6ce04-json.log",

And you will see similar output in that file:

	<> tail /var/lib/docker/containers/b224b578dc500a0715957e0ffdbec960fe8588d45a5e595dc3d42f6b1fd6ce04/b224b578dc500a0715957e0ffdbec960fe8588d45a5e595dc3d42f6b1fd6ce04-json.log
	[sudo] password for elatov:
	{"log":"172.17.0.1 - - [17/Mar/2018 15:09:51] \"GET /messages/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae HTTP/1.1\" 200 -\n","stream":"stderr","time":"2018-03-17T15:09:51.47950832Z"}
	{"log":"172.17.0.1 - - [17/Mar/2018 15:09:59] \"GET /messages/2c26b46b68ffc68ff HTTP/1.1\" 404 -\n","stream":"stderr","time":"2018-03-17T15:09:59.275791811Z"}
	{"log":"172.17.0.1 - - [17/Mar/2018 15:10:07] \"GET /messages/2c26b46b68ffc68ff HTTP/1.1\" 404 -\n","stream":"stderr","time":"2018-03-17T15:10:07.970795481Z"}
	{"log":"172.17.0.1 - - [17/Mar/2018 15:10:32] \"GET /messages/2c26b46b68ffc68ff HTTP/1.1\" 404 -\n","stream":"stderr","time":"2018-03-17T15:10:32.906107034Z"}
	{"log":"172.17.0.1 - - [17/Mar/2018 15:12:03] \"GET /messages/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa HTTP/1.1\" 404 -\n","stream":"stderr","time":"2018-03-17T15:12:03.759798076Z"}
	{"log":"172.17.0.1 - - [17/Mar/2018 15:12:03] \"POST /messages HTTP/1.1\" 201 -\n","stream":"stderr","time":"2018-03-17T15:12:03.777279402Z"}
	{"log":"172.17.0.1 - - [17/Mar/2018 15:12:03] \"GET /messages/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae HTTP/1.1\" 200 -\n","stream":"stderr","time":"2018-03-17T15:12:03.793606438Z"}
	{"log":"172.17.0.1 - - [17/Mar/2018 15:12:03] \"POST /messages HTTP/1.1\" 201 -\n","stream":"stderr","time":"2018-03-17T15:12:03.809901231Z"}
	{"log":"172.17.0.1 - - [17/Mar/2018 15:12:03] \"GET /messages/fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9 HTTP/1.1\" 200 -\n","stream":"stderr","time":"2018-03-17T15:12:03.825801468Z"}
	{"log":"172.17.0.1 - - [17/Mar/2018 15:12:03] \"GET /messages/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae HTTP/1.1\" 200 -\n","stream":"stderr","time":"2018-03-17T15:12:03.841734957Z"}

### Cleaning up
To stop the container run the following:

	<> docker-compose down
	Stopping flask-app ... done
	Removing flask-app ... done

Then you can also delete the built image:

	<> docker rmi test-flask
	Untagged: test-flask:latest
	Deleted: sha256:0573e5ce8687771dae72b5c9515a16c228f7ff2d2262039c3969bdfcd2294f9e
	Deleted: sha256:b577ca6e98b45a64f608769b48d330cf9cc217897abf476043a32e5ee224ed7e
	Deleted: sha256:284f969a72a5fdc20b4030543fe5cf563d7db843a303e2683dd4f7afc0c86a48
	Deleted: sha256:482536343dc0862814fb4bda812e9726f2dcffcb264912a35deb07fe23ffbf84
	Deleted: sha256:1cb107b2d90ad30ae1e4bbc20ca57b6faf6a29f3dd5ea5eeda07291212d4a624
	Deleted: sha256:6f1d35bf02b0ec1eb57a3733faf7f604659f092facd8ff9ec92248171e8794fc
	Deleted: sha256:c9e8d0b5cf3a11bb54ee4dfede26b844a660abb674cfa358db9c0acc17778e5a

And lastly you can remove the git repo:

	<> rm -r simple-flask-app/
	
That should be it.
### References
Good resources used during this app creation:

* [JSON File logging driver](https://docs.docker.com/config/containers/logging/json-file/)
* [python-flask-docker-hello-world](https://github.com/shekhargulati/python-flask-docker-hello-world) 
* [Running Your Flask Application Over HTTPS](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https) 
* [Flask API Exceptions](http://www.flaskapi.org/api-guide/exceptions/)
* [Implementing a RESTful Web API with Python & Flask ](http://blog.luisrei.com/articles/flaskrest.html)
* [Flask Quickstart](http://flask.pocoo.org/docs/0.12/quickstart/)