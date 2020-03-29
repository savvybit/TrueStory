# TrueStory

*Be your own journalist!*

Web platform and API for gathering and exposing similar but opposed news articles. This
lives into the Google Cloud Platform, but works and can be tested locally too.
(outside of GAE)


## Installation

#### Set up Google Cloud environment and tools

Make sure you have Python 2 installed and active in the system.

1. Follow the steps here: https://cloud.google.com/sdk/
2. Install App Engine tools:
```console
$ gcloud components install app-engine-python app-engine-python-extras cloud-datastore-emulator beta
$ gcloud components update  # from time to time
```

#### Clone repository and run server

```console
$ git clone https://gitlab.com/truestory-one/TrueStory.git
$ cd TrueStory
```

Before running it, in order to not have any conflicts with the `gcloud` suite, it's
recommended to play with the project in a virtual environment. Make sure you follow the
instructions [here](https://github.com/pyenv/pyenv) and also configure your *.bashrc*,
*.bash_profile* or *.profile* accordingly.

```console
$ brew install pyenv pyenv-virtualenv pyenv-virtualenvwrapper
$ pyenv install -l  # pick a 3.x version
$ pyenv install 3.8.2  # install the picked version like this
$ pyenv virtualenv 3.8.2 truestory  # creates a 3.8 venv named 'truestory'
$ pyenv local truestory  # sets it as the default venv for this project root
```

Now don't forget to configure the above virtual environment in your favorite IDE too
(as default interpreter).

Finally, install base requirements and the package, then run the Flask app:

```console
$ make && make install  # requirements and package installation
$ make run  # runs in production mode (with remote DB)
```

You can also develop & debug the server with:

```console
$ make develop  # symlinks package
$ make debug  # runs in development mode (remote development DB) OR
$ make debug-gae  # on-prem GAE development mode (local DB)
```

#### Run tests

This will also spawn a Datastore emulator in order to run DB related tests too.

```console
$ make test
```

If you want to retrieve and display one article from each of the saved RSS targets:

```console
$ make test-crawl
```


## Usage

#### Run CLI and explore various commands

```console
$ truestory --help
```

Computes the token given the e-mail address:

```console
$ truestory token hello@truestory.one
Token: d897703467a4fe7b958b68426f1721dd
Authorized: True
```

Crawl and save articles into the *development* remote database:

```console
$ truestory -v crawl -s
```

Put a `-h` after each command in order to see detailed info about it and what it does.

#### Other useful commands

```console
$ make update-source  # just updates the available site sources (from media bias data)
$ make update-rss  # updates sources first, then RSS targets (from targets JSON)
$ make clean  # shows what it cleans (dry run)
$ make clean YES=1  # safely cleans-up all git ignored files 
```


## Deployment

Run `gcloud init` (outside virtualenv, by operating from a `pyenv shell system` first)
for configuring GAE project settings.

Then simply run `$ make deploy` script  with any of the *develop* or *master* parameters
(representing app's preferred version), as following:

```console
$ make deploy  # default develop deployment without traffic redirect (no promotion)
$ make deploy DEPLOY_VERSION=master  # deploy into production (with promotion)
```

#### Notes

- Everything deployed into *master* will automatically be promoted, meaning that the
  entire traffic will be redirected in this version.
- Deployments under *develop* are not promoted, but they are accessible through URLs
  like https://develop-dot-truestory.appspot.com.
- Tests are using the **testing** namespace no matter if the remote or emulated
  Datastore is used.
- Local server will automatically have DEBUG mode activated and use the **development**
  Flask config, settings and Datastore namespace (so look for entities there if you're
  exploring the remote online Datastore console).  
- If you're asked for any credentials (using remote Datastore in development or
  production), don't forget to make them available like this:
  ```console
  $ export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials/TrueStory-83153701f337.json"
  ```
  *Ask Cosmin for the JSON file, then configure it in the Makefile and keep it
  private.*

----

* Source: https://gitlab.com/truestory-one/TrueStory.git
* License: MIT
* Contributors:
    + Cosmin Poieana \<cmin764@gmail.com\>
    + Irina Bejan \<irinam.bejan@gmail.com\>
