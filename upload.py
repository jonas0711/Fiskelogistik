import customtkinter as ctk
from tkinter import filedialog
import pandas as pd
import sqlite3
from datetime import datetime
import os

class UploadWindow:
    def __init__(self):
        # Tilføj DPI awareness
        ctk.deactivate_automatic_dpi_awareness()
        
        # Grundlæggende opsætning
        self.root = ctk.CTk()
        self.root.title("RIO Data Upload")
        self.root.state("zoomed")  # Maksimer vinduet

        
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
        
        # Variables
        self.selected_month = None
        self.selected_year = None
        self.selected_type = None
        self.file_path = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Hovedcontainer
        main_container = ctk.CTkFrame(self.root, fg_color=self.colors["background"])
        main_container.pack(expand=True, fill="both")
        
        # Titel sektion
        self.create_title_section(main_container)
        
        # Dato sektion
        self.create_date_section(main_container)
        
        # Data type sektion
        self.create_data_type_section(main_container)
        
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
            text="Upload RIO Data",
            font=("Segoe UI", 24, "bold"),
            text_color=self.colors["primary"]
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Vælg måned, år og data type",
            font=("Segoe UI", 14),
            text_color=self.colors["text_secondary"]
        )
        subtitle.pack(pady=(5, 0))

    def create_date_section(self, parent):
        date_frame = ctk.CTkFrame(parent, fg_color=self.colors["card"])
        date_frame.pack(fill="x", padx=40, pady=10)
        
        # Opret dropdown frames
        dropdowns_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        dropdowns_frame.pack(pady=10, padx=20)
        
        # Måned dropdown
        month_label = ctk.CTkLabel(
            dropdowns_frame,
            text="Måned:",
            font=("Segoe UI", 14),
            text_color=self.colors["text_primary"]
        )
        month_label.grid(row=0, column=0, padx=(0, 10), pady=5)
        
        months = ["Januar", "Februar", "Marts", "April", "Maj", "Juni", 
                 "Juli", "August", "September", "Oktober", "November", "December"]
        self.month_var = ctk.StringVar(value="Vælg måned")
        month_dropdown = ctk.CTkOptionMenu(
            dropdowns_frame,
            values=months,
            variable=self.month_var,
            font=("Segoe UI", 12),
            command=self.month_selected,
            width=200
        )
        month_dropdown.grid(row=0, column=1, pady=5)
        
        # År dropdown
        year_label = ctk.CTkLabel(
            dropdowns_frame,
            text="År:",
            font=("Segoe UI", 14),
            text_color=self.colors["text_primary"]
        )
        year_label.grid(row=1, column=0, padx=(0, 10), pady=5)
        
        current_year = datetime.now().year
        years = [str(year) for year in range(current_year-5, current_year+1)]
        self.year_var = ctk.StringVar(value=str(current_year))
        year_dropdown = ctk.CTkOptionMenu(
            dropdowns_frame,
            values=years,
            variable=self.year_var,
            font=("Segoe UI", 12),
            command=self.year_selected,
            width=200
        )
        year_dropdown.grid(row=1, column=1, pady=5)
        
        # Konfigurer grid
        dropdowns_frame.grid_columnconfigure(1, weight=1)

    def create_data_type_section(self, parent):
        type_frame = ctk.CTkFrame(parent, fg_color="transparent")
        type_frame.pack(fill="x", padx=40, pady=10)
        
        # Container for de to bokse
        boxes_frame = ctk.CTkFrame(type_frame, fg_color="transparent")
        boxes_frame.pack(expand=True, fill="both")
        boxes_frame.grid_columnconfigure(0, weight=1)
        boxes_frame.grid_columnconfigure(1, weight=1)
        
        # Chauffør data boks
        self.create_type_box(
            boxes_frame, 
            "Chauffør Data", 
            "Upload chauffør\nrelateret data",
            0
        )
        
        # Kørsels data boks
        self.create_type_box(
            boxes_frame, 
            "Kørsels Data", 
            "Upload køretøjs og\nkørsels data",
            1
        )

    def create_type_box(self, parent, title, description, column):
        box_container = ctk.CTkFrame(
            parent,
            fg_color=self.colors["card"],
            corner_radius=15
        )
        box_container.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        
        title_label = ctk.CTkLabel(
            box_container,
            text=title,
            font=("Segoe UI", 18, "bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(20, 5))
        
        desc_label = ctk.CTkLabel(
            box_container,
            text=description,
            font=("Segoe UI", 12),
            text_color=self.colors["text_secondary"]
        )
        desc_label.pack(pady=(0, 20))
        
        upload_button = ctk.CTkButton(
            box_container,
            text="Vælg Excel fil",
            font=("Segoe UI", 12),
            fg_color=self.colors["primary"],
            hover_color="#1874CD",
            command=lambda t=title: self.type_selected(t)
        )
        upload_button.pack(pady=(0, 20))
        
    def month_selected(self, month):
        self.selected_month = month
        self.update_status()
        
    def year_selected(self, year):
        self.selected_year = year
        self.update_status()

    def type_selected(self, type_name):
        if not self.selected_month or not self.selected_year:
            self.status_label.configure(
                text="Vælg venligst både måned og år først",
                text_color="red"
            )
            return
            
        self.selected_type = type_name
        self.select_file()
        
    def select_file(self):
        file_types = [('Excel filer', '*.xlsx *.xls')]
        self.file_path = filedialog.askopenfilename(filetypes=file_types)
        
        if self.file_path:
            self.status_label.configure(
                text="Konverterer fil...",
                text_color=self.colors["text_secondary"]
            )
            self.root.update()
            self.convert_to_sql()
            
    def convert_to_sql(self):
        try:
            # Læs Excel fil
            df = pd.read_excel(self.file_path)
            
            # Validér at filen indeholder data
            if df.empty:
                raise ValueError("Excel filen er tom")
            
            # Den specifikke bemærkningstekst vi leder efter
            bemærkning_tekst = "Bemærk venligst, at en præstationsanalyse kun kan tage hensyn til delvise aspekter vedrørende driftsmåden (f.eks. friløb) og de påvirkningsfaktorer (f.eks. typen af indsættelse). Af denne grund er denne rapport kun en generel hjælp og bør aftales mellem chaufføren og køretræneren/flådechefen. Alvorligheden af brugen bestemt i Service MAN Perform og underklassificeringerne/den samlede vurdering er en MAN-specifik løsning og kan derfor ikke sammenlignes med ratings eller ydeevneindikatorer fra andre producenter"
            
            # Tjek om første kolonne indeholder bemærkningsteksten
            første_kolonne_navn = df.columns[0]
            if isinstance(første_kolonne_navn, str) and første_kolonne_navn.strip() == bemærkning_tekst.strip():
                # Hvis ja, fjern første kolonne
                df = df.iloc[:, 1:]
            
            # Generer database navn med år
            db_name = f"{self.selected_type.lower().replace(' ', '_')}_{self.selected_month.lower()}_{self.selected_year}.db"
            
            # Opret database mappe hvis den ikke eksisterer
            db_path = 'databases'
            if not os.path.exists(db_path):
                os.makedirs(db_path)
            
            # Sikr at databasefilen ikke allerede eksisterer
            full_db_path = os.path.join(db_path, db_name)
            if os.path.exists(full_db_path):
                if not ctk.messagebox.askyesno("Bekræft overskrivning", 
                    "En database for denne måned og år eksisterer allerede. Vil du overskrive den?"):
                    self.status_label.configure(
                        text="Upload annulleret",
                        text_color="orange"
                    )
                    return
                    
            # Opret forbindelse til SQLite database
            conn = sqlite3.connect(full_db_path)
            
            # Konverter dataframe til SQL tabel
            table_name = f"{self.selected_type.lower().replace(' ', '_')}_data"
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            
            conn.close()
            
            self.status_label.configure(
                text=f"Data er blevet gemt i databasen: {db_name}",
                text_color="green"
            )
            
        except pd.errors.EmptyDataError:
            self.status_label.configure(
                text="Fejl: Excel filen er tom",
                text_color="red"
            )
        except Exception as e:
            self.status_label.configure(
                text=f"Fejl under konvertering: {str(e)}",
                text_color="red"
            )
            
    def update_status(self):
        if self.selected_month and self.selected_year:
            self.status_label.configure(
                text=f"Valgt periode: {self.selected_month} {self.selected_year}",
                text_color=self.colors["text_primary"]
            )
            
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
            print(f"Fejl ved lukning af upload vindue: {str(e)}")

if __name__ == "__main__":
    app = UploadWindow()
    app.run()