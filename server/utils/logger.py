import logging
import os
from datetime import datetime

class RatLogger:
    def __init__(self, log_dir="./logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # setup logging
        self.setup_logging()
        
    def setup_logging(self):
        # configure le logging
        log_filename = datetime.now().strftime("rat_server_%Y%m%d.log")
        log_path = os.path.join(self.log_dir, log_filename)
        
        # format des logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # handler pour fichier
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # handler pour console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)
        
        # logger principal
        logger = logging.getLogger('rat_server')
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        self.logger = logger
        
    def log_client_connection(self, client_id, addr, info=None):
        # log une connexion client
        self.logger.info(f"Client {client_id} connected from {addr[0]}:{addr[1]}")
        if info:
            self.logger.info(f"Client {client_id} info: {info}")
            
    def log_client_disconnection(self, client_id, reason=""):
        # log une deconnexion
        self.logger.info(f"Client {client_id} disconnected. Reason: {reason}")
        
    def log_command_execution(self, client_id, command, success=True, result=None):
        # log l'execution d'une commande
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"[{status}] Client {client_id} executed: {command}")
        
        if not success and result:
            self.logger.error(f"Command error for client {client_id}: {result}")
            
    def log_file_transfer(self, client_id, filename, direction, size=0):
        # log un transfert de fichier
        self.logger.info(f"File {direction} - Client {client_id}: {filename} ({size} bytes)")
        
    def log_error(self, message, exception=None):
        # log une erreur
        self.logger.error(message)
        if exception:
            self.logger.exception(f"Exception details: {exception}")
            
    def log_security_event(self, event_type, details):
        # log un evenement de securite
        self.logger.warning(f"SECURITY EVENT - {event_type}: {details}")