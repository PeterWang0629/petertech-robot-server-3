import controller.libraries.server.configure as configure
import controller.libraries.server.logger as logger_
import controller.libraries.server.fileio as fileio_

logger = logger_.Logger(configure.get_config("log_file", "/data/log.txt"))
fileio = fileio_.FileIO()

logger.run()
fileio.run()
