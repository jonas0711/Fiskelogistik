# RIO Chauffør Rapport Generator

Et moderne og brugervenligt Python-baseret system til omfattende analyse og visualisering af chauffør- og køretøjsdata fra RIO-systemer. Systemet er designet til at hjælpe virksomheder med at optimere deres transportoperationer gennem detaljeret dataanalyse og automatiseret rapportering.

## Indholdsfortegnelse
1. [Beskrivelse](#beskrivelse)
2. [Hovedfunktioner](#hovedfunktioner)
3. [Installation](#installation)
4. [Systemkrav](#systemkrav)
5. [Teknisk Dokumentation](#teknisk-dokumentation)
6. [Vedligeholdelse](#vedligeholdelse)
7. [Fejlfinding](#fejlfinding)

## Beskrivelse

RIO Chauffør Rapport Generator er et avanceret analyseværktøj udviklet specifikt til transportvirksomheder. Systemet behandler data fra RIO-platforme og omdanner det til handlingsorienterede indsigter og rapporter.

### Primære Anvendelsesområder
- Analyse af chaufførers kørestil og effektivitet
- Overvågning af brændstofforbrug og miljøpåvirkning
- Identifikation af optimeringsmuligheder i driften
- Automatiseret rapportgenerering til ledelse og chauffører
- Performance-tracking over tid

## Hovedfunktioner

### Upload Modul
- **Understøttede Formater**: Excel-filer (.xlsx, .xls) fra RIO
- **Automatisk Validering**: Verificerer dataintegritet
- **Periode-Håndtering**: Organiserer data efter måned og år
- **Duplikeringskontrol**: Forhindrer dobbelt upload

### KPI Dashboard
- **Realtids Visualisering** af:
  - Tomgangsprocent (mål: under 5%)
  - Fartpilot Anvendelse (mål: over 66.5%)
  - Brug af Motorbremse (mål: over 56%)
  - Påløbsdrift (mål: over 7%)
  - Brændstofeffektivitet
  - CO₂ Effektivitet
  - Vægtkorrigeret Forbrug
  - Hastighedsoverskridelser
- **Interaktive Grafer** med trend-linjer og målområder
- **Historisk Data Sammenligning**

### Rapport Generator
- **Formatmuligheder**:
  - Word: Detaljerede analyser med grafer
  - PDF: Kompakte oversigter
  - Excel: Rådata og statistik
- **Automatisk Mail Distribution**
- **Tilpassede Rapportskabeloner**

### Chauffør Administration
- **Individuelle Profiler**
- **Email Håndtering**
- **Performance Tracking**
- **Gruppeadministration**

### Indstillinger
- **Mail Konfiguration**
- **KPI Grænseværdier**
- **Systemparametre**
- **Rapportskabeloner**

## Installation

### Forudsætninger
1. Python 3.8 eller nyere
2. Git (for versionsstyring)
3. Pip (Python package manager)

### Installationstrin
1. Klon repository:
   ```bash
   git clone [repository-url]
   ```

2. Installer afhængigheder:
   ```bash
   pip install -r requirements.txt
   ```

3. Konfigurer databasen:
   ```bash
   python setup_database.py
   ```

4. Start programmet:
   ```bash
   python app.py
   ```

## Systemkrav

### Minimum Krav
- **OS**: Windows 10
- **Processor**: Intel Core i3 eller tilsvarende
- **RAM**: 4 GB
- **Lagerplads**: 500 MB fri plads
- **Skærm**: 1200x800 opløsning

### Anbefalede Specifikationer
- **Processor**: Intel Core i5 eller bedre
- **RAM**: 8 GB
- **Lagerplads**: 1 GB fri plads
- **Skærm**: 1920x1080 opløsning

## Teknisk Dokumentation

### Mappestruktur
```
rio_system/
├── app.py                 # Hovedapplikation
├── database_connection.py # Database håndtering
├── upload.py             # Data upload
├── kpi_view.py          # KPI visualisering
├── driver_view.py       # Chauffør administration
├── report_view.py       # Rapport generering
├── settings_view.py     # Indstillinger
├── mail_handler.py      # Email funktionalitet
├── word_report.py       # Word rapport generator
└── logging_config.py    # Logging konfiguration
```

### Database Struktur

#### settings.db
- Systemindstillinger
- Mail konfiguration
- KPI grænseværdier

#### chauffør_data_[måned]_[år].db
- Kørselsdata
- Performance metrics
- Chauffør statistik

### Centrale Klasser

#### ModernRIOMenu (app.py)
- Hovedmenu og navigation
- UI initialisering
- Vindueshåndtering

#### KPIWindow (kpi_view.py)
- KPI visualisering
- Performance analyse
- Historisk data sammenligning

#### DatabaseConnection (database_connection.py)
- Database operationer
- Data migration
- Connection pooling

#### MailHandler (mail_handler.py)
- Email konfiguration
- Rapport distribution
- Template håndtering

## Vedligeholdelse

### Daglig Vedligeholdelse
- Backup af databases/
- Verificér databaseforbindelser
- Monitorer logfiler

### Ugentlig Vedligeholdelse
- Data validering
- Systemoptimering
- Temporary fil oprydning

### Månedlig Vedligeholdelse
- Systemopdateringer
- Database optimering
- Fuld system backup

## Fejlfinding

### Almindelige Problemer

#### Database Fejl
- Tjek rettigheder i databases/
- Verificér databasestruktur
- Kontroller disk plads

#### Upload Fejl
- Validér filformat
- Tjek Excel struktur
- Kontroller duplikering

#### Rapport Fejl
- Tjek minimum km indstilling
- Verificér mail konfiguration
- Kontroller template integritet