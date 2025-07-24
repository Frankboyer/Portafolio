import logging
import sys
from datetime import datetime
from typing import Optional

def setup_logger(name: str, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """Configura logger con manejo de archivo y consola"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Formato común
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo si se especifica
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def log_error(logger: logging.Logger, error: Exception, context: str = "") -> None:
    """Registra errores con contexto"""
    error_msg = f"{context}: {str(error)}" if context else str(error)
    logger.error(error_msg, exc_info=True)

def log_simulation(logger: logging.Logger, simulation_params: Dict[str, Any], results: Dict[str, Any]) -> None:
    """Registra resultados de simulación"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "parameters": simulation_params,
        "results": results
    }
    logger.info(f"Simulation completed: {log_entry}")
