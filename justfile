# start the server : on port : http://127.0.0.1:8000/
#  django admin panel after running the server : http://127.0.0.1:8000/admin/
dev: 
  python manage.py runserver

# activate the virtual environment ( venv ) :
venv: 
  venv\Scripts\activate

# apply changes from the models in the database :
makeMigrations: 
  python manage.py makemigrations

# create the super user account :
createUser: 
  python manage.py createsuperuser

#
migrate: 
  python manage.py migrate

# format the project
format:
  ruff format .

# lint the project
lint: 
  ruff check . --fix
