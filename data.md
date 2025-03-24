# Kørselsdata - Detaljeret Beskrivelse

Dette dokument giver en detaljeret forklaring af de data, der fremgår i databaserne. Filen indeholder omfattende kørselsdata for chauffører, herunder informationer om køretøjer, brændstofforbrug, køreadfærd og meget mere.

## Filformat og Struktur

- **Antal rækker**: 34
- **Antal kolonner**: 59

## Detaljeret Beskrivelse af Kolonner

### 1. Chauffør
Indeholder navnet på chaufføren.

**Eksempel**: `Andersen, Kent René`

### 2. Køretøjer
Angiver antallet af køretøjer, som chaufføren har ført i den registrerede periode.

**Eksempel**: `2`

### 3. Forudseende kørsel (vurdering) [%]
En procentvis vurdering af, hvor forudseende chaufførens kørestil er, baseret på forskellige parametre. Højere værdi indikerer mere forudseende kørsel.

**Eksempel**: `25,7` (bemærk at komma bruges som decimalseparator)

### 4. Forudseende kørsel uden kørehastighedsregulering [%]
En procentvis vurdering af chaufførens forudseende kørsel, når kørehastighedsregulering (fartpilot) ikke er aktiveret.

**Eksempel**: `34,9`

### 5. Fra
Startdatoen og -tidspunktet for den registrerede periode.

**Format**: `DD-MM-YYYY HH:MM`  
**Eksempel**: `01-02-2025 06:45`

### 6. Til
Slutdatoen og -tidspunktet for den registrerede periode.

**Format**: `DD-MM-YYYY HH:MM`  
**Eksempel**: `28-02-2025 00:00`

### 7. Ø Forbrug [l/100km]
Gennemsnitligt brændstofforbrug målt i liter pr. 100 kilometer.

**Eksempel**: `25,7`

### 8. Ø Forbrug ved kørsel [l/100km]
Gennemsnitligt brændstofforbrug under aktiv kørsel (eksklusiv tomgang) målt i liter pr. 100 kilometer.

**Eksempel**: `25,6`

### 9. Ø Forbrug ved tomgang [l/t]
Gennemsnitligt brændstofforbrug ved tomgang målt i liter pr. time.

**Eksempel**: `2,4`

### 10. Ø Rækkevidde ved forbrug [km/l]
Gennemsnitlig rækkevidde baseret på faktisk forbrug målt i kilometer pr. liter.

**Eksempel**: `3,9`

### 11. Forbrug [l]
Totalt brændstofforbrug i perioden målt i liter.

**Eksempel**: `2233,5`

### 12. Ø totalvægt [t]
Gennemsnitlig totalvægt af køretøjet under kørsel målt i ton.

**Eksempel**: `27,4`

### 13. Kørestrækning [km]
Den samlede kørestrækning i perioden målt i kilometer.

**Eksempel**: `8681,8`

### 14. Effektivitet [l/t/100km]
Et effektivitetsmål som kombinerer forbrug, vægt og distance - målt i liter pr. ton pr. 100 kilometer.

**Eksempel**: `0,9`

### 15. Motordriftstid [hh:mm:ss]
Den samlede tid, hvor motoren har været i drift.

**Format**: `Timer:Minutter:Sekunder`  
**Eksempel**: `132:46:04`

### 16. Køretid [hh:mm:ss]
Den samlede tid, hvor køretøjet faktisk har været i bevægelse.

**Format**: `Timer:Minutter:Sekunder`  
**Eksempel**: `127:06:01`

### 17. Tomgang / stilstandstid [hh:mm:ss]
Den samlede tid, hvor motoren har været i gang, men køretøjet har stået stille.

**Format**: `Timer:Minutter:Sekunder`  
**Eksempel**: `05:40:03`

### 18. Ø-hastighed [km/h]
Gennemsnitshastighed under kørsel målt i kilometer pr. time.

**Eksempel**: `68,3`

### 19. CO₂-emission [kg]
Den estimerede CO₂-udledning i perioden målt i kilogram.

**Eksempel**: `5851,8`

### 20. Vurdering af påløbsdrift [%]
En procentvis vurdering af chaufførens udnyttelse af påløbsdrift (hvor køretøjet kører uden aktiv trækkraft/motorbremsning).

**Eksempel**: `50`

### 21. Aktiv påløbsdrift (km) [km]
Den samlede distance tilbagelagt med aktiv påløbsdrift målt i kilometer.

**Eksempel**: `257,7`

### 22. Varigheden af aktiv påløbsdrift [hh:mm:ss]
Den samlede tid tilbragt i aktiv påløbsdrift.

