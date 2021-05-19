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

#### The Python Representation For The Sensors
All sensors will be reachable through a sensor module. This module has submodules for each supported hardware platform.
this is currently only esp32. In these submodules every sensor will have a standardised submodule with one class in it.

The sensors are separated to keep memory usage low, because in most use cases not all sensors will be used at once.

Both the sensor file/module and class will get the same name with respect to the python convention.
(modules start lower case and classes start upper case)

Each sensor class holds a current value as public attribute, which can be of any serializable type. Each sensor also
implements an update method which will be called before the current value is used by the framework. That means a sensor
has to set value fast during his update call for the current iteration.

In the current selection of sensors there are three update lengths for these sensors. The first kind takes nearly no
time (a few microseconds), as the update method only has to read current pin states. The second kind takes longer
because some serial logic is required to read the sensor data. This can take up to a few milliseconds and is the
slowest acceptable synchronous update method. This could already be done with interrupts, but the complicated logic 
required is not feasible to implement at the moment. The last kind takes longer than 10 milliseconds. A good example
for this would be the co2 sensor and its pwm output, which has a period length of 1004 milliseconds. For these sensors
interrupts are a feasible solution. Their logic is often not complicated but slow, so the interrupt handlers take care
of interpreting the current state and if there is a new correct state, the update method can take this state and write
i into the value attribute.

To respect invalid value attribute states the framework will not process the value attribute if its value is exactly 
None.

To save performance a sensor that uses interrupts must implement the start_irq() and stop_irq() methods. On start irq
the sensor is allowed to set appropriate irq handlers on its pin handles. On stop irq the sensor must overwrite all
irq handlers with None. (Call the exact same irq methods as on start_irq() with the exact same arguments, but None as
the handler method)

There is one important aspect to interrupts, which is object allocation. This is not allowed in hardware interrupts.
As we want to be as performant as possible sensor should use hardware interrupts if possible. This results in some
precautions that must be taken when writing interrupt handlers. For example integers are not allowed to get bigger
than 2\*\*30 -1 and -2\*\*30 because then they will be converted to objects and not be atomar values anymore.
If this happens inside an interrupt handler it will crash. We could use micropython.schedule(), but we need exact timing
and micropython.schedule() cannot guarantee this. We also do have a fast and regular call to sensor.update(), so we can
do any delayed computation there.

#### The Python Representation For The Sensor Data
After each computational step I need the data to be json-serializable because at any step it can reach a network gate,
at which values will be aggregated and send over the network in JSON arrays. With this requirement the data returned
from each step/method and sensor must be json-serializable. Because python supports dynamic typing it is very easy for
us to support a wide variety of data types with only one requirement, but this also means that the individual steps
must be smarter, or the selection of steps must be smarter according to the input type. But this will be the task
of future versions.

#### The Network Communication Protocol
Used modules:
* standard (MicroPython standard): socket (usocket), struct (usocket), json (ujson)

Used modules for encryption (maybe later):
* standard (MicroPython standard): ssl (ussl)

The Stack:
* TCP socket connection
* (TLS socket wrapper) (maybe later)
* Each message consists of length + data. The length part has the struct format '!I', which is an unsigned integer, 
  big-endian.
* The data part is a UTF-8 encoded string
* The string is either a JSON-object or a JSON-array
    * A JSON-object is a control message
    * A JSON-array is a data message
    
The Handshake:
* The client starts the connection
* With encryption:
    * client and server try to elevate their socket to TLS
      (currently this is not implemented and used because esp32 MicroPython does not validate certificates)
* The client sends a JSON-object with a sensor request
* The server sends back JSON-arrays with the sensor data until the socket gets closed down


The JSON-Object:
* The control messages should be human-readable. The communication speed at this point is not critical. That is why
I can use a more convenient representation for messages.
* Structure:
    * (KEY: DATA)
    * data-request: JSON-Object::
        * sensor: "Sensor-Kind" -one-of-> (temperature, touchpad, poti, gyro, dht11)
        * time-frame: "Integer" -> send values every x milliseconds 
            * (0 or key not specified is wildcard for send every value individually -> probably slow)
        * values-per-time-frame: "Integer" -> gather x timely evenly spaced values in a time-frame
            * (time-frame has precedence over value-count, which means if the timeframe is expired, all gathered values
              will be send, even if the value-count is not met) 
            * (0 or key not specified is wildcard for send as much values as possible per time-frame)

