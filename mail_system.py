# Import nødvendige biblioteker
import smtplib
import ssl
import logging
import os
import time
import threading
import sqlite3
import traceback
import re
import unicodedata
from queue import Queue
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from database_connection import DatabaseConnection

class MailSystem:
    def __init__(self, db_connection=None, max_retries=3, timeout=30):
        """
        Initialiserer mail-systemet med database forbindelse og mail kø
        
        Args:
            db_connection: DatabaseConnection objekt
            max_retries: Maksimalt antal forsøg på at sende en mail
            timeout: Timeout i sekunder for SMTP-operationer
        """
        self.db = db_connection
        self.mail_queue = Queue()
        self.queue_processing = False
        self.max_retries = max_retries
        self.timeout = timeout
        self.queue_thread = None
        
        # Opsæt logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('MailSystem')
        
    def get_mail_config(self):
        """
        Henter mail konfiguration fra databasen
        
        Returns:
            dict: Mail konfiguration med nøglerne email, password, smtp_server, port
        """
        try:
            if self.db:
                return self.db.get_mail_config()
            else:
                # Fallback til direkte database adgang
                self.logger.warning("Ingen DatabaseConnection, bruger direkte adgang til databasen")
                with sqlite3.connect('databases/settings.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT email, password, smtp_server, port FROM mail_config LIMIT 1')
                    result = cursor.fetchone()
                    if result:
                        return {
                            'email': result[0],
                            'password': result[1],
                            'smtp_server': result[2],
                            'port': int(result[3])
                        }
            
            self.logger.error("Ingen mail konfiguration fundet")
            return None
        except Exception as e:
            self.logger.error(f"Fejl ved hentning af mail konfiguration: {str(e)}")
            return None
    
    def validate_mail_config(self):
        """
        Validerer at mail konfigurationen er komplet
        
        Returns:
            bool: True hvis konfigurationen er valid, ellers False
        """
        config = self.get_mail_config()
        if not config:
            self.logger.warning("Ingen mail konfiguration fundet")
            return False
            
        # Tjek at alle nødvendige felter er udfyldt
        required_fields = ['email', 'password', 'smtp_server', 'port']
        for field in required_fields:
            if field not in config or not config[field]:
                self.logger.warning(f"Mail konfiguration mangler felt: {field}")
                return False
                
        # Validér email format
        if '@' not in config['email'] or '.' not in config['email']:
            self.logger.warning(f"Ugyldig afsender email format: {config['email']}")
            return False
            
        return True
        
    def create_smtp_connection(self, config=None):
        """
        Opretter SMTP forbindelse med timeout-håndtering
        
        Args:
            config: Mail konfiguration (hvis None, hentes fra databasen)
            
        Returns:
            smtplib.SMTP or smtplib.SMTP_SSL: SMTP forbindelse
        """
        if not config:
            config = self.get_mail_config()
            if not config:
                self.logger.error("Kunne ikke oprette SMTP forbindelse: Ingen konfiguration")
                raise ValueError("Ingen mail konfiguration fundet")
        
        # Valider at alle nødvendige konfigurationsværdier findes
        required_keys = ['smtp_server', 'email', 'password']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            error_msg = f"Manglende mail konfiguration: {', '.join(missing_keys)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
                
        try:
            # Opret SMTP forbindelse med timeout
            # Brug standard port 587 (TLS) hvis port ikke er angivet
            port = int(config.get('port', 587))
            self.logger.info(f"Opretter forbindelse til {config['smtp_server']}:{port}")
            
            # Vælg SSL eller TLS baseret på port
            if port == 465:
                self.logger.info("Anvender SMTP_SSL forbindelse")
                server = smtplib.SMTP_SSL(config['smtp_server'], port, timeout=self.timeout)
            else:
                self.logger.info("Anvender standard SMTP forbindelse")
                server = smtplib.SMTP(config['smtp_server'], port, timeout=self.timeout)
                
                # Start TLS hvis det ikke er port 25
                if port != 25:
                    self.logger.info("Starter TLS")
                    server.starttls()
                    
            # Login
            self.logger.info(f"Logger ind med {config['email']}")
            server.login(config['email'], config['password'])
            self.logger.info("SMTP forbindelse oprettet succesfuldt")
            return server
            
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"SMTP Autentificeringsfejl: {str(e)}")
            raise
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP Fejl: {str(e)}")
            raise
        except TimeoutError as e:
            self.logger.error(f"Timeout ved SMTP forbindelse: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Uventet fejl ved SMTP forbindelse: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
            
    def start_queue_processing(self):
        """Starter en baggrundsproces til at håndtere mail køen"""
        if self.queue_processing:
            self.logger.info("Mail kø processor kører allerede")
            return
            
        self.queue_processing = True
        
        def process_mail_queue():
            self.logger.info("Mail kø processor startet")
            while self.queue_processing:
                try:
                    # Behandler mail køen med timeout og lukning
                    self.process_mail_queue()
                    # Vent lidt før næste check
                    time.sleep(2)
                except Exception as e:
                    self.logger.error(f"Fejl i mail kø processor: {str(e)}")
                    time.sleep(5)  # Længere delay efter fejl
            
            self.logger.info("Mail kø processor stoppet")
                
        # Start tråd hvis den ikke kører
        if not self.queue_thread or not self.queue_thread.is_alive():
            self.queue_thread = threading.Thread(target=process_mail_queue)
            self.queue_thread.daemon = True
            self.queue_thread.start()
            self.logger.info("Mail kø håndteringstråd startet")
        
    def stop_queue_processing(self):
        """Stopper mail kø processoren"""
        self.queue_processing = False
        if self.queue_thread and self.queue_thread.is_alive():
            self.logger.info("Stopper mail kø processor...")
            self.queue_thread.join(timeout=5)
            self.logger.info("Mail kø processor stoppet")
    
    def process_mail_queue(self):
        """Processor mail køen og sender ventende mails"""
        if self.mail_queue.empty():
            return
            
        self.logger.info(f"Behandler mail kø ({self.mail_queue.qsize()} mails)")
        
        try:
            # Opret en enkelt forbindelse til alle mails i køen
            config = self.get_mail_config()
            if not config:
                self.logger.error("Kunne ikke sende mails: Ingen konfiguration")
                return
                
            # Opret SMTP forbindelse
            smtp = self.create_smtp_connection(config)
            
            try:
                # Proces køen
                while not self.mail_queue.empty():
                    mail_data = self.mail_queue.get()
                    
                    attempts = 0
                    while attempts < self.max_retries:
                        try:
                            # Send mailen
                            self.logger.info(f"Sender mail til {mail_data['to']}")
                            
                            # Brug MIMEMultipart hvis der er vedhæftninger
                            if mail_data.get('attachments'):
                                msg = self._create_mime_message(mail_data)
                                smtp.send_message(msg)
                            else:
                                # Simpel mail uden vedhæftninger
                                smtp.sendmail(
                                    config['email'],
                                    mail_data['to'],
                                    f"From: {config['email']}\r\n"
                                    f"To: {mail_data['to']}\r\n"
                                    f"Subject: {mail_data['subject']}\r\n"
                                    f"Content-Type: {'text/html; charset=utf-8' if mail_data.get('is_html', False) else 'text/plain; charset=utf-8'}\r\n\r\n"
                                    f"{mail_data['body']}"
                                )
                                
                            self.logger.info(f"Mail sendt til {mail_data['to']}")
                            
                            # Log succes hvis driver_id er angivet
                            if 'driver_id' in mail_data:
                                self._log_mail_sent(mail_data['driver_id'])
                                
                            # Bryd løkken hvis det lykkedes
                            break
                            
                        except smtplib.SMTPServerDisconnected:
                            # Server disconnection - forsøg at genoprette forbindelsen
                            self.logger.warning(f"SMTP server forbindelse afbrudt. Forsøger at genoprette ({attempts+1}/{self.max_retries})")
                            attempts += 1
                            try:
                                # Genopret forbindelse
                                smtp = self.create_smtp_connection(config)
                                time.sleep(5)  # Vent 5 sekunder før genoprettelse
                            except Exception as conn_error:
                                self.logger.error(f"Fejl ved genoprettelse af SMTP forbindelse: {str(conn_error)}")
                            
                        except smtplib.SMTPSenderRefused:
                            # Server afviser afsender - muligvis for mange mails for hurtigt
                            self.logger.warning("SMTP server afviser afsender - venter længere mellem forsøg")
                            attempts += 1
                            time.sleep(10)  # Længere ventetid ved afsenderafvisning
                            
                        except Exception as e:
                            attempts += 1
                            self.logger.error(f"Fejl ved afsendelse af mail (forsøg {attempts}): {str(e)}")
                            if attempts >= self.max_retries:
                                self.logger.error(f"Opgiver at sende mail til {mail_data['to']} efter {self.max_retries} forsøg")
                                # Log fejl hvis driver_id er angivet
                                if 'driver_id' in mail_data:
                                    self._log_mail_error(mail_data['driver_id'], str(e))
                            else:
                                # Vent før næste forsøg - længere ventetid mellem hver forsøg
                                time.sleep(2 * attempts)  # Stigende ventetid for hvert forsøg
                                
                    # Markér mail som håndteret
                    self.mail_queue.task_done()
                    
                    # Tilføj en kort pause mellem hver mail i køen for at undgå rate limiting
                    time.sleep(1)  # 1 sekunds pause mellem hver mail
                    
            finally:
                # Luk SMTP forbindelsen
                try:
                    smtp.quit()
                except Exception as e:
                    self.logger.warning(f"Fejl ved lukning af SMTP forbindelse: {str(e)}")
                
        except Exception as e:
            self.logger.error(f"Fejl ved behandling af mail kø: {str(e)}")
            self.logger.error(traceback.format_exc())
    
    def _create_mime_message(self, mail_data):
        """Opret et MIME besked objekt med vedhæftninger"""
        msg = MIMEMultipart()
        msg['From'] = self.get_mail_config()['email']
        msg['To'] = mail_data['to']
        msg['Subject'] = mail_data['subject']
        
        # Tilføj brødtekst
        if mail_data.get('is_html', False):
            body_part = MIMEText(mail_data['body'], 'html', 'utf-8')
        else:
            body_part = MIMEText(mail_data['body'], 'plain', 'utf-8')
        msg.attach(body_part)
        
        # Tilføj vedhæftninger
        if mail_data.get('attachments'):
            for filename, file_data in mail_data['attachments'].items():
                self._attach_file_data(msg, file_data, filename)
                
        return msg
        
    def _attach_file_data(self, msg, file_data, filename):
        """
        Vedhæfter binært indhold til en mail med korrekt filnavn
        
        Args:
            msg: MIMEMultipart besked at vedhæfte til
            file_data: Binært indhold
            filename: Filnavn til vedhæftningen
        """
        try:
            # Bestem MIME-type baseret på filudvidelse
            extension = os.path.splitext(filename)[1].lower()
            
            if extension == '.docx':
                mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif extension == '.xlsx':
                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif extension == '.pdf':
                mime_type = 'application/pdf'
            else:
                mime_type = 'application/octet-stream'
                
            # Opret vedhæftning
            part = MIMEApplication(file_data, _subtype=mime_type.split('/')[1])
            
            # Fjern potentielt ugyldige tegn fra filnavn
            safe_filename = self._sanitize_filename(filename)
            
            # Tilføj header
            part.add_header('Content-Disposition', 'attachment', filename=safe_filename)
            
            # Vedhæft til beskeden
            msg.attach(part)
            self.logger.info(f"Fil vedhæftet: {safe_filename} ({len(file_data)} bytes)")
            return True
            
        except Exception as e:
            self.logger.error(f"Fejl ved vedhæftning af fil: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
    
    def _sanitize_filename(self, filename):
        """
        Renser filnavn for ugyldige tegn
        
        Args:
            filename: Filnavn at rense
            
        Returns:
            str: Renset filnavn
        """
        # Normaliser Unicode-tegn
        cleaned = unicodedata.normalize('NFKC', filename)
        # Fjern ugyldige tegn for filnavne
        cleaned = re.sub(r'[\\/*?:"<>|]', '', cleaned)
        # Fjern linjeskift og whitespace
        cleaned = cleaned.replace('\n', ' ').replace('\r', '').strip()
        
        # Sørg for at filnavnet ikke er tomt
        if not cleaned:
            cleaned = "attachment"
            
        self.logger.debug(f"Saniteret filnavn: {cleaned}")
        return cleaned
    
    def _log_mail_sent(self, driver_id):
        """Logger en vellykket mail-afsendelse i databasen"""
        try:
            if self.db:
                with sqlite3.connect('databases/settings.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO mail_log (driver_id, timestamp, status, message) VALUES (?, ?, ?, ?)',
                        (driver_id, datetime.now().isoformat(), 'success', 'Mail sendt succesfuldt')
                    )
                    conn.commit()
                    self.logger.info(f"Mail succes logget for chauffør {driver_id}")
        except Exception as e:
            self.logger.error(f"Kunne ikke logge mail succes: {str(e)}")
    
    def _log_mail_error(self, driver_id, error_message):
        """Logger en fejlet mail-afsendelse i databasen"""
        try:
            if self.db:
                with sqlite3.connect('databases/settings.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO mail_log (driver_id, timestamp, status, message) VALUES (?, ?, ?, ?)',
                        (driver_id, datetime.now().isoformat(), 'error', error_message)
                    )
                    conn.commit()
                    self.logger.info(f"Mail fejl logget for chauffør {driver_id}")
        except Exception as e:
            self.logger.error(f"Kunne ikke logge mail fejl: {str(e)}")
    
    def send_mail(self, to, subject, body, attachments=None, driver_id=None, is_html=False):
        """
        Tilføjer en mail til sendekøen
        
        Args:
            to: Modtagerens email
            subject: Emne
            body: Brødtekst
            attachments: Dict med filnavn:fil_data for vedhæftninger
            driver_id: Chauffør ID, hvis relevant
            is_html: True hvis body er HTML
            
        Returns:
            bool: True hvis mail blev tilføjet til køen
        """
        try:
            # Validér input
            if not to or '@' not in to or '.' not in to:
                self.logger.error(f"Ugyldig modtager email: {to}")
                raise ValueError("Ugyldig modtager email")
                
            if not subject or not body:
                self.logger.error("Emne eller brødtekst mangler")
                raise ValueError("Emne eller brødtekst mangler")
                
            # Tilføj til køen
            self.mail_queue.put({
                'to': to,
                'subject': subject,
                'body': body,
                'attachments': attachments,
                'driver_id': driver_id,
                'is_html': is_html
            })
            
            self.logger.info(f"Mail til {to} tilføjet til sendekøen")
            
            # Sikr at kø-processen kører
            self.start_queue_processing()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Fejl ved tilføjelse af mail til kø: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
    
    def send_batch_mail(self, recipients, subject, body, attachments=None, is_html=False):
        """
        Sender samme mail til flere modtagere
        
        Args:
            recipients: Liste af email adresser
            subject: Emne
            body: Brødtekst
            attachments: Dict med filnavn:fil_data for vedhæftninger
            is_html: True hvis body er HTML
            
        Returns:
            tuple: (antal_success, antal_fejl)
        """
        success_count = 0
        error_count = 0
        
        for recipient in recipients:
            try:
                if self.send_mail(recipient, subject, body, attachments, is_html=is_html):
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                self.logger.error(f"Fejl ved afsendelse til {recipient}: {str(e)}")
                error_count += 1
                
        self.logger.info(f"Batch mail: {success_count} sendt, {error_count} fejl")
        return (success_count, error_count)
    
    def test_connection(self):
        """
        Tester SMTP forbindelsen
        
        Returns:
            tuple: (success, message)
        """
        try:
            # Validér konfiguration
            if not self.validate_mail_config():
                return (False, "Ugyldig mail konfiguration")
                
            # Opret forbindelse
            config = self.get_mail_config()
            smtp = self.create_smtp_connection(config)
            
            # Luk forbindelsen efter test
            smtp.quit()
            
            self.logger.info("SMTP forbindelsestest succesfuld")
            return (True, "Forbindelsen til mail serveren er oprettet succesfuldt")
            
        except smtplib.SMTPAuthenticationError:
            self.logger.error("SMTP autentificeringsfejl")
            return (False, "Forkert brugernavn eller adgangskode")
            
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP server fejl: {str(e)}")
            return (False, f"Mail server fejl: {str(e)}")
            
        except TimeoutError:
            self.logger.error("Timeout ved forbindelse til mail server")
            return (False, "Timeout ved forbindelse til mail server")
            
        except Exception as e:
            self.logger.error(f"Uventet fejl ved test af forbindelse: {str(e)}")
            return (False, f"Uventet fejl: {str(e)}")
    
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
            # Hent chauffør information
            driver = self._get_driver_info(driver_id)
            if not driver:
                self.logger.error(f"Ingen chauffør fundet med ID {driver_id}")
                return False
                
            # Hent modtager email
            to_email = recipient
            if not to_email:
                to_email = self._get_driver_email(driver_id)
                
            if not to_email:
                self.logger.error(f"Ingen email fundet for chauffør {driver['name']}")
                return False
                
            # Generer filnavn for vedhæftning
            filename = f"Rapport_{driver['name']}_{datetime.now().strftime('%Y%m%d')}.docx"
            
            # Opret emne og brødtekst
            subject = f"Chauffør Rapport - {driver['name']}"
            html_body = self._create_html_report(report_data, driver['name'])
            
            # Send mail
            attachments = None
            if isinstance(report_data, dict) and 'rapport' in report_data:
                attachments = {filename: report_data['rapport']}
                
            # Send mailen
            success = self.send_mail(
                to=to_email,
                subject=subject,
                body=html_body,
                attachments=attachments,
                driver_id=driver_id,
                is_html=True
            )
            
            self.logger.info(f"Rapport {'sendt' if success else 'ikke sendt'} til {driver['name']} ({to_email})")
            return success
            
        except Exception as e:
            self.logger.error(f"Fejl ved afsendelse af rapport: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
    
    def send_report_with_email(self, driver_id, report_data, email):
        """
        Sender en rapport direkte til en given email uden at tilgå databasen for at hente mail
        Designet til at løse trådsikkerhedsproblemer med SQLite
        
        Args:
            driver_id: Chauffør ID (kun brugt til logning)
            report_data: Rapport data (dict med rapport:binære data)
            email: Email-adresse at sende til
            
        Returns:
            bool: True hvis rapporten blev sendt
        """
        try:
            # Validér input
            if not email or '@' not in email or '.' not in email:
                self.logger.error(f"Ugyldig email-adresse for chauffør {driver_id}: {email}")
                return False
                
            if not report_data:
                self.logger.error(f"Ingen rapport data for chauffør {driver_id}")
                return False
                
            # Ekstrahér navn fra driver_id (typisk format: "Efternavn, Fornavn")
            driver_name = driver_id
            
            # Generer filnavn for vedhæftning
            filename = f"Rapport_{driver_name}_{datetime.now().strftime('%Y%m%d')}.docx"
            
            # Opret emne og brødtekst
            subject = f"Chauffør Rapport - {driver_name}"
            html_body = self._create_html_report(report_data, driver_name)
            
            # Send mail
            attachments = None
            if isinstance(report_data, dict) and 'rapport' in report_data:
                attachments = {filename: report_data['rapport']}
                
            # Send mailen
            self.logger.info(f"Sender rapport direkte til {email} for chauffør {driver_id}")
            success = self.send_mail(
                to=email,
                subject=subject,
                body=html_body,
                attachments=attachments,
                driver_id=driver_id,
                is_html=True
            )
            
            self.logger.info(f"Rapport {'sendt' if success else 'ikke sendt'} til {driver_id} ({email})")
            return success
            
        except Exception as e:
            self.logger.error(f"Fejl ved direkte afsendelse af rapport til {email} for chauffør {driver_id}: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
    
    def _get_driver_info(self, driver_id):
        """Henter chauffør information fra databasen"""
        try:
            # Tjek om databaseforbindelsen findes og har den nødvendige metode
            if self.db and hasattr(self.db, 'get_driver_info'):
                return self.db.get_driver_info(driver_id)
            else:
                # Log årsag til fallback
                if not self.db:
                    self.logger.warning(f"Ingen databaseforbindelse tilgængelig for at hente chauffør {driver_id}")
                elif not hasattr(self.db, 'get_driver_info'):
                    self.logger.warning(f"Databasen mangler get_driver_info metoden for chauffør {driver_id}")
                
                # Fallback til direkte database adgang
                with sqlite3.connect('databases/settings.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT id, name FROM drivers WHERE id = ?', (driver_id,))
                    result = cursor.fetchone()
                    if result:
                        return {'id': result[0], 'name': result[1]}
            return None
        except Exception as e:
            self.logger.error(f"Fejl ved hentning af chauffør info: {str(e)}")
            return None
    
    def _get_driver_email(self, driver_id):
        """Henter chauffør email fra databasen"""
        try:
            # Tjek om databaseforbindelsen findes og har den nødvendige metode
            if self.db and hasattr(self.db, 'get_driver_email'):
                return self.db.get_driver_email(driver_id)
            else:
                # Log årsag til fallback
                if not self.db:
                    self.logger.warning(f"Ingen databaseforbindelse tilgængelig for at hente email for chauffør {driver_id}")
                elif not hasattr(self.db, 'get_driver_email'):
                    self.logger.warning(f"Databasen mangler get_driver_email metoden for chauffør {driver_id}")
                
                # Fallback til direkte database adgang
                with sqlite3.connect('databases/settings.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT email FROM driver_emails WHERE driver_id = ?', (driver_id,))
                    result = cursor.fetchone()
                    if result:
                        return result[0]
            return None
        except Exception as e:
            self.logger.error(f"Fejl ved hentning af chauffør email: {str(e)}")
            return None
    
    def _get_first_name(self, full_name):
        """Udtrækker fornavnet fra et fuldt navn"""
        if not full_name:
            return ""
            
        # Håndterer formatet "Efternavn, Fornavn Mellemnavn"
        if ',' in full_name:
            # Splitter ved komma og tager første ord fra anden del
            parts = full_name.split(',')
            if len(parts) > 1 and parts[1].strip():
                return parts[1].strip().split()[0]
                
        # Standard format "Fornavn Mellemnavn Efternavn"
        return full_name.split()[0]
    
    def _create_html_report(self, report_data, driver_name):
        """
        Opret HTML rapport baseret på data
        
        Args:
            report_data: Rapport data
            driver_name: Chaufførens navn
        
        Returns:
            str: HTML indhold
        """
        try:
            # Hent statistik fra report_data
            if isinstance(report_data, dict) and 'statistik' in report_data:
                statistik = report_data['statistik']
            else:
                # Fallback hvis statistik ikke findes
                return f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Chauffør Rapport - {driver_name}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                        h1, h2 {{ color: #2c5282; }}
                        .header {{ background-color: #f0f4f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                        .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; font-size: 0.9em; color: #666; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Chauffør Rapport</h1>
                        <p>Kære {self._get_first_name(driver_name)},</p>
                        <p>Hermed din personlige rapport med dine resultater og statistikker.</p>
                    </div>
                    <p>Ingen detaljerede data tilgængelige. Se venligst den vedhæftede rapport for flere oplysninger.</p>
                    <div class="footer">
                        <p>Dette er en automatisk genereret rapport. Venligst svar ikke på denne mail.</p>
                        <p>Hvis du har spørgsmål til rapporten, kontakt venligst din supervisor.</p>
                    </div>
                </body>
                </html>
                """

            # Udtræk fornavn fra det fulde navn
            fornavn = self._get_first_name(driver_name)

            # Opret HTML header og styling
            html_header = f"""<html>
<head>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        .header {{ 
            margin-bottom: 30px;
            border-bottom: 2px solid #1E90FF;
            padding-bottom: 20px;
        }}
        .greeting {{
            font-size: 18px;
            margin-bottom: 20px;
        }}
        .goals-container {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .goal-item {{
            margin: 15px 0;
            padding: 10px;
            border-radius: 5px;
        }}
        .goal-value {{
            font-weight: bold;
            font-size: 18px;
        }}
        .goal-target {{
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }}
        .success {{
            color: #28a745;
        }}
        .warning {{
            color: #dc3545;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #666;
            font-size: 14px;
        }}
        .contact-info {{
            margin-top: 20px;
            background: #e9ecef;
            padding: 15px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h2 style="color: #1E90FF; margin: 0;">Fiskelogistik Rapport</h2>
    </div>
"""

            # Opret personlig hilsen med fornavn
            html_body = f"""
    <div class="greeting">
        Kære {fornavn},
    </div>
    <p>Hermed din månedlige kørselsrapport for {statistik.get('date', 'denne periode')}.</p>
    
    <div class="goals-container">
        <h3 style="margin-top: 0;">Din performance på de 4 målsætninger:</h3>
"""
            
            # Definer målsætninger og tjek om de er opfyldt
            # Brug værdier fra statistik, eller standardværdier hvis ikke tilgængelige
            goals = {
                'Tomgang': {
                    'value': statistik.get('tomgangsprocent', 0),
                    'target': 5.0,
                    'text': 'Mål: Under 5%',
                    'success': statistik.get('tomgangsprocent', 100) <= 5.0,
                    'reverse': True  # Lavere er bedre
                },
                'Fartpilot anvendelse': {
                    'value': statistik.get('fartpilot_andel', 0),
                    'target': 66.5,
                    'text': 'Mål: Over 66,5%',
                    'success': statistik.get('fartpilot_andel', 0) >= 66.5,
                    'reverse': False
                },
                'Brug af motorbremse': {
                    'value': statistik.get('motorbremse_andel', 0),
                    'target': 50.0,
                    'text': 'Mål: Over 50%',
                    'success': statistik.get('motorbremse_andel', 0) >= 50.0,
                    'reverse': False
                },
                'Påløbsdrift': {
                    'value': statistik.get('paalobsdrift_andel', 0),
                    'target': 7.0,
                    'text': 'Mål: Over 7%',
                    'success': statistik.get('paalobsdrift_andel', 0) >= 7.0,
                    'reverse': False
                }
            }

            # Tilføj hver målsætning til HTML
            for name, goal in goals.items():
                status_class = 'success' if goal['success'] else 'warning'
                html_body += f"""
        <div class="goal-item">
            <div>{name}</div>
            <div class="goal-value {status_class}">{goal['value']:.1f}%</div>
            <div class="goal-target">{goal['text']}</div>
        </div>"""

            # Tilføj afsluttende tekst og kontaktinformation
            html_body += f"""
    </div>
    
    <p>Den komplette rapport er vedhæftet som fil, hvor du kan finde flere detaljer om din kørsel.</p>
    
    <div class="contact-info">
        <strong>Har du spørgsmål til rapporten?</strong><br>
        Kontakt venligst:<br>
        • Susan<br>
        • Rasmus
    </div>
    
    <div class="footer">
        <p>Med venlig hilsen<br>Fiskelogistik</p>
    </div>
"""

            html_footer = "</body></html>"

            return html_header + html_body + html_footer
            
        except Exception as e:
            self.logger.error(f"Fejl ved generering af HTML rapport: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            # Returner en simpel fallback rapport ved fejl
            return f"""
            <html>
            <body>
                <h1>Chauffør Rapport</h1>
                <p>Kære {self._get_first_name(driver_name)},</p>
                <p>Hermed din personlige rapport. Se venligst den vedhæftede fil for detaljer.</p>
                <p><small>Der opstod en fejl ved generering af rapport-indhold.</small></p>
            </body>
            </html>
            """ 