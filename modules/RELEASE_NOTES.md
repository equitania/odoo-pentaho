### 26.06.2017
### pentaho_reports, 0.8
#### CHG
- composition mode wird jetzt dynamisch gesetzt, siehe Beschreibung im Quellcode (Jira-Issue OBA-28)

### 18.05.2017
### pentaho_reports, 0.7
#### CHG
- Hilfen herausgenommen

### 18.05.2017
### pentaho_reports, 0.6
#### FIX
- Email-Versand unter Kunden wieder möglich.

### 17.05.2017
### pentaho_reports, 0.5
#### FIX
- Model im Report wird dynamisch gezogen, vorher nur sale.order

### 09.05.2017
### pentaho_reports, 0.4
#### CHG/FIX
-  Workaround bezüglich Ticket 4067 durchgeführt. Es wird beim Template-Wechsel kein onchange-Ereignis mehr ausgelöst, sondern das Wechseln des Templates muss manuell per Button Klick getätigt werden.

### 11.04.2016
### pentaho_reports, 0.2
#### FIX
- Pentaho war object: True gesetzt. Im Standard ist object aber nicht (nicht mehr?) vorhanden. object: True wurde nun in der ui.py (pentaho_reports) auskommentiert