import logging, os

def get_logger(name: str='mbx', level: str|int=None) -> logging.Logger:
    lv = level if level is not None else os.getenv('MBX_LOG_LEVEL','INFO')
    lg = logging.getLogger(name)
    if not lg.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s'))
        lg.addHandler(h)
    lg.setLevel(lv)
    return lg
