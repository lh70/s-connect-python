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

Anwendungszweck des Frameworks wird das Generieren/Auslesen von Sensordaten von Mikrocontrollern wie der Arduino, 
ESP8266 oder der ESP32 Plattform und das Auswerten dieser Sensordaten über verteilte Rechnersysteme.

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
Das Framework ist ein Programm, welches auf Python und eventuell auch auf C läuft (vereinfacht).
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
### Revision 1 - Überblick
Die Umsetzung erfolgt mit MicroPython

Es wird der WIFI-fähige Mikrocontroller ESP-32-WROOM-32(D) verwendet.

Es wird das später definierte TCP-Protokoll zur Kommunikation verwendet.

Folgende Sensoren werden (erstmal) unterstützt:
* Sensor (Anschluss)
* Temperatur (Intern) !!!Eventuell auf den Testboards nicht vorhanden!!!
* Touchpad (Intern - Micropython Standard Library)
* Potentiometer (Extern - Analog - 1 Pin)
* GyroSensor (Extern - I2C) https://elektro.turanis.de/html/prj075/index.html
* Temperatur + Feuchtigkeit (Extern - Micropython Standard Library) https://github.com/adidax/dht11

#### MicroPython https://micropython.org
Wie auf der Webseite von MicroPython gut beschrieben steht ist MicroPython eine Python Implementation für Mikrocontroller.
Dabei ist ein kleiner Teil der Python 3 Standard Library (CPython) mit kleineren aber genau beschriebenen Abänderungen vorhanden.
Dies ermöglicht es CPython und Mikropython kompatiblen Code zu schreiben.
Um MicroPython zum laufen zu bekommen muss die Sprache und damit der Interpreter auf dem Mikrocontroller installiert werden.
Es wird dann ein Interface zur Verfügung gestellt um mit der Installation zu interagieren. 
Diese ist an der normalen Python Interpreter Shell orientiert, 
bietet aber zusätzlich unter Anderem die Möglichkeit Programme an den Mikrocontroller zu überspielen und auszuführen.

#### Framework - MicroPython - Revision 1
Grundsätzlich wird das Framework Python und MikroPython kompatibel entworfen. 
Dies soll im späteren Verlauf ermöglichen das das Framework auf allen Endgeräten gleiche Funktionalität bereitstellt.

Die erste Priorität wird aber sein die Sensordaten auf den Mikrocontrollern auslesen zu können und über das Netzwerk an
ein Endgerät zu schicken welches sich mit dem Mikrocontroller verbindet.

Dazu werden die folgenden Komponenten zuerst entwickelt: Die Python-Repräsentation der Sensoren, 
die Python-Repräsentation der Daten, das Netzwerkkommunikationsmodel, ein einfacher Testclient und Testserver.

#### Python-Repräsentation der Sensoren
TODO

#### Python-Repräsentation der Daten
TODO

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
    * der Client schickt einen timestamp und ID signiert mit seinem public key an den Server
    * der Server überprüft die Signatur und schickt einen symmetrischen Schlüssel verschlüsselt mit dem Public Key an den Client
    * der Client und der Server initialisiern Fernet und kommunizieren ab jetzt noch mit verschlüsselt
* der client schickt ein JSON-Object mit einer Sensor Datenanfrage
* der server liefert JSON-Arrays mit den Daten bis der Socket geschlossen wird

#### Testclient + Testserver
TODO
