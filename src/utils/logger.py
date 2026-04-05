"""
日誌工具
統一系統日誌輸出格式
"""
import logging
import sys


def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """設定 logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger
