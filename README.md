# RIO Chauffør Rapport Generator

Et moderne og brugervenligt Python-baseret system til omfattende analyse og visualisering af chauffør- og køretøjsdata fra RIO-systemer. Systemet er designet til at hjælpe virksomheder med at optimere deres transportoperationer gennem detaljeret dataanalyse og automatiseret rapportering.

## Indholdsfortegnelse
1. [Beskrivelse](#beskrivelse)
2. [Funktioner](#funktioner)
3. [Installation](#installation)
4. [Detaljeret Anvendelsesguide](#detaljeret-anvendelsesguide)
5. [Systemkrav](#systemkrav)
6. [Teknisk Dokumentation](#teknisk-dokumentation)
7. [Vedligeholdelse](#vedligeholdelse)
8. [Fejlfinding](#fejlfinding)
9. [FAQ](#faq)

## Beskrivelse

RIO Chauffør Rapport Generator er et avanceret analyseværktøj udviklet specifikt til transportvirksomheder. Systemet behandler data fra RIO-platforme og omdanner det til handlingsorienterede indsigter og rapporter.

### Primære Anvendelsesområder
- Analyse af chaufførers kørestil og effektivitet
- Overvågning af brændstofforbrug og miljøpåvirkning
- Identifikation af optimeringsmuligheder i driften
- Automatiseret rapportgenerering til ledelse og chauffører
- Performance-tracking over tid

## Funktioner

### Upload Module
- **Understøttede Formater**: Excel-filer (.xlsx, .xls) fra RIO
- **Automatisk Validering**: Verificerer dataintegritet
- **Periode-Håndtering**: Organiserer data efter måned og år
- **Duplikeringskontrol**: Forhindrer dobbelt upload

### KPI Dashboard
- **Realtids Visualisering** af:
  - Brændstofforbrug
  - Tomgangsprocenter
  - Køretidsanalyse
  - Hastighedsoverholdelse
- **Sammenligningsmuligheder** mellem perioder
- **Eksport** af grafer og data

### Rapport Generator
Producerer professionelle rapporter i flere formater:
- **Word**: Detaljerede analyser med grafer
- **PDF**: Kompakte oversigter
- **Excel**: Rådata til videre analyse

### Chauffør Administration
- **Individuelle Profiler** for hver chauffør
- **Performance Tracking** over tid
- **Automatisk Kategorisering** baseret på KPI'er

### Indstillinger
- Konfigurerbare grænseværdier for KPI'er
- Tilpasning af rapportskabeloner
- Systemparametre justering

## Installation

### Forudsætninger
1. Python 3.8 eller nyere installeret
2. Git installeret (for versionsstyring)
3. Administratorrettigheder på maskinen

### Trin-for-Trin Installation

1. **Klargør Python-miljø**
```bash
# Opret virtuelt miljø
python -m venv rio_env

# Aktivér miljø
# Windows:
rio_env\Scripts\activate
# Linux/Mac:
source rio_env/bin/activate
```

2. **Installér afhængigheder**
```bash
# Installér alle nødvendige pakker
pip install -r requirements.txt
```

3. **Konfigurér system**
```bash
# Opret nødvendige mapper
mkdir databases
mkdir rapporter
```

4. **Test installation**
```bash
python app.py
```

## Detaljeret Anvendelsesguide

### 1. Første Opstart
1. Start programmet via `app.py`
2. Konfigurér grundlæggende indstillinger:
   - Minimum kilometer for analyse
   - Diesel pris
   - Rapporteringsperiode

### 2. Data Upload
1. Åbn "Upload" modulet
2. Vælg datotype (Chauffør/Køretøj)
3. Vælg periode (måned/år)
4. Vælg Excel-fil fra RIO
5. Bekræft upload

### 3. KPI Dashboard Anvendelse
1. Vælg analyseperiode
2. Vælg visningstype:
   - Samlet overblik
   - Individuelle chauffører
   - Sammenligning mellem perioder
3. Eksportér data efter behov

### 4. Rapportgenerering
1. Vælg rapporttype:
   - Chauffør rapport
   - Flåderapport
   - KPI oversigt
2. Vælg periode
3. Vælg format (Word/PDF/Excel)
4. Generer og gem rapport

### 5. Chauffør Administration
1. Tilgå chaufføroversigt
2. Filtrer efter:
   - Periode
   - Performance
   - KPI'er
3. Eksportér chaufførdata

## Systemkrav

### Minimum Krav
- **Processor**: Intel Core i3 eller tilsvarende
- **RAM**: 4 GB
- **Lagerplads**: 500 MB fri plads
- **Skærm**: 1200x800 opløsning
- **OS**: Windows 10, macOS 10.14+, Linux

### Anbefalede Specifikationer
- **Processor**: Intel Core i5 eller bedre
- **RAM**: 8 GB
- **Lagerplads**: 1 GB fri plads
- **Skærm**: 1920x1080 opløsning

## Teknisk Dokumentation

### Mappestruktur
```
rio_system/
├── app.py                 # Hovedapplikation og GUI
├── modules/              # Kernemoduler
│   ├── upload.py        # Data upload funktionalitet
│   ├── kpi_view.py      # KPI visualisering og analyse
│   ├── driver_view.py   # Chauffør administration
│   ├── report_view.py   # Rapport generering
│   └── settings_view.py # System indstillinger
├── utils/               # Hjælpefunktioner
│   ├── data_processor.py
│   └── validators.py
├── templates/           # Rapport skabeloner
├── databases/          # SQLite databaser
└── rapporter/         # Genererede rapporter
```

### Database Struktur
#### settings.db
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

#### chauffør_data_[måned]_[år].db
```sql
CREATE TABLE chauffør_data_data (
    Chauffør TEXT,
    "Kørestrækning [km]" REAL,
    "Forbrug [l]" REAL,
    -- Andre kolonner
);
```

### API Reference
Centrale klasser og metoder:
```python
class UploadWindow:
    def __init__(self)
    def setup_ui(self)
    def convert_to_sql(self)

class KPIWindow:
    def __init__(self)
    def beregn_noegletal(self)
    def create_kpi_graphs(self)

class ReportWindow:
    def __init__(self)
    def generate_report(self)
```

## Vedligeholdelse

### Daglig Vedligeholdelse
1. **Backup**
   - Tag daglig backup af databases/
   - Arkiver gamle rapporter

2. **Systemtjek**
   - Verificér databaseforbindelser
   - Tjek diskplads
   - Monitorer logfiler

### Ugentlig Vedligeholdelse
1. **Data Validering**
   - Tjek for datakonsistens
   - Verificér KPI beregninger

2. **Systemoptimering**
   - Ryd gamle temporary filer
   - Optimer databaser

### Månedlig Vedligeholdelse
1. **Systemopdatering**
   - Opdatér Python pakker
   - Tjek for nye RIO dataformater
   - Backup hele systemet

## Fejlfinding

### Almindelige Problemer og Løsninger

#### 1. Upload Fejler
**Problem**: Kan ikke uploade Excel-fil
**Løsning**:
- Tjek filformat og encoding
- Verificér Excel-struktur
- Tjek rettigheder i databases/

#### 2. Rapport Generering Fejler
**Problem**: Kan ikke generere rapport
**Løsning**:
- Tjek minimum km indstilling
- Verificér databaseforbindelse
- Tjek diskplads

#### 3. KPI Visning Fejler
**Problem**: Grafer vises ikke korrekt
**Løsning**:
- Genstart applikationen
- Tjek datavaliditet
- Opdatér matplotlib

## FAQ

### Generelle Spørgsmål
**Q**: Hvor ofte skal data uploades?
**A**: Det anbefales at uploade data månedligt for bedste resultater.

**Q**: Kan systemet håndtere flere køretøjstyper?
**A**: Ja, systemet er designet til at håndtere alle RIO-kompatible køretøjer.

### Tekniske Spørgsmål
**Q**: Hvordan udvides databaseskemaet?
**A**: Kontakt systemadministrator for skemaændringer.

**Q**: Kan rapporthyppighed ændres?
**A**: Ja, dette kan konfigureres i indstillinger.

## Support og Kontakt

### Teknisk Support
- Email: support@example.com
- Telefon: +45 xxxx xxxx
- Hjemmeside: www.example.com/support

### Dokumentation
Fuld teknisk dokumentation findes i systemets docs/ mappe.

## Versionering

Dette projekt følger [Semantic Versioning](https://semver.org/). 
Nuværende version: 1.0.0

## Licens

Intern software - alle rettigheder forbeholdes.