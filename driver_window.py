from mail_handler import MailHandler
from tkinter import messagebox
import logging

class DriverWindow:
    def __init__(self, parent):
        # ... existing code ...
        
        # Tilføj mail handler
        self.mail_handler = MailHandler()
        
        # Opret knapper frame
        self.button_frame = ctk.CTkFrame(self.window)
        self.button_frame.pack(fill="x", padx=20, pady=10)
        
        # Tilføj Send Rapport knap
        self.send_report_button = ctk.CTkButton(
            self.button_frame,
            text="Send Rapport",
            command=self.send_report,
            fg_color=self.colors["primary"]
        )
        self.send_report_button.pack(side="left", padx=5)
        
        # Tilføj Mail Liste knap
        self.mail_list_button = ctk.CTkButton(
            self.button_frame,
            text="Mail Liste",
            command=self.show_mail_list
        )
        self.mail_list_button.pack(side="left", padx=5)
        
        # Tilføj Administrer Grupper knap
        self.manage_groups_button = ctk.CTkButton(
            self.button_frame,
            text="Administrer Grupper",
            command=self.show_group_manager
        )
        self.manage_groups_button.pack(side="left", padx=5)
        
    def send_report(self):
        """Sender rapport til chauffør via email"""
        try:
            # Hent valgt chauffør
            selected_driver = self.get_selected_driver()
            if not selected_driver:
                messagebox.showwarning("Advarsel", "Vælg venligst en chauffør først")
                return
                
            # Hent rapport data for chaufføren
            report_data = self.get_driver_report_data(selected_driver['id'])
            if not report_data:
                messagebox.showwarning("Advarsel", "Ingen rapport data fundet for denne chauffør")
                return
                
            # Bekræft afsendelse
            if not messagebox.askyesno("Bekræft", 
                f"Er du sikker på at du vil sende en rapport til {selected_driver['name']}?"):
                return
                
            # Send rapport
            self.mail_handler.send_report(selected_driver['id'], report_data)
            
            # Vis success besked
            messagebox.showinfo("Success", f"Rapport sendt succesfuldt til {selected_driver['name']}")
            
        except ValueError as ve:
            messagebox.showerror("Fejl", str(ve))
        except Exception as e:
            logging.error(f"Fejl ved afsendelse af rapport: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke sende rapport: {str(e)}")
            
    def get_driver_report_data(self, driver_id):
        """Henter rapport data for en specifik chauffør"""
        try:
            # Hent data fra word_report
            report_data = self.word_report.get_report_data(driver_id)
            
            # Formater data til mail rapport
            return {
                'date': report_data['date'],
                'total_trips': report_data['total_trips'],
                'total_distance': report_data['total_distance'],
                'total_time': report_data['total_time'],
                'avg_trip_length': report_data['avg_trip_length'],
                'avg_trip_time': report_data['avg_trip_time']
            }
            
        except Exception as e:
            logging.error(f"Fejl ved hentning af chauffør rapport data: {str(e)}")
            raise

    def edit_driver_email(self, driver):
        # # DEBUG: Åbner email redigerings vindue for chauffør
        current_email = self.db.get_driver_email(driver['id'])  # Henter chaufførens nuværende email
        email_window = ctk.CTkToplevel(self.window)
        email_window.title(f"Rediger Email for {driver['name']}")
        email_window.geometry("400x200")
        email_window.grab_set()  # Gør vinduet modalt
        
        # Label til email
        email_label = ctk.CTkLabel(email_window, text="Email:")
        email_label.pack()
        
        # Entry til email
        email_entry = ctk.CTkEntry(email_window)
        email_entry.pack()
        if current_email:
            email_entry.insert(0, current_email)
        
        # Gem-knap til at gemme ændret email
        save_button = ctk.CTkButton(
            email_window, text="Gem", 
            command=lambda: self.save_driver_email(driver['id'], email_entry.get())
        )
        save_button.pack(pady=5)
        
        # Ny knap til at downloade chaufførens rapport
        download_button = ctk.CTkButton(
            email_window, text="Download Rapport", 
            command=lambda: self.download_driver_report(driver)
        )
        download_button.pack(pady=5)
        
        # Ny knap til at sende en testmail med chaufførens rapport
        test_mail_button = ctk.CTkButton(
            email_window, text="Send Test Mail", 
            command=lambda: self.send_test_mail(driver)
        )
        test_mail_button.pack(pady=5)
        
    # Ny metode til at sende en testmail
    def send_test_mail(self, driver):
        # # DEBUG: Starter send_test_mail for chauffør
        try:
            # Hent rapport data for chaufføren
            report_data = self.get_driver_report_data(driver['id'])
            if not report_data:
                messagebox.showwarning("Advarsel", f"Ingen rapport data fundet for {driver['name']}")
                return
            
            # Hent test email fra indstillinger via databasen
            test_email = self.db.get_test_email()  # Forudsætter, at denne metode er implementeret
            if not test_email:
                messagebox.showwarning("Advarsel", "Ingen test email konfigureret i Indstillinger")
                return
            
            # Send test mail ved at bruge den opdaterede MailHandler med 'recipient' parameteren
            self.mail_handler.send_report(driver['id'], report_data, recipient=test_email)
            messagebox.showinfo("Success", f"Test mail sendt til {test_email}")
        except Exception as e:
            logging.error(f"Fejl ved afsendelse af test mail for {driver['name']}: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke sende test mail: {str(e)}")
# ... existing code ... 