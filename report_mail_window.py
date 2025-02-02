# Import nødvendige biblioteker
import customtkinter as ctk
from tkinter import messagebox
import logging
from mail_handler import MailHandler
from database_connection import DatabaseConnection
import os
from datetime import datetime
import threading
from word_report import WordReportGenerator
import sqlite3

class ReportMailWindow:
    def __init__(self, parent, selected_database, report_type, group_name=None, driver_name=None):
        """Initialiserer rapport mail vinduet"""
        self.parent = parent
        self.selected_database = selected_database
        self.report_type = report_type
        self.group_name = group_name
        self.driver_name = driver_name
        
        # Opret database forbindelse og mail handler
        self.db = DatabaseConnection('settings.db')
        self.mail_handler = MailHandler()
        
        # Opret word report generator
        self.word_report = WordReportGenerator(self.selected_database)
        
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
        self.load_drivers()
        
    def setup_window(self):
        """Opsætter vinduet og dets komponenter"""
        # Opret toplevel vindue
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Send Rapporter")
        
        # Beregn skærmstørrelse
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Sæt vinduesstørrelse til 60% af skærmbredden og 70% af skærmhøjden
        window_width = int(screen_width * 0.60)
        window_height = int(screen_height * 0.70)
        
        # Beregn x og y koordinater for centrering
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Sæt geometri
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.minsize(600, 400)
        
        # Gør vinduet modalt
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.focus_force()
        
        # Hovedcontainer med gradient baggrund
        main_frame = ctk.CTkFrame(
            self.window,
            fg_color=self.colors["background"],
            corner_radius=15
        )
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header sektion med titel og beskrivelse
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Send Rapporter",
            font=("Segoe UI", 24, "bold"),
            text_color=self.colors["primary"]
        )
        title.pack(anchor="center")
        
        description = ctk.CTkLabel(
            header_frame,
            text="Vælg chauffører og send deres individuelle rapporter via mail",
            font=("Segoe UI", 12),
            text_color=self.colors["text_secondary"]
        )
        description.pack(anchor="center", pady=(5, 0))
        
        # Content frame med afrundede hjørner og skygge-effekt
        content_frame = ctk.CTkFrame(
            main_frame,
            fg_color=self.colors["card"],
            corner_radius=10
        )
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Liste frame med chauffører
        self.list_frame = ctk.CTkScrollableFrame(
            content_frame,
            fg_color="transparent",
            width=window_width - 120,
            height=window_height - 250
        )
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Headers med moderne styling
        header_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent", height=40)
        header_frame.pack(fill="x", padx=10, pady=(0, 5))
        header_frame.pack_propagate(False)
        
        # Chauffør header
        ctk.CTkLabel(
            header_frame,
            text="Chauffør",
            font=("Segoe UI", 12, "bold"),
            text_color=self.colors["text_primary"]
        ).pack(side="left", padx=(10, 0))
        
        # Status header
        ctk.CTkLabel(
            header_frame,
            text="Status",
            font=("Segoe UI", 12, "bold"),
            text_color=self.colors["text_primary"]
        ).pack(side="right", padx=(0, 150))
        
        # Separator med gradient
        separator = ctk.CTkFrame(self.list_frame, height=2, fg_color=self.colors["primary"])
        separator.pack(fill="x", padx=10, pady=(0, 10))
        
        # Footer frame med knapper
        footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent", height=50)
        footer_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Send alle knap med moderne design
        self.send_all_button = ctk.CTkButton(
            footer_frame,
            text="Send Til Alle",
            command=self.send_all_reports,
            fg_color=self.colors["primary"],
            hover_color="#1874CD",
            height=36,
            corner_radius=8,
            font=("Segoe UI", 12, "bold")
        )
        self.send_all_button.pack(side="right", padx=5)
        
        # Progress sektion
        self.progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.progress_frame.pack(fill="x", padx=20, pady=5)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=("Segoe UI", 11),
            text_color=self.colors["text_secondary"]
        )
        self.progress_label.pack(pady=3)
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=6,
            corner_radius=3
        )
        self.progress_bar.pack(fill="x", pady=3)
        self.progress_bar.set(0)
        self.progress_frame.pack_forget()
        
    def load_drivers(self):
        """Indlæser chauffører og deres mail status"""
        try:
            # Hent minimum kilometer indstilling fra settings databasen
            with sqlite3.connect('databases/settings.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM settings WHERE key = "min_km"')
                result = cursor.fetchone()
                min_km = float(result[0]) if result else 100.0
            
            # Hent alle chauffører fra databasen
            with sqlite3.connect(self.selected_database) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT Chauffør, "Kørestrækning [km]" FROM chauffør_data_data')
                all_drivers = cursor.fetchall()

            # Filtrer chauffører
            drivers = []
            for row in all_drivers:
                driver_name = row[0]
                try:
                    km = float(row[1])
                    if km >= min_km:
                        drivers.append({'id': driver_name, 'name': driver_name})
                except Exception as e:
                    logging.debug(f"Konvertering af km fejlede for chauffør {driver_name}: {e}")
            
            # Hent alle mail adresser
            driver_emails = self.db.get_all_driver_emails()
            
            self.driver_rows = {}
            
            # Tilføj hver chauffør til listen med nyt visuelt design
            for driver in drivers:
                # Opret container for hver række
                row_frame = ctk.CTkFrame(
                    self.list_frame,
                    fg_color="transparent",
                    height=50
                )
                row_frame.pack(fill="x", padx=10, pady=5)
                row_frame.pack_propagate(False)
                
                # Chauffør navn med moderne font
                name_label = ctk.CTkLabel(
                    row_frame,
                    text=driver['name'],
                    font=("Segoe UI", 12),
                    text_color=self.colors["text_primary"]
                )
                name_label.pack(side="left", padx=(10, 0))
                
                # Højre side container til status og knapper
                right_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                right_frame.pack(side="right", padx=(0, 10))
                
                # Email status
                has_email = driver['id'] in driver_emails and driver_emails[driver['id']] != ""
                status_color = self.colors["success"] if has_email else self.colors["danger"]
                status_text = "✓ " + driver_emails[driver['id']] if has_email else "✗ Mangler email"
                
                status_label = ctk.CTkLabel(
                    right_frame,
                    text=status_text,
                    font=("Segoe UI", 11),
                    text_color=status_color
                )
                status_label.pack(side="left", padx=(0, 20))
                
                # Rediger email knap
                edit_button = ctk.CTkButton(
                    right_frame,
                    text="Profil",
                    command=lambda d=driver: self.edit_driver_email(d),
                    fg_color=status_color,
                    hover_color="#1e7e34" if has_email else "#dc3545",
                    width=90,
                    height=32,
                    corner_radius=8
                )
                edit_button.pack(side="left")
                
                # Gem referencer
                self.driver_rows[driver['id']] = {
                    'frame': row_frame,
                    'name_label': name_label,
                    'status_label': status_label,
                    'edit_button': edit_button,
                    'has_email': has_email
                }
                
                # Tilføj separator efter hver række undtagen den sidste
                if driver != drivers[-1]:
                    separator = ctk.CTkFrame(
                        self.list_frame,
                        height=1,
                        fg_color=self.colors["text_secondary"]
                    )
                    separator.pack(fill="x", padx=20, pady=(0, 5))
                
        except Exception as e:
            logging.error(f"Fejl ved indlæsning af chauffører: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke indlæse chauffører: {str(e)}", parent=self.window)
            
    def update_driver_status(self, driver_id):
        """Opdaterer status visning for en chauffør"""
        try:
            if driver_id in self.driver_rows:
                # Hent den aktuelle email
                current_email = self.db.get_driver_email(driver_id)
                has_email = bool(current_email and current_email.strip())
                
                # Opdater status
                status_color = self.colors["success"] if has_email else self.colors["danger"]
                status_text = f"✓ {current_email}" if has_email else "✗ Mangler email"
                
                # Opdater UI elementer
                self.driver_rows[driver_id]['status_label'].configure(
                    text=status_text,
                    text_color=status_color
                )
                self.driver_rows[driver_id]['edit_button'].configure(
                    fg_color=status_color,
                    hover_color="#1e7e34" if has_email else "#dc3545"
                )
                self.driver_rows[driver_id]['has_email'] = has_email
                
        except Exception as e:
            logging.error(f"Fejl ved opdatering af status for {driver_id}: {str(e)}")

    def edit_driver_email(self, driver):
        """Redigerer email for en chauffør"""
        # Hent den nuværende email for chaufføren
        current_email = self.db.get_driver_email(driver['id'])
        
        # Opret pop-up vindue
        email_window = ctk.CTkToplevel(self.window)
        email_window.title(f"Rediger Email for {driver['name']}")
        
        # Beregn vinduesstørrelse (40% af hovedvinduet)
        window_width = int(self.window.winfo_width() * 0.4)
        window_height = int(self.window.winfo_height() * 0.25)
        
        # Beregn position for centrering
        parent_x = self.window.winfo_x()
        parent_y = self.window.winfo_y()
        x = parent_x + (self.window.winfo_width() - window_width) // 2
        y = parent_y + (self.window.winfo_height() - window_height) // 2
        
        # Sæt geometri
        email_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        email_window.minsize(400, 200)
        email_window.grab_set()
        
        # Hovedcontainer med padding og baggrundsfarve
        main_container = ctk.CTkFrame(email_window, fg_color=self.colors["background"])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Email label med titel styling
        email_label = ctk.CTkLabel(
            main_container,
            text="Email:",
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors["text_primary"]
        )
        email_label.pack(pady=(0, 10))
        
        # Email input felt med større bredde
        email_entry = ctk.CTkEntry(
            main_container,
            width=window_width - 80,
            height=35,
            placeholder_text="Indtast email adresse"
        )
        email_entry.pack(pady=(0, 20))
        if current_email:
            email_entry.insert(0, current_email)
        
        # Knap container med centreret layout
        button_container = ctk.CTkFrame(main_container, fg_color="transparent")
        button_container.pack(fill="x", pady=(10, 0))
        
        # Indre container til centrering af knapper
        button_center = ctk.CTkFrame(button_container, fg_color="transparent")
        button_center.pack(expand=True)
        
        # Gem knap
        def save_email():
            new_email = email_entry.get().strip()
            if new_email:
                self.db.save_driver_email(driver['id'], new_email)
            else:
                self.db.delete_driver_email(driver['id'])
            
            # Opdater status visning
            self.update_driver_status(driver['id'])
            email_window.destroy()
        
        save_button = ctk.CTkButton(
            button_center,
            text="Gem",
            command=save_email,
            width=100,
            height=32,
            fg_color=self.colors["success"],
            hover_color="#1e7e34"
        )
        save_button.pack(side="left", padx=5)
        
        # Download knap
        def download_report_handler():
            try:
                # Generer rapport
                filename = f"Rapport_{driver['name']}_{datetime.now().strftime('%Y%m%d')}.docx"
                
                # Opret rapporter mappe hvis den ikke findes
                if not os.path.exists('rapporter'):
                    os.makedirs('rapporter')
                
                # Generer rapport med fuld sti
                fuld_sti = os.path.join('rapporter', filename)
                self.word_report.generer_individuel_rapport(driver['id'])
                
                messagebox.showinfo("Success", f"Rapport gemt som {filename}", parent=email_window)
            except Exception as e:
                logging.error(f"Fejl ved download af rapport for {driver['name']}: {str(e)}")
                messagebox.showerror("Fejl", f"Kunne ikke downloade rapport: {str(e)}", parent=email_window)
        
        download_button = ctk.CTkButton(
            button_center,
            text="Download Rapport",
            command=download_report_handler,
            width=120,
            height=32
        )
        download_button.pack(side="left", padx=5)
        
        # Send Test Mail knap
        def send_test_mail_handler():
            try:
                report_data = self.word_report.get_report_data(driver['id'])
                if not report_data:
                    messagebox.showwarning("Advarsel", f"Ingen rapport data fundet for {driver['name']}", parent=email_window)
                    return
                test_mail = self.db.get_test_mail()
                if not test_mail:
                    messagebox.showwarning("Advarsel", "Ingen testmail fundet i indstillinger.", parent=email_window)
                    return
                self.mail_handler.send_report(driver['id'], report_data, recipient=test_mail)
                messagebox.showinfo("Success", f"Test mail sendt til {test_mail}", parent=email_window)
            except Exception as e:
                logging.error(f"Fejl ved afsendelse af test mail for {driver['name']}: {str(e)}")
                messagebox.showerror("Fejl", f"Kunne ikke sende test mail: {str(e)}", parent=email_window)
        
        test_mail_button = ctk.CTkButton(
            button_center,
            text="Send Test Mail",
            command=send_test_mail_handler,
            width=100,
            height=32
        )
        test_mail_button.pack(side="left", padx=5)
        
        # Fokuser på email feltet
        email_entry.focus_force()
        
    def download_report(self, driver):
        """Downloader rapport for en chauffør"""
        try:
            # Generer rapport
            report_data = self.word_report.get_report_data(driver['id'])
            if not report_data:
                messagebox.showwarning("Advarsel", f"Ingen rapport data fundet for {driver['name']}")
                return
                
            # Gem rapport
            filename = f"Rapport_{driver['name']}_{datetime.now().strftime('%Y%m%d')}.docx"
            self.word_report.generate_report(driver['id'], filename)
            
            messagebox.showinfo("Success", f"Rapport gemt som {filename}")
            
        except Exception as e:
            logging.error(f"Fejl ved download af rapport: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke downloade rapport: {str(e)}")
            
    def send_single_report(self, driver):
        """Sender rapport til en enkelt chauffør"""
        try:
            report_data = self.word_report.get_report_data(driver['id'])
            if not report_data:
                messagebox.showwarning("Advarsel", f"Ingen rapport data fundet for {driver['name']}", parent=self.window)
                return
                
            self.mail_handler.send_report(driver['id'], report_data)
            
            row = self.driver_rows[driver['id']]
            row['edit_button'].configure(state="disabled", text="Rapport Sendt")
            
            messagebox.showinfo("Success", f"Rapport sendt til {driver['name']}", parent=self.window)
            
        except Exception as e:
            logging.error(f"Fejl ved sending af rapport til {driver['name']}: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke sende rapport til {driver['name']}: {str(e)}", parent=self.window)
            
    def send_all_reports(self):
        """Sender rapporter til alle chauffører med email"""
        try:
            drivers_with_email = [
                driver_id for driver_id, row in self.driver_rows.items()
                if row['has_email'] and row['edit_button'].cget('state') != 'disabled'
            ]
            
            if not drivers_with_email:
                messagebox.showinfo("Info", "Ingen chauffører at sende til", parent=self.window)
                return
                
            if not messagebox.askyesno("Bekræft", 
                f"Er du sikker på at du vil sende rapporter til {len(drivers_with_email)} chauffører?",
                parent=self.window):
                return
                
            self.progress_frame.pack(fill="x", padx=20, pady=10)
            self.progress_bar.set(0)
            total_drivers = len(drivers_with_email)
            
            def send_reports():
                for i, driver_id in enumerate(drivers_with_email, 1):
                    try:
                        progress = i / total_drivers
                        self.progress_bar.set(progress)
                        self.progress_label.configure(
                            text=f"Sender rapporter... {i}/{total_drivers}"
                        )
                        
                        report_data = self.word_report.get_report_data(driver_id)
                        if report_data:
                            self.mail_handler.send_report(driver_id, report_data)
                            
                            row = self.driver_rows[driver_id]
                            row['edit_button'].configure(state="disabled", text="Rapport Sendt")
                            
                    except Exception as e:
                        logging.error(f"Fejl ved sending af rapport til chauffør {driver_id}: {str(e)}")
                        
                self.progress_label.configure(text="Alle rapporter sendt!")
                messagebox.showinfo("Success", "Alle rapporter er blevet sendt!", parent=self.window)
            
            thread = threading.Thread(target=send_reports)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logging.error(f"Fejl ved sending af alle rapporter: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke sende rapporter: {str(e)}", parent=self.window)
            
    def run(self):
        """Starter vinduet"""
        # Opdater vinduet for at sikre at alle widgets er korrekt placeret
        self.window.update_idletasks()
        # Ingen geometri-sætning her, da det allerede er håndteret i setup_window 