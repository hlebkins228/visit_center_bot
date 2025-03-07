import logging
from config import LOGFILE_PATH, DATE_FORMAT
import os
from datetime import datetime


class Logger:
    def __init__(self) -> None:
        if not os.path.exists(LOGFILE_PATH):
            os.mkdir(LOGFILE_PATH)

        logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s\n',
        filename=LOGFILE_PATH + f'{datetime.now().strftime(DATE_FORMAT)}.log',
        filemode='a')

        self.logger = logging
    
    def error_msg(self, msg: str) -> None:
        self.logger.error(msg)
        print(msg)
    
    def error_exp(self, e: Exception) -> None:
        self.logger.error(f"Error: {e}")
        print("error: ", e)
    
    def info(self, msg: str) -> None:
        self.logger.info(msg)


logger_client = Logger()
