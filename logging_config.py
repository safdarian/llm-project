import logging
import os

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # General logging handler
    file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"), mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s [%(levelname)s] %(message)s'))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s [%(levelname)s] %(message)s'))
    
    # Adding handlers to the root logger
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            file_handler,
            console_handler
        ]
    )

setup_logging()