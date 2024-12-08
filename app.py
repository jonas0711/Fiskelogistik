# Standard biblioteker
import os
from datetime import datetime
from tkinter import filedialog, messagebox

# Third-party biblioteker
import customtkinter as ctk
from PIL import Image

# Lokale moduler
from upload import UploadWindow
from report_view import ReportWindow
from kpi_view import KPIWindow
from driver_view import DriverWindow
from settings_view import SettingsWindow

class ModernRIOMenu:
    def __init__(self):
        # Tilføj DPI awareness
        ctk.deactivate_automatic_dpi_awareness()
        
        # Grundlæggende opsætning
        self.root = ctk.CTk()
        self.root.title("RIO Chauffør Rapport Generator")
        self.root.state("zoomed")  # Maksimer vinduet
        
        # Farver - inspireret af det lyse moderne design
        self.colors = {
            "primary": "#1E90FF",    
            "secondary": "#7F8C8D",   
            "background": "#F5F7FA",  
            "card": "#FFFFFF",        
            "text_primary": "#2C3E50",
            "text_secondary": "#7F8C8D"
        }
        
        # Tema indstillinger
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Initialisering af UI
        self.setup_ui()

    def setup_ui(self):
        try:
            # Hovedcontainer med scrolling
            main_container = ctk.CTkScrollableFrame(
                self.root,
                fg_color=self.colors["background"],
                height=800
            )
            main_container.pack(expand=True, fill="both", padx=0, pady=0)
            
            # Top bar med logo og kontrolknapper
            self.create_top_bar()
            
            # Titel sektion
            self.create_title_section(main_container)
            
            # Uploads sektion
            self.create_upload_section(main_container)
            
            # Hovedknapper
            self.create_buttons_section(main_container)
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Fejl ved oprettelse af brugergrænsefladen: {str(e)}")

    def open_group_window(self):
        """Åbner gruppe administrations vinduet"""
        try:
            from group_view import GroupWindow
            group_window = GroupWindow(parent=self.root)
            group_window.run()
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke åbne gruppe administration: {str(e)}")

    def create_top_bar(self):
        try:
            top_frame = ctk.CTkFrame(self.root, fg_color=self.colors["card"], height=40)
            top_frame.pack(fill="x", padx=0, pady=0)
            
            # Logo (venstre side)
            logo_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
            logo_frame.pack(side="left", padx=10)
            
            logo_text = ctk.CTkLabel(
                logo_frame,
                text="RIO",
                font=("Segoe UI", 16, "bold"),
                text_color=self.colors["primary"]
            )
            logo_text.pack(side="left")
            
            name_text = ctk.CTkLabel(
                logo_frame,
                text="Rapport Generator",
                font=("Segoe UI", 16),
                text_color=self.colors["text_primary"]
            )
            name_text.pack(side="left", padx=5)
            
            # Window controls (højre side)
            controls_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
            controls_frame.pack(side="right", padx=10)
            
            date_label = ctk.CTkLabel(
                controls_frame,
                text=datetime.now().strftime("%d-%m-%Y %H:%M"),
                font=("Segoe UI", 12),
                text_color=self.colors["text_secondary"]
            )
            date_label.pack(side="right", padx=20)
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Fejl ved oprettelse af top bar: {str(e)}")

    def create_title_section(self, parent):
        try:
            title_frame = ctk.CTkFrame(parent, fg_color="transparent")
            title_frame.pack(fill="x", pady=(40, 20), padx=40)
            
            main_title = ctk.CTkLabel(
                title_frame,
                text="RIO Chauffør Rapport Generator",
                font=("Segoe UI", 32, "bold"),
                text_color=self.colors["primary"]
            )
            main_title.pack()
            
            subtitle = ctk.CTkLabel(
                title_frame,
                text="Vælg den ønskede funktion nedenfor",
                font=("Segoe UI", 16),
                text_color=self.colors["text_secondary"]
            )
            subtitle.pack(pady=(5, 0))
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Fejl ved oprettelse af titel sektion: {str(e)}")

    def create_upload_section(self, parent):
        try:
            upload_frame = ctk.CTkFrame(
                parent,
                fg_color=self.colors["card"],
                corner_radius=15
            )
            upload_frame.pack(fill="x", padx=40, pady=20)
            
            # Upload box med skyggeeffekt og hover
            upload_box = ctk.CTkFrame(
                upload_frame,
                fg_color=self.colors["background"],
                corner_radius=10
            )
            upload_box.pack(padx=40, pady=30, fill="x")
            
            upload_title = ctk.CTkLabel(
                upload_box,
                text="Upload RIO Data",
                font=("Segoe UI", 18, "bold"),
                text_color=self.colors["primary"]
            )
            upload_title.pack(pady=(20, 5))
            
            upload_desc = ctk.CTkLabel(
                upload_box,
                text="Træk filer hertil eller klik for at vælge",
                font=("Segoe UI", 14),
                text_color=self.colors["text_secondary"]
            )
            upload_desc.pack(pady=(0, 20))
            
            upload_button = ctk.CTkButton(
                upload_box,
                text="Vælg filer",
                font=("Segoe UI", 14),
                fg_color=self.colors["primary"],
                hover_color="#1874CD",
                height=40,
                command=self.open_upload_window
            )
            upload_button.pack(pady=(0, 20))
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Fejl ved oprettelse af upload sektion: {str(e)}")

    def create_buttons_section(self, parent):
        try:
            buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
            buttons_frame.pack(fill="x", padx=40, pady=20)
            
            # Knap configuration
            buttons = [
                ("Chauffører", "Administrer chauffører\nog deres præstationer", "icons/driver.png"),
                ("Køretøjer", "Håndter flåden og\nkøretøjsdata", "icons/vehicle.png"),
                ("Rapporter", "Generer og vis\ndetaljerede rapporter", "icons/report.png"),
                ("Indstillinger", "Konfigurer system-\nindstillinger", "icons/settings.png")
            ]
            
            for i, (title, desc, icon_path) in enumerate(buttons):
                self.create_menu_button(buttons_frame, title, desc, icon_path, i)
            
            buttons_frame.grid_columnconfigure((0,1,2,3), weight=1)
            
            # Tilføj KPI knap under de andre knapper
            self.create_kpi_section(parent)
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Fejl ved oprettelse af knap sektion: {str(e)}")

    def create_kpi_section(self, parent):
        try:
            kpi_frame = ctk.CTkFrame(parent, fg_color="transparent")
            kpi_frame.pack(fill="x", padx=40, pady=(0, 20))
            
            # Opret KPI boks
            kpi_container = ctk.CTkFrame(
                kpi_frame,
                fg_color=self.colors["card"],
                corner_radius=15
            )
            kpi_container.pack(fill="x", pady=10)
            
            # KPI titel
            kpi_title = ctk.CTkLabel(
                kpi_container,
                text="Key Performance Indicators",
                font=("Segoe UI", 18, "bold"),
                text_color=self.colors["primary"]
            )
            kpi_title.pack(pady=(20, 5))
            
            # KPI beskrivelse
            kpi_desc = ctk.CTkLabel(
                kpi_container,
                text="Visualiser og analyser\nnøgletalsindikatorer",
                font=("Segoe UI", 12),
                text_color=self.colors["text_secondary"]
            )
            kpi_desc.pack(pady=(0, 20))
            
            # KPI knap
            kpi_button = ctk.CTkButton(
                kpi_container,
                text="Åbn KPI Oversigt",
                font=("Segoe UI", 12),
                fg_color=self.colors["primary"],
                hover_color="#1874CD",
                height=32,
                command=self.handle_kpi_click
            )
            kpi_button.pack(pady=(0, 20))
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Fejl ved oprettelse af KPI sektion: {str(e)}")

    def create_menu_button(self, parent, title, description, icon_path, column):
        try:
            # Container med hvid baggrund og skygge
            button_container = ctk.CTkFrame(
                parent,
                fg_color=self.colors["card"],
                corner_radius=15
            )
            button_container.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
            
            # Titel
            title_label = ctk.CTkLabel(
                button_container,
                text=title,
                font=("Segoe UI", 18, "bold"),
                text_color=self.colors["primary"]
            )
            title_label.pack(pady=(20, 5))
            
            # Beskrivelse
            desc_label = ctk.CTkLabel(
                button_container,
                text=description,
                font=("Segoe UI", 12),
                text_color=self.colors["text_secondary"]
            )
            desc_label.pack(pady=(0, 20))
            
            # Knap
            button = ctk.CTkButton(
                button_container,
                text=f"Åbn {title}",
                font=("Segoe UI", 12),
                fg_color=self.colors["primary"],
                hover_color="#1874CD",
                height=32,
                command=lambda t=title: self.handle_button_click(t)
            )
            button.pack(pady=(0, 20))
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Fejl ved oprettelse af menu knap: {str(e)}")

    def open_upload_window(self):
        """Åbner upload vinduet"""
        try:
            upload_window = UploadWindow()
            upload_window.run()
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke åbne upload vindue: {str(e)}")

    def handle_button_click(self, title):
        """Håndterer klik på hovedknapperne"""
        try:
            if title == "Chauffører":
                driver_window = DriverWindow()
                driver_window.run()
            elif title == "Indstillinger":
                settings_window = SettingsWindow()
                settings_window.run()
            elif title == "Rapporter":
                report_window = ReportWindow(parent=self.root)
                report_window.run()
            else:
                messagebox.showinfo("Information", f"Funktionen '{title}' er under udvikling")
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke åbne {title} vindue: {str(e)}")

    def handle_kpi_click(self):
        """Håndterer klik på KPI knappen"""
        try:
            kpi_window = KPIWindow()
            kpi_window.run()
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke åbne KPI oversigt: {str(e)}")

    def destroy(self):
        """Lukker applikationen og alle vinduer"""
        try:
            # Destroy alle child windows først
            for widget in self.root.winfo_children():
                if isinstance(widget, ctk.CTkToplevel):
                    widget.destroy()
            
            # Destroy hovedvinduet
            self.root.destroy()
            
            # Afbryd mainloop
            self.root.quit()
            
        except Exception as e:
            print(f"Fejl ved lukning af applikation: {str(e)}")

    def run(self):
        """Starter applikationen"""
        try:
            # Sæt vinduet til maksimeret tilstand
            self.root.state("zoomed")  # Maksimer vinduet
    
            # Tilføj protocol handler for window closure
            self.root.protocol("WM_DELETE_WINDOW", self.destroy)
    
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Fatal Fejl", f"Applikationen kunne ikke starte: {str(e)}")

if __name__ == "__main__":
    try:
        app = ModernRIOMenu()
        app.run()
    except Exception as e:
        messagebox.showerror("Fatal Fejl", f"Kunne ikke initialisere applikationen: {str(e)}")