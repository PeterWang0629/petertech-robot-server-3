import library.server.configure as configure
import library as logger_
import library.server.fileio as fileio_

logger = logger_.Logger(configure.get_config("log_file", "/data/log.txt"))
fileio = fileio_.FileIO()

logger.run()
fileio.run()
