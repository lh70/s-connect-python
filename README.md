# Bachelor Thesis
Dies wird das Software Archiv für meine Bachelor Arbeit.

## Author
Lukas Holst - lukas.holst@stud.tu-darmstadt.de

## Ziel
Es soll die Optimierung der Verarbeitung von dezentral verarbeiteten kontinuierlichen Daten getestet werden.

BISHERIGE beobachtbare Größen und Optimierungsmöglichkeiten: Rechenpower, Verteilungsgrad, Netzwerk/Verbindungsverzögerung

## Ideen
Dies wird ein Framework das auf Python und MicroPython basiert. 

Es soll einen zentral erstellten Rechenablauf dezentralisiert Verteilen können.

Anwendungszweck des Frameworks wird das Generieren/Auslesen von Sensordaten von Mikrocontrollern wie der ESP8266 oder
der ESP32 Plattform und das Auswerten dieser Sensordaten über verteilte Rechnersysteme.

Die Ziel/Endpunkte, sowie die beispielhafte Datenverarbeitung sind noch NICHT definiert.

### Die Sensoren
Erste Idee: an einem Mikrocontroller können Sensoren angeschlossen werden. 
Diese können von diesem Mikrocontroller kontinuierlich abgefragt werden.
Diese Daten können von dem Mikrocontroller dann als Datenstrom bereitgestellt werden.

Zweite Idee: die Mikrocontroller können als Rechenpower genutzt werden. 

Dadurch entstehen zwei Möglichkeiten: 
* Ein Mikrocontroller ist für einen oder mehrere Sensoren zuständig und 
liefert diese Daten so schnell wie möglich an die nächste Instanz und verbraucht dadurch seine komplette Rechenpower.
* Ein Mikrocontroller ist für einen oder mehrere Sensoren zuständig und
liefert vorgefilterte/verarbeitete Daten an die nächste Instanz weiter.
Dadurch nimmt die Sensor-Abfragegeschwindigkeit entsprechend ab, 
aber der Mikrocontroller selber wird teil des Rechenpower-Netzwerks an welches die Verarbeitung verteilt wird.

Punkt zwei inkludiert die Möglichkeit eins und ist daher aus Test- Mehrwertsicht klar zu Bevorzugen, 
aber es erhöht den Grad an Komplexität, da das Framework auf mindestens zwei Sprachen lauffähig sein muss.
Durch die Wahl von MicroPython kann dieser Aufwand reduziert werden, 
da Code für beide Sprachen lauffähig geschrieben werden kann wenn einige Unterschiede beachtet werden.

### Die Kommunikation
Die Kommunikation kann in zwei generelle Bereiche unterteilt werden. 

Einerseits muss die Verteilung des Rechenablaufs und alle Fähigkeiten des Frameworks, die Endgeräte betreffend, möglich sein.
Alle Endgeräte werden über das Netzwerk verbunden. Dadurch kann hier generell auf ein Netzwerkfähiges Protokoll gesetzt werden.

Die zweite nötige Kommunikation betrifft das Weiterleiten der Ergebnisse in der verteilten Verarbeitung.
Im Hinblick auf das dynamische Verteilen von Ressourcen und somit Rechenaufgaben und die eventuelle Möglichkeit 
die Verarbeitung auf die Mikrocontroller zu Verschieben ist hier auf eine Kommunikation zu setzen, 
welche Netzwerkfähig ist, aber auch Kommunikation innerhalb eines Gerätes ermöglicht,
ohne den Umweg über das Netzwerk gehen zu müssen.
Die Logik muss hier auf Frameworkeben erfolgen und verschiedene Möglichkeiten zur Verfügung stellen.

### Die Verarbeitung
Durch die Wahl von Python ergibt sich unter anderem das Performanceproblem, 
dass pro Endgerät erstmal nur ein Prozess und damit nur ein Prozessor-Thread genutzt wird.

Ein Prozess muss mehrere Verarbeitungsschritte durchführen können und die Kommunikation der Zwischenergebnisse
muss dementsprechend auch innerhalb eines Prozesses möglich sein.

Um das Auslastungsproblem anzugehen gibt es folgende Möglichkeiten:

* Hier könnte die Möglichkeit genutzt werden, einen Prozess als ein Endgerät zu betrachten
und somit Prozesse in Anzahl der logischen Prozssorkerne zu wählen. 
Dadurch ergigt sich der Vorteil das die Netzwerkommunikation hier zwischen den Prozessen verwendet werden kann.
Zusätzlich kann der Verteilungsmechanismus auf einen Anwendungsfall beschränkt werden,
da ein Endgerät immer aus einem Prozess besteht.

