from src import app

app.secret_key = "kahit ano"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
