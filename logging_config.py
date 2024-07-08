import os
import logging
import logging.config
from enum import Enum
from utils import AgentState
import json

log_directory = "logs"
eval_log_directory = f"{log_directory}/eval_logs"

if not os.path.exists(log_directory):
    os.makedirs(log_directory, exist_ok=True)
if not os.path.exists(eval_log_directory):
    os.makedirs(eval_log_directory, exist_ok=True)


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
    "final_io_logger", os.path.join(eval_log_directory, "final_io.log"), format="%(message)s"
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
    def save_final_io(report: AgentState):
        files_number = len(os.listdir(eval_log_directory))
        final_log_directory = os.path.join(eval_log_directory, f'report_{files_number}')
        os.makedirs(final_log_directory, exist_ok=True)

        def copy_file(src, dst):
            if os.name == 'nt':  # Windows
                cmd = f'copy "{src}" "{dst}"'
            else:  # Unix/Linux
                cmd = f'cp "{src}" "{dst}"'
            os.system(cmd)
        
        try:
            # Copy Image
            plot_filename = report["plot_generator_results"]["plot_filename"]
            copy_file(plot_filename, os.path.join(final_log_directory, 'plot.png'))
            final_output = report["data_storytelling_results"]
        except:
            print("Error in saving final IO")
            return

        initial_input = report['question']
        log_message = {
            "initial_input": initial_input,
            "final_output": final_output,
            "image_path": os.path.join(final_log_directory, 'plot.png')
        }

        report_file = os.path.join(final_log_directory, "final_output.json")
        with open(report_file, "w") as f:
            json.dump(log_message, f, indent=4)

        final_io_logger.info(log_message)