* Die andere Möglichkeit wäre das ein Endgerät einen Python Prozess mit mehreren Sub-Prozessen haben kann.
Generell kann hier dann immer noch komplett die Netzwerkkommunikationsmöglichkeit aus dem ersten Vorschlag übernommen werden.
Andererseits kann dann auch die Interprozess-Kommunikation von Python genutzt werden. Die würde die Effizienz erhöhen,
aber auch die Komplexität, da beide Kommunikationen auch auf Python-Interprozess-Ebene umgesetzt werden müssen.

Hier ist noch KEINE Entscheidung gefallen.

### Das Framework
Das Framework ist ein Programm, welches auf Python und Micropython läuft.
Die Aufgabe des Frameworks ist es einen Verarbeitungsprozess auf vorhandene Rechner-Ressourcen aufzuteilen.

Dazu sind mindestens die folgenden Entitäten nötig: 

* Ein Controller Prozess, welcher den eigentlichen Verarbeitungsprozess kennt, sowie alle anderen beteiligten Entitäten
und Steuerung der Arbeiter und Sensoren übernimmt.
* Worker, welche Teile des Verarbeitungsprozesses zugewiesen bekommen können.
* Sensoren, welche ungefiltert Daten der Sensoren liefern.

Diese Art der Steuerung setzt voraus das der Controller von jedem Endgerät erreichbar ist und
somit alle Endgeräte in einem Netzwerk sind.

### Vorschlag Domänen: 
In einem realen Netz gibt es abgeschottete Bereiche, welche nicht von allen Geräten erreichbar sind.
Um dies in diesem Framework darzustellen würde ich den Begriff der Domänen einführen. 
Eine Domäne stellt eine Gruppe an Endgeräten dar, welche direkt miteinander kommunizieren können. 
Wenn nun Worker und Sensoren miteinander oder der Controller mit den Workern und Sensoren kommunizieren soll, 
dann kann dies unter Umständen nicht direkt passieren.

Deshalb muss ein Worker auch die Weiterleitung sowohl von Steuerkommunikation als auch von Verarbeitungskommunikation
unterstützen.

Weiterhin reicht es nicht mehr das ein Endgerät sich bei dem Controller anmeldet, 
da dieser unter Umständen nicht direkt erreichbar ist. 
Vielmehr ist man hier gezwungen von der Controllerseite aus zu agieren und hier alle Endgeräte im vorhinein zu definieren,
damit mögliche Routen an die Endgeräte mitgeteilt werden können.

Zusätzlich wird die Fehlerbehebung anspruchsvoller, da ausgefallene Geräte einen zentralen Knotenpunkt darstellen können
und somit unter Umständen keine ausweichende Verarbeitung möglich ist, aber dies stellt auch einen experimentellen Mehrwert dar.


## Umsetzung
### Version 1 - Überblick
Die Umsetzung erfolgt mit MicroPython

Es wird der WIFI-fähige Mikrocontroller ESP-32-WROOM-32(D) verwendet.

Es wird das später definierte TCP-Protokoll zur Kommunikation verwendet.

Folgende Sensoren werden (erstmal) unterstützt:
* Sensor (Anschluss)
* Temperatur (Intern) !!!Eventuell auf den Testboards nicht vorhanden!!!
* Touchpad (Intern - Micropython Standard Library)
* Hall Sensor (Intern - Micropython Standard Library)
* Potentiometer (Extern - Analog - 1 Pin)
* Gyro Sensor (Extern - I2C) https://elektro.turanis.de/html/prj075/index.html
* Temperatur + Feuchtigkeit (Extern - Micropython Standard Library) https://github.com/adidax/dht11
* Ultraschall Sensor (Extern - Digital - 2 Pin - Trigger / Echo) https://create.arduino.cc/projecthub/abdularbi17/ultrasonic-sensor-hc-sr04-with-arduino-tutorial-327ff6
* CO2 Sensor (Extern - Digital - 1 Pin) https://funduino.de/nr-51-co2-messung-mit-arduino-co2-ampel

#### MicroPython https://micropython.org
Wie auf der Webseite von MicroPython gut beschrieben steht ist MicroPython eine Python Implementation für Mikrocontroller.
Dabei ist ein kleiner Teil der Python 3 Standard Library (CPython) mit kleineren aber genau beschriebenen Abänderungen vorhanden.
Dies ermöglicht es CPython und Mikropython kompatiblen Code zu schreiben.
Um MicroPython zum laufen zu bekommen muss die Sprache und damit der Interpreter auf dem Mikrocontroller installiert werden.
Es wird dann ein Interface zur Verfügung gestellt um mit der Installation zu interagieren. 
Diese ist an der normalen Python Interpreter Shell orientiert, 
bietet aber zusätzlich unter Anderem die Möglichkeit Programme an den Mikrocontroller zu überspielen und auszuführen.

