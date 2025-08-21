import logging
import sys

def get_logger():
    logger = logging.getLogger("ndac-alerts")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    fh = logging.FileHandler("service.log")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
