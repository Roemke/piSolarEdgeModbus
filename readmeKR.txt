eigene Readme, Bastelstatus, läuft aber bei mir

urspruengliches Projekt dürfte von https://pypi.org/project/solaredge-modbus/
sein? https://github.com/nmakel/solaredge_modbus

hatte ich mal angefangen, aber nicht dokumentiert und ich habe keine Ahnung
mehr, was genau ich vor hatte. Ich glaube ich wollte mal in der influxdb
speichern, aber eigentlich brauche ich die Daten ja nicht. 

Für die Steuerung meiner Batterie / einspeisung sollte ich aber die Daten,
die ich vom Inverter abfrage zur Verfügung stellen. Dann brauche ich kein
modbus auf dem ESP.

Kopiere mal influx2WebServ.py, ich glaube dass sollte die Daten mal
als Webservice darstellen, ich reduziere es, auf eine Anfrage, 
die die Werte als json liefert. influx war auf dem älteren pi ein problem
wenn ich es richtig in Erinnerung habe. 

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

Nochmal claude darauf los gelassen, er behauptet: 
Dein /data API-Response:
json

{"power":28.17, "power_ac":1132.7, "power_bat":-78.0, "power_dc":1150.0, "soe":23.33}

Feld		Quelle	Bedeutung
power/Grid	Meter	Netzbezug/Einspeisung (positiv = Einspeisung, negativ = Bezug)
power_ac	Inverter	Wechselrichter-Ausgang AC
power_dc	Inverter	Solar-Eingang DC von den Panels
power_bat	Battery	Batterie (negativ = entlädt, positiv = lädt)
soe		Battery	SolarEdge-Akku Ladestand %

Hausverbrauch = power_ac - power (also Wechselrichter + was vom Netz dazu kommt)

power_ac ist der Gesamt-Output des SolarEdge-Wechselrichters, also Solar + Speicher kombiniert ins Haus. 
Der Wechselrichter macht da keinen Unterschied, er liefert einfach was gebraucht wird aus beiden Quellen.

power_dc  = 1150W   → kommt von den Panels (DC)
power_bat = -78W    → Speicher gibt 78W dazu (DC)
power_ac  = 1132W   → Wechselrichter liefert das ins Haus (AC, mit Wandlungsverlusten)
power     = 28W     → minimaler Netzbezug, Haus braucht etwas mehr als der Wechselrichter liefert

Hausverbrauch wäre dann: 1132 - 28 = 1104W

Und die ~18W Differenz (1150 + 78 - 1132) sind die Wandlungsverluste des Wechselrichters — das passt gut.
