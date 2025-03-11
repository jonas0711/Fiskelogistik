import customtkinter as ctk
import sqlite3
import os
import logging
from tkinter import messagebox
import re
from database_connection import DatabaseConnection

class SettingsWindow:
    def __init__(self):
        # Tilføj DPI-konfiguration som i andre vinduer
        ctk.set_widget_scaling(1.0)
        ctk.deactivate_automatic_dpi_awareness()
        
        # Grundlæggende opsætning
        self.root = ctk.CTk()
        self.root.title("RIO Indstillinger")
        self.root.after(300, self._safe_window_init)  # Forsinket initialisering
        
        # Farver - samme som hovedapplikationen
        self.colors = {
            "primary": "#1E90FF",    # Bright blue
            "background": "#F5F7FA",  # Light gray
            "card": "#FFFFFF",        # White
            "text_primary": "#2C3E50",# Dark blue/gray
            "text_secondary": "#7F8C8D",# Medium gray
            "success": "#28a745",
            "danger": "#dc3545",
            "warning": "#ffc107"
        }
        
        # Tema indstillinger
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Opret database hvis den ikke eksisterer
        self.setup_database()
        
        # Load eksisterende indstillinger
        self.current_settings = self.load_settings()
        
        self.db = DatabaseConnection("databases/settings.db")
        
        self.setup_ui()

    def setup_database(self):
        # Opret database mappe hvis den ikke eksisterer
        if not os.path.exists('databases'):
            os.makedirs('databases')
            
        # Opret forbindelse til database
        conn = sqlite3.connect('databases/settings.db')
        cursor = conn.cursor()
        
        # Opret tabel hvis den ikke eksisterer
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        ''')
        
        conn.commit()
        conn.close()

    def load_settings(self):
        conn = sqlite3.connect('databases/settings.db')
        cursor = conn.cursor()
        
        # Hent alle indstillinger
        cursor.execute('SELECT key, value FROM settings')
        settings = dict(cursor.fetchall())
        
        conn.close()
        
        # Returner indstillinger med standardværdier hvis de ikke findes
        return {
            'min_km': settings.get('min_km', '100'),
            'diesel_price': settings.get('diesel_price', '13.50')
        }

    def save_settings(self):
        # Valider input for minimum KM
        try:
            min_km = int(self.min_km_entry.get())
            if min_km < 0:
                raise ValueError("Minimum KM skal være et positivt tal")
        except ValueError as e:
            self.status_label.configure(
                text=f"Fejl: {str(e)}",
                text_color="red"
            )
            return

        # Valider input for diesel pris
        try:
            diesel_price = float(self.diesel_price_entry.get().replace(',', '.'))
            if diesel_price <= 0:
                raise ValueError("Diesel pris skal være større end 0")
        except ValueError as e:
            self.status_label.configure(
                text="Fejl: Diesel pris skal være et gyldigt tal større end 0",
                text_color="red"
            )
            return

        conn = sqlite3.connect('databases/settings.db')
        cursor = conn.cursor()
        
        # Gem indstillinger
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                      ('min_km', str(min_km)))
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                      ('diesel_price', str(diesel_price)))
        
        conn.commit()
        conn.close()
        
        self.status_label.configure(
            text="Indstillinger gemt succesfuldt!",
            text_color="green"
        )
        
    def setup_ui(self):
        """Opsætter brugergrænsefladen"""
        # Hovedcontainer
        self.main_container = ctk.CTkFrame(self.root, fg_color=self.colors["background"])
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Opret tabs
        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.pack(fill="both", expand=True)
        
        # Tilføj tabs
        self.general_tab = self.tabview.add("Generelt")
        self.mail_tab = self.tabview.add("Mail")
        self.template_tab = self.tabview.add("Mail Skabeloner")
        
        self.setup_general_tab()
        self.setup_mail_tab()
        self.setup_template_tab()
        
    def setup_general_tab(self):
        # Titel sektion
        self.create_title_section(self.general_tab)
        
        # Indstillinger sektion
        self.create_settings_section(self.general_tab)
        
    def create_title_section(self, parent):
        title_frame = ctk.CTkFrame(parent, fg_color="transparent")
        title_frame.pack(fill="x", pady=(20, 20), padx=40)
        
        title = ctk.CTkLabel(
            title_frame,
            text="System Indstillinger",
            font=("Segoe UI", 24, "bold"),
            text_color=self.colors["primary"]
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Konfigurer systemets grundlæggende indstillinger",
            font=("Segoe UI", 14),
            text_color=self.colors["text_secondary"]
        )
        subtitle.pack(pady=(5, 0))

    def create_settings_section(self, parent):
        settings_frame = ctk.CTkFrame(parent, fg_color=self.colors["card"])
        settings_frame.pack(fill="x", padx=40, pady=10)
        
        # Container til indstillinger
        container = ctk.CTkFrame(settings_frame, fg_color="transparent")
        container.pack(pady=20, padx=20, fill="x")
        
        # Minimum KM indstilling
        km_label = ctk.CTkLabel(
            container,
            text="Minimum antal KM kørt:",
            font=("Segoe UI", 14),
            text_color=self.colors["text_primary"]
        )
        km_label.pack(anchor="w", pady=(0, 5))
        
        self.min_km_entry = ctk.CTkEntry(
            container,
            placeholder_text="Indtast minimum antal kilometer",
            font=("Segoe UI", 12),
            width=200
        )
        self.min_km_entry.pack(anchor="w")
        self.min_km_entry.insert(0, self.current_settings['min_km'])
        
        # Beskrivelse for KM
        km_desc = ctk.CTkLabel(
            container,
            text="Chauffører med færre kilometer vil ikke indgå i rapporter",
            font=("Segoe UI", 12),
            text_color=self.colors["text_secondary"]
        )
        km_desc.pack(anchor="w", pady=(5, 20))

        # Diesel pris indstilling
        diesel_label = ctk.CTkLabel(
            container,
            text="Diesel pris pr. liter (DKK):",
            font=("Segoe UI", 14),
            text_color=self.colors["text_primary"]
        )
        diesel_label.pack(anchor="w", pady=(0, 5))
        
        self.diesel_price_entry = ctk.CTkEntry(
            container,
            placeholder_text="Indtast diesel pris",
            font=("Segoe UI", 12),
            width=200
        )
        self.diesel_price_entry.pack(anchor="w")
        self.diesel_price_entry.insert(0, self.current_settings['diesel_price'])
        
        # Beskrivelse for diesel pris
        diesel_desc = ctk.CTkLabel(
            container,
            text="Bruges til beregning af brændstofomkostninger i rapporter",
            font=("Segoe UI", 12),
            text_color=self.colors["text_secondary"]
        )
        diesel_desc.pack(anchor="w", pady=(5, 20))
        
        # Gem knap
        save_button = ctk.CTkButton(
            container,
            text="Gem Indstillinger",
            font=("Segoe UI", 12),
            fg_color=self.colors["primary"],
            hover_color="#1874CD",
            command=self.save_settings
        )
        save_button.pack(pady=20)

    def setup_mail_tab(self):
        """Opsætter mail indstillinger tab"""
        # Mail konfiguration frame
        mail_frame = ctk.CTkFrame(self.mail_tab, fg_color=self.colors["card"])
        mail_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        title = ctk.CTkLabel(
            mail_frame,
            text="Mail Konfiguration",
            font=("Segoe UI", 20, "bold"),
            text_color=self.colors["primary"]
        )
        title.pack(pady=(20,10))
        
        # Beskrivelse
        description = ctk.CTkLabel(
            mail_frame,
            text="Konfigurer mail indstillinger for rapport afsendelse",
            font=("Segoe UI", 12),
            text_color=self.colors["text_secondary"]
        )
        description.pack(pady=(0,20))
        
        # Input container
        input_container = ctk.CTkFrame(mail_frame, fg_color="transparent")
        input_container.pack(fill="x", padx=40)
        
        # SMTP Server
        smtp_label = ctk.CTkLabel(
            input_container,
            text="SMTP Server:",
            font=("Segoe UI", 12),
            text_color=self.colors["text_primary"]
        )
        smtp_label.pack(anchor="w", pady=(0,5))
        
        self.smtp_entry = ctk.CTkEntry(
            input_container,
            placeholder_text="f.eks. smtp.gmail.com",
            width=300
        )
        self.smtp_entry.pack(anchor="w")
        
        # SMTP Port
        port_label = ctk.CTkLabel(
            input_container,
            text="SMTP Port:",
            font=("Segoe UI", 12),
            text_color=self.colors["text_primary"]
        )
        port_label.pack(anchor="w", pady=(20,5))
        
        self.port_entry = ctk.CTkEntry(
            input_container,
            placeholder_text="f.eks. 587",
            width=300
        )
        self.port_entry.pack(anchor="w")
        
        # Email
        email_label = ctk.CTkLabel(
            input_container,
            text="Email:",
            font=("Segoe UI", 12),
            text_color=self.colors["text_primary"]
        )
        email_label.pack(anchor="w", pady=(20,5))
        
        self.email_entry = ctk.CTkEntry(
            input_container,
            placeholder_text="Din email adresse",
            width=300
        )
        self.email_entry.pack(anchor="w")
        
        # Password
        password_label = ctk.CTkLabel(
            input_container,
            text="App Password:",
            font=("Segoe UI", 12),
            text_color=self.colors["text_primary"]
        )
        password_label.pack(anchor="w", pady=(20,5))
        
        self.password_entry = ctk.CTkEntry(
            input_container,
            placeholder_text="Dit app password",
            width=300,
            show="*"
        )
        self.password_entry.pack(anchor="w")
        
        # Test Email
        test_email_label = ctk.CTkLabel(
            input_container,
            text="Test Email:",
            font=("Segoe UI", 12),
            text_color=self.colors["text_primary"]
        )
        test_email_label.pack(anchor="w", pady=(20,5))
        
        self.test_email_entry = ctk.CTkEntry(
            input_container,
            placeholder_text="Email for test mails",
            width=300
        )
        self.test_email_entry.pack(anchor="w")
        
        # Knapper
        button_container = ctk.CTkFrame(mail_frame, fg_color="transparent")
        button_container.pack(fill="x", padx=40, pady=30)
        
        # Gem knap
        save_button = ctk.CTkButton(
            button_container,
            text="Gem Indstillinger",
            command=self.save_mail_config,
            fg_color=self.colors["success"]
        )
        save_button.pack(side="left", padx=5)
        
        # Test forbindelse knap
        test_button = ctk.CTkButton(
            button_container,
            text="Test Forbindelse",
            command=self.test_mail_connection
        )
        test_button.pack(side="left", padx=5)
        
        # Status label
        self.mail_status_label = ctk.CTkLabel(
            mail_frame,
            text="",
            font=("Segoe UI", 12)
        )
        self.mail_status_label.pack(pady=10)
        
        # Indlæs eksisterende konfiguration
        self.load_mail_config()
        
    def setup_template_tab(self):
        """Opsætter mail skabelon tab"""
        template_frame = ctk.CTkFrame(self.template_tab, fg_color=self.colors["card"])
        template_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        title = ctk.CTkLabel(
            template_frame,
            text="Mail Skabelon",
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors["primary"]
        )
        title.pack(pady=(20,10))
        
        # Template navn
        name_frame = ctk.CTkFrame(template_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=20, pady=5)
        
        name_label = ctk.CTkLabel(
            name_frame,
            text="Skabelon Navn",
            font=("Segoe UI", 12),
            text_color=self.colors["text_primary"]
        )
        name_label.pack(side="left", padx=5)
        
        self.template_name = ctk.CTkEntry(name_frame, width=300)
        self.template_name.pack(side="right", padx=5)
        
        # Subject
        subject_frame = ctk.CTkFrame(template_frame, fg_color="transparent")
        subject_frame.pack(fill="x", padx=20, pady=5)
        
        subject_label = ctk.CTkLabel(
            subject_frame,
            text="Email Emne",
            font=("Segoe UI", 12),
            text_color=self.colors["text_primary"]
        )
        subject_label.pack(side="left", padx=5)
        
        self.template_subject = ctk.CTkEntry(subject_frame, width=300)
        self.template_subject.pack(side="right", padx=5)
        
        # Template body
        body_label = ctk.CTkLabel(
            template_frame,
            text="Email Indhold",
            font=("Segoe UI", 12),
            text_color=self.colors["text_primary"]
        )
        body_label.pack(padx=20, pady=(10,5), anchor="w")
        
        self.template_body = ctk.CTkTextbox(
            template_frame,
            width=600,
            height=300
        )
        self.template_body.pack(padx=20, pady=5)
        
        # Variable info
        variables_text = """
Tilgængelige variabler:
{CHAUFFØR_NAVN} - Indsætter chaufførens navn
{MÅNED} - Indsætter måneden for rapporten
{ÅR} - Indsætter året for rapporten
{FIRMA_NAVN} - Indsætter firmaets navn
        """
        
        variables_label = ctk.CTkLabel(
            template_frame,
            text=variables_text,
            font=("Segoe UI", 12),
            text_color=self.colors["text_secondary"],
            justify="left"
        )
        variables_label.pack(padx=20, pady=10, anchor="w")
        
        # Knapper
        button_frame = ctk.CTkFrame(template_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        preview_button = ctk.CTkButton(
            button_frame,
            text="Forhåndsvis",
            command=self.preview_template,
            fg_color=self.colors["primary"]
        )
        preview_button.pack(side="left", padx=5)
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Gem som Standard",
            command=self.save_template,
            fg_color=self.colors["success"]
        )
        save_button.pack(side="right", padx=5)
        
        # Load eksisterende template
        self.load_template()
        
    def test_mail_connection(self):
        """Tester mail forbindelsen"""
        try:
            # Få aktuel konfiguration
            smtp_server = self.smtp_entry.get().strip()
            smtp_port = self.port_entry.get().strip()
            email = self.email_entry.get().strip()
            password = self.password_entry.get().strip()
            
            if not all([smtp_server, smtp_port, email, password]):
                raise ValueError("Udfyld venligst alle felter først")
                
            # Test forbindelse
            from mail_system import MailSystem
            mail_system = MailSystem()
            
            if mail_system.test_connection():
                self.mail_status_label.configure(
                    text="Forbindelse testet succesfuldt!",
                    text_color=self.colors["success"]
                )
            else:
                self.mail_status_label.configure(
                    text="Kunne ikke oprette forbindelse",
                    text_color=self.colors["danger"]
                )
                
        except Exception as e:
            self.mail_status_label.configure(
                text=f"Fejl: {str(e)}",
                text_color=self.colors["danger"]
            )
            
    def load_mail_config(self):
        """Indlæser eksisterende mail konfiguration"""
        try:
            config = self.db.get_mail_config()
            if config:
                self.smtp_entry.delete(0, 'end')
                self.smtp_entry.insert(0, config['smtp_server'])
                
                self.port_entry.delete(0, 'end')
                self.port_entry.insert(0, str(config['smtp_port']))
                
                self.email_entry.delete(0, 'end')
                self.email_entry.insert(0, config['email'])
                
                self.password_entry.delete(0, 'end')
                self.password_entry.insert(0, config['password'])
                
            # Indlæs test email
            test_email = self.db.get_test_email()
            if test_email:
                self.test_email_entry.delete(0, 'end')
                self.test_email_entry.insert(0, test_email)
                
        except Exception as e:
            logging.error(f"Fejl ved indlæsning af mail indstillinger: {str(e)}")
            self.mail_status_label.configure(
                text=f"Fejl ved indlæsning: {str(e)}",
                text_color=self.colors["danger"]
            )
            
    def save_mail_config(self):
        """Gemmer mail konfiguration"""
        try:
            # Valider input
            smtp_server = self.smtp_entry.get().strip()
            smtp_port = self.port_entry.get().strip()
            email = self.email_entry.get().strip()
            password = self.password_entry.get().strip()
            test_email = self.test_email_entry.get().strip()
            
            if not all([smtp_server, smtp_port, email, password]):
                raise ValueError("Alle felter skal udfyldes")
                
            try:
                smtp_port = int(smtp_port)
            except:
                raise ValueError("SMTP port skal være et tal")
                
            # Valider email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                raise ValueError("Ugyldig email adresse")
                
            if test_email and not re.match(r"[^@]+@[^@]+\.[^@]+", test_email):
                raise ValueError("Ugyldig test email adresse")
                
            # Gem konfiguration
            config = {
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'email': email,
                'password': password
            }
            
            self.db.save_mail_config(config)
            
            # Gem test email hvis angivet
            if test_email:
                self.db.save_test_email(test_email)
                
            self.mail_status_label.configure(
                text="Mail konfiguration gemt succesfuldt!",
                text_color=self.colors["success"]
            )
            
        except Exception as e:
            self.mail_status_label.configure(
                text=f"Fejl: {str(e)}",
                text_color=self.colors["danger"]
            )
            
    def preview_template(self):
        """Viser forhåndsvisning af mail template"""
        try:
            # Hent template værdier
            name = self.template_name.get()
            subject = self.template_subject.get()
            body = self.template_body.get("1.0", "end-1c")
            
            # Valider input
            if not all([name, subject, body]):
                messagebox.showerror("Fejl", "Alle felter skal udfyldes")
                return
                
            # Erstat variabler med eksempel værdier
            preview_body = body.replace("{CHAUFFØR_NAVN}", "John Doe")\
                             .replace("{MÅNED}", "Januar")\
                             .replace("{ÅR}", "2024")\
                             .replace("{FIRMA_NAVN}", "Transport A/S")
                             
            # Vis preview
            preview_window = ctk.CTkToplevel(self.root)
            preview_window.title("Forhåndsvisning")
            
            preview_frame = ctk.CTkFrame(preview_window, fg_color=self.colors["card"])
            preview_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            preview_text = ctk.CTkTextbox(
                preview_frame,
                width=600,
                height=400
            )
            preview_text.pack(padx=20, pady=20)
            
            preview_text.insert("1.0", f"Emne: {subject}\n\n{preview_body}")
            preview_text.configure(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke vise forhåndsvisning: {str(e)}")
            
    def save_template(self):
        """Gemmer mail template som standard"""
        try:
            # Hent template værdier
            name = self.template_name.get()
            subject = self.template_subject.get()
            body = self.template_body.get("1.0", "end-1c")
            
            # Valider input
            if not all([name, subject, body]):
                messagebox.showerror("Fejl", "Alle felter skal udfyldes")
                return
                
            # Gem i database
            self.db.save_mail_template(name, subject, body, is_default=True)
            
            messagebox.showinfo("Success", "Mail skabelon gemt som standard!")
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke gemme mail skabelon: {str(e)}")
            
    def load_template(self):
        """Indlæser eksisterende standard template"""
        try:
            # # DEBUG: Forsøger at indlæse mail-skabelon
            logging.info("Forsøger at indlæse mail-skabelon")
            template = self.db.get_mail_template()
            
            if template:
                # # DEBUG: Skabelon fundet, indhold: {subject, body}
                logging.info(f"Mail-skabelon fundet: {template.keys()}")
                
                # Opdateret kode til at håndtere dictionary-format i stedet for tuple
                self.template_name.delete(0, "end")
                self.template_name.insert(0, "chauffør_report")  # Standardnavn
                
                self.template_subject.delete(0, "end")
                self.template_subject.insert(0, template['subject'])
                
                self.template_body.delete("1.0", "end")
                self.template_body.insert("1.0", template['body'])
                
                # # DEBUG: Skabelon indlæst succesfuldt
                logging.info("Mail-skabelon indlæst succesfuldt")
            else:
                # # DEBUG: Ingen skabelon fundet
                logging.warning("Ingen mail-skabelon fundet i databasen")
                
        except Exception as e:
            # # DEBUG: Detaljeret fejlmeddelelse
            logging.error(f"Fejl ved indlæsning af mail skabelon: {str(e)}")
            logging.error(f"Fejltype: {type(e).__name__}")
            if hasattr(e, '__traceback__'):
                import traceback
                trace = ''.join(traceback.format_tb(e.__traceback__))
                logging.error(f"Stacktrace: {trace}")

    def _safe_window_init(self):
        """Sikrer korrekt vinduesstørrelse efter UI-load"""
        self.root.update_idletasks()
        self.root.state("zoomed")
        self.root.minsize(800, 600)  # Minimumsstørrelse for indstillinger
        logging.info("Indstillingsvindue fuldt initialiseret")

    def run(self):
        # Centrer vinduet
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.mainloop()

if __name__ == "__main__":
    app = SettingsWindow()
    app.run()