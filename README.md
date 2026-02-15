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

![](assests/demo.gif)

## Architecture

![Diagram](assests/diagram.svg)