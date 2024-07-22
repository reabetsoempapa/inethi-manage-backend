# API for Management Backend

## Prerequisites
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