#### Framework - MicroPython - Version 1
Grundsätzlich wird das Framework Python und MikroPython kompatibel entworfen. 
Dies soll im späteren Verlauf ermöglichen das das Framework auf allen Endgeräten gleiche Funktionalität bereitstellt.

Die erste Priorität wird aber sein die Sensordaten auf den Mikrocontrollern auslesen zu können und über das Netzwerk an
ein Endgerät zu schicken welches sich mit dem Mikrocontroller verbindet.

Dazu werden die folgenden Komponenten zuerst entwickelt: Die Python-Repräsentation der Sensoren, 
die Python-Repräsentation der Daten, das Netzwerkkommunikationsmodel, ein einfacher Testclient und Testserver.

#### Python-Repräsentation der Sensoren
Die Sensoren bekommen ein eigenes modul, welches sensors genannt wird. 

Aufgrund des knappen Speichers auf Mikrocontrollern wird jeder Sensor ein eigenes Sub-Modul bekommen,
welches eine Klasse enthält, die die Sensorfunktionalität bereitstellt. 

Das Sub-Modul und die Klasse bekommen den gleichen Namen, nach Python Konvention.
(Modul startet klein, Klasse startet groß)

Dadurch wird verhindert das ein Mikrocontroller alle Sensor-Klassen in einem Modul importiert, 
obwohl meistens nur eine Sensorklasse verwendet wird.

Jede Sensorklasse stellt einen indiviudellen Konstruktor und eine universelle get() Methode bereit. 
Über diese Methode wird ein aktueller Sensorwert ausgelesen und zurückgegeben. 
Für die meisten Sensoren sollte dies ausreichend sein, da der Auslesevorgang sehr in wenigen Mikrosekunden stattfindet.
Auch I2C wird in diesem Zusammenhang als schnell genug angesehen. 

Es gibt allerdings Sensoren mit langen und/oder variablen Antwortzeiten. 
Dies betrifft zum Beispiel den Ultraschall Sensor und den CO2 Sensor.
Bei diesen Sensoren kann davon ausgegangen werden das die Antwortzeit 'länger' dauert und 
eine synchrone Abfrage den Mikrocontroller zu stark ausbremsen würde.
Deshalb wird hier auf Hardware-Interrupts zurückgegriffen.
Diese werden mit dem Initialisieren der Klasse aktiviert und sorgen für eine korrekte Abfrage der Sensorwerte. 
Der aktuelle Sensorwert wird in eine atomare Variable gespeichert.

Hier muss geschaut werden welche Größen nötig sind. Integer, Byte, Boolean und Arrays dieser sind möglich.
Jedoch dürfen Integer die Größen 2\*\*30 -1 und -2\*\*30 nicht überschreiten, 
da Python größere Integer (Long Integer) zwar unterstützt, aber für diese eine Objekt-Repräsentation wählt und 
die Objekt-Allokation ist in Hardware-Interrupts deaktiviert.

Grundsätzlich ist es möglich micropython.schedule() zu verwenden, was einen Software-Interrupt darstellt, 
welcher dann jeden Python-Code ausführen kann, jedoch gibt es zwei Gründe dagegen: 
* Erstens, den aktuellen Wert zu bestimmen und in eine vor-allokierte Variable zu speichern
ist eine einfache Aufgabe die ohne Objekt-Allokation zu machen sein sollte.
* Zweitens, Software-Interrupts haben keine zeitliche Garantie, 
sodass die oft zeitlich kritische Abfrage und Berechnung der Sensorwerte ungenau wird.

Die eigentliche Aufgabe von Software-Interrupts ist die nachträgliche Verarbeitung von mit Hardware-Interrupts aggregierten Sensorwerten.
Da dies aber in diesem Framework von der Main-Loop übernommen wird kann komplett auf Software-Interrupts verzichtet werden.

Sensoren mit Hardware-Interrupts liefern also mit ihrer get() Methode den aktuellsten Wert zurück, 
der durch den letzten Interrupt-Handler geschrieben wurde.

#### Python-Repräsentation der Daten
Damit die Sensor-Werte auch weiterverarbeitet werden können müssen sie in ein universelles Format gebracht werden.
In dem Netzwerkabschnitt wird die Daten-Repräsentation in Form eines JSON Arrays gewählt. 
In der nächsten Version des Frameworks soll jedoch auch die Verarbeitung intern erfolgen können und somit muss eine
Repräsentation gewählt werden, welche für die Methodenübergänge möglichst effizient ist.

An dieser Stelle wird für die zweite Version des Frameworks schon vorgegriffen. 
Das Ziel wird es sein Verarbeitungsschritte beliebig hintereinander zu hängen und 
eigentlich soll jeder Wert die komplette Verarbeitungskette einzeln durchlaufen. 
Somit sollen lokal alle Schritte direkt aneinander gehängt werden, 
aber verteilte Rechner haben das Problem das das Netzwerk keine Garantie liefert, wann gesendeter Wert ankommt.
Deshalb werden hier die in der Netzwerkkommunikation beschriebenen zeitlichen Datenframes verwendet.

