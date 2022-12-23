#! /bin/bash
printy() {
  printf "\e[33;1m%s\n" "$1"
}

print_no_colour() {
  printf "\e[0m%s\n" "$1"
}

# install psql + create db using .env
printy "Installing postgres..."
print_no_colour ""
#brew install libpq
#
#brew link --force libpq
#brew install postgresql
#
#brew services start postgresql
printy "Creating db and user..."
print_no_colour ""
set -o allexport && source .env
#psql postgres -c "CREATE USER $POSTGRES_USER WITH ENCRYPTED PASSWORD '$POSTGRES_PASSWORD';"
#psql postgres -c "CREATE DATABASE $POSTGRES_DB;"
#psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB to $POSTGRES_DB;"

printy "Installing python..."
print_no_colour ""
#brew install python
pip --version
# if doesn't work, run
# brew unlink python && brew link python
printy "Installing venv and requirements..."
print_no_colour ""
#pip install virtualenv
#python3 -m venv venv
source .venv/bin/activate
pip install -r requirements.txt
printy "Updating migrations..."
print_no_colour ""
alembic upgrade head
printy "Running app..."
printy "You can find docs at http://127.0.0.1:$APP_PORT/docs/"
print_no_colour ""
python -m uvicorn core.main:app --reload --port "$APP_PORT"
