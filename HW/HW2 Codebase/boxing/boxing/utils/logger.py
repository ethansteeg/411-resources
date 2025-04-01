import logging
import sys

from flask import current_app, has_request_context


def configure_logger(logger):
    """
    This function sets up a basic logging configuration that outputs log messages to stderr.
    It uses a formatter to include the timestamp, logger name, log level, and message in the output. 

    Args:
        logger (logging.Logger): The logger object to configure 

    """
    logger.setLevel(logging.DEBUG)
    logger.debug("Configuring logger...")

    # Create a console handler that logs to stderr
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)

    # Create a formatter with a timestamp
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add the formatter to the handler
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    # We also need to add the handler to the Flask logger
    if has_request_context():
        app_logger = current_app.logger
        for handler in app_logger.handlers:
            logger.addHandler(handler)