import customtkinter as ctk
import sqlite3
import os

class SettingsWindow:
    def __init__(self):
        # Tilføj DPI awareness
        ctk.deactivate_automatic_dpi_awareness()
        
        # Grundlæggende opsætning
        self.root = ctk.CTk()
        self.root.title("RIO Indstillinger")
        self.root.geometry("800x600")
        

        
        # Farver - samme som hovedapplikationen
        self.colors = {
            "primary": "#1E90FF",    # Bright blue
            "background": "#F5F7FA",  # Light gray
            "card": "#FFFFFF",        # White
            "text_primary": "#2C3E50",# Dark blue/gray
            "text_secondary": "#7F8C8D"# Medium gray
        }
        
        # Tema indstillinger
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Opret database hvis den ikke eksisterer
        self.setup_database()
        
        # Load eksisterende indstillinger
        self.current_settings = self.load_settings()
        
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
        # Hovedcontainer
        main_container = ctk.CTkFrame(self.root, fg_color=self.colors["background"])
        main_container.pack(expand=True, fill="both")
        
        # Titel sektion
        self.create_title_section(main_container)
        
        # Indstillinger sektion
        self.create_settings_section(main_container)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_container,
            text="",
            font=("Segoe UI", 12),
            text_color=self.colors["text_secondary"]
        )
        self.status_label.pack(pady=20)

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