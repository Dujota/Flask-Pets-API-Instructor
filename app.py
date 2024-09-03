# Import the 'Flask' class from the 'flask' library.
from flask import Flask, request
from flask_cors import CORS
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

CORS(app)
# Define our route
# This syntax is using a Python decorator, which is essentially a succinct way to wrap a function in another function.
@app.route('/')
def home():
  return "Hello, world!"

# PETS ROUTES
# app.py
@app.route('/pets')
def index():
  try:
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # query
    query = "SELECT * FROM pets;"
    cursor.execute(query)

    pets = cursor.fetchall()
    connection.close()
    return pets, 200
  except Exception:
    return "Application Error", 500

@app.route('/pets', methods=['POST'])
def create_pet():
  try:
    pet_data = request.json
    # first grab the fields from the converted req.body
    name = pet_data['name']
    age = pet_data['age']
    breed = pet_data['breed']

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


@app.route('/pets/<pet_id>', methods=['GET'])
def show_pet(pet_id):
    try:
      # connect to the database
      connection = get_db_connection()
      cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

      # setup the SQL query
      query = "SELECT * FROM pets WHERE id = %s;"
      value = (pet_id)

      # execute the query
      cursor.execute(query, value)
      pet = cursor.fetchone()
      # check if the pet exists else return pet
      if pet is None:
        connection.close()
        return " Pet Not Found", 404
      else:
      # close the connection
        connection.close()
        return pet, 200
    except Exception as e:
      return str(e), 400

@app.route('/pets/<pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
  try:
     # connect to the database
      connection = get_db_connection()
      cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

       # setup the SQL query
      query = "DELETE FROM pets WHERE id = %s;"
      value = (pet_id)

      # execute the query
      cursor.execute(query, value)

      # make the changes final
      connection.commit()
      connection.close()
      return "Pet deleted successfully", 204

  except Exception as e:
    return str(e), 400

@app.route('/pets/<pet_id>', methods=['PUT'])
def update_pet(pet_id):
    try:
      # connect to the database
      connection = get_db_connection()
      cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

      # grab the fields from the converted req.body
      pet_data = request.json

      name = pet_data['name']
      age = pet_data['age']
      breed = pet_data['breed']

       # setup the SQL query
      query = "UPDATE pets set name = %s, age = %s, breed = %s WHERE id = %s RETURNING *;"
      value = (name, age, breed, pet_id)

      # execute the query
      cursor.execute(query, value)
      pet = cursor.fetchone()

      if pet is None:
        connection.close()
        return " Pet Not Found", 404
      else:
        # make the changes final
        connection.commit()
        connection.close()
        return pet, 202

    except Exception as e:
      return str(e), 400





# Run our application, by default on port 5000
app.run()