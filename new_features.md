Beskrivelse af nye features:
Vi skal implementere en løsning hvor man via programmet kan sende hver enkelt chaufførs rapport for en pågældende måned. Det gøres ved at der oprettes en google konto til formålet og anvende Gmail som SMTP-server. Så det skal være muligt at gå ind i rapporter. Så skal der være en ny knap der hedder send mails. Så skal man vælge en database inden man kommer ind til mail systemet. Mail systemet skal så fremvise alle de chauffører som opfylder kravene for den pågældene database. Så skal hver chauffør have en knap man kan trykke på. Hvis de har en mail registreret skal deres knap være grøn. Hvis de ikke har en mail registreret skal de være røde. Hvis alle er grønne skal man kunne trykke på en knap der hedder send mail til alle (Her sender den så individuel mail til hver med hver deres individuelle rapport ligesom individuel rapport laver). Der skal være en html skitse hvor variabler såsom navn måned og år gør hver mail unik men ud fra samme skabelon. Uanset om knappen er rød eller grøn skal man kunne trykke på enhver chauffør. Her skal der komme en pop up hvor der er en boks med mailadressen hvis der er en. Her skal man kunne ændre den hvis man ønsker det eller indtaste den hvis der ikke er nogen. Man skal kunne trykke på en knap der hedder send rapport. Så skal man også kunne vælge en knap der hedder download rapport. 

I Chauffør knappen på hovedsiden skal man kunne åbne den og se alle chauffører som den gør nu. Herinde skal man så kunne trykke på en knap der hedder mail liste. Når man trykker på den knap skal der komme et pop up vindue hvor alle chaufører fremgår i liste format. Ud fra hver chauffør skal man kunne indtaste eller redigere en mail adresse som så tilknyttes deres profil til når man skal sende mails med individuelle rapporter.

Alt konfigurering af mailadresse opsætning som afsender skal kunne opsættes i Indstillinger.


Steps:
1. DATABASE UDVIDELSE
Hvorfor:


Systemet har brug for at kunne gemme to typer af mail-relateret data permanent: SMTP konfiguration og chauffør mailadresser
Den eksisterende settings.db bruges allerede til systemkonfiguration, så det er logisk at udvide denne
Ved at bruge samme database struktur sikrer vi konsistens i datahåndteringen
SQLite er ideelt da det er lightweight og kræver ingen ekstra server

Hvad skal implementeres:

En mail_config tabel der følger samme key-value struktur som eksisterende settings tabel
En driver_emails tabel der knytter mailadresser til chauffører
Timestamps for at spore ændringer og sendte mails
Udvidelse af DatabaseConnection klassen til at håndtere disse nye tabeller
Migrationsscript til at opgradere eksisterende databaser

Integration med eksisterende system:

Skal følge samme connection pattern som ses i andre moduler
Skal implementere samme fejlhåndtering
Skal bruge samme logging system
Skal følge samme transaktionshåndtering

2. INDSTILLINGER UDVIDELSE (settings_view.py)
Hvorfor:


SMTP konfiguration skal kun sættes op én gang og bruges af hele systemet
Skal integreres i eksisterende indstillinger for at bevare konsistent brugeroplevelse
Skal være let tilgængeligt for administratorer

Hvad skal implementeres:

Ny sektion i settings_view der følger eksisterende design patterns
SMTP konfigurationsfelter (server, port, credentials)
Test-forbindelse funktionalitet
HTML skabelon editor med variabel system
Validation af alle input felter
Gem/Hent funktionalitet til database

Integration med eksisterende system:

Skal følge samme UI design som andre sektioner
Skal bruge samme farver og styling
Skal implementere samme error handling
Skal bruge samme notification system

3. CHAUFFØR VINDUE UDVIDELSE (driver_view.py)
Hvorfor:
- Der skal være en central placering hvor mailadresser kan administreres
- Det er logisk at placere dette i chauffør modulet da det relaterer direkte til chauffør administration
- Mail administration skal være tilgængelig uden at skulle gå gennem rapport systemet

Hvad skal implementeres:
- Ny "Mail Liste" knap der følger eksisterende knap design
- Pop-up vindue til mail administration der følger eksisterende vinduesstruktur
- Liste visning med samme styling som eksisterende tabeller
- Redigering/tilføjelse af mails direkte i listen
- Validering af mailadresser før gemning
- Statusindikator for hver chauffør (har mail/har ikke mail)

Integration med eksisterende system:
- Skal genbruge eksisterende DatabaseConnection pattern
- Skal følge samme vinduesstruktur som andre pop-ups
- Skal implementere samme error handling og logging
- Skal bruge samme farver og styling system

