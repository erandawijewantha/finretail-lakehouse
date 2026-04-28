from __future__ import annotations

import logging
from pathlib import Path

def get_logger(name: str) -> logging.logger:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok = True)
    
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    ) 
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    file_handler = logging.FileHandler(log_dir / "finretail.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    
    return logger