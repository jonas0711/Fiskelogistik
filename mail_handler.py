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
    def __init__(self):
        """Initialiserer MailHandler med database forbindelse og mail system"""
        # Opret database forbindelse
        self.db_path = os.path.join('databases', 'settings.db')
        self.db = DatabaseConnection(self.db_path)
        
        # Initialiser mail system
        self.mail_system = MailSystem()
        
    def _get_first_name(self, full_name):
        """Udtrækker fornavnet fra det fulde navn i formatet 'Efternavn, Fornavn'"""
        try:
            # Split på komma og tag anden del (fornavn delen)
            parts = full_name.split(',')
            if len(parts) >= 2:
                # Tag første ord fra fornavn delen (i tilfælde af mellemnavn)
                first_name = parts[1].strip().split()[0]
                return first_name
            return full_name  # Returner hele navnet hvis formatet ikke passer
        except Exception:
            return full_name  # Returner hele navnet ved fejl

    def create_html_report(self, report_data, driver_name):
        """Opretter HTML formateret rapport baseret på report_data for en given chauffør.
        
        Denne metode forventer at report_data er et dictionary med statistik og rapport data.
        """
        try:
            # Hent statistik fra report_data
            if isinstance(report_data, dict) and 'statistik' in report_data:
                statistik = report_data['statistik']
            else:
                raise ValueError("Ugyldig report_data format - mangler statistik")

            # Udtræk fornavn fra det fulde navn
            fornavn = self._get_first_name(statistik['name'])

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
            Hej {fornavn},
        </div>
        <p>Her er din månedlige kørselsrapport for {statistik['date']}.</p>
        
        <div class="goals-container">
            <h3 style="margin-top: 0;">Din performance på de 4 målsætningerne:</h3>