**Format**: `Timer:Minutter:Sekunder`  
**Eksempel**: `04:07:33`

### 23. Aktivt skubbedrev (stk.)
Antal gange, hvor aktivt skubbedrev (en form for påløbsdrift) er blevet anvendt.

**Eksempel**: `7007`

### 24. Afstand i påløbsdrift [km]
Den samlede distance tilbagelagt i påløbsdrift målt i kilometer.

**Eksempel**: `204,1`

### 25. Varighed af påløbsdrift med kørehastighedsregulering [hh:mm:ss]
Den samlede tid tilbragt i påløbsdrift, mens kørehastighedsregulering (fartpilot) var aktiveret.

**Format**: `Timer:Minutter:Sekunder`  
**Eksempel**: `02:23:25`

### 26. Antal faser i påløbsdrift
Antal separate episoder af påløbsdrift i perioden.

**Eksempel**: `2888`

### 27. Gaspedal-vurdering [%]
En procentvis vurdering af chaufførens brug af gaspedalen, hvor højere værdi indikerer mere økonomisk brug.

**Eksempel**: `20`

### 28. Kickdown (km) [km]
Den samlede distance tilbagelagt med kickdown (fuld acceleration) aktiveret målt i kilometer.

**Eksempel**: `13,7`

### 29. Varighed af brugen af kickdown [hh:mm:ss]
Den samlede tid, hvor kickdown har været aktiveret.

**Format**: `Timer:Minutter:Sekunder`  
**Eksempel**: `00:09:21`

### 30. Kickdown (stk.)
Antal gange, hvor kickdown er blevet aktiveret.

**Eksempel**: `13`

### 31. Tilbagelagt afstand ved aktivering af gaspedal og tilkoblet kørehastighedsregulering [km]
Den samlede distance, hvor chaufføren har aktiveret gaspedalen, mens kørehastighedsregulering samtidig var tilkoblet, målt i kilometer.

**Eksempel**: `224,7`

### 32. Varigheden af aktivering af gaspedal og tilkoblet kørehastighedsregulering [hh:mm:ss]
Den samlede tid, hvor gaspedalen har været aktiveret samtidig med kørehastighedsregulering.

**Format**: `Timer:Minutter:Sekunder`  
**Eksempel**: `02:34:52`

### 33. Antal aktiveringer af gaspedal ved kørehastighedsregulering
Antal gange, hvor gaspedalen er blevet aktiveret, mens kørehastighedsregulering var tilkoblet.

**Eksempel**: `762`

### 34. Forbrug uden kørehastighedsregulering [l/100km]
Gennemsnitligt brændstofforbrug, når kørehastighedsregulering ikke er aktiveret, målt i liter pr. 100 kilometer.

**Eksempel**: `27,6`

### 35. Forbrug med kørehastighedsregulering [l/100km]
Gennemsnitligt brændstofforbrug, når kørehastighedsregulering er aktiveret, målt i liter pr. 100 kilometer.

**Eksempel**: `24`

### 36. Vurdering af bremseadfærd [%]
En procentvis vurdering af chaufførens bremseadfærd, hvor højere værdi indikerer mere effektiv bremsning.

**Eksempel**: `15`

### 37. Driftsbremse (km) [km]
Den samlede distance, hvor driftsbremsen har været aktiveret, målt i kilometer.

**Eksempel**: `384,2`

### 38. Varighed driftsbremse [hh:mm:ss]
Den samlede tid, hvor driftsbremsen har været aktiveret.

**Format**: `Timer:Minutter:Sekunder`  
**Eksempel**: `10:23:29`

### 39. Driftsbremse (stk.)
Antal gange, hvor driftsbremsen er blevet aktiveret.

**Eksempel**: `3742`

### 40. Afstand motorbremse [km]
Den samlede distance, hvor motorbremsen har været aktiveret, målt i kilometer.

**Eksempel**: `154,5`

### 41. Varighed af motorbremse [hh:mm:ss]
Den samlede tid, hvor motorbremsen har været aktiveret.

**Format**: `Timer:Minutter:Sekunder`  
**Eksempel**: `02:10:07`

### 42. Motorbremse (tæller)
Antal gange, hvor motorbremsen er blevet aktiveret.

**Eksempel**: `3026`

### 43. Afstand retarder [km]
Den samlede distance, hvor retarder (en form for hjælpebremse) har været aktiveret, målt i kilometer.

**Bemærk**: Kan være tom, hvis ikke relevant for køretøjet.

### 44. Varighed retarder [hh:mm:ss]
Den samlede tid, hvor retarder har været aktiveret.

**Format**: `Timer:Minutter:Sekunder`  
**Bemærk**: Kan være tom, hvis ikke relevant for køretøjet.

