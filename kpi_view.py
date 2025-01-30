import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from dateutil.relativedelta import relativedelta
import calendar
from functools import lru_cache
import logging
import tkinter.messagebox as messagebox

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

class KPIWindow:
    def __init__(self):
        # Ensret DPI-indstillinger
        ctk.set_widget_scaling(1.0)
        ctk.deactivate_automatic_dpi_awareness()
        
        self.root = ctk.CTk()
        self.root.after(300, self._safe_maximize)  # Kortere delay før init
        
        # Farver - opdateret med alle nødvendige farver
        self.colors = {
            "primary": "#1E90FF",     # Bright blue
            "secondary": "#7F8C8D",    # Medium gray (tilføjet)
            "background": "#F5F7FA",   # Light gray
            "card": "#FFFFFF",         # White
            "text_primary": "#2C3E50", # Dark blue/gray
            "text_secondary": "#7F8C8D",# Medium gray
            "success": "#28a745",      # Grøn
            "danger": "#dc3545",       # Rød
            "warning": "#ffc107",      # Gul
            "info": "#17a2b8"          # Info blå
        }
        
        # KPI definitioner og deres optimeringsmål
        self.kpi_config = {
            'Tomgangsprocent': {
                'navn': 'Tomgang',
                'er_hovedkpi': True,
                'format': '{:.1f}%',
                'maal_min': 0,
                'maal_max': 5,
                'hoejere_er_bedre': False,
                'beskrivelse': 'Procentdel af total motordriftstid brugt i tomgang.',
                'forklaring': 'Viser hvor meget tid motoren kører uden at køretøjet bevæger sig. En lavere procent er bedre, da tomgang bruger unødvendigt brændstof.'
            },
            'Fartpilot Andel': {
                'navn': 'Fartpilot Anvendelse',
                'er_hovedkpi': True,
                'format': '{:.1f}%',
                'maal_min': 66.5,
                'maal_max': 100,
                'hoejere_er_bedre': True,
                'beskrivelse': 'Procentdel af køretid hvor fartpilot er aktivt.',
                'forklaring': 'Viser hvor meget fartpiloten bruges. En højere procent er bedre, da det giver mere jævn og økonomisk kørsel.'
            },
            'Motorbremse Andel': {
                'navn': 'Brug af Motorbremse',
                'er_hovedkpi': True,
                'format': '{:.1f}%',
                'maal_min': 56,
                'maal_max': 100,
                'hoejere_er_bedre': True,
                'beskrivelse': 'Procentdel af total bremsning udført med motorbremse.',
                'forklaring': 'Viser hvor meget motorbremsning bruges i forhold til normale bremser. En højere procent er bedre.'
            },
            'Påløbsdrift Andel': {
                'navn': 'Påløbsdrift',
                'er_hovedkpi': True,
                'format': '{:.1f}%',
                'maal_min': 7,
                'maal_max': 100,
                'hoejere_er_bedre': True,
                'beskrivelse': 'Procentdel af køretid i påløbsdrift.',
                'forklaring': 'Viser hvor meget køretøjet ruller uden motorens trækkraft. En højere procent er bedre.'
            },
            'Diesel Effektivitet': {
                'navn': 'Brændstofeffektivitet',
                'er_hovedkpi': False,
                'format': '{:.2f} km/l',
                'maal_min': None,
                'maal_max': None,
                'hoejere_er_bedre': True,
                'beskrivelse': 'Antal kilometer kørt per liter brændstof.',
                'forklaring': 'Viser hvor langt køretøjet kører på en liter brændstof. En højere værdi er bedre.'
            },
            'Vægtkorrigeret Forbrug': {
                'navn': 'Vægtkorrigeret Forbrug',
                'er_hovedkpi': False,
                'format': '{:.2f} l/100km/t',
                'maal_min': None,
                'maal_max': None,
                'hoejere_er_bedre': False,
                'beskrivelse': 'Brændstofforbrug justeret for lastens vægt.',
                'forklaring': 'Viser brændstofforbruget justeret for lastens vægt. En lavere værdi er bedre.'
            },
            'Overspeed Andel': {
                'navn': 'Hastighedsoverskridelser',
                'er_hovedkpi': False,
                'format': '{:.1f}%',
                'maal_min': None,
                'maal_max': None,
                'hoejere_er_bedre': False,
                'beskrivelse': 'Procentdel af køretid over hastighedsgrænsen.',
                'forklaring': 'Viser hvor meget der køres over hastighedsgrænsen. En lavere procent er bedre.'
            },
            'CO2 Effektivitet': {
                'navn': 'CO₂ Effektivitet',
                'er_hovedkpi': True,
                'format': '{:.3f} kg/tkm',
                'maal_min': None,
                'maal_max': None,
                'hoejere_er_bedre': False,
                'beskrivelse': 'CO₂-udledning per ton-kilometer',
                'forklaring': 'Måler hvor meget CO₂ der udledes per transporteret ton-kilometer. En lavere værdi er bedre.'
            }
        }
        
        # Hent minimum kilometer indstilling
        self.min_km = self.get_min_km_setting()
        
        # Hent historisk data
        self.historical_data = {}
        
        # Hent måned og år fra den nyeste database
        databases = self.find_all_databases()
        if databases:
            latest_db = databases[0]  # Den nyeste database
            self.month_year = latest_db['display_date']  # Gem måned og år
        else:
            self.month_year = "Ukendt"  # Standardværdi hvis ingen databaser findes
        
        # Setup UI
        self.setup_ui()
        
        # Tilføj window closure handler
        self.root.protocol("WM_DELETE_WINDOW", self.destroy)
        
        self._noegletal_cache = {}
        
        self.setup_logging()
        
    def setup_logging(self):
        """Implementer proper logging"""
        logging.basicConfig(
            filename='kpi_view.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def destroy(self):
        """Lukker vinduet og frigør ressourcer"""
        try:
            plt.close('all')  # Luk alle matplotlib figurer
            self.root.destroy()
        except Exception as e:
            print(f"Fejl ved lukning af KPI vindue: {str(e)}")
        
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
            
    def find_all_databases(self):
        """Finder alle kvalificerede chauffør databaser"""
        databases = []
        if not os.path.exists('databases'):
            return databases
            
        for file in os.listdir('databases'):
            if file.startswith('chauffør_data_') and file.endswith('.db'):
                # Udtræk måned og år fra filnavn
                parts = file.replace('.db', '').split('_')
                if len(parts) >= 4:
                    month = parts[2].lower()
                    year = parts[3]
                    
                    # Konverter måned til nummer for sortering
                    months = {
                        'januar': 1, 'februar': 2, 'marts': 3, 'april': 4,
                        'maj': 5, 'juni': 6, 'juli': 7, 'august': 8,
                        'september': 9, 'oktober': 10, 'november': 11, 'december': 12
                    }
                    
                    if month in months:
                        month_num = months[month]
                        databases.append({
                            'path': os.path.join('databases', file),
                            'month': month,
                            'year': int(year),
                            'month_num': month_num,
                            'display_date': f"{month.capitalize()} {year}"
                        })
        
        # Sorter efter år og måned i faldende rækkefølge
        return sorted(databases, key=lambda x: (x['year'], x['month_num']), reverse=True)

    def convert_time_to_seconds(self, time_str):
        """Konverterer tid fra 'HH:MM:SS' format til sekunder"""
        try:
            h, m, s = map(int, time_str.split(':'))
            return h * 3600 + m * 60 + s
        except:
            return 0

    @lru_cache(maxsize=128)
    def beregn_noegletal(self, data_tuple):
        """Beregner nøgletal for given data med caching"""
        try:
            # Konverter tuple tilbage til dictionary
            if isinstance(data_tuple, tuple):
                data = dict(data_tuple)
            else:
                data = data_tuple
                
            noegletal = self._calculate_noegletal(data)
            logging.info(f"Nøgletal beregnet for chauffør")
            return noegletal
                
        except Exception as e:
            logging.error(f"Fejl i nøgletalsberegning: {str(e)}")
            raise

    def get_kpi_historical_data(self):
        """Henter historisk KPI data fra alle databaser"""
        historical_data = {}
        databases = self.find_all_databases()
        
        for db_info in databases:
            try:
                with DatabaseConnection(db_info['path']) as conn:
                    query = f'''
                        SELECT * FROM chauffør_data_data 
                        WHERE "Kørestrækning [km]" >= {self.min_km}
                    '''
                    df = pd.read_sql_query(query, conn)
                    
                    if not df.empty:
                        # Beregn gennemsnit af KPIer for kvalificerede chauffører
                        kpis = {}
                        for _, row in df.iterrows():
                            # Konverter row til tuple for caching
                            row_tuple = tuple(row.items())
                            current_kpis = self.beregn_noegletal(row_tuple)
                            for key, value in current_kpis.items():
                                kpis[key] = kpis.get(key, []) + [value]
                        
                        # Beregn gennemsnit for hver KPI
                        avg_kpis = {k: sum(v)/len(v) for k, v in kpis.items() if v}
                        historical_data[db_info['display_date']] = avg_kpis
                            
            except Exception as e:
                logging.error(f"Fejl ved læsning af {db_info['path']}: {str(e)}")
                    
        return historical_data

    def setup_ui(self):
        try:
            # Hovedcontainer med scrolling
            self.main_container = ctk.CTkScrollableFrame(
                self.root,
                fg_color=self.colors["background"],
                height=800
            )
            self.main_container.pack(expand=True, fill="both", padx=0, pady=0)
            
            # Titel sektion
            self.create_title_section()
            
            # Hent historisk data
            self.historical_data = self.get_kpi_historical_data()
            
            if self.historical_data:
                # Få seneste KPI værdier
                current_values = list(self.historical_data.values())[0]  # Tag den første værdi (nyeste)
                
                # KPI Cards sektion
                self.create_kpi_cards(current_values)
                
                # Graf sektion med individuelle grafer
                self.create_kpi_graphs()
            else:
                # Vis fejlbesked hvis ingen data findes
                self.show_no_data_message()
            
        except Exception as e:
            print(f"Fejl i setup_ui: {str(e)}")

    def create_title_section(self):
        title_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(20, 20), padx=40)
        
        title = ctk.CTkLabel(
            title_frame,
            text="KPI Oversigt",
            font=("Segoe UI", 24, "bold"),
            text_color=self.colors["primary"]
        )
        title.pack()
        
        # Tilføj måned og årstal fra instansvariablen
        month_year_label = ctk.CTkLabel(
            title_frame,
            text=f"Data for: {self.month_year}",
            font=("Segoe UI", 14),
            text_color=self.colors["text_secondary"]
        )
        month_year_label.pack(pady=(5, 0))

        subtitle = ctk.CTkLabel(
            title_frame,
            text="Nøgletal og udvikling over tid",
            font=("Segoe UI", 14),
            text_color=self.colors["text_secondary"]
        )
        subtitle.pack(pady=(5, 0))

    def create_kpi_cards(self, current_values):
        # Container til KPI kort
        cards_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        cards_frame.pack(fill="x", padx=40, pady=10)
        
        # Grid layout for kort
        row = 0
        col = 0
        max_cols = 4
        
        for kpi_name, value in current_values.items():
            card = self.create_kpi_card(cards_frame, kpi_name, value)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Opdater grid position
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
        # Konfigurer grid columns
        for i in range(max_cols):
            cards_frame.grid_columnconfigure(i, weight=1)

    def create_kpi_card(self, parent, title, current_value):
        """Opretter et KPI kort med farver og pile baseret på udvikling"""
        card = ctk.CTkFrame(parent, fg_color=self.colors["card"])
        
        # Find forrige måneds værdi
        dates = list(self.historical_data.keys())
        if len(dates) >= 2:
            # Nyeste måned er index 0, så den forrige er index 1
            prev_month = dates[1]
            prev_value = self.historical_data[prev_month].get(title, 0)
            
            # Beregn ændring
            pct_change = ((current_value - prev_value) / prev_value * 100 
                        if prev_value != 0 else 0)
            
            # Bestem farve og pil baseret på om højere er bedre
            higher_is_better = self.kpi_config[title]['hoejere_er_bedre']
            
            # Hvis højere er bedre:
            #   - Positivt ændring (pil op) og højere er bedre = grøn
            #   - Negativt ændring (pil ned) og højere er bedre = rød
            # Hvis lavere er bedre:
            #   - Positivt ændring (pil op) og lavere er bedre = rød
            #   - Negativt ændring (pil ned) og lavere er bedre = grøn
            is_improvement = (pct_change > 0) == higher_is_better
            
            color = self.colors["success"] if is_improvement else self.colors["danger"]
            arrow = "↑" if pct_change > 0 else "↓"
        else:
            color = self.colors["primary"]
            pct_change = 0
            arrow = ""
        
        # KPI titel og beskrivelse
        desc_label = ctk.CTkLabel(
            card,
            text=self.kpi_config[title]['beskrivelse'],
            font=("Segoe UI", 12),
            text_color=self.colors["text_secondary"]
        )
        desc_label.pack(pady=(10, 0))
        
        title_label = ctk.CTkLabel(
            card,
            text=self.kpi_config[title]['navn'],  # Brug 'navn' i stedet for direkte titel
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=(0, 5))
        
        # KPI værdi med ændring
        value_frame = ctk.CTkFrame(card, fg_color="transparent")
        value_frame.pack(pady=5)
        
        value_label = ctk.CTkLabel(
            value_frame,
            text=self.kpi_config[title]['format'].format(current_value),
            font=("Segoe UI", 24, "bold"),
            text_color=color
        )
        value_label.pack(side="left", padx=5)
        
        if arrow:
            change_label = ctk.CTkLabel(
                value_frame,
                text=f"{arrow} {abs(pct_change):.1f}%",
                font=("Segoe UI", 14),
                text_color=color
            )
            change_label.pack(side="left")
        
        return card

    def create_kpi_graphs(self):
        """Forbedret memory management for grafer"""
        # Ryd tidligere grafer
        if hasattr(self, '_current_figures'):
            for fig in self._current_figures:
                plt.close(fig)
        self._current_figures = []
        
        # Container til alle grafer
        graphs_container = ctk.CTkFrame(self.main_container, fg_color=self.colors["card"])
        graphs_container.pack(fill="x", padx=40, pady=10)
        
        # Opret nye grafer med kontrolleret memory brug
        for kpi_name in self.kpi_config.keys():
            self.create_interactive_kpi_graph(graphs_container, kpi_name)

    def create_interactive_kpi_graph(self, parent, kpi_name):
        """Opretter en interaktiv graf for en KPI"""
        # Graf container
        graph_frame = ctk.CTkFrame(parent, fg_color=self.colors["background"])
        graph_frame.pack(fill="x", padx=20, pady=10)
        
        # Graf titel og beskrivelse
        title_frame = ctk.CTkFrame(graph_frame, fg_color="transparent")
        title_frame.pack(pady=5)
        
        title = ctk.CTkLabel(
            title_frame,
            text=self.kpi_config[kpi_name]['navn'],
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors["primary"]
        )
        title.pack()
        
        description = ctk.CTkLabel(
            title_frame,
            text=self.kpi_config[kpi_name]['beskrivelse'],
            font=("Segoe UI", 12),
            text_color=self.colors["text_secondary"]
        )
        description.pack()
        
        try:
            # Opret figur og axes med specifik størrelse og DPI
            fig, ax = plt.subplots(figsize=(12, 4), dpi=100)
            self._current_figures.append(fig)
            
            # Stil indstillinger
            fig.patch.set_facecolor(self.colors["background"])
            ax.set_facecolor(self.colors["background"])
            
            # Forbered data
            dates = list(reversed(self.historical_data.keys()))  # Vend rækkefølgen
            values = [self.historical_data[date][kpi_name] for date in dates]
            
            # Formatér x-akse labels
            formatted_dates = []
            for date in dates:
                # Fjern årstal fra visningen hvis det er samme år
                if date.endswith('2024'):
                    formatted_dates.append(date.replace(' 2024', ''))
                elif date.endswith('2023'):
                    formatted_dates.append(date.replace(' 2023', '\'23'))
                else:
                    formatted_dates.append(date)
            
            # Plot hovedlinje med punkter
            line = ax.plot(formatted_dates, values, 'o-', color=self.colors["primary"], 
                        linewidth=2, markersize=6, label='Faktisk værdi')[0]
            
            # Tilføj trend line hvis der er mere end ét datapunkt
            if len(values) > 1:
                z = np.polyfit(range(len(values)), values, 1)
                p = np.poly1d(z)
                ax.plot(formatted_dates, p(range(len(values))), "--", 
                    color=self.colors["text_secondary"], alpha=0.8, 
                    label='Trend', linewidth=1.5)
            
            # Konfigurer graf
            ax.grid(True, linestyle='--', alpha=0.3)
            ax.set_ylabel(f"Værdi ({self.kpi_config[kpi_name]['format'].split()[1] if ' ' in self.kpi_config[kpi_name]['format'] else '%'})")
            
            # Juster x-akse labels
            plt.xticks(rotation=45, ha='right')
            ax.tick_params(axis='x', labelsize=8)
            
            # Tilføj målområde hvis defineret
            if self.kpi_config[kpi_name]['maal_min'] is not None and self.kpi_config[kpi_name]['maal_max'] is not None:
                maal_min = self.kpi_config[kpi_name]['maal_min']
                maal_max = self.kpi_config[kpi_name]['maal_max']
                if self.kpi_config[kpi_name]['hoejere_er_bedre']:
                    ax.axhspan(maal_min, maal_max, 
                            color=self.colors["success"], alpha=0.1,
                            label=f"Målområde")
                else:
                    ax.axhspan(0, maal_max, 
                            color=self.colors["success"], alpha=0.1,
                            label=f"Målområde")
            
            # Tilføj legend med transparent baggrund
            ax.legend(loc='upper right', facecolor=self.colors["background"], 
                    framealpha=0.8, fontsize=8)
            
            # Tilføj tooltips med dynamisk positionering
            tooltip = ax.annotate("", 
                xy=(0,0), 
                xytext=(20,20),
                textcoords="offset points",
                bbox=dict(
                    boxstyle="round,pad=0.5", 
                    fc="white", 
                    ec="0.5", 
                    alpha=0.9
                ),
                arrowprops=dict(arrowstyle="->"))
            tooltip.set_visible(False)

            def hover(event):
                if event.inaxes == ax:
                    cont, ind = line.contains(event)
                    if cont:
                        x = formatted_dates[ind["ind"][0]]
                        y = values[ind["ind"][0]]
                        
                        # Brug kun y-værdien til transformation da x er en dato string
                        display_coords = ax.transData.transform([(0, float(y))])[0]
                        fig_coords = fig.transFigure.inverted().transform(display_coords)
                        
                        # Juster position baseret på x-koordinat i plot
                        x_pos = ind["ind"][0] / (len(dates)-1)  # Normaliseret x-position (0-1)
                        
                        # Bestem tooltip position
                        if x_pos > 0.8:  # Hvis punktet er i højre side
                            tooltip.set_position((-120, 20))
                        else:
                            tooltip.set_position((20, 20))
                            
                        # Juster y position hvis punktet er nær top eller bund
                        if fig_coords[1] > 0.8:
                            tooltip.set_position((tooltip.xyann[0], -20))
                        elif fig_coords[1] < 0.2:
                            tooltip.set_position((tooltip.xyann[0], 20))
                            
                        # Sæt tooltip data og position
                        tooltip.xy = (x, y)
                        tooltip.set_text(f"{x}\n{self.kpi_config[kpi_name]['format'].format(y)}")
                        tooltip.set_visible(True)
                        fig.canvas.draw_idle()
                    else:
                        tooltip.set_visible(False)
                        fig.canvas.draw_idle()

            # Tilføj hover event
            fig.canvas.mpl_connect("motion_notify_event", hover)
            
            # Juster layout
            plt.tight_layout()
            
            # Juster margener for bedre visning
            plt.subplots_adjust(bottom=0.2, left=0.1, right=0.95, top=0.95)
            
            # Embed graf i tkinter vindue med korrekt størrelse
            canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            logging.error(f"Fejl ved oprettelse af graf for {kpi_name}: {str(e)}")
            error_label = ctk.CTkLabel(
                graph_frame,
                text=f"Kunne ikke oprette graf: {str(e)}",
                text_color=self.colors["danger"]
            )
            error_label.pack(pady=20)

    def show_no_data_message(self):
            """Viser besked når ingen data er tilgængelig"""
            message_frame = ctk.CTkFrame(
                self.main_container,
                fg_color=self.colors["card"]
            )
            message_frame.pack(expand=True, fill="both", padx=40, pady=20)
            
            message = ctk.CTkLabel(
                message_frame,
                text="Ingen KPI data tilgængelig\n\nUpload venligst data via Upload funktionen",
                font=("Segoe UI", 14),
                text_color=self.colors["text_secondary"]
            )
            message.pack(expand=True)

    def run(self):
        """Starter applikationen"""
        try:
            self.root.state("zoomed")  # Tilføj ekstra sikkerhed
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Fejl", f"Kunne ikke starte KPI-vindue: {str(e)}")

    def get_historical_data(self):
        """Implementer progressiv data loading med progress feedback"""
        try:
            databases = self.find_all_databases()
            total_chunks = (len(databases) + 9) // 10  # Ceil division
            
            # Opret progress bar
            progress_window = ctk.CTkToplevel()
            progress_window.title("Indlæser data")
            progress_window.geometry("300x150")
            
            # Centrer progress window
            progress_window.update_idletasks()
            x = (progress_window.winfo_screenwidth() // 2) - (300 // 2)
            y = (progress_window.winfo_screenheight() // 2) - (150 // 2)
            progress_window.geometry(f'+{x}+{y}')
            
            progress_label = ctk.CTkLabel(
                progress_window,
                text="Indlæser historisk data...",
                font=("Segoe UI", 12)
            )
            progress_label.pack(pady=20)
            
            progress_bar = ctk.CTkProgressBar(progress_window)
            progress_bar.pack(pady=10, padx=20, fill="x")
            progress_bar.set(0)
            
            def load_chunk(start_idx, chunk_size=10):
                end_idx = min(start_idx + chunk_size, len(databases))
                chunk_data = databases[start_idx:end_idx]
                return {db['display_date']: self._process_database(db) 
                        for db in chunk_data}
            
            self.historical_data = {}
            for i in range(0, len(databases), 10):
                chunk = load_chunk(i)
                self.historical_data.update(chunk)
                
                # Opdater progress
                progress = (i + 10) / len(databases)
                progress_bar.set(min(progress, 1.0))
                progress_label.configure(
                    text=f"Indlæser historisk data... {int(progress * 100)}%"
                )
                progress_window.update()
                
                self.update_ui()
                    
            logging.info("Historisk data indlæst succesfuldt")
            progress_window.destroy()
                
        except Exception as e:
            logging.error(f"Fejl ved indlæsning af historisk data: {str(e)}")
            self.historical_data = {}
            if 'progress_window' in locals():
                progress_window.destroy()

    def _calculate_noegletal(self, data):
        """Beregner nøgletal baseret på kørselsdata"""
        try:
            noegletal = {}
            
            # Beregn tomgangsprocent
            motor_tid = self.convert_time_to_seconds(data['Motordriftstid [hh:mm:ss]'])
            tomgangs_tid = self.convert_time_to_seconds(data['Tomgang / stilstandstid [hh:mm:ss]'])
            noegletal['Tomgangsprocent'] = (tomgangs_tid / motor_tid) * 100 if motor_tid > 0 else 0
            
            # Beregn cruise control andel
            distance_over_50 = float(data['Afstand med kørehastighedsregulering (> 50 km/h) [km]']) + \
                             float(data['Afstand > 50 km/h uden kørehastighedsregulering [km]'])
            cruise_distance = float(data['Afstand med kørehastighedsregulering (> 50 km/h) [km]'])
            noegletal['Fartpilot Andel'] = (cruise_distance / distance_over_50) * 100 if distance_over_50 > 0 else 0
            
            # Beregn motorbremse andel
            driftsbremse = float(data['Driftsbremse (km) [km]'])
            motorbremse = float(data['Afstand motorbremse [km]'])
            total_bremse = driftsbremse + motorbremse
            noegletal['Motorbremse Andel'] = (motorbremse / total_bremse) * 100 if total_bremse > 0 else 0
            
            # Beregn påløbsdrift andel
            total_distance = float(data['Kørestrækning [km]'])
            paalobsdrift = float(data['Aktiv påløbsdrift (km) [km]']) + float(data['Afstand i påløbsdrift [km]'])
            noegletal['Påløbsdrift Andel'] = (paalobsdrift / total_distance) * 100 if total_distance > 0 else 0
            
            # Beregn diesel effektivitet
            forbrug = float(data['Forbrug [l]'])
            noegletal['Diesel Effektivitet'] = total_distance / forbrug if forbrug > 0 else 0
            
            # Beregn vægtkorrigeret forbrug
            total_vaegt = float(data.get('Ø totalvægt [t]', 0))
            if total_vaegt > 0 and total_distance > 0:
                noegletal['Vægtkorrigeret Forbrug'] = (forbrug / total_distance * 100) / total_vaegt
            else:
                noegletal['Vægtkorrigeret Forbrug'] = 0
                
            # Beregn overspeed andel
            overspeed = float(data['Overspeed (km uden påløbsdrift) [km]'])
            noegletal['Overspeed Andel'] = (overspeed / total_distance) * 100 if total_distance > 0 else 0
            
            # Beregn CO₂ effektivitet (kg CO₂ per ton-kilometer)
            co2_emission = float(data['CO₂-emission [kg]'])
            if total_distance > 0 and total_vaegt > 0:
                # Først beregn CO₂ per kilometer
                co2_per_km = co2_emission / total_distance
                # Derefter normaliser med vægten for at få kg CO₂ per ton-kilometer
                noegletal['CO2 Effektivitet'] = co2_per_km / total_vaegt
            else:
                noegletal['CO2 Effektivitet'] = 0
            
            logging.info(f"Nøgletal beregnet succesfuldt")
            return noegletal
            
        except Exception as e:
            logging.error(f"Fejl i _calculate_noegletal: {str(e)}")
            raise

    def update_ui(self):
        """Opdaterer brugergrænsefladen med nye data"""
        try:
            if self.historical_data:
                current_values = list(self.historical_data.values())[0]
                self.create_kpi_cards(current_values)
                self.create_kpi_graphs()
            self.root.update()
        except Exception as e:
            logging.error(f"Fejl ved opdatering af UI: {str(e)}")

    def _process_database(self, db_info):
        """Processerer en database og returnerer dens KPI data"""
        try:
            with DatabaseConnection(db_info['path']) as conn:
                query = f'''
                    SELECT * FROM chauffør_data_data 
                    WHERE "Kørestrækning [km]" >= {self.min_km}
                '''
                df = pd.read_sql_query(query, conn)
                
                if not df.empty:
                    kpis = {}
                    for _, row in df.iterrows():
                        row_dict = dict(row)
                        current_kpis = self._calculate_noegletal(row_dict)
                        for key, value in current_kpis.items():
                            kpis[key] = kpis.get(key, []) + [value]
                            
                    return {k: sum(v)/len(v) for k, v in kpis.items() if v}
                return {}
                
        except Exception as e:
            logging.error(f"Fejl ved processering af database {db_info['path']}: {str(e)}")
            return {}

    def _safe_maximize(self):
        """Forhindrer minimering under load"""
        self.root.update_idletasks()  # Opdaterer alle widgets
        if self.root.state() != "zoomed":
            self.root.state("zoomed")
        self.root.minsize(1024, 768)  # Sæt minimumsstørrelse

    if __name__ == "__main__":
        try:
            app = KPIWindow()
            app.run()
        except Exception as e:
            print(f"Fejl ved start af applikationen: {str(e)}")