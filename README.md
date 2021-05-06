# Bachelor Thesis
This is the software archive for my bachelor thesis.

## Author
Lukas Holst - lukas.holst@stud.tu-darmstadt.de

## Goal
This project will test the optimisation of decentralized generation and processing of continuous data.

My gathered watchable variables are currently: processing-power, decentralization, network delay

## Idea
This Framework will be made to work on Python and MicroPython.

The idea is to have a central control unit where a processing sequence is defined.
This will then be executed decentralized on a network of computers.

The actual use-case will be the generation and further processing of sensory data.
For this I will use the ESP32 platform, but in theory the framework should work on any MicroPython ready platform.
To open up the further processing to more platforms the framework (except the sensor-data gathering) will be 
fully CPython compliant.

The final destinations of this processing are not yet defined.

### The Sensors
First idea: we can connect multiple sensors to one microcontroller.
These sensors can then be continuously read by the microcontroller.
This data can then be continuously fed as a data-stream to other computers.

Second idea: the microcontrollers can also be used as computing power.

We therefore get two possible scenarios:
* One microcontroller has one or more sensors connected to it and delivers
as much sensory data as possible as fast as possible to the next computing instance.
* One microcontroller has one or more sensors connected to it and delivers
filtered/computed data to the next instance. This can reduce the polling speed but can also reduce network load.

When reviewing scenario two we can see that the microcontroller will be part of the computing network and
therefore open up the possibility for more and variable testing. It will come at the cost of complexity,
as the framework must be fully micropython compliant. The advantage after will be the uniform framework,
where every device can do everything (except sensor polling of course). 
The final advantage which will diminish the argument of design overhead is that scenario one can be fully tested when
using a scenario two compliant framework.

I will therefore go with scenario two.

### The Communication
The communication will be divided into two different areas of interest.

On the one side the decentralization of processing requires a control and feedback communication that reaches all
devices. Because we look at this from a device standpoint, the protocol can be network based.

The other side of communication is the transfer of sensory and computed sensory data throughout the network.
Because it will be possible to have multiple computing steps on a single device we must pursue a solution that works 
on networks and on the devices itself. The control and data delivery logic for this must be done on the 
framework layer and must at least support the two discussed scenarios.

### The Processing
With the choice of Python we get at least one performance problem,
because every device will just use one logical processing thread.

One requirement I defined earlier was that one device must possibly do multiple processing steps and therefore
the sensory data flow must also happen inside individual devices.

There are two possible solutions to use more than one processing thread
* The first solution is to consider one processing thread as one device. In this scenario we can run as many processes
as we like on one device to get full processor utilization. We can also reuse the network communication, as it is same
to communicate between devices as it is to communicate between processes. One downfall of this solution is that
network communication adds an overhead to the inter-process communication. Thankfully when using the localhost address
network cards nowadays skip a few layers of the networking protocol, which adds to the performance.
* The second solution would be the multiprocessing capabilities of CPython. It is possible to spawn multiple 
sub-processes with one main process and communicate between them using queues. This is faster than using network 
communication, but it comes at the cost of an additional protocol and additional control logic.

The final decision is to use the first solution. The added complexity of using sub-processes does outweigh the
performance gains from the second solution. Additionally, as we use socket communication and socket communication is 
standardized in python we can maybe also use unix sockets instead of the localhost address when using the framework on
linux. This will be as fast as interprocess communication can be with subprocesses and queues.

### The Framework
The Framework is a program that must run on CPython and MicroPython.
The general task of this framework is to divide a processing sequence and deploy it on a pool of processing resources.

For this we need at least the following entities:
* One controller process, which knows the complete processing sequence and all processing resources.
This process will do the controlling and division of work for workers and sensors.
* Worker processes, which will get assigned parts of the processing sequence.
* Sensor processes, which deliver unfiltered sensor data. As discussed earlier the sensor processes can also do 
processing and are therefore also worker processes

For this construct to work, the controller must be reachable from all endpoints and vice versa.
This results in that all processes must be run in one network environment.

### Proposal: Domains:
In a real network there are restrictions and private areas, which results in devices being not reachable for everyone.
To adequately represent this in this framework I propose the use of domains. One domain is a group of devices, which
can reach each other. This reachability is bi-directional. A gateway can therefore be for example designed by having
two distinct domains, where each domain has one device that is in a gateway domain.

Another possibility is uni-directional reachability. This could be achieved by connecting domains, where one can
explicitly set two domains as connected and must specify the direction.

These theoretical conditions require special care by the framework.
Besides, the own framework communication a worker must also support the forwarding of control communication.
Furthermore, the controller process must support these domains and intelligently place processing. This also requires
a pass-through processing, where the controller can assign a process to just do gateway work.

