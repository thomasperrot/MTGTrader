#!/usr/bin/env bash

# wait for PSQL server to start
sleep 10

## Uses the user postgres, the only one that can currently run psql command
su postgres
## Creates the database mtg
psql --command "CREATE DATABASE mtg;"
## Creates user mtg and grant him privileges on mtg database
psql --command "CREATE USER mtg WITH PASSWORD 'mtgmtg';"
psql --command "ALTER ROLE mtg SET client_encoding TO 'utf8';"
psql --command "ALTER ROLE mtg SET default_transaction_isolation TO 'read committed';"
psql --command "ALTER ROLE mtg SET timezone TO 'UTC';"
psql --command "GRANT ALL PRIVILEGES ON DATABASE mtg TO mtg;"
