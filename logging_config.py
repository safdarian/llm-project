import os
import logging
import logging.config
from enum import Enum

log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)


def setup_logger(name, log_file, level=logging.INFO, format=None):
    handler = logging.FileHandler(log_file)
    handler.setLevel(level)
    if format:
        formatter = logging.Formatter(format)
        handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


flow_metric_logger = setup_logger(
    "flow_metric_logger",
    os.path.join(log_directory, "flow_metric.log"),
    format="%(asctime)s - %(message)s",
)
flow_logger = setup_logger(
    "flow_logger", os.path.join(log_directory, "flow_log.log"), format="%(message)s"
)
final_io_logger = setup_logger(
    "final_io_logger", os.path.join(log_directory, "final_io.log"), format="%(message)s"
)


class LogState(Enum):
    RESULT = "RESULT"
    START = "START"
    RESPONSE = "RESPONSE"
    FINISH = "FINISH"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LoggerManager:
    @staticmethod
    def log_flow_metric(node, state: LogState, content=None):
        log_message = f"[{node}] {state}"
        if content != None:
            log_message += f" - {content}"
        flow_metric_logger.info(log_message)

    @staticmethod
    def log_flow(message: str, node: str = None, state: LogState = None):
        log_message = message
        if node is not None:
            log_message = f"[{node}] " + log_message

            if state is not None:
                LoggerManager.log_flow_metric(node=node, state=state)

        flow_logger.info(log_message)

    @staticmethod
    def save_final_io(initial_input, final_output):
        input_dir = os.path.join(log_directory, "inputs")
        output_dir = os.path.join(log_directory, "outputs")
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        input_file = os.path.join(input_dir, "initial_input.txt")
        output_file = os.path.join(output_dir, "final_output.txt")

        with open(input_file, "w") as f:
            f.write(initial_input)

        with open(output_file, "w") as f:
            f.write(final_output)

        log_message = f"Initial input and final output saved.\nInitial input: {initial_input}\nFinal output: {final_output}"
        final_io_logger.info(log_message)
