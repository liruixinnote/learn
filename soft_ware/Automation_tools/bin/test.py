
import  logging
from  logging import  handlers

log(msg):
        logger = logging.getLogger("test.log")
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(settings.DEBUG_LOG, encoding="utf-8")
        fh.setLevel(logging.WARNING)
        fh_formatter = logging.Formatter('%(asctime)s  %(filename)s:%(lineno)d   - %(levelname)s: %(message)s')
        fh.setFormatter(fh_formatter)
        logger.addHandler(fh)
        logger.debug(msg)