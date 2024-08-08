from flask import Flask, redirect, url_for, render_template, jsonify, request, session
import logging
from datetime import datetime


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://bjwell19:rxid41vFRAPgfxUZ@cluster0.t4psin3.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi("1"))

# Access your desired database
db = client["iEstetik"]

# Access your desired collection within that database
collection_user = db["User"]
collection_files = db["Files"]
collection_files_chunks = db["File_chunk"]

# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    logging.debug("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    logging.debug(e)


@app.route("/Dashboard")
def dash():
    return render_template("Dashboard.html")


@app.route("/")
def run():
    session.clear()
    return render_template("Login and Register.html")


files_data = {"fileName": None, "userData": None}


@app.route("/add_user", methods=["POST"])
def add():
    body_data = request.get_json()
    user_data = body_data["info"]

    userData = {
        "name": user_data.get("firstName"),
        "email": user_data.get("lastName"),
        "password": user_data.get("studentNumber"),
        "mobile number": user_data.get("mobileNumber"),
        "department": user_data.get("selectDepartment"),
    }
    file_name = body_data["file"]

    files_data["fileName"] = file_name
    files_data["userData"] = userData

    return jsonify({"message": "File metadata received successfully"}), 200

    if not files_data["fileName"]:
        return jsonify({"message": "Missing file name. Send file data first."}), 400

    file = request.files["file"]
    current_chunk = int(request.form["dzchunkindex"])
    total_chunks = int(request.form["dztotalchunkcount"])
    file_size = int(request.form["dztotalfilesize"])

    try:

        file_data = file.stream.read()
        if current_chunk == 0:
            collection_user.insert_one(files_data["userData"])

            collection_files.insert_one(
                {
                    "fileName": files_data["fileName"],
                    "fileLength": file_size,
                    "fileChunkSize": len(file_data),
                    "timestamp": datetime.utcnow(),
                }
            )

        collection_files_chunks.insert_one(
            {
                "fileName": files_data["fileName"],
                "current_chunk": current_chunk,
                "file_data": file_data,
            }
        )

        if current_chunk + 1 == total_chunks:
            existing_file = collection_files.find_one(
                {"fileName": files_data["fileName"]}
            )
            if existing_file is not None:
                existing_file_size = existing_file["fileLength"]
                if existing_file_size != file_size:
                    return jsonify({"message": "Size mismatch", "status": 500}), 500
                else:
                    return (
                        jsonify({"message": "File upload successful", "status": 200}),
                        200,
                    )

        return jsonify({"message": "File upload successful", "status": 200}), 200

    except Exception as e:
        logging.error(e)
        return (
            jsonify({"error": f"An error occurred while uploading the file - {e}"}),
            500,
        )


@app.route("/get", methods=["GET"])
def get_data():
    document_array = []
    projection = {"_id": 0}  # Exclude the _id field from the query results
    cursor = collection_user.find({}, projection)
    for document in cursor:
        document_array.append(document)

    return jsonify({"data": document_array}), 200


@app.route("/login", methods=["POST"])
def login():
    body = request.get_json()
    email = body["email"]
    password = body["password"]

    user = collection_user.find_one({"email": email})
    if user is not None:
        if password == user["password"]:
            session["user"] = user["username"]
            return jsonify({"message": "Login Success!!"}), 200
        else:
            return jsonify({"message": "!! Incorrect password !!"}), 401

    else:
        return jsonify({"message": "This user is not found"}), 404


@app.route("/logout")
def logout():
    session.clear()
    return "ok", 200


@app.route("/register", methods=["POST"])
def register():
    body = request.get_json()
    email = body["email"]
    username = body["username"]
    password = body["password"]

    user = collection_user.find_one({"email": email})
    if user is None:
        collection_user.insert_one(
            {"email": email, "username": username, "password": password}
        )
        return jsonify({"message": "Already Created!! please login"}), 200

    else:
        return jsonify({"message": "This user already exists"}), 404
