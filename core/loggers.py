import logging
from colorlog import ColoredFormatter
import requests

STATUS = 35
logging.addLevelName(STATUS, "STATUS")

def status(self, message, *args, **kwargs):
    if self.isEnabledFor(STATUS):
        self._log(STATUS, message, args, **kwargs)

logging.Logger.status = status

def create_colored_formatter():
    return ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(log_color)s%(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'STATUS': 'blue',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

class NtfyHandler(logging.Handler):
    def __init__(self, name, channel="sts"):
        super().__init__()
        self.name = name
        self.channel = channel
    
    def send_notification(self, message: str, title: str = "Logger", priority: str = "default"):
        url = f"https://ntfy.sh/{self.channel}"
        headers = {"Title": title, "Priority": priority}
        try:
            response = requests.post(url, data=message.encode("utf-8"), headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            pass

    def emit(self, record):
        log_entry = self.format(record)
        self.send_notification(log_entry, title=f"GRC: {self.name}", priority="default")

def setup_logger(name: str, level: int = logging.DEBUG, ntfy_channel: str = "sts") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    formatter = create_colored_formatter()
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    ntfy_handler = NtfyHandler(name, channel=ntfy_channel)
    ntfy_handler.setLevel(STATUS)
    ntfy_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(ntfy_handler)

    return logger

logger = setup_logger("GRC_logger")
