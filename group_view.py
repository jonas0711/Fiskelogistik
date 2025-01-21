import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import os
import logging
from PIL import Image
from tkinter import ttk

class DatabaseConnection:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        return self.conn
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

class GroupWindow:
    def __init__(self, parent):
        logging.info("Initialiserer GroupWindow")
        try:
            self.parent = parent
            self.root = ctk.CTkToplevel(parent)
            self.root.title("Administrer Grupper")
            
            # Farver
            self.colors = {
                "primary": "#1E90FF",    
                "background": "#F5F7FA",  
                "card": "#FFFFFF",        
                "text_primary": "#2C3E50",
                "text_secondary": "#7F8C8D"
            }
            
            # Hent minimum kilometer indstilling
            self.min_km = self.get_min_km_setting()
            
            # Indlæs eksisterende grupper
            self.groups = self.load_groups()
            
            # Setup UI
            self.setup_ui()
            
            # Centrér vinduet
            self.center_window()
            
            # Gør vinduet modalt
            self.root.transient(parent)
            self.root.grab_set()
            
            logging.info("GroupWindow initialiseret succesfuldt")
        except Exception as e:
            logging.error(f"Fejl ved initialisering af GroupWindow: {str(e)}")
            raise

    def center_window(self):
        """Centrerer vinduet på skærmen"""
        window_width = 800
        window_height = 600
        
        # Få skærmens dimensioner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Beregn x og y koordinater
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Sæt vinduets position og størrelse
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def setup_ui(self):
        # Hovedcontainer
        self.main_container = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["background"]
        )
        self.main_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Titel
        title = ctk.CTkLabel(
            self.main_container,
            text="Administrer Grupper",
            font=("Segoe UI", 24, "bold"),
            text_color=self.colors["primary"]
        )
        title.pack(pady=(0, 20))

        # Opret to frames side om side
        content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # Venstre side - Gruppe liste
        left_frame = ctk.CTkFrame(content_frame, fg_color=self.colors["card"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        group_label = ctk.CTkLabel(
            left_frame,
            text="Grupper",
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors["text_primary"]
        )
        group_label.pack(pady=10)
        
        # Tilføj gruppe knap
        add_group_btn = ctk.CTkButton(
            left_frame,
            text="+ Opret Ny Gruppe",
            command=self.create_new_group,
            font=("Segoe UI", 12)
        )
        add_group_btn.pack(pady=10, padx=20)
        
        # Gruppe liste
        self.group_listbox = ctk.CTkScrollableFrame(
            left_frame,
            fg_color=self.colors["background"]
        )
        self.group_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Højre side - Gruppe detaljer
        right_frame = ctk.CTkFrame(content_frame, fg_color=self.colors["card"])
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        details_label = ctk.CTkLabel(
            right_frame,
            text="Gruppe Detaljer",
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors["text_primary"]
        )
        details_label.pack(pady=10)
        
        # Medlems sektion
        self.members_frame = ctk.CTkScrollableFrame(
            right_frame,
            fg_color=self.colors["background"]
        )
        self.members_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tilføj medlem knap
        add_member_btn = ctk.CTkButton(
            right_frame,
            text="+ Tilføj Medlem",
            command=self.add_member_to_group,
            font=("Segoe UI", 12)
        )
        add_member_btn.pack(pady=10, padx=20)
        
        # Indlæs eksisterende grupper
        self.load_groups_to_ui()

    def run(self):
        """Starter gruppe vinduet"""
        try:
            # Konfigurer vinduet
            self.root.protocol("WM_DELETE_WINDOW", self.destroy)
            
            # Vent på at vinduet lukkes
            self.root.wait_window()
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke starte gruppe vindue: {str(e)}")

    def destroy(self):
        """Lukker vinduet og frigør ressourcer"""
        try:
            # Frigiv grab
            self.root.grab_release()
            
            # Destroy vinduet
            self.root.destroy()
            
        except Exception as e:
            print(f"Fejl ved lukning af gruppe vindue: {str(e)}")

    def load_groups(self):
        """Indlæser eksisterende grupper fra databasen"""
        try:
            with DatabaseConnection('databases/settings.db') as conn:
                cursor = conn.cursor()
                
                # Opret gruppe tabel hvis den ikke eksisterer
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS groups
                    (id INTEGER PRIMARY KEY, name TEXT UNIQUE)
                ''')
                
                # Opret gruppe_medlemmer tabel hvis den ikke eksisterer
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS group_members
                    (group_id INTEGER, driver_name TEXT,
                    FOREIGN KEY(group_id) REFERENCES groups(id))
                ''')
                
                # Hent alle grupper
                cursor.execute('SELECT id, name FROM groups')
                groups = cursor.fetchall()
                
                conn.commit()
                
                # Konverter til dictionary
                return {group_id: name for group_id, name in groups}
                
        except Exception as e:
            logging.error(f"Fejl ved indlæsning af grupper: {str(e)}")
            return {}

    def create_new_group(self):
        """Opretter en ny gruppe"""
        logging.info("Starter oprettelse af ny gruppe")
        try:
            self.root.grab_release()
            
            name_dialog = ctk.CTkInputDialog(
                text="Indtast navn på ny gruppe:",
                title="Opret Gruppe"
            )
            group_name = name_dialog.get_input()
            logging.info(f"Bruger indtastede gruppe navn: {group_name}")
            
            if group_name:
                logging.info("Åbner chauffør vælger dialog")
                driver_dialog = DriverSelectionDialog(self.root, min_km=self.min_km)
                self.root.wait_window(driver_dialog.dialog)
                
                if driver_dialog.selected_drivers:
                    logging.info(f"Valgte chauffører: {driver_dialog.selected_drivers}")
                    try:
                        with DatabaseConnection('databases/settings.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute('INSERT INTO groups (name) VALUES (?)', 
                                         (group_name,))
                            group_id = cursor.lastrowid
                            logging.info(f"Oprettet gruppe med ID: {group_id}")
                            
                            for driver in driver_dialog.selected_drivers:
                                cursor.execute('''
                                    INSERT INTO group_members (group_id, driver_name)
                                    VALUES (?, ?)
                                ''', (group_id, driver))
                            
                            conn.commit()
                            logging.info("Gruppe og medlemmer gemt i database")
                        
                        self.groups = self.load_groups()
                        self.load_groups_to_ui()
                        logging.info("UI opdateret med ny gruppe")
                        
                    except sqlite3.IntegrityError as e:
                        logging.error(f"Gruppe navn eksisterer allerede: {str(e)}")
                        messagebox.showerror("Fejl", 
                                           "En gruppe med dette navn eksisterer allerede")
                    except Exception as e:
                        logging.error(f"Fejl ved oprettelse af gruppe: {str(e)}")
                        messagebox.showerror("Fejl", 
                                           f"Kunne ikke oprette gruppe: {str(e)}")
            
            self.root.grab_set()
            
        except Exception as e:
            logging.error(f"Fejl ved oprettelse af gruppe dialog: {str(e)}")
            messagebox.showerror("Fejl", f"Kunne ikke oprette gruppe dialog: {str(e)}")
            self.root.grab_set()

    def load_groups_to_ui(self):
        """Indlæser grupper i UI'en"""
        # Ryd eksisterende gruppe knapper
        for widget in self.group_listbox.winfo_children():
            widget.destroy()
        
        # Indlæs og vis grupper
        for group_id, group_name in self.groups.items():
            group_frame = ctk.CTkFrame(
                self.group_listbox,
                fg_color=self.colors["background"]
            )
            group_frame.pack(fill="x", pady=2)
            
            # Gruppe navn knap
            group_btn = ctk.CTkButton(
                group_frame,
                text=group_name,
                command=lambda g_id=group_id, g_name=group_name: self.show_group_details(g_id, g_name),
                fg_color=self.colors["card"],
                text_color=self.colors["text_primary"],
                hover_color="#E8E8E8"
            )
            group_btn.pack(side="left", fill="x", expand=True)
            
            # Knap container til højre
            button_container = ctk.CTkFrame(
                group_frame,
                fg_color="transparent"
            )
            button_container.pack(side="right", padx=5)
            
            # Rediger knap
            edit_btn = ctk.CTkButton(
                button_container,
                text="✎",  # Unicode edit symbol
                width=30,
                command=lambda g_id=group_id, g_name=group_name: self.edit_group(g_id, g_name),
                fg_color="orange",
                hover_color="darkorange"
            )
            edit_btn.pack(side="left", padx=2)
            
            # Slet knap
            delete_btn = ctk.CTkButton(
                button_container,
                text="×",
                width=30,
                command=lambda g_id=group_id: self.delete_group(g_id),
                fg_color="red",
                hover_color="darkred"
            )
            delete_btn.pack(side="left", padx=2)

    def show_group_details(self, group_id, group_name):
        """Viser detaljer for den valgte gruppe"""
        # Gem den valgte gruppe's ID
        self.current_group_id = group_id
        
        # Ryd tidligere medlemmer
        for widget in self.members_frame.winfo_children():
            widget.destroy()
        
        # Vis gruppe navn
        name_label = ctk.CTkLabel(
            self.members_frame,
            text=f"Gruppe: {group_name}",
            font=("Segoe UI", 14, "bold")
        )
        name_label.pack(pady=10)
        
        # Hent og vis medlemmer
        try:
            with DatabaseConnection('databases/settings.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT driver_name FROM group_members WHERE group_id = ?',
                    (group_id,)
                )
                members = cursor.fetchall()
                
                if not members:
                    # Vis besked hvis gruppen er tom
                    empty_label = ctk.CTkLabel(
                        self.members_frame,
                        text="Ingen medlemmer i gruppen",
                        font=("Segoe UI", 12),
                        text_color=self.colors["text_secondary"]
                    )
                    empty_label.pack(pady=20)
                else:
                    for member in members:
                        member_frame = ctk.CTkFrame(
                            self.members_frame,
                            fg_color=self.colors["card"]
                        )
                        member_frame.pack(fill="x", pady=2)
                        
                        member_label = ctk.CTkLabel(
                            member_frame,
                            text=member[0],
                            font=("Segoe UI", 12)
                        )
                        member_label.pack(side="left", padx=10)
                        
                        remove_btn = ctk.CTkButton(
                            member_frame,
                            text="Fjern",
                            command=lambda m=member[0], g=group_id: self.remove_member(g, m),
                            fg_color="red",
                            hover_color="darkred",
                            width=60
                        )
                        remove_btn.pack(side="right", padx=5, pady=5)
                        
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke hente gruppemedlemmer: {str(e)}")

    def add_member_to_group(self):
        """Tilføjer et medlem til den valgte gruppe"""
        # Først tjek om en gruppe er valgt
        if not hasattr(self, 'current_group_id'):
            messagebox.showwarning("Advarsel", "Vælg venligst en gruppe først")
            return
        
        try:
            # Frigiv det nuværende grab før vi åbner dialogen
            self.root.grab_release()
            
            # Hent alle tilgængelige chauffører fra databasen
            available_drivers = self.get_available_drivers()
            
            if not available_drivers:
                messagebox.showinfo("Information", "Ingen tilgængelige chauffører fundet")
                self.root.grab_set()  # Genetabler grab
                return
            
            # Opret dialog til valg af chauffør
            dialog = ctk.CTkInputDialog(
                text="Vælg chauffør der skal tilføjes:",
                title="Tilføj Medlem"
            )
            selected_driver = dialog.get_input()
            
            if selected_driver and selected_driver in available_drivers:
                # Tilføj chauffør til gruppen
                with DatabaseConnection('databases/settings.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO group_members (group_id, driver_name)
                        VALUES (?, ?)
                    ''', (self.current_group_id, selected_driver))
                    conn.commit()
                
                # Opdater visningen
                self.show_group_details(self.current_group_id, self.groups[self.current_group_id])
            else:
                messagebox.showwarning("Advarsel", "Vælg venligst en gyldig chauffør")
            
            # Genetabler grab på hovedvinduet
            self.root.grab_set()
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke tilføje medlem: {str(e)}")
            # Sikr at grab bliver genetableret selv ved fejl
            self.root.grab_set()

    def get_available_drivers(self):
        """Henter liste over tilgængelige chauffører"""
        available_drivers = set()
        
        try:
            # Gennemgå alle chauffør databaser
            for file in os.listdir('databases'):
                if file.startswith('chauffør_data_') and file.endswith('.db'):
                    db_path = os.path.join('databases', file)
                    with DatabaseConnection(db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute(f'''
                            SELECT DISTINCT Chauffør 
                            FROM chauffør_data_data 
                            WHERE "Kørestrækning [km]" >= {self.min_km}
                        ''')
                        
                        for row in cursor.fetchall():
                            if row[0] and not row[0].startswith("Bemærk venligst"):
                                available_drivers.add(row[0])
                            
            return sorted(list(available_drivers))
            
        except Exception as e:
            logging.error(f"Fejl ved hentning af chauffører: {str(e)}")
            return []

    def delete_group(self, group_id):
        """Sletter en gruppe"""
        if messagebox.askyesno("Bekræft sletning", 
                              "Er du sikker på at du vil slette denne gruppe?"):
            try:
                with DatabaseConnection('databases/settings.db') as conn:
                    cursor = conn.cursor()
                    # Slet først alle medlemmer
                    cursor.execute('DELETE FROM group_members WHERE group_id = ?', 
                                 (group_id,))
                    # Slet derefter gruppen
                    cursor.execute('DELETE FROM groups WHERE id = ?', (group_id,))
                    conn.commit()
                    
                # Opdater groups dictionary og UI
                self.groups = self.load_groups()
                self.load_groups_to_ui()
                
                # Ryd medlemsvisningen hvis den slettede gruppe var valgt
                if hasattr(self, 'current_group_id') and self.current_group_id == group_id:
                    for widget in self.members_frame.winfo_children():
                        widget.destroy()
                    delattr(self, 'current_group_id')
                    
            except Exception as e:
                messagebox.showerror("Fejl", f"Kunne ikke slette gruppe: {str(e)}")

    def remove_member(self, group_id, member_name):
        """Fjerner et medlem fra en gruppe"""
        if messagebox.askyesno("Bekræft fjernelse", 
                              f"Er du sikker på at du vil fjerne {member_name} fra gruppen?"):
            try:
                with DatabaseConnection('databases/settings.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        DELETE FROM group_members 
                        WHERE group_id = ? AND driver_name = ?
                    ''', (group_id, member_name))
                    conn.commit()
                    
                # Opdater visningen
                self.show_group_details(group_id, self.groups[group_id])
                
            except Exception as e:
                messagebox.showerror("Fejl", f"Kunne ikke fjerne medlem: {str(e)}")

    def get_min_km_setting(self):
        """Henter minimum kilometer indstilling fra databasen"""
        try:
            with DatabaseConnection('databases/settings.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM settings WHERE key = "min_km"')
                result = cursor.fetchone()
                return float(result[0]) if result else 100.0
        except:
            return 100.0

    def edit_group(self, group_id, group_name):
        """Redigerer en eksisterende gruppe"""
        try:
            # Frigiv det nuværende grab før vi åbner dialogen
            self.root.grab_release()
            
            # Få nyt gruppe navn
            name_dialog = ctk.CTkInputDialog(
                text=f"Rediger gruppe navn (nuværende: {group_name}):",
                title="Rediger Gruppe"
            )
            new_name = name_dialog.get_input()
            
            if new_name and new_name != group_name:
                # Åbn chauffør vælger dialog med eksisterende medlemmer valgt
                driver_dialog = DriverSelectionDialog(self.root, group_id, min_km=self.min_km)
                self.root.wait_window(driver_dialog.dialog)
                
                if driver_dialog.selected_drivers is not None:  # None betyder at brugeren annullerede
                    try:
                        with DatabaseConnection('databases/settings.db') as conn:
                            cursor = conn.cursor()
                            # Opdater gruppe navn
                            cursor.execute('UPDATE groups SET name = ? WHERE id = ?', 
                                         (new_name, group_id))
                            
                            # Slet eksisterende medlemmer
                            cursor.execute('DELETE FROM group_members WHERE group_id = ?', 
                                         (group_id,))
                            
                            # Tilføj nye medlemmer
                            for driver in driver_dialog.selected_drivers:
                                cursor.execute('''
                                    INSERT INTO group_members (group_id, driver_name)
                                    VALUES (?, ?)
                                ''', (group_id, driver))
                            
                            conn.commit()
                        
                        # Opdater groups dictionary og UI
                        self.groups = self.load_groups()
                        self.load_groups_to_ui()
                        
                        # Opdater detalje visningen hvis den redigerede gruppe er valgt
                        if hasattr(self, 'current_group_id') and self.current_group_id == group_id:
                            self.show_group_details(group_id, new_name)
                        
                    except sqlite3.IntegrityError:
                        messagebox.showerror("Fejl", 
                                           "En gruppe med dette navn eksisterer allerede")
                    except Exception as e:
                        messagebox.showerror("Fejl", 
                                           f"Kunne ikke opdatere gruppe: {str(e)}")
            
            # Genetabler grab på hovedvinduet
            self.root.grab_set()
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke redigere gruppe: {str(e)}")
            # Sikr at grab bliver genetableret selv ved fejl
            self.root.grab_set()

class DriverSelectionDialog:
    def __init__(self, parent, existing_group_id=None, min_km=100.0):
        logging.info("Initialiserer DriverSelectionDialog")
        try:
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title("Vælg Chauffører")
            self.existing_group_id = existing_group_id
            self.min_km = min_km
            
            # Centrér dialogen
            window_width = 400
            window_height = 500
            screen_width = self.dialog.winfo_screenwidth()
            screen_height = self.dialog.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Gør vinduet modalt
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            # Variable til at gemme valgte chauffører
            self.selected_drivers = []
            
            self.setup_ui()
            
            logging.info("DriverSelectionDialog initialiseret succesfuldt")
        except Exception as e:
            logging.error(f"Fejl ved initialisering af DriverSelectionDialog: {str(e)}")
            raise

    def setup_ui(self):
        # Titel
        title = ctk.CTkLabel(
            self.dialog,
            text="Vælg Chauffører til Gruppen",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=10)
        
        # Scrollbar frame til checkboxes
        self.checkbox_frame = ctk.CTkScrollableFrame(
            self.dialog,
            width=350,
            height=350
        )
        self.checkbox_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Hent og vis alle chauffører
        self.load_drivers()
        
        # Knapper
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        # Vælg alle knap
        select_all_btn = ctk.CTkButton(
            button_frame,
            text="Vælg Alle",
            command=self.select_all,
            width=100
        )
        select_all_btn.pack(side="left", padx=5)
        
        # Fravælg alle knap
        deselect_all_btn = ctk.CTkButton(
            button_frame,
            text="Fravælg Alle",
            command=self.deselect_all,
            width=100
        )
        deselect_all_btn.pack(side="left", padx=5)
        
        # OK og Annuller knapper
        ok_btn = ctk.CTkButton(
            self.dialog,
            text="OK",
            command=self.on_ok,
            width=100
        )
        ok_btn.pack(pady=5)
        
        cancel_btn = ctk.CTkButton(
            self.dialog,
            text="Annuller",
            command=self.on_cancel,
            width=100
        )
        cancel_btn.pack(pady=5)
        
    def load_drivers(self):
        """Indlæser alle unikke chauffører fra databaserne"""
        logging.info("Starter indlæsning af chauffører")
        try:
            self.checkboxes = {}
            self.checkbox_vars = {}
            
            # Hent alle unikke chauffører
            available_drivers = set()
            for file in os.listdir('databases'):
                if file.startswith('chauffør_data_') and file.endswith('.db'):
                    db_path = os.path.join('databases', file)
                    logging.info(f"Læser fra database: {db_path}")
                    try:
                        with DatabaseConnection(db_path) as conn:
                            cursor = conn.cursor()
                            cursor.execute(f'''
                                SELECT DISTINCT Chauffør 
                                FROM chauffør_data_data 
                                WHERE "Kørestrækning [km]" >= {self.min_km}
                            ''')
                            
                            for row in cursor.fetchall():
                                if row[0] and not row[0].startswith("Bemærk venligst"):
                                    available_drivers.add(row[0])
                    except Exception as e:
                        logging.error(f"Fejl ved læsning af database {file}: {str(e)}")
            
            logging.info(f"Fandt {len(available_drivers)} tilgængelige chauffører")
            
            # Opret checkboxes
            for driver in sorted(available_drivers):
                var = ctk.BooleanVar()
                self.checkbox_vars[driver] = var
                
                checkbox = ctk.CTkCheckBox(
                    self.checkbox_frame,
                    text=driver,
                    variable=var,
                    font=("Segoe UI", 12)
                )
                checkbox.pack(anchor="w", pady=2)
                self.checkboxes[driver] = checkbox
                
        except Exception as e:
            logging.error(f"Fejl ved indlæsning af chauffører: {str(e)}")
            raise
    
    def select_all(self):
        """Vælger alle chauffører"""
        for var in self.checkbox_vars.values():
            var.set(True)
    
    def deselect_all(self):
        """Fravælger alle chauffører"""
        for var in self.checkbox_vars.values():
            var.set(False)
    
    def on_ok(self):
        """Gemmer de valgte chauffører og lukker dialogen"""
        self.selected_drivers = [
            driver for driver, var in self.checkbox_vars.items() 
            if var.get()
        ]
        self.dialog.destroy()
    
    def on_cancel(self):
        """Lukker dialogen uden at gemme"""
        self.selected_drivers = []
        self.dialog.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = GroupWindow(root)
    app.run()
    root.mainloop()