Die Kontrolle darüber wann auf das Netzwerk verteilt wird und welche Zeit-Frames gewählt werden wird Aufgabe 
des zukünftigen Kontrollers werden.

Für die aktuelle Version ist es also ausreichend wenn die einzelnen Werte als Methoden-Rückgabe/-Eingabe weiterverarbeitet werden können.
Durch das dynamische Typensystem in Python ist dies ohne Probleme möglich. 

Am Ende der lokalen Kette steht dann eine Klasse welche beliebige (serialisierbare) Eingabe-Werte/-Objekte in Time-Frames aggregiert
und diese and das Netzwerk-Modul weitergibt.

#### Das Netzwerkkommunikationsmodel
Verwendete Module: 
* Standard (MikroPython Standard): socket (usocket), struct (usocket), json (ujson)


Verwendete Module für symmetrische Verschlüsselung (nur eventuell):
* Python: 
    * Standard: cryptography.fernet
* Mikropython:
    * Standard: ucryptolib.aes, ubinascii, uhashlib, utime, uos, ustruct
    * Selbst implementiert: Fernet nach https://github.com/oz123/python-fernet/blob/master/fernet.py mit den Standard Libraries

Verwendete Module für asymmetrische Verschlüsselung (nur eventuell):
TODO

Rssourcen:
* https://hwwong168.wordpress.com/2019/09/25/esp32-micropython-implementation-of-cryptographic/
* https://pypi.org/project/rsa/

Der Stack:
* TCP Socket Verbindung
* Jede Nachricht besteht aus Länge + Nutzdaten. Die Länge hat das struct Format '!I', also ein unsigned Integer in big-endian.
* (eventuell) Die Nutzdaten sind symmetrisch verschlüsselt mit AES
* Die Nutzdaten sind ein UTF-8 kodierter String.
* Der String enthält ein JSON-Object oder einen JSON-Array
    * Handelt es sich um ein JSON-Object ist dies eine Steuernachricht
    * Handelt es sich um einen JSON-Array ist dies eine Datennachricht

Der Handshake:
* Initial mit Verschlüsselung:
    * der Client startet die Verbindung
    * der Client schickt einen timestamp und ID signiert mit seinem Public Key an den Server
    * der Server überprüft die Signatur und schickt einen symmetrischen Schlüssel verschlüsselt mit dem Public Key an den Client
    * der Client und der Server initialisiern Fernet und kommunizieren ab jetzt nur noch verschlüsselt
* der client schickt ein JSON-Object mit einer Sensor Datenanfrage
* der server liefert JSON-Arrays mit den Daten bis der Socket geschlossen wird

Das JSON-Object:
* Die Steuerbefehle sollen menschenlesbar sein. Somit sind hier die Geschwindigkeit und Bandbreitensparsamkeit nicht entscheidend.
Dies ergibt sich auch dadurch das der effiziente Teil der Kommunikation auf die JSON-Arrays mit den Rechendaten geschoben wird.
* Aufbau:
    * (KEY: DATA)
    * data-request: JSON-Object::
        * sensor: "Sensor-Kind" -one-of-> (temperature, touchpad, poti, gyro, dht11)
        * time-frame: "Integer" -> send values every x milliseconds 
            * (0 or key not specified is wildcard for send every value individually -> probably slow)
        * values-per-time-frame: "Integer" -> gather x timely evenly spaced values in a time-frame
            * (time-frame has precedence over value-count, which means if the timeframe is expired, all gathered values will be send, 
            even if the value-count is not met) 
            * (0 or key not specified is wildcard for send as much values as possible per time-frame)

Der JSON-Array:
* Hier ist Geschwindigkeit wichtig. Alle Werte eines Timeframes werden in einem Array verschickt. 
Das bedeutet es dürfen nur primitive oder serialisierbare Datentypen als Ergebnisse versendet werden.
Als serialisierbar zählen Klassen welche direkt vom json-Modul als serialisierbar erkannt werden. 
Somit sind die einzig komplexen zugelassenen Datentypen dict und list.
* Aufbau:
    * JSON-ARRAY::
        * -list-of-> "Result-Object"

#### Testclient + Testserver
TODO

### Version 2 - FUTURE
Serialisieren von Funktionen:
* https://medium.com/@emlynoregan/serialising-all-the-functions-in-python-cd880a63b591
* https://stackoverflow.com/questions/1253528/is-there-an-easy-way-to-pickle-a-python-function-or-otherwise-serialize-its-cod
