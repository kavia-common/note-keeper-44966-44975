from app import app

if __name__ == "__main__":
    # Bind to 0.0.0.0 for container use and run on port 3001
    app.run(host="0.0.0.0", port=3001)
