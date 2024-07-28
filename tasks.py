import library.server.configure as configure
import library.server.logger as logger_
import library.server.fileio as fileio_

logger = logger_.Logger(configure.get_config("log_file", "log.txt"))
fileio = fileio_.FileIO()

logger.run()
fileio.run()