The JSON-Array:
* This part is speed-critical, because we want to send as much sensor data as possible. All values that are aggregated
  in the connection buffer will be packed into one JSON-array and send over the network. That means we have a minimal
  overhead on the transport, but also the values must be JSON-serializable. That results in dict and list (and tuple) 
  being the only supported complex data type.
* Structure:
    * JSON-ARRAY::
        * -list-of-> "Result-Object"

#### Testclient + Testserver
To keep it simple the testclient can request one sensor in a specified manner. The testclient will print all received 
data until it gets killed. The testserver accepts an infinite number of connection requests and delivers the requested
sensor data in the format the client wants. The testserver holds an output buffer for each connection started, so there
can in the future be crashing situation, if too many connections are accepted with a too long time frame, so the buffers
occupy too much memory.


### Version 2
In Version 2 I want to be able to have clients to a predefined process, where the inputs can be sensor data or other
clients that process data. This processed data can then be transferred to other clients or printed out. The whole
process which is scattered over the clients can be assigned and removed by an external client that sends control
messages.

In Version 1 there were four core elements: the sensor representation, the network layer, the communication layer and
the testing applications. For Version 2 I will use the sensor representation and network layer from Version 1 while
rewriting the communication protocol, because it is too limited for the goals of Version 2.

Version 2 therefore adds these new components :
* Worker
* Assignment
* Pipeline

Worker are the main component of this Version. Each Worker identifies with its address, and the port it opens its 
server on. The workers listen for general connections and when a connection gets opened, control messages can be sent
to this worker. Each control message will be acknowledged and any errors will result in a connection close.
The following control messages are supported:
* Assignment, which includes the information of input pipes, processing tree and output pipes. Processing tree is not
  yet fully supported and currently it is only possible to link inputs to outputs, thereby allowing for pass-through,
  but no further processing. Assignments are further discussed in the Assignment section.
* Assignment Removal, which deletes an assignment, identified with an ID, if it exists
* Pipeline Request, which includes the assignment id and pipeline id, as well as necessary pipeline attributes. The 
  worker checks if it has this assignment and if this assignment has not yet opened an output pipeline with this ID, 
  which should prevent a client from opening the same pipeline twice. Pipelines are further discussed in the pipeline
  section.

Each worker can theoretically have an unlimited number of assignments. As an assignment spans over multiple workers and
represents one tree like processing there is currently no need to support multiple assignments, but maybe in the future
and for testing purposes the need may arise. Currently, an assignment links inputs to outputs, where inputs may be
pipelines or sensors and the outputs may also be pipelines or print outs. Assignments build from the base up, where
an assignment may have closed output pipelines which results in the values being thrown away, but an input pipeline
must always be open and valid. With this convention it is possible for an external script opening client connections and
assigning the assignment in a correct and working order.

Pipelines are opened and maintained by the assignments. If a worker receives a pipeline request the current network
socket gets handed over to the assignment and gets removed from the known general connections of the worker. The
assignment then promotes the socket to an output pipeline and maintains its state. Input pipelines are opened on
assignment creation, where the assignment opens general connections and requests pipelines from other workers.
Each pipeline has attributes which are taken from the Version 1 sensor request of this framework. There is a time-frame,
values-per-time-frame and a pipeline-id. The pipeline-id replaces the requested sensor, as the pipeline is now
assignment specific and can transmit any serializable value, which is determined by the assignment process. The other
two attributes work as specified in Version 1, with also values-per-time-frame not being implemented, because it is not
the top priority and fits better in a later development, where load balancing and automated pipeline feedback may play 
a role.

Currently, pipelines have an input and output buffer this buffer is checked for defined constant maximum size and the
framework will make a hard cut if the limit is reached. There will be solutions regarding this manner in Version 3.

Currently, only general connection can receive and process control messages and will raise an exception if data messages
are sent. Currently, I do not see any reason why there should be data messages on general connection. 
In contrast, pipeline connections can currently only process data messages and will raise an exception if control
messages are received after promotion from general connection. In the future the will most likely be control messages
supported for load balancing and automatic adjustments.

TODO: Write the worker (control message) communication structure like done for Version 1
