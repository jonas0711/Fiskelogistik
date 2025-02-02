import customtkinter as ctk
from tkinter import messagebox
import logging
import re
import os
from database_connection import DatabaseConnection
import sqlite3
import tkinter as tk

class DriverMailList:
    def __init__(self, parent, drivers=None):
        """Initialiserer mail liste vinduet"""
        try:
            self.parent = parent
            self.db = DatabaseConnection('settings.db')
            
            # Sikr at databasen er initialiseret
            self._initialize_database()
            
            # Gem oprindelige værdier til fortryd
            self.original_emails = {}
            self.modified = False
            
            # Gem drivers hvis de er givet
            self.drivers = drivers
            
            logging.info("Initialiserer mail liste vindue")
            self.setup_window()
            
        except Exception as e:
            error_msg = f"Fejl ved initialisering af mail liste: {str(e)}"
            logging.error(error_msg)
            raise Exception(error_msg)
        
    def _initialize_database(self):
        """Sikrer at driver_emails tabellen eksisterer"""
        try:
            # Brug den samme databasefil som DatabaseConnection refererer til
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Opret driver_emails tabel hvis den ikke findes
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS driver_emails (
                        driver_id TEXT PRIMARY KEY,
                        email TEXT NOT NULL,
                        last_report_sent TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logging.info("Database initialiseret succesfuldt")
                
        except Exception as e:
            error_msg = f"Fejl ved database initialisering: {str(e)}"
            logging.error(error_msg)
            raise Exception(error_msg)
        
    def setup_window(self):
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Chauffør Mail Liste")
        
        # Beregn vinduesstørrelse (50% af skærmbredden og 70% af skærmhøjden)
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.7)
        
        # Beregn position for centrering i forhold til forældrevinduet
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        # Sæt geometri
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.minsize(800, 600)
        
        # Gør vinduet modalt
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.focus_force()
        
        # Hovedcontainer med moderne design
        main_frame = ctk.CTkFrame(
            self.window,
            fg_color="#f0f0f0",
            corner_radius=15
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel med skygge effekt
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20,30))
        
        title = ctk.CTkLabel(
            title_frame,
            text="Chauffør Mail Liste",
            font=("Segoe UI", 28, "bold"),
            text_color="#1a1a1a"
        )
        title.pack(anchor="center")
        
        # Liste container med fast højde og moderne styling
        self.list_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="white",
            corner_radius=10,
            height=window_height - 250
        )
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0,20))
        
        # Knap container med moderne design
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent", height=50)
        button_frame.pack(fill="x", padx=20, pady=(0,10))
        
        # Gem knap med forbedret styling
        self.save_button = ctk.CTkButton(
            button_frame,
            text="Gem Ændringer",
            command=self.save_changes,
            state="disabled",
            fg_color="#28a745",
            hover_color="#218838",
            height=38,
            corner_radius=8,
            font=("Segoe UI", 12, "bold")
        )
        self.save_button.pack(side="right", padx=5)
        
        # Fortryd knap med forbedret styling
        self.undo_button = ctk.CTkButton(
            button_frame,
            text="Fortryd Ændringer",
            command=self.undo_changes,
            state="disabled",
            fg_color="#6c757d",
            hover_color="#5a6268",
            height=38,
            corner_radius=8,
            font=("Segoe UI", 12, "bold")
        )
        self.undo_button.pack(side="right", padx=5)
        
        self.load_drivers()
        
        # Bind lukke event
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_drivers(self):
        try:
            # Brug givne drivers hvis tilgængelige, ellers hent fra database
            if self.drivers is None:
                self.drivers = self.get_all_drivers()
            
            logging.info(f"Indlæser {len(self.drivers)} chauffører")
            
            # Hent alle chauffører og deres emails direkte fra driver_emails tabellen
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT TRIM(driver_id), email FROM driver_emails")
                emails = dict(cursor.fetchall())
            logging.info(f"Fandt {len(emails)} eksisterende email adresser")
            
            # Merge: Hvis der findes emails for chauffører, der ikke er med i self.drivers,
            # så tilføjes de til listen. Vi sammenligner trimmede værdier for at undgå mismatches.
            for d_id in emails.keys():
                if not any(driver['id'].strip() == d_id.strip() for driver in self.drivers):
                    logging.info(f"Tilføjer chauffør {d_id.strip()} fra emails til driver listen")
                    self.drivers.append({'id': d_id.strip(), 'name': d_id.strip()})
            
            # Gem oprindelige værdier
            self.original_emails = emails.copy()
            self.email_entries = {}
            
            # Header row
            header_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent", height=40)
            header_frame.pack(fill="x", padx=10, pady=(0, 10))
            header_frame.pack_propagate(False)
            
            # Chauffør header
            ctk.CTkLabel(
                header_frame,
                text="Chauffør",
                font=("Segoe UI", 12, "bold"),
                text_color="#1a1a1a"
            ).pack(side="left", padx=(20, 0))
            
            # Email header
            ctk.CTkLabel(
                header_frame,
                text="Email",
                font=("Segoe UI", 12, "bold"),
                text_color="#1a1a1a"
            ).pack(side="right", padx=(0, 20))
            
            # Separator under header
            separator = ctk.CTkFrame(self.list_frame, height=2, fg_color="#e0e0e0")
            separator.pack(fill="x", padx=10, pady=(0, 10))
            
            # Opret alle rækker på én gang for alle chauffører i den opdaterede self.drivers liste
            for driver in self.drivers:
                # Normaliser chauffør-id ved at trimme eventuelle ekstra mellemrum
                d_id = driver['id'].strip()

                row = ctk.CTkFrame(self.list_frame, fg_color="transparent", height=45)
                row.pack(fill="x", padx=10, pady=5)
                row.pack_propagate(False)
                
                # Chauffør navn med bedre styling
                name = ctk.CTkLabel(
                    row,
                    text=driver['name'],
                    font=("Segoe UI", 12),
                    anchor="w",
                    width=300
                )
                name.pack(side="left", padx=20)
                
                # Email entry med forbedret styling
                email_var = tk.StringVar(value=emails.get(d_id, ""))
                email_entry = ctk.CTkEntry(
                    row,
                    textvariable=email_var,
                    width=400,
                    height=32,
                    placeholder_text="Indtast email adresse",
                    font=("Segoe UI", 12)
                )
                email_entry.pack(side="right", padx=20)
                
                # Hvis der er en gemt email for chaufføren, indsæt den eksplicit
                current_email = emails.get(d_id, "")
                if current_email:
                    email_entry.delete(0, tk.END)
                    email_entry.insert(0, current_email)
                
                # Tilføj binding til tastetryk
                email_entry.bind("<KeyRelease>", lambda event, d_id=d_id: self.on_email_changed(d_id))
                
                self.email_entries[d_id] = {
                    'entry': email_entry,
                    'var': email_var,
                    'row': row
                }
                
                # Tilføj separator efter hver række undtagen den sidste
                if driver != self.drivers[-1]:
                    separator = ctk.CTkFrame(self.list_frame, height=1, fg_color="#e0e0e0")
                    separator.pack(fill="x", padx=30, pady=(5, 0))
            
            # Opdater vinduet én gang til sidst
            self.window.update_idletasks()
            logging.info("Chauffør liste indlæst succesfuldt")
            
        except Exception as e:
            error_msg = f"Kunne ikke indlæse chauffører: {str(e)}"
            logging.error(error_msg)
            messagebox.showerror("Fejl", error_msg)
            
    def on_email_changed(self, driver_id):
        """Håndterer ændringer i email felter"""
        try:
            # Vi henter den opdaterede værdi direkte fra entry-widgeten for at sikre at vi 
            # får den aktuelle tekst. Dette er en lille ændring fra at bruge .get() på StringVar.
            changed = False
            for d_id, entry_data in self.email_entries.items():
                # Hent den direkte tekst fra entry widgeten
                current = entry_data['entry'].get().strip()
                orig = self.original_emails.get(d_id, "")
                logging.debug(f"on_email_changed: chauffør {d_id}, current='{current}', orig='{orig}'")
                if current != orig:
                    changed = True
                    logging.info(f"Email ændret for chauffør {d_id}. Ny værdi: {current}, Original: {orig}")
                    break
            self.modified = changed

            # Opdater knap-tilstande baseret på om der er ændringer
            if self.modified:
                self.undo_button.configure(state="normal")
                self.save_button.configure(state="normal")
                logging.info("Aktiverer gem og fortryd knapper")
            else:
                self.undo_button.configure(state="disabled")
                self.save_button.configure(state="disabled")
                logging.info("Deaktiverer gem og fortryd knapper")
                
        except Exception as e:
            error_msg = f"Fejl i on_email_changed: {str(e)}"
            logging.error(error_msg)
            messagebox.showerror("Fejl", error_msg)
        
    def undo_changes(self):
        """Fortryd alle ændringer og gendan de originale email værdier.
        Hvis fx en email er blevet ændret (fx et "m" slettet), vil denne funktion rulle ændringen tilbage.
        """
        try:
            # For hver entry i self.email_entries, gendan den oprindelige værdi fra self.original_emails
            for driver_id, entry_data in self.email_entries.items():
                original = self.original_emails.get(driver_id, "")
                # Ryd entry widgeten og indsæt original værdi
                entry_data['entry'].delete(0, tk.END)
                entry_data['entry'].insert(0, original)
            self.modified = False
            # Deaktiver "Gem" og "Fortryd" knapper, da ændringerne nu er fortrudt
            self.undo_button.configure(state="disabled")
            self.save_button.configure(state="disabled")
            logging.info("Ændringer fortrydt succesfuldt")
        except Exception as e:
            logging.error(f"Fejl ved fortryd ændringer: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke fortryde ændringer: {str(e)}")
        
    def save_changes(self):
        """Gemmer alle ændringer"""
        try:
            changes_made = False
            errors = []
            
            # Start transaktion
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                try:
                    for driver_id, entry_data in self.email_entries.items():
                        # Hent den direkte tekst fra entry widgeten i stedet for at bruge StringVar objektet
                        new_email = entry_data['entry'].get().strip()
                        original = self.original_emails.get(driver_id, "")
                        logging.debug(f"save_changes: chauffør {driver_id}, new_email='{new_email}', original='{original}'")
                        
                        if new_email != original:
                            try:
                                # Valider email format med regex
                                if new_email and not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
                                    errors.append(f"Ugyldig email for {driver_id}: {new_email}")
                                    continue
                                    
                                if new_email:
                                    cursor.execute("""
                                        INSERT OR REPLACE INTO driver_emails 
                                        (driver_id, email, updated_at) 
                                        VALUES (?, ?, CURRENT_TIMESTAMP)
                                    """, (driver_id, new_email))
                                else:
                                    cursor.execute(
                                        "DELETE FROM driver_emails WHERE driver_id = ?", 
                                        (driver_id,)
                                    )
                                changes_made = True
                                
                            except Exception as e:
                                errors.append(f"Fejl ved gemning af email for {driver_id}: {str(e)}")
                    
                    if errors:
                        error_msg = "\n".join(errors)
                        messagebox.showerror("Fejl ved gemning", error_msg)
                        return
                    
                    conn.commit()  # Eksplicit commit
                    
                    if changes_made:
                        # Opdater oprindelige værdier direkte fra databasen
                        cursor.execute('SELECT driver_id, email FROM driver_emails')
                        self.original_emails = dict(cursor.fetchall())
                        
                        self.modified = False
                        self.undo_button.configure(state="disabled")
                        self.save_button.configure(state="disabled")
                        
                        messagebox.showinfo("Success", "Ændringer gemt succesfuldt")
                        # Sørg for, at vinduet ikke minimiseres efter meddelelsen
                        self.window.deiconify()
                    else:
                        messagebox.showinfo("Info", "Ingen ændringer at gemme")
                    
                except Exception as e:
                    conn.rollback()
                    raise e

        except Exception as e:
            error_msg = f"Kunne ikke gemme ændringer: {str(e)}"
            logging.error(error_msg)
            messagebox.showerror("Fejl", error_msg)
            
    def on_closing(self):
        """Håndterer lukning af vinduet"""
        try:
            if self.modified:
                response = messagebox.askyesnocancel(
                    "Gem Ændringer?",
                    "Du har ugemte ændringer. Vil du gemme dem før du lukker?",
                    icon="warning"
                )
                
                if response is None:  # Cancel
                    return
                elif response:  # Yes
                    self.save_changes()  # Gemmer før luk
                
            self.window.destroy()
            
        except Exception as e:
            logging.error(f"Fejl ved lukning: {str(e)}")
            self.window.destroy()
        
    def get_all_drivers(self):
        """Henter alle unikke chauffører fra chauffør databaserne"""
        try:
            available_drivers = set()
            
            # Find alle chauffør databaser og prøv alternative tabelnavne
            for file in os.listdir('databases'):
                # Matcher databaser med prefixet 'chauffør_data_' og endelsen '.db'
                if file.startswith('chauffør_data_') and file.endswith('.db'):
                    db_path = os.path.join('databases', file)
                    try:
                        with sqlite3.connect(db_path) as conn:
                            cursor = conn.cursor()
                            # Prøv alternative tabelnavne
                            tabel_navne = ['chauffør_data_data', 'chaufførdata', 'chauffør_data']
                            found = False
                            for tabel in tabel_navne:
                                try:
                                    cursor.execute(f'SELECT DISTINCT Chauffør FROM {tabel}')
                                    rows = cursor.fetchall()
                                    if rows:
                                        for row in rows:
                                            # Tjekker at værdien ikke er tom og ikke starter med "Bemærk venligst"
                                            if row[0] and not row[0].startswith("Bemærk venligst"):
                                                available_drivers.add(row[0])
                                        found = True
                                        break  # Afslut forsøget for denne database, når en tabel lykkes
                                except Exception as inner_e:
                                    # Forsæt til næste tabelnavn hvis forespørgslen fejler
                                    continue
                    except Exception as e:
                        logging.error(f"Fejl ved læsning af database {file}: {str(e)}")
            
            # Returnér listen af chauffører som dictionaries med 'id' og 'name'
            return [{'id': name, 'name': name} for name in sorted(available_drivers)]
            
        except Exception as e:
            logging.error(f"Fejl ved hentning af chauffører: {str(e)}")
            return []
            
    def run(self):
        """Starter vinduet og venter på det lukkes"""
        try:
            # Centrer vinduet
            self.window.update_idletasks()
            width = self.window.winfo_width()
            height = self.window.winfo_height()
            x = (self.window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.window.winfo_screenheight() // 2) - (height // 2)
            self.window.geometry(f'{width}x{height}+{x}+{y}')
            
            # Gør vinduet modalt
            self.window.transient(self.parent)
            self.window.grab_set()
            self.window.focus_set()
            
            # Vent på vinduet lukkes
            self.window.wait_window()
            
        except Exception as e:
            error_msg = f"Fejl ved visning af mail liste: {str(e)}"
            logging.error(error_msg)
            messagebox.showerror("Fejl", error_msg) 