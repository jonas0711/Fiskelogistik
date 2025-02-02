# Import nødvendige biblioteker
import customtkinter as ctk
from tkinter import messagebox
import logging
import os
from database_connection import DatabaseConnection
from datetime import datetime
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class MailTemplateManager:
    def __init__(self, parent):
        """Initialiserer mail template manager"""
        self.parent = parent
        
        # Opret database forbindelse
        self.db_path = os.path.join('databases', 'settings.db')
        self.db = DatabaseConnection(self.db_path)
        
        # Definer standard variabler
        self.default_variables = {
            "{{CHAUFFØR_NAVN}}": "Chaufførens navn",
            "{{FIRMA_NAVN}}": "Firmaets navn",
            "{{DATO}}": "Dagens dato",
            "{{RAPPORT_PERIODE}}": "Rapport periode",
            "{{TOTAL_TURE}}": "Antal ture",
            "{{TOTAL_DISTANCE}}": "Total distance",
            "{{TOTAL_TID}}": "Total tid",
            "{{GNS_TUR_LÆNGDE}}": "Gennemsnitlig tur længde",
            "{{GNS_TUR_TID}}": "Gennemsnitlig tur tid"
        }
        
        # Definer farver
        self.colors = {
            "primary": "#1E90FF",    # Bright blue
            "background": "#F5F7FA",  # Light gray
            "card": "#FFFFFF",        # White
            "text_primary": "#2C3E50",# Dark blue/gray
            "text_secondary": "#7F8C8D",# Medium gray
            "success": "#28a745",     # Grøn
            "danger": "#dc3545",      # Rød
            "warning": "#ffc107"      # Gul
        }
        
        self.setup_window()
        
    def setup_window(self):
        """Opsætter template manager vinduet"""
        # Opret toplevel vindue
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Mail Skabelon")
        
        # Beregn vinduesstørrelse (70% af skærmbredden og 80% af skærmhøjden)
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = int(screen_width * 0.7)
        window_height = int(screen_height * 0.8)
        
        # Beregn position for centrering
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Sæt geometri
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.minsize(1000, 800)
        
        # Hovedcontainer med moderne design
        main_frame = ctk.CTkFrame(
            self.window,
            fg_color="#f5f5f5",
            corner_radius=15
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel sektion
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20,30))
        
        title = ctk.CTkLabel(
            title_frame,
            text="Mail Skabelon",
            font=("Segoe UI", 32, "bold"),
            text_color="#1a1a1a"
        )
        title.pack(anchor="center")
        
        # Content container
        content_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=10)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0,20))
        
        # Input sektion med labels og felter
        input_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=40, pady=30)
        
        # Skabelon navn
        name_label = ctk.CTkLabel(
            input_frame,
            text="Skabelon Navn",
            font=("Segoe UI", 14, "bold"),
            text_color="#1a1a1a"
        )
        name_label.pack(anchor="w", pady=(0,5))
        
        self.name_entry = ctk.CTkEntry(
            input_frame,
            width=window_width-200,
            height=35,
            font=("Segoe UI", 12),
            placeholder_text="Indtast navn på skabelonen"
        )
        self.name_entry.pack(fill="x", pady=(0,20))
        
        # Email emne
        subject_label = ctk.CTkLabel(
            input_frame,
            text="Email Emne",
            font=("Segoe UI", 14, "bold"),
            text_color="#1a1a1a"
        )
        subject_label.pack(anchor="w", pady=(0,5))
        
        self.subject_entry = ctk.CTkEntry(
            input_frame,
            width=window_width-200,
            height=35,
            font=("Segoe UI", 12),
            placeholder_text="Indtast emne for emailen"
        )
        self.subject_entry.pack(fill="x", pady=(0,20))
        
        # Email indhold
        content_label = ctk.CTkLabel(
            input_frame,
            text="Email Indhold",
            font=("Segoe UI", 14, "bold"),
            text_color="#1a1a1a"
        )
        content_label.pack(anchor="w", pady=(0,5))
        
        # HTML Editor med forbedret styling
        self.html_editor = ctk.CTkTextbox(
            input_frame,
            width=window_width-200,
            height=400,
            font=("Segoe UI", 12),
            fg_color="white",
            border_color="#e0e0e0",
            border_width=1
        )
        self.html_editor.pack(fill="both", expand=True, pady=(0,20))
        
        # Variabler sektion
        var_frame = ctk.CTkFrame(input_frame, fg_color="#f8f9fa", corner_radius=10)
        var_frame.pack(fill="x", pady=(0,20))
        
        var_title = ctk.CTkLabel(
            var_frame,
            text="Tilgængelige Variabler",
            font=("Segoe UI", 14, "bold"),
            text_color="#1a1a1a"
        )
        var_title.pack(anchor="w", padx=20, pady=(15,10))
        
        for var, desc in self.default_variables.items():
            var_item = ctk.CTkLabel(
                var_frame,
                text=f"{var} - {desc}",
                font=("Segoe UI", 12),
                text_color="#495057"
            )
            var_item.pack(anchor="w", padx=20, pady=2)
        
        # Knap container
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=40, pady=(0,30))
        
        # Gem knap
        self.save_button = ctk.CTkButton(
            button_frame,
            text="Gem Skabelon",
            command=self.save_template,
            fg_color="#28a745",
            hover_color="#218838",
            height=38,
            corner_radius=8,
            font=("Segoe UI", 12, "bold")
        )
        self.save_button.pack(side="left", padx=5)
        
        # Preview knap
        preview_button = ctk.CTkButton(
            button_frame,
            text="Vis Preview",
            command=self.show_preview,
            fg_color="#17a2b8",
            hover_color="#138496",
            height=38,
            corner_radius=8,
            font=("Segoe UI", 12, "bold")
        )
        preview_button.pack(side="left", padx=5)
        
        # Send test mail knap
        test_button = ctk.CTkButton(
            button_frame,
            text="Send Test Mail",
            command=self.send_test_mail,
            fg_color="#6c757d",
            hover_color="#5a6268",
            height=38,
            corner_radius=8,
            font=("Segoe UI", 12, "bold")
        )
        test_button.pack(side="left", padx=5)
        
        # Sæt som standard knap
        self.default_button = ctk.CTkButton(
            button_frame,
            text="Sæt Som Standard",
            command=self.set_as_default,
            fg_color="#007bff",
            hover_color="#0056b3",
            height=38,
            corner_radius=8,
            font=("Segoe UI", 12, "bold")
        )
        self.default_button.pack(side="right", padx=5)
        
        # Indlæs templates
        self.load_templates()
        
    def load_templates(self):
        """Indlæser alle templates fra databasen"""
        try:
            templates = self.db.get_all_mail_templates()
            
            # Ryd eksisterende liste
            for widget in self.template_list.winfo_children():
                widget.destroy()
                
            # Tilføj hver template til listen
            for template in templates:
                is_default = template.get('is_default', False)
                name = template['name']
                if is_default:
                    name += " (Standard)"
                    
                button = ctk.CTkButton(
                    self.template_list,
                    text=name,
                    command=lambda t=template: self.load_template(t),
                    fg_color="transparent",
                    text_color=self.colors["text_primary"],
                    hover_color=self.colors["background"]
                )
                button.pack(fill="x", pady=2)
                
        except Exception as e:
            logging.error(f"Fejl ved indlæsning af templates: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke indlæse templates: {str(e)}")
            
    def load_template(self, template):
        """Indlæser en specifik template i editoren"""
        try:
            self.current_template = template
            
            # Opdater UI
            self.name_entry.delete(0, 'end')
            self.name_entry.insert(0, template['name'])
            
            self.subject_entry.delete(0, 'end')
            self.subject_entry.insert(0, template['subject'])
            
            self.html_editor.delete('1.0', 'end')
            self.html_editor.insert('1.0', template['body'])
            
            # Aktiver knapper
            self.delete_button.configure(state="normal")
            self.default_button.configure(
                text="Fjern Som Standard" if template.get('is_default', False) else "Sæt Som Standard"
            )
            
        except Exception as e:
            logging.error(f"Fejl ved indlæsning af template: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke indlæse template: {str(e)}")
            
    def new_template(self):
        """Opretter en ny tom template"""
        self.current_template = None
        
        # Ryd felter
        self.name_entry.delete(0, 'end')
        self.subject_entry.delete(0, 'end')
        self.html_editor.delete('1.0', 'end')
        
        # Indsæt standard HTML struktur
        self.html_editor.insert('1.0', """
<!DOCTYPE html>
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
</html>
""")
        
        # Deaktiver knapper
        self.delete_button.configure(state="disabled")
        self.default_button.configure(text="Sæt Som Standard")
        
    def save_template(self):
        """Gemmer den aktuelle template"""
        try:
            name = self.name_entry.get().strip()
            subject = self.subject_entry.get().strip()
            body = self.html_editor.get('1.0', 'end').strip()
            
            if not name or not subject or not body:
                messagebox.showwarning("Advarsel", "Alle felter skal udfyldes")
                return
                
            # Gem template
            template_id = self.current_template['id'] if self.current_template else None
            is_default = self.current_template.get('is_default', False)
            
            self.db.save_mail_template(
                template_id=template_id,
                name=name,
                subject=subject,
                body=body,
                is_default=is_default
            )
            
            # Genindlæs templates
            self.load_templates()
            
            messagebox.showinfo("Success", "Skabelon gemt succesfuldt")
            
        except Exception as e:
            logging.error(f"Fejl ved gemning af template: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke gemme template: {str(e)}")
            
    def delete_template(self):
        """Sletter den aktuelle template"""
        try:
            if not self.current_template:
                return
                
            if not messagebox.askyesno("Bekræft", 
                f"Er du sikker på at du vil slette skabelonen '{self.current_template['name']}'?"):
                return
                
            self.db.delete_mail_template(self.current_template['id'])
            
            # Genindlæs templates
            self.load_templates()
            
            # Ryd editor
            self.new_template()
            
            messagebox.showinfo("Success", "Skabelon slettet succesfuldt")
            
        except Exception as e:
            logging.error(f"Fejl ved sletning af template: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke slette template: {str(e)}")
            
    def set_as_default(self):
        """Sætter eller fjerner den aktuelle template som standard"""
        try:
            if not self.current_template:
                return
                
            is_default = self.current_template.get('is_default', False)
            
            # Opdater database
            self.db.set_default_template(
                self.current_template['id'],
                not is_default
            )
            
            # Opdater current template
            self.current_template['is_default'] = not is_default
            
            # Opdater knap tekst
            self.default_button.configure(
                text="Fjern Som Standard" if not is_default else "Sæt Som Standard"
            )
            
            # Genindlæs templates
            self.load_templates()
            
        except Exception as e:
            logging.error(f"Fejl ved ændring af standard template: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke ændre standard template: {str(e)}")
            
    def show_preview(self):
        """Viser preview af den aktuelle template"""
        try:
            # Få template indhold
            body = self.html_editor.get('1.0', 'end').strip()
            
            # Erstat variabler med eksempel værdier
            preview_data = {
                "{{CHAUFFØR_NAVN}}": "John Doe",
                "{{FIRMA_NAVN}}": "Test Firma A/S",
                "{{DATO}}": datetime.now().strftime("%d-%m-%Y"),
                "{{RAPPORT_PERIODE}}": "Januar 2024",
                "{{TOTAL_TURE}}": "42",
                "{{TOTAL_DISTANCE}}": "1337",
                "{{TOTAL_TID}}": "24",
                "{{GNS_TUR_LÆNGDE}}": "31.8",
                "{{GNS_TUR_TID}}": "0.57"
            }
            
            preview_html = body
            for var, value in preview_data.items():
                preview_html = preview_html.replace(var, str(value))
                
            # Gem preview til temp fil
            preview_path = os.path.join('temp', 'preview.html')
            os.makedirs('temp', exist_ok=True)
            
            with open(preview_path, 'w', encoding='utf-8') as f:
                f.write(preview_html)
                
            # Åbn i standard browser
            os.startfile(preview_path)
            
        except Exception as e:
            logging.error(f"Fejl ved visning af preview: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke vise preview: {str(e)}")
            
    def send_test_mail(self):
        """Sender en test mail med den aktuelle template"""
        try:
            # Få test mail fra indstillinger
            test_email = self.db.get_test_email()
            if not test_email:
                messagebox.showwarning(
                    "Advarsel",
                    "Ingen test email konfigureret. Gå til Indstillinger -> Mail for at konfigurere."
                )
                return
                
            # Få template indhold
            subject = self.subject_entry.get().strip()
            body = self.html_editor.get('1.0', 'end').strip()
            
            # Erstat variabler med test værdier
            test_data = {
                "{{CHAUFFØR_NAVN}}": "Test Chauffør",
                "{{FIRMA_NAVN}}": "Test Firma A/S",
                "{{DATO}}": datetime.now().strftime("%d-%m-%Y"),
                "{{RAPPORT_PERIODE}}": "Test Periode",
                "{{TOTAL_TURE}}": "10",
                "{{TOTAL_DISTANCE}}": "500",
                "{{TOTAL_TID}}": "8",
                "{{GNS_TUR_LÆNGDE}}": "50",
                "{{GNS_TUR_TID}}": "0.8"
            }
            
            test_body = body
            for var, value in test_data.items():
                test_body = test_body.replace(var, str(value))
                
            # Send test mail
            from mail_system import MailSystem
            mail_system = MailSystem()
            
            mail_system.send_mail(
                to=test_email,
                subject=f"TEST: {subject}",
                body=test_body,
                is_html=True
            )
            
            messagebox.showinfo(
                "Success",
                f"Test mail sendt til {test_email}\nTjek din indbakke (og spam mappe)"
            )
            
        except Exception as e:
            logging.error(f"Fejl ved sending af test mail: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke sende test mail: {str(e)}")
            
    def run(self):
        """Starter vinduet"""
        # Centrer vinduet
        self.window.update_idletasks()
        width = 1000
        height = 800
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Gør vinduet modalt
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.focus_set()

    def get_template(self, template_name):
        # # DEBUG: Starter hentning af template med navn: {template_name}
        logging.debug(f"Starter hentning af template: {template_name}")
        # Ændret SQL-forespørgsel: Bruger nu den korrekte tabel "mail_templates" og kolonnen "body" til HTML-indholdet
        query = "SELECT body FROM mail_templates WHERE name = ?"
        cursor = self.db.connection.cursor()  # # Opretter cursor for at udføre SQL forespørgslen
        cursor.execute(query, (template_name,))
        result = cursor.fetchall()  # # Henter alle resultater
        if result:
            template = result[0]['body']  # # Henter HTML-indholdet fra "body" kolonnen
            logging.debug("Template fundet og returneret fra databasen.")
            return template
        else:
            logging.error("Ingen mail template fundet med navn: " + template_name)
            return "<html><body>Mail template ikke fundet</body></html>"

    def send_rapport_mail(self, driver_name, email, rapport_path, report_date):
        try:
            # Hent template med korrekt navn og sprog
            template = self.db.get_mail_template('chauffør_report', 'da')
            
            if not template:
                # Fallback HTML-template
                template = {
                    'subject': 'Chauffør Rapport - {driver_name}',
                    'body': '''<html><body>
                        <h1>Rapport for {driver_name}</h1>
                        <p>Dato: {report_date}</p>
                        <p>Vedhæftet fil indeholder din månedlige rapport.</p>
                    </body></html>'''
                }
                logging.warning("Bruger standard mail template")

            # Åbn rapportfil i binær tilstand
            with open(rapport_path, 'rb') as f:
                file_data = f.read()
            
            # Opret meddelelse med korrekt MIME-typer
            msg = MIMEMultipart()
            msg.attach(MIMEText(template['body'].format(
                driver_name=driver_name,
                report_date=report_date
            ), 'html'))
            
            # Tilføj vedhæftning korrekt
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file_data)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            'attachment; filename="{}"'.format(os.path.basename(rapport_path)))
            msg.attach(part)
            
            # Send mail
            self.mail_handler.send_mail(email, msg)
        except Exception as e:
            logging.error(f"Fejl ved sending af rapport mail: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke sende rapport mail: {str(e)}") 