# Density

[![Build
Status](https://travis-ci.org/ADI-Labs/density.svg?branch=master)](https://travis-ci.org/ADI-Labs/density)

[Density](https://density.adicu.com) estimates how full different parts of
Columbia are, based on the number of devices connected to the WiFi (data
graciously provided by CUIT in coordination with ESC).


## Contributing

### Local Development

Density currently runs on Python 3.6.3 and PostgreSQL 9.6. Our Python
dependencies are managed via [Pipenv](https://docs.pipenv.org/). If you
have Python 3.6 already installed, just run:

```bash
pip install -U pipenv
pipenv install --dev
./scripts/bootstrap.sh
```

### Vagrant

If you don't know how to install Python 3.6.3 and PostgreSQL 9.6
yourself, we also have a [Vagrant](https://www.vagrantup.com/) setup. Go
to [Vagrant Downloads](https://www.vagrantup.com/downloads.html) to
download Vagrant, and then in the terminal run:

```bash
vagrant up
vagrant ssh
```

This should `ssh` you into `vagrant@vagrant` virtualmachine. Go to
`/vagrant` and then run `pipenv install --dev`.

### Environment variables

We use `.env` file (automatically loaded by `pipenv`) to handle
configuration. This should automatically be created for you when you run
`./scripts/bootstrap.sh` (or when Vagrant provisions itself).

In production, we use a different set of environment variables.

## Running the Server

```
pipenv run flask run
```

to start the server. If you're using Vagrant, you'll have to run:

```
pipenv run flask run --host=0.0.0.0
```

### Testing

We use `py.test` for testing and `flake8` for linting. All tests are defined
in `density/tests`. To run tests locally, in the app root directory you should
run:

```bash
pipenv run flake8
pipenv run py.test
```

We have [Travis CI](https://travis-ci.org/ADI-Labs/density/) set-up to enforce
passing tests.

### Deployment

Density is currently deployed on ADI's server via Docker (defined in the
`Dockerfile`). To build the Docker image locally, install Docker and run:

```bash
docker build -t density .
docker run --net=host -d density
```

To deploy new changes or features on the server, first push your changes to the master branch and check that it builds on Travis CI. Afterwards push your changes to the deploy branch. 

### Project Layout

```
.
├── API.md              -- API documentation
├── density
│   ├── config.py       -- Load configuration from `.env` file
│   ├── data.py         -- Raw data for rooms
│   ├── db.py           -- Handle all database access
│   ├── graphics.py     -- Build graphs for predictions
│   ├── __init__.py     -- Bulk of the app logic
│   ├── librarytimes.py -- Handle building hour display
│   ├── predict.py      -- Predictions for current day
│   ├── static/         -- Static assets for Flask
│   ├── templates/      -- Jinja2 templates for Flask
│   └── tests/          -- various tests
├── Dockerfile
├── Pipfile             -- List of Python dependencies
├── Pipfile.lock
├── README.md
├── scripts
│   ├── bootstrap.sh    -- Set-up PostgreSQL logic and `.env`
│   ├── drop.sql        -- Drop database
│   ├── dump.sql        -- Dump of database for development
│   ├── schema.sql      -- Database schema (for reference)
│   └── vagrant.sh      -- Script to setup Vagrant
├── setup.cfg           -- Setup for CI
└── Vagrantfile
```

## Mobile

We're in the process of developing an app that uses the Density API. It displays the same information about available space as the website and also provides users the option to set personal preferences (e.g. study time) through accounts accessible through their university email. The app is written in React Native, and it can be ported to Android without needing to change too much). The essential functionality of the app is in place now, and the IOS version will be released once some final bugs are addressed.

The app is divided into 3 pages: home, predictions, and settings. Home prompts the user to log in and then shows the same information as the Density homepage, and predictions shows the same information as the predictions page on the website. Settings lets users enter a preferred dining hall and library and visiting time for each.

### App Structure

All app-related material is found in /densityApp. Most of the custom code is in /densityApp/screen and /densityApp/components. App.js is just the entrypoint, and the rest is configuration options or boilerplate.

AuthLoadingScreen.js and LoginScreen.js handle the sign-in prompt. HomeScreen.js is the normal content of the home page (once the login pop-up has been dismissed). Link.js is the predictions page, and SettingsScreen.js is the settings page.

Fresh library data comes from the APIs exposed by the server, which are called in componentDidMount() in HomeScreen.js. and LinkScreen.js. They are calling different APIs. The predictions page uses a API that just returns the prediction for each building; the home page uses an earlier API that returns several pieces of information about each building, such as its start and close times.
