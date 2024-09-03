# Import the 'Flask' class from the 'flask' library.
from flask import Flask, request
from dotenv import load_dotenv
import os
import psycopg2, psycopg2.extras

load_dotenv()

def get_db_connection():
    connection = psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        database=os.environ['POSTGRES_DB_NAME'],
        user=os.environ['POSTGRES_USER'],
        # password=os.environ['POSTGRES_PASSWORD']
    )
    return connection


# Initialize Flask
# We'll use the pre-defined global '__name__' variable to tell Flask where it is.
app = Flask(__name__)

# Define our route
# This syntax is using a Python decorator, which is essentially a succinct way to wrap a function in another function.
@app.route('/')
def home():
  return "Hello, world!"

# PETS ROUTES
# app.py
@app.route('/pets')
def index():
  connection = get_db_connection()
  cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

  # query
  query = "SELECT * FROM pets"
  cursor.execute(query)

  pets = cursor.fetchall()
  connection.close()
  return pets

@app.route('/pets', methods=['POST'])
def create_pet():
  try:
    new_pet = request.json

    # first grab the fields from the converted req.body
    name = new_pet['name']
    age = new_pet['age']
    breed = new_pet['breed']

    # connect to the database
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # setup the SQL query
    query = "INSERT INTO pets (name, age, breed) VALUES (%s, %s, %s) RETURNING *;"

    values = (name, age, breed)

    # execute the query and
    cursor.execute(query, values)
    new_pet = cursor.fetchone()

    # make the changes final
    connection.commit()
    connection.close()
    return new_pet, 201
  except Exception as e:
    return str(e), 400







  return new_pet

# Run our application, by default on port 5000
app.run()