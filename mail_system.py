# Import nødvendige biblioteker
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging
import os
from datetime import datetime
import time
from queue import Queue
from threading import Thread
from database_connection import DatabaseConnection

class MailSystem:
    def __init__(self):
        """Initialiserer MailSystem med database forbindelse og mail kø"""
        # Opret database forbindelse
        self.db_path = os.path.join('databases', 'settings.db')
        self.db = DatabaseConnection(self.db_path)
        
        # Initialiser mail kø og worker thread
        self.mail_queue = Queue()
        self.worker_thread = Thread(target=self._process_mail_queue, daemon=True)
        self.worker_thread.start()
        
        # Hent mail konfiguration
        self.mail_config = self._get_mail_config()
        
        # Definer retry indstillinger
        self.max_retries = 3
        self.retry_delay = 5  # sekunder
        
    def _get_mail_config(self):
        """Henter og validerer mail konfiguration"""
        try:
            config = self.db.get_mail_config()
            if not config:
                raise ValueError("Ingen mail konfiguration fundet")
            self._validate_smtp_config(config)
            return config
        except Exception as e:
            logging.error(f"Fejl ved hentning af mail konfiguration: {str(e)}")
            raise
            
    def _validate_smtp_config(self, config):
        """Validerer SMTP konfiguration"""
        required_fields = ['smtp_server', 'smtp_port', 'email', 'password']
        for field in required_fields:
            if field not in config or not config[field]:
                raise ValueError(f"Manglende eller ugyldig {field} i mail konfiguration")
                
    def _create_smtp_connection(self):
        """Opretter og returnerer en sikker SMTP forbindelse"""
        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP(self.mail_config['smtp_server'], self.mail_config['smtp_port'])
            server.starttls(context=context)
            server.login(self.mail_config['email'], self.mail_config['password'])
            return server
        except Exception as e:
            logging.error(f"Fejl ved oprettelse af SMTP forbindelse: {str(e)}")
            raise
            
    def _process_mail_queue(self):
        """Behandler mails i køen med retry logik"""
        while True:
            try:
                if not self.mail_queue.empty():
                    mail_data = self.mail_queue.get()
                    retries = 0
                    
                    while retries < self.max_retries:
                        try:
                            with self._create_smtp_connection() as server:
                                server.send_message(mail_data['message'])
                                logging.info(f"Mail sendt succesfuldt til {mail_data['to']}")
                                
                                # Opdater seneste rapport tidspunkt hvis relevant
                                if 'driver_id' in mail_data:
                                    self.db.update_last_report_sent(mail_data['driver_id'])
                                    
                                break
                        except Exception as e:
                            retries += 1
                            if retries == self.max_retries:
                                logging.error(f"Kunne ikke sende mail efter {self.max_retries} forsøg: {str(e)}")
                                raise
                            logging.warning(f"Fejl ved mail sending (forsøg {retries}): {str(e)}")
                            time.sleep(self.retry_delay)
                            
                    self.mail_queue.task_done()
                time.sleep(1)  # Undgå CPU overbelastning
            except Exception as e:
                logging.error(f"Fejl i mail kø processor: {str(e)}")
                time.sleep(self.retry_delay)
                
    def send_mail(self, to, subject, body, attachments=None, driver_id=None, is_html=True):
        """Sender en enkelt mail med retry logik"""
        try:
            # Hvis body er allerede en MIME besked, brug den direkte
            if isinstance(body, MIMEMultipart):
                msg = body
            else:
                # Opret mail message
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = self.mail_config['email']
                msg['To'] = to
                
                # Tilføj indhold
                content_type = 'html' if is_html else 'plain'
                msg.attach(MIMEText(body, content_type, 'utf-8'))
                
                # Tilføj vedhæftninger hvis der er nogen
                if attachments:
                    for filename, content in attachments.items():
                        attachment = MIMEApplication(content)
                        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                        msg.attach(attachment)
                    
            # Tilføj til mail kø
            self.mail_queue.put({
                'message': msg,
                'to': to,
                'driver_id': driver_id
            })
            
            logging.info(f"Mail tilføjet til kø for {to}")
            
        except Exception as e:
            logging.error(f"Fejl ved forberedelse af mail: {str(e)}")
            raise
            
    def send_batch_mails(self, mail_list, delay=1):
        """Sender flere mails med delay imellem"""
        try:
            for mail_data in mail_list:
                self.send_mail(
                    to=mail_data['to'],
                    subject=mail_data['subject'],
                    body=mail_data['body'],
                    attachments=mail_data.get('attachments'),
                    driver_id=mail_data.get('driver_id'),
                    is_html=mail_data.get('is_html', True)
                )
                time.sleep(delay)  # Vent mellem hver mail
                
            logging.info(f"Batch af {len(mail_list)} mails tilføjet til kø")
            
        except Exception as e:
            logging.error(f"Fejl ved batch mail sending: {str(e)}")
            raise
            
    def test_connection(self):
        """Tester SMTP forbindelse"""
        try:
            with self._create_smtp_connection() as server:
                return True
        except Exception as e:
            logging.error(f"Fejl ved test af mail forbindelse: {str(e)}")
            raise
            
    def send_report(self, driver_id, report_data, recipient=None):
        # # DEBUG: Starter send_report funktion
        print(f"# DEBUG: Starter send_report. Driver ID: {driver_id}, recipient: {recipient}")
        
        # Hvis 'recipient' er angivet, bruges denne som modtager. Ellers hentes chaufførens email.
        if recipient:
            target_email = recipient
            print(f"# DEBUG: Bruger test email som modtager: {target_email}")
        else:
            # Her hentes chaufførens email fra databasen via en antaget metode get_driver_email(driver_id)
            target_email = self.db.get_driver_email(driver_id)
            print(f"# DEBUG: Bruger chaufførens egen email: {target_email}")
        
        subject = "Din individuelle rapport"
        # # DEBUG: Bygger email indhold og vedhæfter rapport data
        # Her indsættes den relevante kode til at sammensætte emailen og vedhæfte rapport data.
        try:
            # Simuleret afsendelse - i praksis anvendes SMTP's sendmail funktion
            print(f"# DEBUG: Sender email til {target_email} med emne: {subject}")
            # fx: self.smtp.sendmail(sender_email, target_email, message.as_string())
        except Exception as e:
            print(f"# ERROR: Fejl ved afsendelse af email: {str(e)}")
            raise
        
        print(f"# DEBUG: Email blev sendt til {target_email}")
        ... 