4. MAIL SYSTEM IMPLEMENTATION (mail_system.py)
Hvorfor:
- Mail funktionalitet skal være centraliseret i ét modul
- Skal kunne genbruges af forskellige dele af systemet
- Skal håndtere alle mail-relaterede operationer konsistent

Hvad skal implementeres:
- Dedikeret MailSystem klasse der håndterer:
  * SMTP forbindelse og authentication
  * Mail template processing
  * Rapport vedhæftning
  * Batch mail processing
  * Fejlhåndtering og retry logic
  * Mail queue system ved mange mails
  * Logging af alle mail operationer
- Template system der kan:
  * Indlæse HTML templates
  * Substituere variabler
  * Validere template struktur
  * Preview funktionalitet

Integration med eksisterende system:
- Skal bruge samme logging system
- Skal implementere samme error handling patterns
- Skal kunne integreres med eksisterende rapport generering
- Skal følge samme konfigurationshåndtering

5. RAPPORT VINDUE UDVIDELSE (report_view.py)
Hvorfor:
- Der skal være direkte integration mellem rapport generering og mail sending
- Brugeren skal kunne se mail status direkte i rapport interfacet
- Der skal være mulighed for både enkelt og masse-mail sending (Ved masse mail sendes alle med hver deres individuelle rapport. Sørg for loading indikation og sørg for at det er muligt at sende til alle med korrekt delay og mailadresser så vi undgår crash)

Hvad skal implementeres:
- Ny "Send Mails" knap i hovedinterfacet
- Nyt vindue til mail sending der viser:
  * Liste over kvalificerede chauffører
  * Mail status indikation (grøn/rød)
  * Mulighed for at sende enkelte mails
  * Mulighed for at sende til alle med hver deres individuelle rapport
  * Mulighed for at redigere mail inden sending
- Pop-up dialog til mail redigering der:
  * Viser eksisterende mail hvis findes
  * Tillader indtastning/redigering
  * Validerer input
  * Viser status feedback

Integration med eksisterende system:
- Skal genbruge eksisterende rapport genererings logik
- Skal følge samme UI patterns
- Skal implementere samme status feedback system
- Skal bruge samme database connection patterns

6. MAIL SKABELON SYSTEM
Hvorfor:
- Mails skal have konsistent udseende
- Skal kunne personaliseres for hver chauffør
- Skal kunne vedligeholdes centralt
- Skal kunne bruges af forskellige dele af systemet
- Du skal lave en html skabelon som er standard for alle mails med de inkluderet variabler. Denne skal kunne redigeres i indstillinger.
- Det skal være muligt at sende en test mail til en mailadresse som man har valgt i indstillinger som test mail. Denne skal implementeres på tværs af alle steder hvor man kan sende mail. Her skal man kunne trykke på en knap der hedder send test mail. Så kan jeg sende den til den mailadresse som er valgt i indstillinger og sikre det er korrekt før jeg sender den afsted til den reele chauffør.

Hvad skal implementeres:
- Template management system der:
  * Gemmer templates i databasen
  * Tillader redigering via UI
  * Håndterer variabler som:
    - Chauffør navn
    - Rapport periode
    - Firma information
    - KPI data
  * Preview system der viser hvordan mail vil se ud
  * Version control af templates
  * Backup system for templates

Integration med eksisterende system:
- Skal bruge samme database struktur
- Skal implementere samme UI patterns
- Skal genbruge eksisterende validering
- Skal følge samme error handling

7. TEST OG VALIDERING SYSTEM
Hvorfor:
- Mail sending er kritisk funktionalitet der skal testes grundigt
- Fejl i mail sending skal fanges tidligt
- System skal være robust og pålideligt

Hvad skal implementeres:
- Test system der kan:
  * Validere SMTP forbindelse
  * Teste mail templates
  * Verificere mail adresser
  * Simulere masse-mail sending
- Validering system der tjekker:
  * Mail adresse format
  * Template variabler
  * SMTP indstillinger
  * Rapport vedhæftning
- Fejlhåndtering der:
  * Logger alle fejl
  * Giver meningsfuld feedback
  * Håndterer recovery
  * Implementerer retry logic

Integration med eksisterende system:
- Skal bruge samme logging system
- Skal implementere samme error handling patterns
- Skal følge samme feedback struktur
- Skal integreres med eksisterende test setup

Dette giver en komplet oversigt over systemet med fokus på hvordan hvert komponent passer ind i den eksisterende struktur og hvorfor det er nødvendigt. Vil du have mig til at starte med implementeringen af et specifikt step?