import os
import logging
import logging.config
from enum import Enum
from utils import AgentState

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
    def save_final_io(report:AgentState):
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
            copy_file(report["report_generation_results"]["plot_filename"], os.path.join(final_log_directory,'plot.png'))
            final_output = report["data_storytelling_results"] #TODO
        except:
            final_output = report["answer_generation"]

        report_file = os.path.join(final_log_directory, "final_output.txt")
        log_message = f"human: {report['question']}\n\nAI: {final_output}"

        with open(report_file, "w") as f:
            f.write(log_message)

        final_io_logger.info(log_message)
