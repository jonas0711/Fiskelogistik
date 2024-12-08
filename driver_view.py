import customtkinter as ctk
import sqlite3
import os
import pandas as pd
from tkinter import messagebox, Canvas, Scrollbar

class DriverWindow:
    def __init__(self):
        # Tilføj DPI awareness
        ctk.deactivate_automatic_dpi_awareness()
        
        # Grundlæggende opsætning
        self.root = ctk.CTk()
        self.root.title("RIO Chauffør Oversigt")
        
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
        
        # Gem den uønskede chauffør tekst som en konstant
        self.EXCLUDE_TEXT = "Bemærk venligst, at en præstationsanalyse kun kan tage hensyn til delvise aspekter vedrørende driftsmåden"
        
        # Hent minimum kilometer indstilling
        self.min_km = self.get_min_km_setting()
        
        self.setup_ui()
    
    def get_min_km_setting(self):
        """Henter minimum kilometer indstilling fra databasen"""
        try:
            conn = sqlite3.connect('databases/settings.db')
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = "min_km"')
            result = cursor.fetchone()
            conn.close()
            return float(result[0]) if result else 100.0
        except:
            return 100.0

    def setup_ui(self):
        # Hovedcontainer
        main_container = ctk.CTkFrame(self.root, fg_color=self.colors["background"])
        main_container.pack(expand=True, fill="both")
        
        # Titel sektion
        self.create_title_section(main_container)
        
        # Filter sektion
        self.create_filter_section(main_container)
        
        # Scrollable frame til chauffør oversigt
        self.driver_container = ctk.CTkScrollableFrame(
            main_container,
            fg_color=self.colors["background"],
            height=400
        )
        self.driver_container.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Chauffør oversigt
        self.create_driver_overview(self.driver_container)
        
        # Data visning (skjult ved start)
        self.create_data_view_section(main_container)

    def create_title_section(self, parent):
        title_frame = ctk.CTkFrame(parent, fg_color="transparent")
        title_frame.pack(fill="x", pady=(20, 10), padx=20)
        
        title = ctk.CTkLabel(
            title_frame,
            text="Chauffør Oversigt",
            font=("Segoe UI", 24, "bold"),
            text_color=self.colors["primary"]
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text=f"Vælg en chauffør for at se detaljeret information (Minimum {self.min_km} km kørt)",
            font=("Segoe UI", 14),
            text_color=self.colors["text_secondary"]
        )
        subtitle.pack(pady=(5, 0))
        
        # Tilføj gruppe knap
        group_button = ctk.CTkButton(
            title_frame,
            text="Administrer Grupper",
            font=("Segoe UI", 12),
            fg_color=self.colors["primary"],
            hover_color="#1874CD",
            command=self.open_group_window,
            width=150
        )
        group_button.pack(side="right", padx=10)

    def create_filter_section(self, parent):
        filter_frame = ctk.CTkFrame(parent, fg_color=self.colors["card"])
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        # Database vælger
        filter_label = ctk.CTkLabel(
            filter_frame,
            text="Vælg periode:",
            font=("Segoe UI", 14),
            text_color=self.colors["text_primary"]
        )
        filter_label.pack(side="left", padx=10, pady=10)
        
        # Find alle tilgængelige databaser
        databases = self.get_available_databases()
        # Tilføj "Alle" som første mulighed
        database_options = ["Alle"] + [self.format_database_name(db) for db in databases]
        
        self.selected_database = ctk.StringVar(value="Alle")
        database_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            values=database_options,
            variable=self.selected_database,
            command=self.filter_drivers,
            width=200
        )
        database_dropdown.pack(side="left", padx=10, pady=10)

    def format_database_name(self, db_name):
        # Fjern .db extension og split på underscore
        parts = db_name.replace('.db', '').split('_')
        if len(parts) >= 4:  # chauffør_data_oktober_2024.db
            month = parts[2].capitalize()
            year = parts[3]
            return f"{month} {year}"
        return db_name

    def get_available_databases(self):
        databases = []
        if not os.path.exists('databases'):
            return databases
        
        for file in os.listdir('databases'):
            if file.startswith('chauffør_data_') and file.endswith('.db'):
                databases.append(file)
        return sorted(databases, reverse=True)  # Nyeste først

    def get_unique_drivers(self):
        if not os.path.exists('databases'):
            return []
        
        unique_drivers = set()
        
        for file in os.listdir('databases'):
            if file.startswith('chauffør_data_') and file.endswith('.db'):
                try:
                    conn = sqlite3.connect(os.path.join('databases', file))
                    query = f"SELECT DISTINCT Chauffør FROM chauffør_data_data WHERE \"Kørestrækning [km]\" >= {self.min_km}"
                    df = pd.read_sql_query(query, conn)
                    conn.close()
                    
                    for driver in df['Chauffør'].unique():
                        if isinstance(driver, str) and not driver.startswith(self.EXCLUDE_TEXT):
                            unique_drivers.add(driver)
                            
                except Exception as e:
                    print(f"Fejl ved læsning af database {file}: {str(e)}")
        
        return sorted(list(unique_drivers))

    def filter_drivers(self, selected_period):
        # Ryd eksisterende chauffør knapper
        for widget in self.driver_container.winfo_children():
            widget.destroy()
        
        if selected_period == "Alle":
            # Vis alle unikke chauffører
            drivers = self.get_unique_drivers()
        else:
            # Find den specifikke database og vis kun chauffører fra den periode
            for db_name in self.get_available_databases():
                if self.format_database_name(db_name) == selected_period:
                    drivers = self.get_drivers_from_database(db_name)
                    break
        
        # Genopbyg chauffør oversigten med de filtrerede chauffører
        self.create_driver_buttons(drivers)

    def get_drivers_from_database(self, db_name):
        drivers = set()
        try:
            conn = sqlite3.connect(os.path.join('databases', db_name))
            query = f"SELECT DISTINCT Chauffør FROM chauffør_data_data WHERE \"Kørestrækning [km]\" >= {self.min_km}"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            for driver in df['Chauffør'].unique():
                if isinstance(driver, str) and not driver.startswith(self.EXCLUDE_TEXT):
                    drivers.add(driver)
                    
        except Exception as e:
            print(f"Fejl ved læsning af database {db_name}: {str(e)}")
        
        return sorted(list(drivers))

    def create_driver_overview(self, parent):
        # Hent unikke chauffører
        drivers = self.get_unique_drivers()
        self.create_driver_buttons(drivers)

    def create_driver_buttons(self, drivers):
        if not drivers:
            no_drivers_label = ctk.CTkLabel(
                self.driver_container,
                text="Ingen chauffører fundet",
                font=("Segoe UI", 12),
                text_color=self.colors["text_secondary"]
            )
            no_drivers_label.pack(pady=10)
            return
        
        # Opret grid til chauffør knapper
        buttons_frame = ctk.CTkFrame(self.driver_container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)
        
        # Beregn antal kolonner baseret på skærmbredde
        BUTTONS_PER_ROW = 4
        
        for i, driver in enumerate(drivers):
            btn = ctk.CTkButton(
                buttons_frame,
                text=driver,
                font=("Segoe UI", 12),
                fg_color=self.colors["primary"],
                hover_color="#1874CD",
                height=32,
                command=lambda d=driver: self.show_driver_data(d)
            )
            btn.grid(row=i//BUTTONS_PER_ROW, column=i%BUTTONS_PER_ROW, padx=5, pady=5, sticky="ew")
            buttons_frame.grid_columnconfigure(i%BUTTONS_PER_ROW, weight=1)

    def create_data_view_section(self, parent):
        self.data_frame = ctk.CTkFrame(parent, fg_color=self.colors["card"])
        self.data_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Placeholder tekst
        self.data_label = ctk.CTkLabel(
            self.data_frame,
            text="Vælg en chauffør for at se data",
            font=("Segoe UI", 14),
            text_color=self.colors["text_secondary"]
        )
        self.data_label.pack(pady=20)

    def show_driver_data(self, driver_name):
        try:
            # Ryd tidligere data visning
            for widget in self.data_frame.winfo_children():
                widget.destroy()

            # Opret en liste til at gemme alle relevante data
            all_data = []
            
            # Gennemgå alle databaser og find chaufførens data
            for file in os.listdir('databases'):
                if file.startswith('chauffør_data_') and file.endswith('.db'):
                    conn = sqlite3.connect(os.path.join('databases', file))
                    query = f"""
                    SELECT * FROM chauffør_data_data 
                    WHERE Chauffør = ? AND "Kørestrækning [km]" >= ?
                    """
                    df = pd.read_sql_query(query, conn, params=(driver_name, self.min_km))
                    conn.close()
                    
                    if not df.empty:
                        all_data.append(df)

            if not all_data:
                self.data_label.configure(text="Ingen data fundet for denne chauffør")
                return

            # Kombiner alle dataframes
            combined_df = pd.concat(all_data, ignore_index=True)

            # Opret canvas og scrollbars
            canvas = Canvas(self.data_frame, bg=self.colors["card"], highlightthickness=0)
            vsb = Scrollbar(self.data_frame, orient="vertical", command=canvas.yview)
            hsb = Scrollbar(self.data_frame, orient="horizontal", command=canvas.xview)
            
            canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

            # Tabel frame inde i canvas
            table_frame = ctk.CTkFrame(canvas, fg_color=self.colors["card"])
            
            # Kolonne bredder
            col_widths = {}
            for col in combined_df.columns:
                max_width = max(
                    len(str(combined_df[col].max())),
                    len(col),
                    10
                )
                col_widths[col] = min(max_width * 10, 300)

            # Opret headers
            for col_idx, col_name in enumerate(combined_df.columns):
                header = ctk.CTkButton(
                    table_frame,
                    text=col_name,
                    font=("Segoe UI", 13, "bold"),
                    text_color=self.colors["primary"],
                    fg_color=self.colors["card"],
                    hover=False,
                    height=40,
                    width=col_widths[col_name]
                )
                header.grid(row=0, column=col_idx, sticky="ew", padx=1, pady=1)

            # Tilføj data
            for row_idx, row in combined_df.iterrows():
                bg_color = self.colors["card"] if row_idx % 2 == 0 else "#F8F9FA"
                
                for col_idx, (col_name, value) in enumerate(row.items()):
                    if isinstance(value, (int, float)):
                        value = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
                    
                    cell = ctk.CTkButton(
                        table_frame,
                        text=str(value),
                        font=("Segoe UI", 12),
                        text_color=self.colors["text_primary"],
                        fg_color=bg_color,
                        hover=False,
                        height=35,
                        width=col_widths[col_name]
                    )
                    cell.grid(row=row_idx+1, column=col_idx, sticky="ew", padx=1, pady=1)

            # Pack scrollbars og canvas
            hsb.pack(side="bottom", fill="x")
            vsb.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)

            # Tilføj tabel frame til canvas
            canvas.create_window((0, 0), window=table_frame, anchor="nw")
            
            # Opdater scroll region
            table_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke indlæse chaufførdata: {str(e)}")

    def run(self):
        try:
            # Sæt vinduet til maksimeret tilstand
            self.root.state("zoomed")  # Maksimer vinduet
    
            # Tilføj protocol handler for window closure
            self.root.protocol("WM_DELETE_WINDOW", self.destroy)
    
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Fatal Fejl", f"Applikationen kunne ikke starte: {str(e)}")

    def destroy(self):
        """Lukker vinduet og frigør ressourcer"""
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
            print(f"Fejl ved lukning af driver vindue: {str(e)}")

    def open_group_window(self):
        """Åbner gruppe administrations vinduet"""
        try:
            # Importer GroupWindow
            from group_view import GroupWindow
            
            # Opret og vis gruppe vinduet med reference til dette vindue
            group_window = GroupWindow(parent=self.root)
            group_window.run()
            
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke åbne gruppe administration: {str(e)}")


if __name__ == "__main__":
    try:
        app = DriverWindow()
        app.run()
    except Exception as e:
        messagebox.showerror("Fatal Fejl", f"Kunne ikke initialisere applikationen: {str(e)}")