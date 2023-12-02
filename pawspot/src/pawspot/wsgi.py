import os
from dotenv import load_dotenv
from pawspot_flask import app
load_dotenv()

if __name__ == '__main__':
    port = os.environ.get("SPOTIPY_PORT", 8080)

    app.run(threaded=True, debug=False, port=int(port))