"""
            
            # Definer målsætninger og tjek om de er opfyldt
            goals = {
                'Tomgang': {
                    'value': statistik['tomgangsprocent'],
                    'target': 5.0,
                    'text': 'Mål: Under 5%',
                    'success': statistik['tomgangsprocent'] <= 5.0,
                    'reverse': True  # Lavere er bedre
                },
                'Fartpilot anvendelse': {
                    'value': statistik['fartpilot_andel'],
                    'target': 66.5,
                    'text': 'Mål: Over 66,5%',
                    'success': statistik['fartpilot_andel'] >= 66.5,
                    'reverse': False
                },
                'Brug af motorbremse': {
                    'value': statistik['motorbremse_andel'],
                    'target': 56.0,
                    'text': 'Mål: Over 56%',
                    'success': statistik['motorbremse_andel'] >= 56.0,
                    'reverse': False
                },
                'Påløbsdrift': {
                    'value': statistik['paalobsdrift_andel'],
                    'target': 7.0,
                    'text': 'Mål: Over 7%',
                    'success': statistik['paalobsdrift_andel'] >= 7.0,
                    'reverse': False
                }
            }

            # Tilføj hver målsætning til HTML
            for name, goal in goals.items():
                status_class = 'success' if goal['success'] else 'warning'
                html_body += f"""
            <div class="goal-item">
                <div>{name}:</div>
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
            logging.error(f"Fejl ved oprettelse af HTML rapport: {str(e)}")
            # Returner en simpel fejlbesked som HTML
            return f"""<html><body>
                <h2>Fejl ved generering af rapport</h2>
                <p>Der opstod en fejl ved generering af rapporten. Kontakt venligst support.</p>
                <p>Se vedhæftede fil for den komplette rapport.</p>
                </body></html>"""
        
    def send_report(self, driver_id, report_data, recipient=None):
        """Sender rapport via email"""
        try:
            # # DEBUG: Starter send_report proces
            logging.info(f"Starter send_report proces for chauffør: {driver_id}, custom-recipient: {recipient is not None}")
            
            # Hent email-adresse
            if recipient is None:
                recipient = self.db.get_driver_email(driver_id)
                logging.info(f"Henter chaufførens email: {recipient}")
                if not recipient:
                    error_msg = f"Ingen email fundet for chauffør {driver_id}"
                    logging.error(error_msg)
                    raise ValueError(error_msg)

            # Hent chauffør information
            driver = self.db.get_driver(driver_id)
            if not driver:
                error_msg = f"Kunne ikke finde chauffør med ID {driver_id}"
                logging.error(error_msg)
                raise ValueError(error_msg)
            logging.info(f"Chauffør fundet: {driver['name']}")

            # Hent mail template
            try:
                # # DEBUG: Forsøger at hente mail-skabelon
                logging.info("Forsøger at hente mail-skabelon 'chauffør_report'")
                template = self.db.get_mail_template('chauffør_report')
                if template:
                    logging.info("Mail-skabelon 'chauffør_report' fundet")
                else:
                    logging.warning("Ingen mail-skabelon fundet, bruger fallback")
            except Exception as template_error:
                # # DEBUG: Fejl ved hentning af mail-skabelon
                logging.error(f"Fejl ved hentning af mail-skabelon: {str(template_error)}")
                template = None
                
            # Brug fallback skabelon hvis ingen fundet
            if not template:
                logging.warning("Bruger fallback mail-skabelon")
                template = {
                    'subject': 'Din Månedlige Chauffør Rapport',
                    'body': '<html><body><p>Se vedhæftede rapport.</p></body></html>'
                }

            # Opret multipart message
            subject = template['subject'].replace('{{CHAUFFØR_NAVN}}', driver['name'])
            logging.info(f"Opretter email med emne: {subject}")
            
            msg = MIMEMultipart('mixed')
            msg['Subject'] = subject
            msg['From'] = self.db.get_mail_config()['email']
            msg['To'] = recipient
            
            # Opret HTML rapport
            logging.info("Genererer HTML rapport indhold")
            html_report = self.create_html_report(report_data, driver['name'])
            
            # Opret HTML del
            html_part = MIMEText(html_report, 'html', 'utf-8')
            msg.attach(html_part)
            logging.info("HTML indhold tilføjet til email")

            # Tilføj rapport som vedhæftning
            try:
                if isinstance(report_data, dict) and 'rapport' in report_data:
                    # Generer filnavn
                    filename = f"Rapport_{driver['name']}_{datetime.now().strftime('%Y%m%d')}.docx"
                    logging.info(f"Tilføjer rapport som vedhæftning: {filename}")
                    
                    # Opret attachment
                    attachment = MIMEBase('application', 'vnd.openxmlformats-officedocument.wordprocessingml.document')
                    attachment.set_payload(report_data['rapport'])
                    encoders.encode_base64(attachment)
                    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                    msg.attach(attachment)
                    logging.info("Rapport vedhæftet succesfuldt")
                else:
                    logging.warning("Ingen rapport data tilgængelig til vedhæftning")
            except Exception as attach_error:
                # # DEBUG: Fejl ved vedhæftning af rapport
                logging.error(f"Fejl ved vedhæftning af rapport: {str(attach_error)}")
                logging.error(f"Fejltype: {type(attach_error).__name__}")
                # Fortsæt selv uden vedhæftning, så email stadig sendes

            # Send mail med den korrekte MIME struktur
            try:
                logging.info(f"Sender email til {recipient}")
                self.mail_system.send_mail(
                    to=recipient,
                    subject=msg['Subject'],
                    body=html_report,  # Send HTML indhold
                    attachments={filename: report_data['rapport']} if isinstance(report_data, dict) and 'rapport' in report_data else None,
                    driver_id=driver_id,
                    is_html=True
                )
                logging.info(f"Email tilføjet til sendekø for {recipient}")
            except Exception as send_error:
                # # DEBUG: Fejl ved afsendelse af email
                logging.error(f"Fejl ved afsendelse af email: {str(send_error)}")
                logging.error(f"Fejltype: {type(send_error).__name__}")
                if hasattr(send_error, '__traceback__'):
                    import traceback
                    trace = ''.join(traceback.format_tb(send_error.__traceback__))
                    logging.error(f"Stacktrace: {trace}")
                raise

            logging.info(f"Rapport send-proces fuldført succesfuldt til {driver['name']} ({recipient})")
            return True

        except Exception as e:
            # # DEBUG: Generel fejl i send_report
            logging.error(f"Fejl ved afsendelse af rapport: {str(e)}")
            logging.error(f"Fejltype: {type(e).__name__}")
            if hasattr(e, '__traceback__'):
                import traceback
                trace = ''.join(traceback.format_tb(e.__traceback__))
                logging.error(f"Stacktrace: {trace}")
            raise
            
    def test_connection(self):
        """Tester mail forbindelse"""
        return self.mail_system.test_connection()

    # Ændret funktion for at rense tekst, men springe binære data over
    def sanitize_text(self, text, is_attachment=False):
        # # DEBUG: Hvis data er en vedhæftet fil (binær), returneres den uændret
        if is_attachment:
            logging.debug("Vedhæftet fil hentes som binære data - rensing springes over.")
            return text
        # Hvis ikke tekst, forsøg at dekode (kan ske, at vi modtager bytes)
        if not isinstance(text, str):
            try:
                # # DEBUG: Forsøg at dekode bytes til UTF-8 tekst
                text = text.decode('utf-8')
            except (AttributeError, UnicodeDecodeError) as e:
                logging.error(f"Kunne ikke dekode tekst: {e}")
                return text
        # Rens teksten for kontroltegn (undtagen newline, carriage return og tab)
        return ''.join(ch for ch in text if unicodedata.category(ch)[0] != 'C' or ch in '\n\r\t')

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