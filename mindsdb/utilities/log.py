import logging
import os
import sys
import traceback
from functools import partial
from logging.config import dictConfig

from mindsdb.utilities.config import Config


def configure_logging():
    logging_config = dict(
        version=1,
        formatters={
            "f": {
                "format": "%(asctime)s %(processName)15s %(levelname)-8s %(name)s: %(message)s"
            }
        },
        handlers={
            "h": {
                "class": "logging.StreamHandler",
                "formatter": "f",
                "level": logging.DEBUG,
            }
        },
        root={
            "handlers": ["h"],
            "level": logging.DEBUG,
        },
    )

    dictConfig(logging_config)


class LoggerWrapper(object):
    def __init__(self, writer_arr, default_writer_pos):
        self._writer_arr = writer_arr
        self.default_writer_pos = default_writer_pos

    def write(self, message):
        if len(message.strip(" \n")) == 0:
            return
        if "DEBUG:" in message:
            self._writer_arr[0](message)
        elif "INFO:" in message:
            self._writer_arr[1](message)
        elif "WARNING:" in message:
            self._writer_arr[2](message)
        elif "ERROR:" in message:
            self._writer_arr[3](message)
        else:
            self._writer_arr[self.default_writer_pos](message)

    def flush(self):
        pass

    def isatty(self):
        return True  # assumes terminal attachment

    def fileno(self):
        return 1  # stdout


# default logger
logger = logging.getLogger("dummy")


def initialize_log(config=None, logger_name="main", wrap_print=False):
    """Create new logger
    :param config: object, app config
    :param logger_name: str, name of logger
    :param wrap_print: bool, if true, then print() calls will be wrapped by log.debug() function.
    """
    global logger
    if config is None:
        config = Config().get_all()

    telemtry_enabled = os.getenv("CHECK_FOR_UPDATES", "1").lower() not in [
        "0",
        "false",
        "False",
    ]

    if telemtry_enabled:
        try:
            import sentry_sdk
            from sentry_sdk import add_breadcrumb, capture_message

            sentry_sdk.init(
                "https://29e64dbdf325404ebf95473d5f4a54d3@o404567.ingest.sentry.io/5633566",
                traces_sample_rate=0,  # Set to `1` to experiment with performance metrics
            )
        except (ImportError, ModuleNotFoundError) as e:
            raise Exception(
                f"to use telemetry please install 'pip install mindsdb[telemetry]': {e}"
            )

    log = logging.getLogger(f"mindsdb.{logger_name}")
    # log.propagate = False
    # log.setLevel(min(
    #     getattr(logging, config['log']['level']['console']),
    #     getattr(logging, config['log']['level']['file'])
    # ))
    # log.setLevel(logging.DEBUG)

    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # console_handler = logging.StreamHandler()
    # #console_handler.setLevel(config['log']['level'].get('console', logging.INFO))
    # console_handler.setLevel(logging.DEBUG)
    # console_handler.setFormatter(formatter)
    # log.addHandler(console_handler)

    # if wrap_print:
    #     pass
    # sys.stdout = LoggerWrapper([log.debug, log.info, log.warning, log.error], 1)
    # sys.stderr = LoggerWrapper([log.debug, log.info, log.warning, log.error], 3)

    # log.error = partial(log.error, exc_info=True)


def get_log(logger_name=None):
    if logger_name is None:
        return logging.getLogger("mindsdb")
    return logging.getLogger(f"mindsdb.{logger_name}")
