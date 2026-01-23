from app import AppEngine
from log.logconfig import setup_logging

if __name__ == "__main__":
    setup_logging()
    app = AppEngine()
    app.run()