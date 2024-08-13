# API for iNethi Management Backend

## Installation

Set up a virtual environment with by running

```bash
python -m venv .venv
```

from the command line. Now you can activate it with

```bash
source .venv/bin/activate
```

Next, install the dependencies (Django, Jose etc)

```bash
pip install -r requirements.txt
```

### Configuring external services

The management backend uses some 'external' services for config, authentication and monitoring, namely [RadiusDesk]('https://www.radiusdesk.com/'), [Keycloak]('https://www.keycloak.org/') and [Unifi]('https://unifi.ui.com/'). For development, we can host these services locally and point the backend to their local URLs. These need to be setup and running first before running the backend.

#### Keycloak

Keycloak manages user authorisation and authentication on both the backend and frontend.

Follow the instructions at https://www.keycloak.org/getting-started/getting-started-docker for getting a local keycloak server up and running in a Docker container. Create a new realm called 'inethi-global-services'. You'll need to add two new clients, one for the backend and one for the frontend, so that both can log in via keycloak.

Frontend: Add a client with ID 'manage-ui'. Leave most of the settings as they are i.e. no client authentication, standard flow etc. This is a public client, because the keycloak.js client doesn't support confidential clients. You'll have to configure some URLs, assuming the frontend is running at `http://localhost:3000`:

1. Home URL: `http://localhost:3000`
2. Valid Redirect URLs: `http://localhost:3000/*`
3. Valid post logout redirect URIs: `+` (Same as redirect URLs)
4. Web Origins: `+`

Backend: Add a client with ID 'manage-backend'. This can be a private client, so client authentication and authorization are checked. Similarly, you want to configure redirect urls, this time using the backend url:

1. Home URL: `http://localhost:8000`
2. Valid Redirect URLs: `http://localhost:8000/*`
3. Valid post logout redirect URIs: `+`
4. Web Origins: `+`

Lastly and add an admin user with a username of your choice. Assign this user a new role, called 'admin'. This user will be able to log in to the backend to access Django's admin interface.

#### Radiusdesk

The CommuNethi app is designed to run alongside a RadiusDesk server. It provides some existing functionality in a new UI as well as extended functionality. To avoid syncing errors, it connects to the same mysql database that is used by radiusdesk, which needs some extra configuration:

First follow the [instructions for running radiusdesk in a docker container]('https://www.radiusdesk.com/wiki24/install_docker'). Then make sure that the mariadb container exposes its database at port 3306, so that django can connect to it. This may involve editing radiusdesk's `docker-compose.yml` file.

Double check the database is exposed by running

```bash
mysql -h localhost -P 3306 -u rd --password=rd
```

## Configuring your environment

(Make sure you've read the above section first!)
Depending on which services you want to configure, you will have to update your `.env` file, typically with the locations of the locally running services If you're running services locally, they will likely be in standard locations, so the `.env.example` file should provide reasonable defaults. If you've deployed the backend somewhere, you will likely have to provide custom environment variables.

Most importantly, you will need to configure the database that your app uses by configuring the database url, e.g.

```bash
DATABASE_URL="sqlite:///home/erikpolzin/db.sqlite3"
```

(NOTE: When using sqlite make sure this file actually exists, even if it's blank - Django will populate it later when migrating. If you're using another database, check out the documentation at [django-environ]('https://django-environ.readthedocs.io/en/latest/types.html#environ-env-db-url') for the database url format)

### Pointing the backend to external services

At a minimum you will have to configure keycloak to handle authentication on the API and Django admin site, typically something along the lines of

```bash
KEYCLOAK_URL="http://localhost:8001"
KEYCLOAK_REALM="inethi-global-services"
KEYCLOAK_CLIENT_ID="manage-backend"
KEYCLOAK_CLIENT_SECRET="<CLIENT_SECRET>"
DRF_KEYCLOAK_CLIENT_ID="manage-ui"
```

NOTE: I've used `localhost:8001` for the keycloak server, since UniFi also binds at port `8080`, and the backend is running at `8000`.

If you have access to the radiusdesk database you can connect directly to it by setting the `RADIUSDESK_DB_URL` environment variable. If you're running locally it will be something along the lines of:

```bash
RADIUSDESK_DB_URL="mysql://rd:rd@127.0.0.1:3306/rd"
```

If you don't specify this parameter, you won't be able to sync data from radiusdesk, and freeradius accounting data won't be available.

## Configuring reverse proxies

Every couple of seconds, both MeshDesk and UniFi routers query their respective management servers for configurations, and provide device stats.
In order to keep this data in sync with our database, the backend has configured a reverse proxy for both types of device to query. Instead of sending data to unifi or radiusdesk, devices now send data to our API, which then forwards it to the correct management server. In order to do this, we need to know
where the Unifi & Radiusdesk servers are running, which we also need configured in the `.env` file.

Specify:

```bash
RADIUSDESK_URL="http://localhost:80"
UNIFI_URL="http://localhost:8080"
```

You need to make sure that our backend is set as the management server in the devices' config - for meshdesk routers this is specified in the `/etc/config/meshdesk` file, and for unifi nodes by the `set-inform` command.

## Running the backend

If you're running the backend for the first time, you will have to migrate changes to the database with

```bash
python manage.py migrate --database=default
python manage.py migrate --database=metrics_db
```

See the note in 'Configuring your environment' if you're using sqlite and the migration complains that the database file does not exist - you have to create if first!

Now you can run the server, using

```bash
python manage.py runserver
```

The base url should redirect you to the keycloak server, where you can log in using the credentials you set up initially. After that, you should be able to access the admin site.

### Running Celery beat

The backend sends periodic pings to its registered devices using [Celery]('https://docs.celeryq.dev/en/stable/getting-started/introduction.html'). To schedule periodic tasks and start a worker process, run

```bash
python -m celery -A backend beat -l info
python -m celery -A backend worker -l info
```

## Running in a Docker container

### Prerequisites

Ensure you have docker and python on your system.

Add your keycloak public key in the [keys](keys) folder and add a .env file in [backend](backend) as per [example.env](backend/backend/.env.example). Add a .env file to users and wallet in a similar way by checking the .env.example files in each directory.

## Running the code

Do the prerequisites first then:

1. `cd backend`
2. `docker compose up inethi-manage-mysql -d`
3. `docker compose build --no-cache`
4. `docker compose up inethi-manage -d`

## Notes

1. Check private key format: `openssl pkey -pubin -in keycloak_public.pem -text -noout`