Another thing to consider is that the controller must know all devices, and their reachability to adequately distribute
work. The easiest solution is to define the network on the controller in advance.

The last challenge that arises from this proposal is the troubleshooting, because if the wrong device fails, a whole
network area my not be reachable anymore. Although this requires for a much more robust framework this also provides
an additional experimental value.

## Setup
This will be held up to date to show how the project is set up.

Repository: GitLab RWTH-Aachen: https://git.rwth-aachen.de/lukas.holst/bachelor-thesis

Local Development Environment: PyCharm Community + MicroPython Plugin

## Implementation
### Version 1 - Overview
MicroPython and CPython wil be supported.
Sensors can only be used/imported with MicroPython.

The wifi-capable ESP-32-WROOM-32(D) will be used as the microcontroller for sensory readouts.

TCP sockets will be used for communication.

The following sensors will be supported:
* Sensor (Connectivity)
* Temperature (internal) !not supported on every board! -> on my boards it is supported
* (Capacitive Touch (internal+external) !special hardware setup required! -> will not be implemented)
* Hall Sensor (internal - MicroPython standard library)
* Potentiometer (external - analog - 1 pin)
* Gyroscope Sensor (external - digital - I2C)
* Temperature + Humidity (external - digital - MicroPython standard library)
* Ultrasonic Sensor (external - digital - 2 pin - special protocol (Trigger/Echo))
* CO2 Sensor (external - digital - 1 pin - PWM (slow -> using interrupts))
* Capacitive Touch (external - digital - 1 pin (like a button))
* Incremental Rotary Encoder (external - digital - 2 pin - special protocol)

Inspiration for the implementations are partially taken from the following tutorials:
* https://elektro.turanis.de/html/prj075/index.html
* https://create.arduino.cc/projecthub/abdularbi17/ultrasonic-sensor-hc-sr04-with-arduino-tutorial-327ff6
* https://funduino.de/nr-51-co2-messung-mit-arduino-co2-ampel

For the implementation of the gyroscope, ultrasonic and co2 sensor readout I also used the following datasheets:
* https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf
* https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf
* https://www.winsen-sensor.com/d/files/infrared-gas-sensor/mh-z19b-co2-ver1_0.pdf

#### MicroPython https://micropython.org
Like described on their website, MicroPython is a Python implementation for microcontrollers that implements a subset
of the Python 3 standard library with minor differences which are well described. This allows one to write CPython and
MicroPython compatible code.

To get MicroPython up and running on a microcontroller the MicroPython firmware needs to be deployed on it. The
MicroPython documentation provides instructions on how to install the firmware, as well as interacting with it.
For example: it is possible to use the MicroPython installation like a Python-Shell, move files onto the 
microcontroller and run python scripts directly on the microcontroller.

#### Framework - MicroPython - Version 1
The framework will be CPython and MicroPython compatible.
All devices will in the end have the same functionality except the sensory readouts.

The first priority will be to read the sensor data and send it over the network to another device, wich requests
this data from the microcontroller.

For this I will first develop the following components:
* The python representation for the sensors
* The python representation for the sensor data
* The network communication protocol
* An easy testclient and testserver

#### Python-Repräsentation der Sensoren
Die Sensoren haben ein eigenes Modul namens sensors. Dieses Modul besitzt Sub-Module mit dem Namen der unterstützten Boards,
worin dann die Implementationen der Sensoren liegen.

Aufgrund des knappen Speichers auf Mikrocontrollern wird jeder Sensor ein eigenes Sub-Modul bekommen,
welches eine Klasse enthält, die die Sensorfunktionalität bereitstellt. 

Das Sub-Modul und die Klasse bekommen den gleichen Namen, nach Python Konvention.
(Modul startet klein, Klasse startet groß)

Dadurch wird verhindert das ein Mikrocontroller alle Sensor-Klassen in einem Modul importiert, 
obwohl meistens nur eine Sensorklasse verwendet wird.

Jede Sensorklasse stellt einen indiviudellen Konstruktor und eine universelle get() Methode bereit. 
Über diese Methode wird ein aktueller Sensorwert ausgelesen und zurückgegeben. 
Für die meisten Sensoren sollte dies ausreichend sein, da der Auslesevorgang sehr in wenigen Mikrosekunden stattfindet.
Auch I2C wird in diesem Zusammenhang als schnell genug angesehen, vorallem da eine Lösung mit Interrupts, 
wie im folgenden Beschrieben mit I2C nicht möglich ist.

Es gibt allerdings Sensoren mit langen und/oder variablen Antwortzeiten. 
Dies betrifft zum Beispiel den CO2 Sensor.
Bei diesem Sensor kann davon ausgegangen werden das die Antwortzeit 'länger' dauert und 
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
