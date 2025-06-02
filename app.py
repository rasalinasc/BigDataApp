from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import zipfile
import os


app = Flask(__name__)

# 1. Obtiene la URI desde una variable de entorno o usa una URI por defecto
mongo_uri = os.environ.get("MONGO_URI")
if not mongo_uri:
    mongo_uri = "mongodb+srv://rsalinasc:Ronald123@rsalinasc.4twj5.mongodb.net/?retryWrites=true&w=majority&appName=rsalinasc"

# 2. Función para conectar a Mongo
def connect_mongo():
    try:
        client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        print("MongoDB connection successful")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

# 3. Función principal (ruta de inicio)
@app.route('/', methods=['GET', 'POST'])
def index():
    client = connect_mongo()
    databases = []
    collections_data = []
    selected_db = None
    error_message = None

    if client:
        try:
            databases = client.list_database_names()

            if request.method == 'POST':
                selected_db = request.form.get('database')
                if selected_db:
                    collections_data = get_collections_data(client, selected_db)

        except Exception as e:
            error_message = "No es posible listar las bases de datos."
            print(f"Error listing databases: {e}")
        finally:
            client.close()
    else:
        error_message = "No se pudo conectar a MongoDB."

    return render_template(
        'index.html',
        databases=databases,
        selected_db=selected_db,
        collections_data=collections_data,
        error_message=error_message
    )

# 4. Función para obtener las colecciones de una base de datos
def get_collections_data(client, selected_db):
    collections_data = []
    try:
        db = client[selected_db]
        collections = db.list_collection_names()
        for index, collection_name in enumerate(collections):
            count = db[collection_name].count_documents({})
            collections_data.append({
                'index': index + 1,
                'name': collection_name,
                'count': count
            })
    except Exception as e:
        print(f"Error al obtener las colecciones de {selected_db}: {e}")

    return collections_data

# 5. Inicia el servidor
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
