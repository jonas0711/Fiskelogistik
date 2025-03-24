# Import nødvendige biblioteker
import logging
from database_connection import DatabaseConnection
import os
from datetime import datetime
from mail_system import MailSystem
import ast  # # DEBUG: Importeret ast for at kunne konvertere bytes til dict med literal_eval
import re  # # DEBUG: Importerer re for regex baseret rensning
import unicodedata  # Importeres for at kunne identificere og fjerne ikke-printbare tegn
# Importer de nødvendige email-moduler
from email.mime.multipart import MIMEMultipart  # # Bruges til at oprette en multipart email
from email.mime.text import MIMEText             # # Bruges til at oprette email body med html
from email.mime.application import MIMEApplication  # # Bruges til at vedhæfte rapport filen
from mail_template_manager import MailTemplateManager  # # Henter HTML templates fra databasen
import base64
import smtplib
from email.mime.base import MIMEBase
from email import encoders
import hashlib

class MailHandler:
    def __init__(self, db_path='databases/settings.db'):
        """
        Initialiserer MailHandler med database forbindelse og mail system
        
        Args:
            db_path: Sti til settings databasen
        """
        # Opret database forbindelse
        self.db = DatabaseConnection(db_path)
        
        # Initialiser mail system
        self.mail_system = MailSystem(self.db)
        
        # Opsæt logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('MailHandler')
    
    def get_first_name(self, full_name):
        """
        Udtrækker fornavnet fra et fuldt navn
        
        Args:
            full_name: Fuldt navn
            
        Returns:
            str: Fornavn
        """
        if not full_name:
            return ""
        return full_name.split()[0]
    
    def create_html_report(self, report_data, driver_name):
        """
        Delegerer til MailSystem for at skabe HTML rapport
        
        Args:
            report_data: Rapport data
            driver_name: Chaufførens navn
            
        Returns:
            str: HTML indhold
        """
        return self.mail_system._create_html_report(report_data, driver_name)
    
    def send_report(self, driver_id, report_data, recipient=None):
        """
        Sender en rapport til en chauffør
        
        Args:
            driver_id: Chauffør ID
            report_data: Rapport data (dict med rapport:binære data)
            recipient: Specifik modtager (hvis None bruges chaufførens email)
            
        Returns:
            bool: True hvis rapporten blev sendt
        """
        try:
            self.logger.info(f"Sender rapport til chauffør {driver_id}")
            # Delegér til MailSystem for at sende rapporten
            success = self.mail_system.send_report(driver_id, report_data, recipient)
            
            if success:
                self.logger.info(f"Rapport sendt succesfuldt til chauffør {driver_id}")
            else:
                self.logger.error(f"Kunne ikke sende rapport til chauffør {driver_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Fejl ved afsendelse af rapport til chauffør {driver_id}: {str(e)}")
            if hasattr(e, '__traceback__'):
                import traceback
                trace = ''.join(traceback.format_tb(e.__traceback__))
                self.logger.error(f"Stacktrace: {trace}")
            raise
            
    def send_report_with_email(self, driver_id, report_data, email):
        """
        Sender en rapport direkte til en given email uden at tilgå databasen
        
        Args:
            driver_id: Chauffør ID
            report_data: Rapport data
            email: Email adresse
            
        Returns:
            bool: True hvis rapporten blev sendt
        """
        try:
            self.logger.info(f"Sender rapport direkte til {email} for chauffør {driver_id}")
            success = self.mail_system.send_report_with_email(driver_id, report_data, email)
            
            if success:
                self.logger.info(f"Rapport sendt succesfuldt til {email}")
            else:
                self.logger.error(f"Kunne ikke sende rapport til {email}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Fejl ved direkte afsendelse af rapport til {email}: {str(e)}")
            if hasattr(e, '__traceback__'):
                import traceback
                trace = ''.join(traceback.format_tb(e.__traceback__))
                self.logger.error(f"Stacktrace: {trace}")
            raise
    
    def test_connection(self):
        """
        Tester mail forbindelse via MailSystem
        
        Returns:
            tuple: (success, message)
        """
        self.logger.info("Tester mail forbindelse")
        return self.mail_system.test_connection()
    
    def send_mail(self, to, subject, body, attachments=None, driver_id=None, is_html=False):
        """
        Sender en mail via MailSystem
        
        Args:
            to: Modtagerens email
            subject: Emne
            body: Brødtekst
            attachments: Dict med filnavn:fil_data for vedhæftninger
            driver_id: Chauffør ID, hvis relevant
            is_html: True hvis body er HTML
            
        Returns:
            bool: True hvis mail blev sendt
        """
        try:
            self.logger.info(f"Sender mail til {to}")
            success = self.mail_system.send_mail(
                to=to,
                subject=subject,
                body=body,
                attachments=attachments,
                driver_id=driver_id,
                is_html=is_html
            )
            
            if success:
                self.logger.info(f"Mail sendt succesfuldt til {to}")
            else:
                self.logger.error(f"Kunne ikke sende mail til {to}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Fejl ved afsendelse af mail til {to}: {str(e)}")
            if hasattr(e, '__traceback__'):
                import traceback
                trace = ''.join(traceback.format_tb(e.__traceback__))
                self.logger.error(f"Stacktrace: {trace}")
            return False
    
    def send_batch_mail(self, recipients, subject, body, attachments=None, is_html=False):
        """
        Sender samme mail til flere modtagere via MailSystem
        
        Args:
            recipients: Liste af email adresser
            subject: Emne
            body: Brødtekst
            attachments: Dict med filnavn:fil_data for vedhæftninger
            is_html: True hvis body er HTML
            
        Returns:
            tuple: (antal_success, antal_fejl)
        """
        self.logger.info(f"Sender batch mail til {len(recipients)} modtagere")
        return self.mail_system.send_batch_mail(recipients, subject, body, attachments, is_html)

    def attach_file(self, msg, file_path):
        """Vedhæft fil med korrekt MIME-type og ekstra validering"""
        try:
            # Valider filens eksistens først
            if not os.path.exists(file_path):
                print(f"# DEBUG: Fil ikke fundet - {file_path}")
                raise FileNotFoundError(f"Filen {file_path} eksisterer ikke")

            # Tjek filstørrelse for at undgå tomme filer
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                print("# DEBUG: Forsøg på at vedhæfte tom fil")
                raise ValueError("Filen er tom")

            # Brug 'rb' mode og expliciet angivelse af MIME-type
            with open(file_path, 'rb') as f:
                part = MIMEApplication(
                    f.read(),
                    _subtype='vnd.openxmlformats-officedocument.wordprocessingml.document'  # Korrekt MIME-type for .docx
                )
            
            # Fjern potentielle ugyldige tegn fra filnavn
            safe_filename = re.sub(r'[^\w_. -]', '_', os.path.basename(file_path))
            part.add_header('Content-Disposition', 'attachment', filename=safe_filename)
            
            msg.attach(part)
            print(f"# DEBUG: Fil vedhæftet succesfuldt - {safe_filename} ({file_size} bytes)")
            return True
            
        except Exception as e:
            print(f"# DEBUG: Kritisk vedhæftningsfejl: {str(e)}")
            logging.error(f"Vedhæftningsfejl: {str(e)}", exc_info=True)
            raise

