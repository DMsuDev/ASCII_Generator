from ascii_engine.app import AppEngine
from ascii_engine.log import setup_logging

if __name__ == "__main__":
    setup_logging()
    app = AppEngine()
    app.run()