### 45. Retarder (stk.)
Antal gange, hvor retarder er blevet aktiveret.

**Bemærk**: Kan være tom, hvis ikke relevant for køretøjet.

### 46. Nødbremseassistent (tæller)
Antal gange, hvor nødbremseassistenten er blevet aktiveret.

**Eksempel**: `0`

### 47. Vurdering af brugen af kørehastighedsregulering [%]
En procentvis vurdering af chaufførens brug af kørehastighedsregulering, hvor højere værdi indikerer mere effektiv brug.

**Eksempel**: `12`

### 48. Afstand med kørehastighedsregulering (> 50 km/h) [km]
Den samlede distance tilbagelagt med kørehastighedsregulering aktiveret ved hastigheder over 50 km/t, målt i kilometer.

**Eksempel**: `5929,3`

### 49. Varighed af kørehastighedsregulering (> 50 km/h) [hh:mm:ss]
Den samlede tid tilbragt med kørehastighedsregulering aktiveret ved hastigheder over 50 km/t.

**Format**: `Timer:Minutter:Sekunder`  
**Eksempel**: `69:21:52`

### 50. Afstand > 50 km/h uden kørehastighedsregulering [km]
Den samlede distance tilbagelagt ved hastigheder over 50 km/t uden kørehastighedsregulering, målt i kilometer.

**Eksempel**: `1803,5`

### 51. Varighed uden kørehastighedsregulering > 50 km/h [hh:mm:ss]
Den samlede tid tilbragt ved hastigheder over 50 km/t uden kørehastighedsregulering.

**Format**: `Timer:Minutter:Sekunder`  
**Eksempel**: `25:30:18`

### 52. Gryde. afstand med fartpilot (> 50 km/h) [km]
Den samlede distance tilbagelagt med fartpilot aktiveret ved hastigheder over 50 km/t (Gryde. er formentlig en forkortelse), målt i kilometer.

**Eksempel**: `7732,8`

### 53. Vurdering overspeed
En vurdering af overskridelse af hastighedsgrænser, hvor 0 indikerer ingen problemer.

**Eksempel**: `0`

### 54. Overspeed (km uden påløbsdrift) [km]
Den samlede distance tilbagelagt med overskridelse af hastighedsgrænser uden påløbsdrift, målt i kilometer.

**Eksempel**: `3030`

### 55. Samlet anvendelse
En kvalitativ beskrivelse af køretøjets samlede anvendelse i perioden.

**Eksempel**: `let`

### 56. Indsatsdage
Antallet af dage, hvor køretøjet har været i brug, ud af det samlede antal dage i perioden.

**Format**: `[Brugte dage] / [Samlede dage]`  
**Eksempel**: `21 / 28`

### 57. Forbrug [kWh]
Det samlede energiforbrug målt i kilowatt-timer. Typisk relevant for el- eller hybridkøretøjer.

**Bemærk**: Kan være tom, hvis ikke relevant for køretøjet.

### 58. Ø Forbrug ved kørsel [kWh/km]
Gennemsnitligt energiforbrug under kørsel målt i kilowatt-timer pr. kilometer.

**Bemærk**: Kan være tom, hvis ikke relevant for køretøjet.

### 59. Gns. stilstandsforbrug [kWh/km]
Gennemsnitligt energiforbrug ved stilstand målt i kilowatt-timer pr. kilometer.

**Bemærk**: Kan være tom, hvis ikke relevant for køretøjet.

### 60. Ø Rækkevidde ved forbrug [km/kWh]
Gennemsnitlig rækkevidde baseret på faktisk energiforbrug målt i kilometer pr. kilowatt-time.

**Bemærk**: Kan være tom, hvis ikke relevant for køretøjet.

### 61. Ø Forbrug [kWh/km]
Gennemsnitligt energiforbrug målt i kilowatt-timer pr. kilometer.

**Bemærk**: Kan være tom, hvis ikke relevant for køretøjet.

### 62. Energieffektivitet [kWh/t/km]
Et effektivitetsmål for energiforbrug som kombinerer energi, vægt og distance - målt i kilowatt-timer pr. ton pr. kilometer.

**Bemærk**: Kan være tom, hvis ikke relevant for køretøjet.

## Sammenfatning

Datasættet giver et detaljeret overblik over kørselsadfærd og -effektivitet for forskellige chauffører. Det inkluderer omfattende information om brændstofforbrug, kørevaner, brug af forskellige kørefunktioner (som fartpilot og bremser), og energieffektivitet. Disse data kan anvendes til at analysere og forbedre chaufførers kørevaner, optimere brændstofforbrug og reducere miljøpåvirkning fra køretøjsflåden.