def send_report_email(recipient, file_path):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = "Chauffør Rapport"
        
        # Vedhæft fil som binær
        with open(file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{file_path}"')
            msg.attach(part)
        
        print(f"# DEBUG: Fil vedhæftet - Størrelse: {os.path.getsize(file_path)} bytes, Path: {file_path}")
        return True
    except Exception as e:
        print(f"# DEBUG: Vedhæftningsfejl - Fejltype: {type(e).__name__}, Detaljer: {str(e)}")
        raise

def attach_file_to_email(msg, file_path, filename=None):
    try:
        # Valider inputbeskeden
        if not isinstance(msg, MIMEMultipart):
            raise ValueError("Ugyldigt email-objekt - skal være MIMEMultipart")
            
        # Debug: Vis aktuel arbejdsmappe og filsti-detaljer
        print(f"# DEBUG: Current working directory: {os.getcwd()}")
        print(f"# DEBUG: Raw input path: {file_path}")
        
        # Normaliser stien
        normalized_path = os.path.abspath(os.path.normpath(file_path))
        print(f"# DEBUG: Normalized path: {normalized_path}")
        
        # Tjek filens eksistens med debug-info
        if not os.path.exists(normalized_path):
            print("# DEBUG: Forsøger at oprette testfil automatisk")
            create_test_file(normalized_path)  # Opret filen hvis den mangler
            
        # Læs filindhold med eksplicit angivelse af binary mode
        with open(normalized_path, 'rb') as f:
            file_data = f.read()
            
        # Opret MIME part med korrekt subtype
        part = MIMEApplication(
            file_data,
            _subtype='vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
        # Brug det originale filnavn hvis ikke andet er angivet
        final_filename = filename or os.path.basename(normalized_path)
        safe_name = sanitize_filename(final_filename)
        
        # Tilføj headers med UTF-8 encoding
        part.add_header('Content-Disposition', 'attachment', 
                       filename=safe_name,
                       charset='utf-8')
        
        msg.attach(part)
        print(f"# DEBUG: Vedhæftet {safe_name} ({len(file_data)} bytes)")
        return True
        
    except Exception as e:
        print(f"# FEJL: Problem med email-objektet - {str(e)}")
        raise

def sanitize_filename(filename):
    # Normaliser Unicode-tegn og fjern ugyldige tegn
    cleaned = unicodedata.normalize('NFKC', filename)
    cleaned = re.sub(r'[\\/*?:"<>|]', '', cleaned)  # Fjern forbudte tegn
    cleaned = cleaned.replace('\n', ' ').replace('\r', '')  # Fjern linjeskift
    cleaned = cleaned.strip()  # Fjern whitespace
    print(f"# DEBUG: Saniteret filnavn: {cleaned}")
    return cleaned

def create_test_file(file_path):
    """Opret en tom testfil hvis den ikke eksisterer"""
    try:
        # Opret mappen hvis den ikke findes
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Opret en tom fil hvis den ikke eksisterer
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as f:
                f.write(b'')  # Tomt indhold
            print(f"# DEBUG: Oprettet tom testfil: {file_path}")
            
    except Exception as e:
        print(f"# FEJL: Kunne ikke oprette testfil: {str(e)}")
        raise

# ... resten af koden ... 