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


def get_logger(name, dbg=False):
    """
    get logger
    """
    fmt_hdr = '%(asctime)s %(levelname)s '
    fmt_loc = '%(filename)s.%(name)s.%(funcName)s:%(lineno)d> '
    handler_fmt = Formatter(fmt_hdr + fmt_loc + '%(message)s',
                            datefmt='%H:%M:%S')

    console_handler = StreamHandler()
    console_handler.setFormatter(handler_fmt)

    logger = getLogger(name)

    # [Important !! ]
    # isinstance()では、boolもintと判定されるので、
    # 先に bool かどうかを判定する

    if isinstance(dbg, bool):
        if dbg:
            console_handler.setLevel(DEBUG)
            logger.setLevel(DEBUG)
        else:
            console_handler.setLevel(INFO)
            logger.setLevel(INFO)

    elif isinstance(dbg, int):
        console_handler.setLevel(dbg)
        logger.setLevel(dbg)

    else:
        raise ValueError('invalid `dbg` value: %s' % (dbg))

    logger.propagate = False
    logger.addHandler(console_handler)

    return logger
