import flask
from flask import Flask
import threading
from werkzeug.serving import make_server

class APIController():
    def __init__(self):
        self.app = Flask(__name__)

    def run(self):
        self.server = make_server("127.0.0.1", 5000, self.app)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print("✅ Flask server started on http://127.0.0.1:5000")

    def stop(self):
            if self.server:
                self.server.shutdown()
                self.thread.join()
                print("❌ Flask server stopped.")



if __name__ == "__main__":
    flask_app = APIController()
    flask_app.run()
    try:
        while True:
            pass  # Keep the script running
    except KeyboardInterrupt:
        print("\nStopping Flask app...")
        flask_app.stop()