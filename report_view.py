import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from docx import Document
from docx.shared import Inches
import pandas as pd
from fpdf import FPDF
from tkinter import messagebox
import matplotlib.pyplot as plt
from PIL import Image

class ReportWindow:
    def __init__(self):
        # Tilføj DPI awareness
        ctk.deactivate_automatic_dpi_awareness()
        
        # Grundlæggende opsætning
        self.root = ctk.CTk()
        self.root.title("RIO Rapport Generator")
        self.root.geometry("1000x800")
        
        
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
        self.selected_type = None
        self.selected_format = None
        self.available_databases = []
        self.selected_database = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Hovedcontainer med scrolling
        self.main_container = ctk.CTkScrollableFrame(
            self.root,
            fg_color=self.colors["background"],
            height=800  # Sæt en passende højde
        )
        self.main_container.pack(expand=True, fill="both", padx=0, pady=0)
        
        # Titel sektion
        self.create_title_section(self.main_container)
        
        # Rapport type sektion
        self.create_type_section(self.main_container)
        
        # Database vælger sektion (skjult ved start)
        self.db_frame = ctk.CTkFrame(self.main_container, fg_color=self.colors["card"])
        
        # Format vælger sektion (skjult ved start)
        self.format_frame = ctk.CTkFrame(self.main_container, fg_color=self.colors["card"])
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_container,
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
            text="Rapport Generator",
            font=("Segoe UI", 24, "bold"),
            text_color=self.colors["primary"]
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Generer detaljerede rapporter over chauffører og køretøjer",
            font=("Segoe UI", 14),
            text_color=self.colors["text_secondary"]
        )
        subtitle.pack(pady=(5, 0))

    def create_type_section(self, parent):
        type_frame = ctk.CTkFrame(parent, fg_color="transparent")
        type_frame.pack(fill="x", padx=40, pady=10)
        
        # Container for de to bokse
        boxes_frame = ctk.CTkFrame(type_frame, fg_color="transparent")
        boxes_frame.pack(expand=True, fill="both")
        boxes_frame.grid_columnconfigure(0, weight=1)
        boxes_frame.grid_columnconfigure(1, weight=1)
        
        # Chauffør rapport boks
        self.create_type_box(
            boxes_frame, 
            "Chauffør Rapport", 
            "Generer rapport over\nchauffør præstationer",
            "Inkluderer kørselsmønstre,\nbrændstofforbrug og performance",
            0
        )
        
        # Køretøjs rapport boks
        self.create_type_box(
            boxes_frame, 
            "Køretøjs Rapport", 
            "Generer rapport over\nkøretøjs data",
            "Inkluderer driftstid,\nvedligeholdelse og effektivitet",
            1
        )

    def create_type_box(self, parent, title, description, details, column):
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
        desc_label.pack(pady=(0, 10))
        
        details_label = ctk.CTkLabel(
            box_container,
            text=details,
            font=("Segoe UI", 11),
            text_color=self.colors["text_secondary"]
        )
        details_label.pack(pady=(0, 20))
        
        select_button = ctk.CTkButton(
            box_container,
            text="Vælg",
            font=("Segoe UI", 12),
            fg_color=self.colors["primary"],
            hover_color="#1874CD",
            command=lambda t=title: self.type_selected(t)
        )
        select_button.pack(pady=(0, 20))

    def create_database_section(self):
        self.db_frame.pack(fill="x", padx=40, pady=10)
        
        # Overskrift
        header = ctk.CTkLabel(
            self.db_frame,
            text="Vælg Database",
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors["primary"]
        )
        header.pack(pady=10)
        
        # Få tilgængelige databaser
        self.available_databases = self.get_available_databases()
        
        if not self.available_databases:
            no_data_label = ctk.CTkLabel(
                self.db_frame,
                text="Ingen databaser fundet for den valgte rapport type",
                font=("Segoe UI", 12),
                text_color=self.colors["text_secondary"]
            )
            no_data_label.pack(pady=10)
            return
                
        # Database vælger container
        db_select_frame = ctk.CTkFrame(self.db_frame, fg_color="transparent")
        db_select_frame.pack(pady=10, fill="x", padx=20)
        
        # Database dropdown
        db_label = ctk.CTkLabel(
            db_select_frame,
            text="Vælg Database:",
            font=("Segoe UI", 14),
            text_color=self.colors["text_primary"]
        )
        db_label.pack(pady=(0, 5))
        
        # Formatér databasenavne til mere læsbare navne
        formatted_names = [self.format_db_name(db) for db in self.available_databases]
        
        self.db_var = ctk.StringVar(value="Vælg database")
        db_dropdown = ctk.CTkOptionMenu(
            db_select_frame,
            values=formatted_names,
            variable=self.db_var,
            command=self.database_selected,
            width=300
        )
        db_dropdown.pack(pady=5)

    def create_format_section(self):
        self.format_frame.pack(fill="x", padx=40, pady=10)
        
        # Overskrift
        header = ctk.CTkLabel(
            self.format_frame,
            text="Vælg Format",
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors["primary"]
        )
        header.pack(pady=10)
        
        # Format container
        formats_frame = ctk.CTkFrame(self.format_frame, fg_color="transparent")
        formats_frame.pack(pady=10)
        
        # Format knapper
        formats = [
            ("Word", "docx", "Detaljeret rapport med tekst og tabeller"),
            ("PDF", "pdf", "Professionelt layout, velegnet til print"),
            ("Excel", "xlsx", "Rådata til videre analyse")
        ]
        
        for format_name, format_ext, format_desc in formats:
            # Format boks
            format_box = ctk.CTkFrame(
                formats_frame,
                fg_color=self.colors["card"],
                corner_radius=10
            )
            format_box.pack(side="left", padx=10, pady=10)
            
            # Format titel
            title = ctk.CTkLabel(
                format_box,
                text=format_name,
                font=("Segoe UI", 16, "bold"),
                text_color=self.colors["primary"]
            )
            title.pack(pady=(15, 5))
            
            # Format beskrivelse
            desc = ctk.CTkLabel(
                format_box,
                text=format_desc,
                font=("Segoe UI", 12),
                text_color=self.colors["text_secondary"],
                wraplength=200
            )
            desc.pack(pady=(0, 15), padx=20)
            
            # Vælg knap
            select_button = ctk.CTkButton(
                format_box,
                text=f"Vælg {format_name}",
                font=("Segoe UI", 12),
                fg_color=self.colors["primary"],
                hover_color="#1874CD",
                command=lambda ext=format_ext: self.format_selected(ext)
            )
            select_button.pack(pady=(0, 15))

    def format_db_name(self, db_name):
        # Fjern .db extension og split på underscore
        parts = db_name.replace('.db', '').split('_')
        if len(parts) >= 4:  # chauffør_data_januar_2024.db
            data_type = parts[0].capitalize()
            month = parts[2].capitalize()
            year = parts[3]
            return f"{data_type} - {month} {year}"
        return db_name

    def database_selected(self, formatted_name):
        # Find den oprindelige database fil ud fra det formaterede navn
        for db in self.available_databases:
            if self.format_db_name(db) == formatted_name:
                try:
                    # Gem den valgte database sti
                    self.selected_database = os.path.join('databases', db)
                    
                    # Vis format vælger
                    self.create_format_section()
                    
                    self.status_label.configure(
                        text=f"Database valgt: {formatted_name}",
                        text_color=self.colors["text_primary"]
                    )
                    
                except Exception as e:
                    self.status_label.configure(
                        text=f"Fejl ved valg af database: {str(e)}",
                        text_color="red"
                    )
                break

    def type_selected(self, type_name):
        self.selected_type = type_name.lower().split()[0]  # "chauffør" eller "køretøjs"
        
        # Fjern tidligere frames hvis de eksisterer
        self.db_frame.pack_forget()
        self.format_frame.pack_forget()
        
        # Opret database vælger
        self.create_database_section()
        
        self.status_label.configure(
            text=f"Valgt: {type_name}",
            text_color=self.colors["text_primary"]
        )

    def get_available_databases(self):
        if not os.path.exists('databases'):
            return []
            
        databases = []
        prefix = f"{self.selected_type}_data"
        
        for file in os.listdir('databases'):
            if file.startswith(prefix) and file.endswith('.db'):
                databases.append(file)
                
        return sorted(databases, reverse=True)  # Nyeste først

    def format_selected(self, format_ext):
        self.selected_format = format_ext
        self.status_label.configure(
            text=f"Format valgt: {format_ext.upper()}",
            text_color=self.colors["text_primary"]
        )
        
        # Generer rapport når format er valgt
        self.generate_report()

    def generate_report(self):
        if self.selected_database is None:
            self.status_label.configure(
                text="Ingen database valgt",
                text_color="red"
            )
            return
                
        try:
            # Opret rapport mappe hvis den ikke eksisterer
            if not os.path.exists('rapporter'):
                os.makedirs('rapporter')
            
            # Generer filnavn
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.selected_type}_rapport_{timestamp}"
            
            if self.selected_format == 'docx':
                try:
                    # Importer WordReportGenerator
                    from word_report import WordReportGenerator
                    
                    # Opret en instance af WordReportGenerator
                    word_generator = WordReportGenerator(self.selected_database)
                    
                    # Generer rapporten
                    generated_filename = word_generator.generer_rapport()
                    
                    self.status_label.configure(
                        text=f"Word rapport genereret: {generated_filename}",
                        text_color="green"
                    )
                    
                    # Vis bekræftelsesbesked
                    messagebox.showinfo(
                        "Rapport Genereret",
                        f"Rapporten er blevet gemt som:\n{generated_filename}\n\ni mappen 'rapporter'"
                    )
                    
                except Exception as e:
                    raise Exception(f"Fejl i Word rapport generering: {str(e)}")
                    
            else:
                # Hent data fra database
                conn = sqlite3.connect(self.selected_database)
                df = pd.read_sql_query(f"SELECT * FROM {self.selected_type}_data_data", conn)
                conn.close()
                
                if self.selected_format == 'pdf':
                    self.generate_pdf_report(filename, df)
                elif self.selected_format == 'xlsx':
                    self.generate_excel_report(filename, df)
                
                # Vis bekræftelsesbesked
                messagebox.showinfo(
                    "Rapport Genereret",
                    f"Rapporten er blevet gemt som:\n{filename}.{self.selected_format}\n\ni mappen 'rapporter'"
                )
                
        except Exception as e:
            self.status_label.configure(
                text=f"Fejl under generering af rapport: {str(e)}",
                text_color="red"
            )
            messagebox.showerror("Fejl", f"Kunne ikke generere rapport: {str(e)}")

    def generate_word_report(self, filename, df):
        doc = Document()
        
        # Tilføj titel
        doc.add_heading(f'{self.selected_type.capitalize()} Rapport', 0)
        doc.add_paragraph(f'Genereret: {datetime.now().strftime("%d-%m-%Y %H:%M")}')
        
        # Tilføj tabel
        table = doc.add_table(rows=1, cols=len(df.columns))
        table.style = 'Table Grid'
        
        # Tilføj headers
        for i, column in enumerate(df.columns):
            table.cell(0, i).text = column
            
        # Tilføj data
            for _, row in df.iterrows():
                cells = table.add_row().cells
                for i, value in enumerate(row):
                    cells[i].text = str(value)
                    
            # Tilføj grundlæggende statistik
            doc.add_heading('Statistik', level=1)
            for column in df.select_dtypes(include=['float64', 'int64']).columns:
                doc.add_paragraph(
                    f'{column}:\n'
                    f'Gennemsnit: {df[column].mean():.2f}\n'
                    f'Minimum: {df[column].min():.2f}\n'
                    f'Maximum: {df[column].max():.2f}'
                )
                    
            doc.save(os.path.join('rapporter', f'{filename}.docx'))

    def generate_pdf_report(self, filename, df):
        pdf = FPDF()
        pdf.add_page()
        
        # Konfigurer font
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)
        
        # Tilføj titel
        pdf.set_font('DejaVu', '', 24)
        pdf.cell(0, 10, f'{self.selected_type.capitalize()} Rapport', ln=True, align='C')
        
        # Tilføj dato
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(0, 10, f'Genereret: {datetime.now().strftime("%d-%m-%Y %H:%M")}', ln=True)
        
        # Tilføj tabel
        pdf.add_page()
        col_width = pdf.w / len(df.columns)
        row_height = pdf.font_size * 1.5
        
        # Headers
        for column in df.columns:
            pdf.cell(col_width, row_height, str(column), 1)
        pdf.ln()
        
        # Data
        for _, row in df.iterrows():
            for value in row:
                pdf.cell(col_width, row_height, str(value), 1)
            pdf.ln()
            
        # Tilføj statistik
        pdf.add_page()
        pdf.set_font('DejaVu', '', 16)
        pdf.cell(0, 10, 'Statistik', ln=True)
        pdf.set_font('DejaVu', '', 12)
        
        for column in df.select_dtypes(include=['float64', 'int64']).columns:
            pdf.multi_cell(0, 10, 
                f'{column}:\n'
                f'Gennemsnit: {df[column].mean():.2f}\n'
                f'Minimum: {df[column].min():.2f}\n'
                f'Maximum: {df[column].max():.2f}\n'
            )
            
        pdf.output(os.path.join('rapporter', f'{filename}.pdf'))

    def generate_excel_report(self, filename, df):
        # Opret Excel writer
        excel_path = os.path.join('rapporter', f'{filename}.xlsx')
        writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')
        
        # Gem hoveddata
        df.to_excel(writer, sheet_name='Data', index=False)
        
        # Opret statistik ark
        stats_df = pd.DataFrame()
        for column in df.select_dtypes(include=['float64', 'int64']).columns:
            stats_df[column] = [
                df[column].mean(),
                df[column].min(),
                df[column].max(),
                df[column].std()
            ]
        
        stats_df.index = ['Gennemsnit', 'Minimum', 'Maximum', 'Standardafvigelse']
        stats_df.to_excel(writer, sheet_name='Statistik')
        
        # Gem og luk
        writer.close()

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
    app = ReportWindow()
    app.run()