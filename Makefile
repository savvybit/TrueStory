# Simulate or really clean-up the entire project.
ifeq ($(YES),)
	clean_arg = -n
	clean_msg = "[!] Dry run, add YES=1 for a real clean."
else
	clean_arg = -fq
	clean_msg = "[i] Clean-up complete!"
endif

ifeq ($(NO_DEPS),)
	pip_install = pip3 install -Ur
else
	pip_install = @echo "Skip pip installing:"
endif

PORT = 8080
WORK_PATH = $(HOME)/Work/TrueStory
export WORK_PATH
GOOGLE_APPLICATION_CREDENTIALS = $(WORK_PATH)/TrueStory-83153701f337.json
export GOOGLE_APPLICATION_CREDENTIALS
_DATASTORE_ENV_YAML = $(WORK_PATH)/env.yaml
DEPLOY_VERSION = develop

.PHONY: test


all:
	# Install all required prerequisites before doing anything.
	$(pip_install) requirements.txt

install:
	# Just normally install the package(s).
	pip3 install -U . --no-cache-dir

run:
	# Run main server in production mode with Gunicorn (remote database).
	@echo "[i] Starting server with Gunicorn."
	gunicorn -b :$(PORT) truestory:app

debug: export FLASK_APP = truestory
debug: export FLASK_ENV = development
debug:
	# Run main server in development mode with Flask (remote database).
	@echo "[i] Starting server with Flask."
	flask run -p $(PORT)

debug-gae:
	# Run main server in development mode with GAE (local database).
	@echo "[i] Saving app data under $(WORK_PATH)."
	mkdir -p $(WORK_PATH)
	@echo "[i] Starting server with GAE."
	$(eval dev_appserver := $(shell which dev_appserver.py))
	@echo "[*] If system's 'python2' is not found then make sure you have" \
		"'pyenv-implicit' enabled."
	python2 $(dev_appserver) . -A truestory --log_level debug \
		--storage_path $(WORK_PATH) \
		--enable_console --support_datastore_emulator True \
        --datastore_emulator_port 8081 --env_var DATASTORE_EMULATOR_HOST=localhost:8081

test: export DATASTORE_ENV_YAML = $(_DATASTORE_ENV_YAML)
test:
	# Test the just installed package(s).
	$(pip_install) requirements-test.txt
	# Open local Datastore emulator.
	./bin/datastore-emulator.sh
	# Finally run the tests.
	pytest -r tests --disable-warnings

develop:
	# Prepare the environment and package(s) for development mode.
	$(pip_install) requirements-dev.txt
	pip3 install -Ue .

deploy:
	# Deploy to Google Cloud the current set-up.
	./bin/deploy.sh $(DEPLOY_VERSION)

update-source:
	# Update latest media bias sources in the database.
	truestory -v source update

update-rss: update-source
	# Update all RSS targets taken from the JSON configuration. (given source for side)
	truestory -v rss update -a

crawl-test: export NLP_ENABLED = 1
crawl-test:
	# Crawl one article from each target without saving. (testing purposes)
	truestory -v crawl -l 1

clean:
	# Do a Git based local ignores clean-up.
	git clean -dx -e ".*" $(clean_arg)
	@echo $(clean_msg)
