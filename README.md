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

### External services

The management backend uses some 'external' services for config, authentication and monitoring, namely [RadiusDesk]('https://www.radiusdesk.com/'), [Keycloak]('https://www.keycloak.org/') and [Prometheus]('https://prometheus.io/'). For development, we can host these services locally and point the backend to their local URLs. These need to be setup and running first before running the backend.

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

#### Prometheus (TODO)

## Running the backend

If you're running the backend for the first time, you will have to migrate changes to the database with

```bash
python manage.py migrate --database=default
python manage.py migrate --database=metrics_db
```

You need to configure the backend to communicate with the keycloak server by registering both frontend and backend clients in the .env file, for example:

```bash
KEYCLOAK_URL="http://localhost:8000"
KEYCLOAK_REALM="inethi-global-services"
KEYCLOAK_CLIENT_ID="manage-backend"
KEYCLOAK_CLIENT_SECRET="<CLIENT_SECRET>"
DRF_KEYCLOAK_CLIENT_ID="manage-ui"
```

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

Add your keycloak public key in the [keys](keys) folder and add a .env file in [backend](backend) as per [example.env](backend/backend/.env.example)

### Running the code

1. `cd backend && pip install -r requirements.txt`
2. `docker compose build --no-cache`
3. `docker compose up inethi-manage-mysql -d`
4. `docker compose up inethi-manage -d`
