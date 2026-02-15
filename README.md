# codex - a simple ***code*** ***ex***ecution tool

## Overview 

**codex** is a simple code execution app. You  write code in one or more files, the resulting code is run on a server and the result is pres to you. Currently only Python is supported.

## Install & Setup

The app has only been tested on macOS, but should run on Linux. For Linux, ensure you have ```openssl``` installed.
Docker and Docker Compose are a prerequisite for running the app, so ensure you have them installed on your machine.

Then just run

```bash
source deploy.sh
```

And browse to ```localhost:3000``` to go to the app.

![](assets/demo.gif)

## Architecture

The diagram below shows the high-level overview of the app architecture. It is microservices based and uses JWT tokens as a simple authentication mechanism.
The main service is the API/gateway component. It will manage HTTP REST requests for tasks like authentication as well as Websockets connections for handling the code execution. Authentication details like username and hashed passwords are stored in Redis. When an authenticated user submits code, it is sent to API which bundles the code with metadata and deposits it as a job on a message queue. Then, a code runner instance will take a job and start running the code. Because there will be multiple instances/pods of the API and Code Runner running, we have to make sure that the API instance with the Websocket connection to the user communicates with the Code Runner instance that is running the user code. To achieve this we use a Redis Pub/Sub service so that both services can exchange events and listen to the one that is relevant for them. 

![Diagram](assets/diagram.svg)
