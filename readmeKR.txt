urspruengliches Projekt dürfte von https://pypi.org/project/solaredge-modbus/
sein? https://github.com/nmakel/solaredge_modbus

hatte ich mal angefangen, aber nicht dokumentiert und ich habe keine Ahnung
mehr, was genau ich vor hatte. Ich glaube ich wollte mal in der influxdb
speichern, aber eigentlich brauche ich die Daten ja nicht. 

Für die Steuerung meiner Batterie / einspeisung sollte ich aber die Daten,
die ich vom Inverter abfrage zur Verfügung stellen. 

Kopiere mal influx2WebServ.py, ich glaube dass sollte die Daten mal
als Webservice darstellen, ich reduziere es, auf eine Anfrage, 
die die Werte als json liefert. 

Neue Datei (reduziert) ist solar.py

dort auch einen anderen webserver, waitress, da Flask wohl nicht zwingend
stabil ist, sagt doku und warning 
pip install waitress nötig

interpretation der daten: 
curl 192.168.0.203:8090/data (curl 192.168.0.203:8090/dataFull liefert mehr)
{"power":1068.9,"power_ac":2833.3,"power_bat":0.0,"power_dc":2876.5,"soe":100.0}
power geht in das externe Netz (Anbieter)
power_ac geht in das interne Netz
power_dc dürfte das sein, was ankommt
power_bat: geht in die Batterie (+ vermute ich, noch nicht genau gecheckt)
soe: prozentualer Stannd Batterie


