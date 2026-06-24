import logging
import asyncio
from datetime import datetime
from collections import deque

log_history = deque(maxlen=100)

log_clients = set()


class HTMXConsoleHandler(logging.Handler):
    def emit(self, record):
        message = record.getMessage()
        time_str = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        css_class = "log-info"
        if record.levelno >= logging.ERROR:
            css_class = "log-error"
        elif record.levelno >= logging.WARNING:
            css_class = "log-warning"
        elif "succès" in message.lower() or "terminé" in message.lower():
            css_class = "log-success"

        html_log = f"<div class='log-line {css_class}'><span class='log-timestamp'>[{time_str}]</span> {message}</div>"
        sse_message = f"event: log\ndata: {html_log}\n\n"

        log_history.append(sse_message)

        for client_queue in list(log_clients):
            try:
                loop = asyncio.get_running_loop()
                loop.call_soon_threadsafe(client_queue.put_nowait, sse_message)
            except RuntimeError:
                pass


def _setup_logger():
    logger = logging.getLogger("AS_Downloader")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("downloads.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    web_handler = HTMXConsoleHandler()

    logger.addHandler(file_handler)
    logger.addHandler(web_handler)

    return logger


app_logger = _setup_logger()
