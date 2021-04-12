# Bachelor Thesis
Dies wird das Software Archiv für meine Bachelor Arbeit.

## Author
Lukas Holst - lukas.holst@stud.tu-darmstadt.de

## Ziel
Es soll die Optimierung der Verarbeitung von dezentral verarbeiteten kontinuierlichen Daten getestet werden.

BISHERIGE beobachtbare Größen und Optimierungsmöglichkeiten: Rechenpower, Verteilungsgrad, Netzwerk/Verbindungsverzögerung

## Ideen
Dies wird ein Framework das auf Python und C basiert. 

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
aber die Mikrocontroller selber wird teil des Rechenpower-Netzwerks an welches die Verarbeitung verteilt wird.

Punkt zwei inkludiert die Möglichkeit eins und ist daher aus Test- Mehrwertsicht klar zu Bevorzugen, 
aber es erhöht den Grad an Komplexität, da das Framework auf zwei Programmiersprachen lauffähig gemacht werden muss.
Der Standard, nach welchem die Verarbeitung geschrieben wird und die Verteilung an sich muss sprachenunabhängig sein.
HIER ist noch KEINE Entscheidung gefallen.

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
