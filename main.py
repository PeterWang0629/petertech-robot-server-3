from waitress import serve
import sys
from tasks import *

global app
sys.stdout = None
if __name__ == "__main__":
    PORT = 1453
    logger.log("INFO", "Logger and Fileio startup complete. Starting Waitress Server.")
    logger.log("INFO", "Server running on port", PORT)
    from controller import create_app
    app = create_app('dev')
    # app.run(threaded=True, host="0.0.0.0", port=PORT)
    serve(app, host="0.0.0.0", port=PORT)