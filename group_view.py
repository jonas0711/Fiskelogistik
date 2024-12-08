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
        # Definer parent som CTkToplevel
        self.root = ctk.CTkToplevel(parent)
        self.root.title("Administrer Grupper")
        
        # Fjern maksimering for Toplevel, hvis nødvendigt
        # self.root.state("zoomed")  # Valgfri: kan fjernes eller justeres
        
        # Resten af initialiseringen forbliver den samme
        # ...

    def run(self):
        try:
            # Konfigurer root vinduet
            self.root.protocol("WM_DELETE_WINDOW", self.destroy)
            
            # Start mainloop for Toplevel
            # self.root.mainloop()  # Fjern denne linje
            # Da Toplevel deler mainloop med hovedvinduet, er det ikke nødvendigt
        except Exception as e:
            if self.parent:
                self.parent.deiconify()
            messagebox.showerror("Fejl", f"Kunne ikke starte gruppe vindue: {str(e)}")

    def destroy(self):
        try:
            for widget in self.root.winfo_children():
                if isinstance(widget, ctk.CTkToplevel):
                    widget.destroy()
            if self.parent:
                self.parent.deiconify()
            self.root.destroy()
            self.root.quit()
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

if __name__ == "__main__":
    app = GroupWindow()
    app.run()