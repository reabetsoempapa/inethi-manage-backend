# API for Management Backend

## Prerequisites
Ensure you have docker and python on your system.

Add your keycloak public key in the [keys](keys) folder and add a .env file in [backend](backend) as per [example.env](backend/backend/.env.example)

## Running the code
1. `cd backend`
2. `pip install -r requirements.txt`
3. `docker compose build --no-cache`
4. `docker compose up inethi-manage-mysql -d`
5. `docker compose up inethi-manage -d`