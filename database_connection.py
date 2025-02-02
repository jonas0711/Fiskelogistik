import sqlite3
import logging
import os
from datetime import datetime

class DatabaseConnection:
    def __init__(self, db_path='databases/settings.db'):
        """Initialiserer database forbindelsen med korrekt metodebinding"""
        # Flyt metodebindingen til toppen af __init__
        self.get_mail_config = self._get_mail_config_implementation
        
        if 'databases' in db_path:
            self.db_path = db_path
        else:
            self.db_path = os.path.join('databases', db_path)
            
        os.makedirs('databases', exist_ok=True)
        
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Så vi kan referere til kolonnenavne
        
        self._initialize_database()
        self._initialize_default_template()
        self.migrate()

    @property
    def cursor(self):
        """Returnerer en cursor til databasen"""
        return self.connection.cursor()

    def __enter__(self):
        """Support for context manager protocol"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for context manager protocol"""
        try:
            if exc_type is None:
                # Ingen fejl opstod, commit ændringer
                self.connection.commit()
            else:
                # Der opstod en fejl, rollback ændringer
                self.connection.rollback()
        finally:
            # Luk forbindelsen under alle omstændigheder
            self.connection.close()

    def close(self):
        """Lukker database forbindelsen"""
        try:
            self.connection.close()
        except Exception as e:
            logging.error(f"Fejl ved lukning af database forbindelse: {str(e)}")

    def _initialize_database(self):
        """Sikrer korrekt databaseopsætning med fejlsikker migration"""
        with sqlite3.connect(self.db_path) as conn:
            # Tjek om mail_config tabellen har korrekt struktur
            try:
                conn.execute("SELECT smtp_server, email FROM mail_config LIMIT 1")
            except sqlite3.OperationalError:
                # Slet eksisterende fejlbehæftet tabel
                conn.execute("DROP TABLE IF EXISTS mail_config")
            
            # Opret mail_config tabel med korrekt struktur
            conn.execute('''CREATE TABLE IF NOT EXISTS mail_config(
                smtp_server TEXT,
                smtp_port INTEGER,
                email TEXT PRIMARY KEY,
                password TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # # DEBUG: Tjekkers om 'test_email' kolonnen findes, og tilføj den hvis den mangler
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(mail_config)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'test_email' not in columns:
                conn.execute("ALTER TABLE mail_config ADD COLUMN test_email TEXT")
                print("# DEBUG: Tilføjet kolonnen 'test_email' til mail_config tabellen")
            
            # Forbedret migrationslogik med fejlhåndtering
            try:
                conn.execute('''
                    INSERT INTO mail_config(smtp_server, smtp_port, email, password)
                    SELECT 
                        (SELECT value FROM settings WHERE key='smtp_server'),
                        (SELECT value FROM settings WHERE key='smtp_port'),
                        (SELECT value FROM settings WHERE key='smtp_username'),
                        (SELECT value FROM settings WHERE key='smtp_password')
                    WHERE EXISTS(SELECT 1 FROM settings WHERE key='smtp_server')
                ''')
            except sqlite3.OperationalError as e:
                logging.warning(f"Migration fejlede: {str(e)}")
            
            # Ryd op kun hvis migration lykkedes (med fejlhåndtering)
            try:
                conn.execute('''
                    DELETE FROM settings 
                    WHERE key IN ('smtp_server', 'smtp_port', 'smtp_username', 'smtp_password')
                    AND EXISTS(SELECT 1 FROM mail_config)
                ''')
            except sqlite3.OperationalError as e:
                logging.warning(f"Kunne ikke rydde op i settings: {str(e)}")
            
            # Opret mail_templates tabel
            conn.execute('''CREATE TABLE IF NOT EXISTS mail_templates(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                template_name TEXT NOT NULL,
                language TEXT DEFAULT 'da',
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Opret driver_emails tabel
            conn.execute('''CREATE TABLE IF NOT EXISTS driver_emails(
                driver_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                last_report_sent TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Opret chauffør_data_data tabel
            conn.execute('''CREATE TABLE IF NOT EXISTS chauffør_data_data(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Chauffør TEXT NOT NULL,
                Antal_ture INTEGER,
                Kørestrækning_km REAL,
                Køretid TEXT,
                Tomgang_tid TEXT,
                Motordriftstid TEXT,
                Forbrug_l REAL,
                Ø_totalvægt_t REAL,
                Aktiv_påløbsdrift_km REAL,
                Afstand_i_påløbsdrift_km REAL,
                Kickdown_km REAL,
                Afstand_med_kørehastighedsregulering_over_50_km_h REAL,
                Afstand_over_50_km_h_uden_kørehastighedsregulering REAL,
                Forbrug_med_kørehastighedsregulering REAL,
                Forbrug_uden_kørehastighedsregulering REAL,
                Driftsbremse_km REAL,
                Afstand_motorbremse_km REAL,
                Overspeed_km REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Chauffør) REFERENCES driver_emails(driver_id)
            )''')
            
            # Tilføj test_email kolonne hvis den ikke findes
            try:
                conn.execute("SELECT test_email FROM mail_config LIMIT 1")
            except sqlite3.OperationalError:
                conn.execute('''
                    ALTER TABLE mail_config 
                    ADD COLUMN test_email TEXT
                ''')
            
            # Tilføj updated_at kolonne
            try:
                conn.execute("SELECT updated_at FROM mail_config LIMIT 1")
            except sqlite3.OperationalError:
                conn.execute('''
                    ALTER TABLE mail_config 
                    ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ''')
            
            conn.commit()

    def _initialize_default_template(self):
        """Initialiserer standard mail template hvis der ikke findes en"""
        try:
            cursor = self.connection.cursor()
            
            # Tjek om der findes en standard template
            cursor.execute('SELECT COUNT(*) FROM mail_templates WHERE is_default = 1')
            if cursor.fetchone()[0] == 0:
                # Opret standard template
                default_template = {
                    'name': 'Standard Chauffør Rapport',
                    'template_name': 'chauffør_report',
                    'language': 'da',
                    'subject': 'Din Månedlige Chauffør Rapport',
                    'body': '''<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { color: #1E90FF; }
        .content { margin: 20px 0; }
        .footer { color: #7F8C8D; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>Rapport for {{CHAUFFØR_NAVN}}</h2>
        <p>Genereret: {{DATO}}</p>
    </div>
    
    <div class="content">
        <p>Kære {{CHAUFFØR_NAVN}},</p>
        <p>Her er din rapport for perioden {{RAPPORT_PERIODE}}.</p>
        
        <h3>Rapport Oversigt</h3>
        <ul>
            <li>Antal ture: {{TOTAL_TURE}}</li>
            <li>Total distance: {{TOTAL_DISTANCE}} km</li>
            <li>Total tid: {{TOTAL_TID}} timer</li>
        </ul>
        
        <h3>Gennemsnit</h3>
        <ul>
            <li>Gennemsnitlig tur længde: {{GNS_TUR_LÆNGDE}} km</li>
            <li>Gennemsnitlig tur tid: {{GNS_TUR_TID}} timer</li>
        </ul>
    </div>
    
    <div class="footer">
        <p>Med venlig hilsen<br>{{FIRMA_NAVN}}</p>
    </div>
</body>
</html>''',
                    'is_default': True
                }
                
                cursor.execute('''
                    INSERT INTO mail_templates (name, template_name, language, subject, body, is_default)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    default_template['name'],
                    default_template['template_name'],
                    default_template['language'],
                    default_template['subject'],
                    default_template['body'],
                    default_template['is_default']
                ))
                
                self.connection.commit()
                logging.info("Standard mail template oprettet")
                
        except sqlite3.Error as e:
            logging.error(f"Fejl ved initialisering af standard mail template: {str(e)}")

    # Mail config metoder
    def save_mail_config(self, config):
        """Gemmer mail konfiguration i databasen"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM mail_config")
                
                # Kommentar: Opdateret query til at gemme test_email sammen med øvrige værdier
                query = """
                    INSERT INTO mail_config (
                        smtp_server,
                        smtp_port,
                        email,
                        password,
                        test_email
                    ) VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(query, (
                    config['smtp_server'],
                    config['smtp_port'],
                    config['email'],
                    config['password'],
                    config.get('test_email', None)  # # Henter test_email hvis den er angivet, ellers None
                ))
                conn.commit()
                
        except Exception as e:
            logging.error(f"Fejl ved gemning af mail konfiguration: {str(e)}")
            raise

    def _get_mail_config_implementation(self):
        """Implementering af get_mail_config"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        smtp_server, 
                        smtp_port, 
                        email, 
                        password,
                        test_email
                    FROM mail_config 
                    LIMIT 1
                ''')
                result = cursor.fetchone()
                
                if result:
                    return {
                        'smtp_server': result[0],
                        'smtp_port': result[1],
                        'email': result[2],
                        'password': result[3],
                        'test_email': result[4]
                    }
                return None
                
        except sqlite3.Error as e:
            logging.error(f"Databasefejl ved mail konfig hentning: {str(e)}")
            return None

    # Chauffør email metoder
    def save_driver_email(self, driver_id, email):
        """Gemmer eller opdaterer mailen for en chauffør"""
        try:
            cursor = self.connection.cursor()
            now = datetime.now().isoformat()  # Bruges til created_at og updated_at
            # Tjek, om en email allerede er gemt for chaufføren
            cursor.execute("SELECT email FROM driver_emails WHERE driver_id = ?", (driver_id,))
            if cursor.fetchone():
                # Opdater eksisterende post
                cursor.execute("UPDATE driver_emails SET email = ?, updated_at = ? WHERE driver_id = ?", (email, now, driver_id))
            else:
                # Indsæt ny post
                cursor.execute("INSERT INTO driver_emails (driver_id, email, created_at, updated_at) VALUES (?, ?, ?, ?)", (driver_id, email, now, now))
            self.connection.commit()  # Sikrer, at ændringer gemmes
            logging.info(f"Email gemt for chauffør {driver_id}: {email}")
        except Exception as e:
            logging.error("Fejl ved gemning af driver email: " + str(e))
            raise

    def get_driver_email(self, driver_id):
        """Henter mail for en given chauffør"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT email FROM driver_emails WHERE driver_id = ?", (driver_id,))
            row = cursor.fetchone()
            if row:
                print(f"# DEBUG: Fundet email for driver_id {driver_id}: {row[0]}")
                return row[0]
            else:
                print(f"# DEBUG: Ingen email fundet for driver_id {driver_id}")
                return None
        except Exception as e:
            logging.error(f"Fejl ved hentning af chaufførs email for {driver_id}: {str(e)}")
            return None

    def get_all_driver_emails(self):
        """Henter alle chaufførers emails i et dict format"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT driver_id, email FROM driver_emails")
            rows = cursor.fetchall()
            # Returner et dict med driver_id som nøgle og email som værdi
            emails = {row["driver_id"]: row["email"] for row in rows}
            return emails
        except Exception as e:
            logging.error("Fejl ved hentning af alle driver emails: " + str(e))
            return {}

    def update_last_report_sent(self, driver_id):
        """Opdaterer tidspunkt for seneste rapport"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE driver_emails 
                    SET last_report_sent = CURRENT_TIMESTAMP
                    WHERE driver_id = ?
                ''', (driver_id,))
                conn.commit()
                logging.info(f"Seneste rapport tidspunkt opdateret for chauffør {driver_id}")
        except Exception as e:
            logging.error(f"Fejl ved opdatering af seneste rapport tidspunkt: {str(e)}")
            raise

    def get_driver_products(self, driver_id):
        """Henter alle produkter for en specifik chauffør"""
        try:
            query = """
                SELECT 
                    p.name,
                    p.quantity,
                    p.expiry_date
                FROM products p
                JOIN driver_products dp ON p.id = dp.product_id
                WHERE dp.driver_id = ?
                ORDER BY p.expiry_date ASC
            """
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (driver_id,))
                
                products = []
                for row in cursor.fetchall():
                    products.append({
                        'name': row[0],
                        'quantity': row[1],
                        'expiry_date': row[2]
                    })
                
                return products
                
        except Exception as e:
            logging.error(f"Fejl ved hentning af chauffør produkter: {str(e)}")
            raise

    # Mail template metoder
    def save_mail_template(self, template_id=None, name=None, template_name=None, language='da', subject=None, body=None, is_default=False):
        """Gemmer eller opdaterer en mail template"""
        try:
            # Hvis template_name ikke er angivet, brug name
            if not template_name:
                template_name = name
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if template_id:
                    # Opdater eksisterende template
                    cursor.execute('''
                        UPDATE mail_templates 
                        SET name = ?, template_name = ?, language = ?, subject = ?, body = ?, is_default = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (name, template_name, language, subject, body, is_default, template_id))
                else:
                    # Opret ny template
                    cursor.execute('''
                        INSERT INTO mail_templates (name, template_name, language, subject, body, is_default)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (name, template_name, language, subject, body, is_default))
                    
                conn.commit()
                logging.info(f"Mail template {'opdateret' if template_id else 'oprettet'} succesfuldt")
                
        except Exception as e:
            logging.error(f"Fejl ved gemning af mail template: {str(e)}")
            raise

    def get_mail_template(self, template_name=None, language='da'):
        """Henter en mail template fra databasen.
        Søger først efter template_name og language, derefter efter name hvis ikke fundet."""
        try:
            cursor = self.connection.cursor()
            
            # Prøv først at finde template med template_name og language
            cursor.execute('''
                SELECT subject, body FROM mail_templates 
                WHERE template_name = ? AND language = ?
            ''', (template_name, language))
            result = cursor.fetchone()
            
            # Hvis ikke fundet, prøv at finde med name
            if not result and template_name:
                cursor.execute('''
                    SELECT subject, body FROM mail_templates 
                    WHERE name = ?
                ''', (template_name,))
                result = cursor.fetchone()
            
            # Hvis stadig ikke fundet, returner default template hvis det findes
            if not result:
                cursor.execute('''
                    SELECT subject, body FROM mail_templates 
                    WHERE is_default = 1
                ''')
                result = cursor.fetchone()
            
            return {'subject': result[0], 'body': result[1]} if result else None
            
        except sqlite3.Error as e:
            logging.error(f"Fejl ved hentning af mailtemplate: {str(e)}")
            return None

    def get_all_mail_templates(self):
        """Henter alle mail templates"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, subject, body, is_default
                    FROM mail_templates
                    ORDER BY name ASC
                ''')
                
                templates = []
                for row in cursor.fetchall():
                    templates.append({
                        'id': row[0],
                        'name': row[1],
                        'subject': row[2],
                        'body': row[3],
                        'is_default': bool(row[4])
                    })
                return templates
                
        except Exception as e:
            logging.error(f"Fejl ved hentning af mail templates: {str(e)}")
            raise

    def delete_mail_template(self, template_id):
        """Sletter en mail template"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM mail_templates WHERE id = ?', (template_id,))
                conn.commit()
                logging.info(f"Mail template {template_id} slettet succesfuldt")
                
        except Exception as e:
            logging.error(f"Fejl ved sletning af mail template: {str(e)}")
            raise

    def set_default_template(self, template_id, is_default):
        """Sætter eller fjerner en template som standard"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if is_default:
                    # Fjern eksisterende default template hvis der er en
                    cursor.execute('UPDATE mail_templates SET is_default = 0')
                    
                # Opdater den valgte template
                cursor.execute('''
                    UPDATE mail_templates 
                    SET is_default = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (is_default, template_id))
                
                conn.commit()
                logging.info(f"Mail template {template_id} {'sat som' if is_default else 'fjernet som'} standard")
                
        except Exception as e:
            logging.error(f"Fejl ved ændring af standard template: {str(e)}")
            raise

    def get_test_email(self):
        """Henter test email fra mail_config tabellen"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT test_email FROM mail_config LIMIT 1")
                result = cursor.fetchone()
                if result:
                    return result[0]  # # Returnerer den gemte test email
        except sqlite3.Error as e:
            logging.error(f"Databasefejl ved test email hentning: {str(e)}")
        return None

    def save_test_email(self, email):
        """Gemmer test email i mail konfiguration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE mail_config 
                    SET test_email = ?, updated_at = CURRENT_TIMESTAMP
                ''', (email,))
                conn.commit()
                logging.info("Test email gemt succesfuldt")
                
        except Exception as e:
            logging.error(f"Fejl ved gemning af test email: {str(e)}")
            raise

    def migrate(self):
        """Kører alle nødvendige database migrationer"""
        try:
            self.migrate_mail_templates()
            logging.info("Database migrationer kørt succesfuldt")
        except Exception as e:
            logging.error(f"Fejl ved kørsel af database migrationer: {str(e)}")
            raise

    def get_test_mail(self):
        # Henter test email fra mail_config tabellen
        try:
            cursor = self.connection.cursor()
            # Vi henter test_email fra mail_config tabellen, da dette er den korrekte lagringslokation for konfigureret testmail
            cursor.execute('SELECT test_email FROM mail_config LIMIT 1')
            result = cursor.fetchone()
            if result is None or not result[0].strip():
                # Hvis der ikke findes en test email, logges en fejl og en exception kastes
                logging.error("Ingen test email fundet i mail_config")
                raise Exception("Ingen test email fundet i mail_config")
            return result[0].strip()  # Returner den konfigurerede test email
        except Exception as e:
            logging.error("Fejl ved hentning af test email: " + str(e))
            raise

    # Ændret get_driver metode til at håndtere manglende chauffør_data_data tabel
    def get_driver(self, driver_id):
        # # DEBUG: Forsøger at hente chauffør data baseret på driver_id
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM chauffør_data_data WHERE Chauffør = ?", (driver_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]  # # DEBUG: Henter kolonnenavne
                driver = dict(zip(columns, row))
                print(f"# DEBUG: Fundet chauffør: {driver}")
                return driver
            else:
                # Returner fallback hvis ingen data findes
                print(f"# DEBUG: Ingen chauffør fundet med id {driver_id}, returnerer fallback")
                return {"id": driver_id, "name": driver_id}  # Fallback: brug driver_id som navn
        except sqlite3.OperationalError as e:
            # Denne exception fanges hvis tabellen ikke findes
            print(f"# DEBUG: Fejl i forespørgsel på chauffør_data_data: {str(e)}, bruger fallback")
            return {"id": driver_id, "name": driver_id}
        except Exception as e:
            logging.error(f"Fejl ved hentning af chauffør med id {driver_id}: {str(e)}")
            return {"id": driver_id, "name": driver_id}

    # # DEBUG: Ny metode til at opdatere eller gemme chaufførens email i driver_emails tabellen
    def update_driver_email(self, driver_id, email):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO driver_emails (driver_id, email, created_at, updated_at) VALUES (?, ?, datetime('now'), datetime('now'))",
                (driver_id, email)
            )
            self.connection.commit()
            print(f"# DEBUG: Email opdateret - DriverID: {driver_id}, Email: {email}")
            
        except Exception as e:
            # Forbedret fejlhåndtering med encoding-detaljer
            logging.error(f"Kritisk fejl under email-opdatering: {str(e)}")
            print(f"# DEBUG: Encoding fejl detaljer - Exception Type: {type(e).__name__}, Args: {e.args}")
            raise

    def migrate_mail_templates(self):
        """Migrerer mail_templates tabellen til den nye struktur"""
        try:
            cursor = self.connection.cursor()
            
            # Tjek om template_name kolonnen eksisterer
            cursor.execute("PRAGMA table_info(mail_templates)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'template_name' not in columns:
                # Backup eksisterende data
                cursor.execute("CREATE TEMPORARY TABLE mail_templates_backup AS SELECT * FROM mail_templates")
                
                # Drop eksisterende tabel
                cursor.execute("DROP TABLE mail_templates")
                
                # Opret ny tabel med opdateret struktur
                cursor.execute('''CREATE TABLE mail_templates(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    template_name TEXT NOT NULL,
                    language TEXT DEFAULT 'da',
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    is_default BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
                
                # Kopier data tilbage med nye kolonner
                cursor.execute('''
                    INSERT INTO mail_templates (id, name, template_name, language, subject, body, is_default, created_at, updated_at)
                    SELECT id, name, name, 'da', subject, body, is_default, created_at, updated_at
                    FROM mail_templates_backup
                ''')
                
                # Drop backup tabel
                cursor.execute("DROP TABLE mail_templates_backup")
                
                self.connection.commit()
                logging.info("Mail templates migreret succesfuldt")
                
        except sqlite3.Error as e:
            logging.error(f"Fejl ved migrering af mail templates: {str(e)}")
            raise 