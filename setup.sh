#!/bin/bash
echo "Please, install python (>=3.9)..."
echo "You can find installing instructions in https://www.python.org/downloads/"""
read -r -p "Press any key to continue... " -n1 -s
echo "Installing requirements..."
pip3 install poetry
python3 -m virtualenv .venv
poetry env use .venv/lib/python3.9
poetry install

echo "Setting up environment..."
echo "Please, install PostgreSQL and add data about future DB to '.env' (you can find following example in '.env-example'):"
echo
cat .env-example
echo
echo
echo "You can find installing instructions in https://www.postgresql.org/download/"
read -r -p "Press any key to continue... " -n1 -s
echo
read -r -p "Do you want to create db automatically? [y/N] " response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    set -o allexport && source .env
    psql postgres -c "CREATE USER $POSTGRES_USER WITH ENCRYPTED PASSWORD '$POSTGRES_PASSWORD';"
    psql postgres -c "CREATE DATABASE $POSTGRES_DB;"
    psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB to $POSTGRES_DB;"
else
    set -o allexport && source .env
fi
set +o allexport
read -r -p "Set up is finished. Do you want to run server?  [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
  source .venv/bin/activate
  make migrations
  make run_server
else
  echo "You can run migrations manually using 'make migrations'"
  echo "You can run server manually using 'make run_server'"
  echo "For further instructions run 'make help'"
fi
