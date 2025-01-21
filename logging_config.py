import logging
import os
from datetime import datetime

def setup_logging():
    """Konfigurerer central logging for hele applikationen"""
    try:
        # Opret logs mappe hvis den ikke eksisterer
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Generer filnavn med dato
        log_filename = os.path.join('logs', f'rio_app_{datetime.now().strftime("%Y%m%d")}.log')
        
        # Konfigurer logging format
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()  # Også output til konsol
            ]
        )
        
        logging.info("Logging system initialiseret")
        
    except Exception as e:
        print(f"FEJL: Kunne ikke konfigurere logging: {str(e)}") 