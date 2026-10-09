# Start Django development server.
# start the server : on port : http://127.0.0.1:8000/
#  django admin panel after running the server : http://127.0.0.1:8000/admin/
dev:
  python manage.py runserver

# Create the local Python virtual environment.
# activate the virtual environment ( venv ) :
venv:
  venv/Scripts/activate

# Install backend dependencies.
install:
  python -m pip install -r requirements.txt
install-dev:
  python -m pip install -r requirements-dev.txt


# Populate Oscar shipping countries used by checkout.
bootstrap:
  python manage.py bootstrap_store

# create the super user account :
# Create the store administrator.
createUser:
  python manage.py createsuperuser

# Run Django system checks.
check:
  python manage.py check

# Apply database migrations.
migrate:
  python manage.py migrate

# format the project
# Format Python files.
format:
  ruff format .

# lint the project
# and fix
# Run Ruff checks.
lint:
  ruff check . --fix
