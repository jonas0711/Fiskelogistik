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

class KPIWindow:
    def __init__(self):
        # Tilføj DPI awareness
        ctk.deactivate_automatic_dpi_awareness()
        
        # Grundlæggende opsætning
        self.root = ctk.CTk()
        self.root.title("RIO KPI Oversigt")
        self.root.geometry("1200x800")
        
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
            "Tomgang": {
                "er_hoved_kpi": True,
                "hoejere_er_bedre": False,
                "enhed": "%",
                "beskrivelse": "Andel af motordriftstid i tomgang",
                "maal": {"min": 0, "max": 10, "optimal": "under 10%"}
            },
            "Fartpilot Anvendelse": {
                "er_hoved_kpi": False,
                "hoejere_er_bedre": True,
                "enhed": "%",
                "beskrivelse": "Andel af kørsel med fartpilot",
                "maal": {"min": 70, "max": 100, "optimal": "over 70%"}
            },
            "Brug af Motorbremse": {
                "er_hoved_kpi": False,
                "hoejere_er_bedre": True,
                "enhed": "%",
                "beskrivelse": "Andel af bremsning med motorbremse",
                "maal": {"min": 30, "max": 100, "optimal": "over 30%"}
            },
            "Påløbsdrift": {
                "er_hoved_kpi": False,
                "hoejere_er_bedre": True,
                "enhed": "%",
                "beskrivelse": "Andel af kørsel i påløbsdrift",
                "maal": {"min": 5, "max": 100, "optimal": "over 5%"}
            },
            "Diesel Effektivitet": {
                "er_hoved_kpi": True,
                "hoejere_er_bedre": True,
                "enhed": "km/l",
                "beskrivelse": "Kilometer kørt pr. liter diesel",
                "maal": {"min": 2.5, "max": 5, "optimal": "over 2.5 km/l"}
            },
            "Vægtkorrigeret Forbrug": {
                "er_hoved_kpi": False,
                "hoejere_er_bedre": False,
                "enhed": "l/100km/t",
                "beskrivelse": "Brændstofforbrug pr. 100 km pr. ton",
                "maal": {"min": 0, "max": 2, "optimal": "under 2 l/100km/t"}
            },
            "Overspeed Andel": {
                "er_hoved_kpi": False,
                "hoejere_er_bedre": False,
                "enhed": "%",
                "beskrivelse": "Andel af kørsel over hastighedsgrænsen",
                "maal": {"min": 0, "max": 5, "optimal": "under 5%"}
            }
        }
        
        # Hent minimum kilometer indstilling
        self.min_km = self.get_min_km_setting()
        
        # Hent historisk data
        self.historical_data = {}
        
        # Setup UI
        self.setup_ui()
        
        # Tilføj window closure handler
        self.root.protocol("WM_DELETE_WINDOW", self.destroy)
        
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
        
        # Sorter efter år og måned
        return sorted(databases, key=lambda x: (x['year'], x['month_num']))

    def convert_time_to_seconds(self, time_str):
        """Konverterer tid fra 'HH:MM:SS' format til sekunder"""
        try:
            h, m, s = map(int, time_str.split(':'))
            return h * 3600 + m * 60 + s
        except:
            return 0

    def beregn_noegletal(self, data):
        """Beregner nøgletal baseret på kørselsdata"""
        noegletal = {}
        
        try:
            # Beregn tomgangsprocent
            motor_tid = self.convert_time_to_seconds(data['Motordriftstid [hh:mm:ss]'])
            tomgangs_tid = self.convert_time_to_seconds(data['Tomgang / stilstandstid [hh:mm:ss]'])
            noegletal['Tomgang'] = (tomgangs_tid / motor_tid) * 100 if motor_tid > 0 else 0
            
            # Beregn cruise control andel
            distance_over_50 = float(data['Afstand med kørehastighedsregulering (> 50 km/h) [km]']) + \
                             float(data['Afstand > 50 km/h uden kørehastighedsregulering [km]'])
            cruise_distance = float(data['Afstand med kørehastighedsregulering (> 50 km/h) [km]'])
            noegletal['Fartpilot Anvendelse'] = (cruise_distance / distance_over_50) * 100 if distance_over_50 > 0 else 0
            
            # Beregn motorbremse andel
            driftsbremse = float(data['Driftsbremse (km) [km]'])
            motorbremse = float(data['Afstand motorbremse [km]'])
            total_bremse = driftsbremse + motorbremse
            noegletal['Brug af Motorbremse'] = (motorbremse / total_bremse) * 100 if total_bremse > 0 else 0
            
            # Beregn påløbsdrift andel
            total_distance = float(data['Kørestrækning [km]'])
            paalobsdrift = float(data['Aktiv påløbsdrift (km) [km]']) + float(data['Afstand i påløbsdrift [km]'])
            noegletal['Påløbsdrift'] = (paalobsdrift / total_distance) * 100 if total_distance > 0 else 0
            
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
            
        except Exception as e:
            print(f"Fejl ved beregning af nøgletal: {str(e)}")
            return {}
            
        return noegletal

    def get_kpi_historical_data(self):
        """Henter historisk KPI data fra alle databaser"""
        historical_data = {}
        databases = self.find_all_databases()
        
        for db_info in databases:
            try:
                conn = sqlite3.connect(db_info['path'])
                query = f'''
                    SELECT * FROM chauffør_data_data 
                    WHERE "Kørestrækning [km]" >= {self.min_km}
                '''
                df = pd.read_sql_query(query, conn)
                conn.close()
                
                if not df.empty:
                    # Beregn gennemsnit af KPIer for kvalificerede chauffører
                    kpis = {}
                    for _, row in df.iterrows():
                        current_kpis = self.beregn_noegletal(dict(row))
                        for key, value in current_kpis.items():
                            kpis[key] = kpis.get(key, []) + [value]
                    
                    # Beregn gennemsnit for hver KPI
                    avg_kpis = {k: sum(v)/len(v) for k, v in kpis.items() if v}
                    historical_data[db_info['display_date']] = avg_kpis
                    
            except Exception as e:
                print(f"Fejl ved læsning af {db_info['path']}: {str(e)}")
                
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
                current_values = list(self.historical_data.values())[-1]
                
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
                prev_month = dates[-2]
                prev_value = self.historical_data[prev_month].get(title, 0)
                
                # Beregn ændring
                pct_change = ((current_value - prev_value) / prev_value * 100 
                            if prev_value != 0 else 0)
                
                # Bestem farve og pil baseret på om højere er bedre
                higher_is_better = self.kpi_config[title]['hoejere_er_bedre']
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
                text=title,
                font=("Segoe UI", 16, "bold"),
                text_color=self.colors["primary"]
            )
            title_label.pack(pady=(0, 5))
            
            # KPI værdi med ændring
            value_frame = ctk.CTkFrame(card, fg_color="transparent")
            value_frame.pack(pady=5)
            
            value_label = ctk.CTkLabel(
                value_frame,
                text=f"{current_value:.1f}{self.kpi_config[title]['enhed']}",
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
            """Opretter KPI grafer"""
            # Overskrift for grafsektionen
            graphs_title = ctk.CTkLabel(
                self.main_container,
                text="KPI Detaljer",
                font=("Segoe UI", 20, "bold"),
                text_color=self.colors["primary"]
            )
            graphs_title.pack(pady=(20, 10))
            
            # Container til alle grafer
            graphs_container = ctk.CTkFrame(self.main_container, fg_color=self.colors["card"])
            graphs_container.pack(fill="x", padx=40, pady=10)
            
            # Opret graf for hver KPI
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
                text=kpi_name,
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
                
                # Stil indstillinger
                fig.patch.set_facecolor(self.colors["background"])
                ax.set_facecolor(self.colors["background"])
                
                # Forbered data
                dates = list(self.historical_data.keys())
                values = [self.historical_data[date][kpi_name] for date in dates]
                
                # Plot hovedlinje med punkter
                line = ax.plot(dates, values, 'o-', color=self.colors["primary"], 
                            linewidth=2, markersize=8, label='Faktisk værdi')[0]
                
                # Tilføj trend line hvis der er mere end ét datapunkt
                if len(values) > 1:
                    z = np.polyfit(range(len(values)), values, 1)
                    p = np.poly1d(z)
                    ax.plot(dates, p(range(len(values))), "--", 
                        color=self.colors["text_secondary"], alpha=0.8, 
                        label='Trend', linewidth=1.5)
                
                # Konfigurer graf
                ax.grid(True, linestyle='--', alpha=0.3)
                ax.set_ylabel(f"Værdi ({self.kpi_config[kpi_name]['enhed']})")
                plt.xticks(rotation=45)
                
                # Tilføj målområde hvis defineret
                if 'maal' in self.kpi_config[kpi_name]:
                    maal = self.kpi_config[kpi_name]['maal']
                    if self.kpi_config[kpi_name]['hoejere_er_bedre']:
                        ax.axhspan(maal['min'], maal['max'], 
                                color=self.colors["success"], alpha=0.1,
                                label=f"Målområde ({maal['optimal']})")
                    else:
                        ax.axhspan(0, maal['max'], 
                                color=self.colors["success"], alpha=0.1,
                                label=f"Målområde ({maal['optimal']})")
                
                # Tilføj legend med transparent baggrund
                ax.legend(loc='upper right', facecolor=self.colors["background"], 
                        framealpha=0.8)
                
                # Tilføj tooltips
                tooltip = ax.annotate("", 
                                    xy=(0,0), xytext=(20,20),
                                    textcoords="offset points",
                                    bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
                                    arrowprops=dict(arrowstyle="->"))
                tooltip.set_visible(False)
                
                def hover(event):
                    if event.inaxes == ax:
                        cont, ind = line.contains(event)
                        if cont:
                            x = dates[ind["ind"][0]]
                            y = values[ind["ind"][0]]
                            tooltip.xy = (x, y)
                            tooltip.set_text(f"{x}\n{y:.2f}{self.kpi_config[kpi_name]['enhed']}")
                            tooltip.set_visible(True)
                            fig.canvas.draw_idle()
                        else:
                            tooltip.set_visible(False)
                            fig.canvas.draw_idle()
                
                # Tilføj hover event
                fig.canvas.mpl_connect("motion_notify_event", hover)
                
                # Juster layout
                plt.tight_layout()
                
                # Embed graf i Tkinter
                canvas = FigureCanvasTkAgg(fig, graph_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
                
            except Exception as e:
                print(f"Fejl ved oprettelse af graf for {kpi_name}: {str(e)}")
                error_label = ctk.CTkLabel(
                    graph_frame,
                    text=f"Kunne ikke oprette graf for {kpi_name}",
                    font=("Segoe UI", 12),
                    text_color=self.colors["danger"]
                )
                error_label.pack(pady=10)

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
                # Centrer vinduet
                self.root.update_idletasks()
                width = self.root.winfo_width()
                height = self.root.winfo_height()
                x = (self.root.winfo_screenwidth() // 2) - (width // 2)
                y = (self.root.winfo_screenheight() // 2) - (height // 2)
                self.root.geometry(f'{width}x{height}+{x}+{y}')
                
                self.root.mainloop()
            except Exception as e:
                print(f"Fejl i run metoden: {str(e)}")

    if __name__ == "__main__":
        try:
            app = KPIWindow()
            app.run()
        except Exception as e:
            print(f"Fejl ved start af applikationen: {str(e)}")