# Guide til Opsætning af Mail System

## 1. Google Konto Forberedelse

### Aktivér 2-trins verificering
1. Gå til [Google Konto Sikkerhed](https://myaccount.google.com/security)
2. Find "2-trins verificering" under "Sådan logger du ind på Google"
3. Klik på "Kom i gang"
4. Følg vejledningen for at aktivere 2-trins verificering

### Opret App-password
1. Gå tilbage til [Google Konto Sikkerhed](https://myaccount.google.com/security)
2. Find "App-adgangskoder" under "2-trins verificering"
3. Klik på "Opret app-adgangskode"
4. Under "Vælg app" vælg "Andre (brugerdefineret navn)"
5. Indtast "RIO Rapport System" som navn
6. Klik på "OPRET"
7. Google vil nu vise et 16-tegn password - GEM DETTE PASSWORD!

## 2. Program Opsætning

### Indtast Mail Indstillinger
1. Åbn RIO programmet
2. Klik på "Indstillinger" i hovedmenuen
3. Gå til fanen "Mail Indstillinger"
4. Udfyld følgende:
   - SMTP Server: `smtp.gmail.com`
   - SMTP Port: `587`
   - Email: Din Gmail-adresse
   - Password: Det 16-tegn app-password du fik fra Google

### Test Forbindelsen
1. Klik på "Test Forbindelse" knappen
2. Hvis alt er korrekt, vil du se en "Forbindelse oprettet succesfuldt" besked
3. Hvis der er fejl, tjek at:
   - Din Gmail-adresse er korrekt
   - App-passwordet er indtastet korrekt (alle 16 tegn)
   - Du har internetforbindelse

## 3. Fejlfinding

### Almindelige Problemer
1. **"Kunne ikke forbinde til SMTP server"**
   - Tjek din internetforbindelse
   - Verificer at SMTP server og port er korrekte
   - Prøv at deaktivere firewall midlertidigt

2. **"Authentication failed"**
   - Dobbelttjek din Gmail-adresse
   - Sørg for at bruge app-password, IKKE dit normale Google password
   - Prøv at generere et nyt app-password

3. **"Mail blev ikke sendt"**
   - Tjek modtagerens email-adresse
   - Se efter i modtagerens spam-mappe
   - Tjek programloggen for detaljerede fejlbeskeder

## 4. Begrænsninger

### Gmail Begrænsninger
- Maksimum 2000 mails per dag
- Maksimum 25 MB per mail (inkl. vedhæftninger)
- Kræver stabil internetforbindelse

### Sikkerhedsanbefalinger
- Skift app-password regelmæssigt
- Brug kun programmet på sikre netværk
- Del aldrig app-passwords med andre

## 5. Support

Hvis du oplever problemer med opsætningen eller har spørgsmål, kontakt support på:
- Email: support@example.com
- Telefon: +45 XX XX XX XX 