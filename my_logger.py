#
# (c) 2020 Yoichi Tanibayashi
#
"""
my_logger.py
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021'

from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
# from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL

FMT_HDR = '%(asctime)s %(levelname)s '
FMT_LOC = '%(filename)s.%(name)s.%(funcName)s:%(lineno)d> '
HANDLER_FMT = Formatter(FMT_HDR + FMT_LOC + '%(message)s',
                        datefmt='%H:%M:%S')

CONSOLE_HANDLER = StreamHandler()
CONSOLE_HANDLER.setFormatter(HANDLER_FMT)
CONSOLE_HANDLER.setLevel(DEBUG)


def get_logger(name, dbg=False):
    """
    get logger
    """
    logger = getLogger(name)
    logger.propagate = False
    logger.addHandler(CONSOLE_HANDLER)
    logger.setLevel(INFO)

    # [Important !! ]
    # isinstance()では、boolもintと判定されるので、
    # 先に bool かどうかを判定する

    if isinstance(dbg, bool) and dbg:
        logger.setLevel(DEBUG)
        return logger

    if isinstance(dbg, int):
        logger.setLevel(dbg)
        return logger

    raise ValueError('invalid `dbg` value: %s' % (dbg))
