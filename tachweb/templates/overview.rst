.. image:: {{STATIC}}/tachweb/whatis.jpg

The Tachyonic Project is an eco-system of Open Source Packages that, when used together, becomes an orchestrator of orchestrators. It allows for rapid development to become the single pane of glass into all your systems. As the glue between your OSS, BSS and Networked elements, it meets the need of all your orchestration and automation requirements. Purposely built for large operators such as mobile telephone operators, commercial and home broadband providers, tier 1 network operators, large data center and cloud providers by experienced network engineers for network engineers. 
 
Tachyonic lets you automate the creation, monitoring, and deployment of resources in your environment. The unique environment platform is designed to be vertically and horizontally scalable. The platform does not necessarily automate all the processes but also works collectively with other orchestrators and automation systems. 
 
Developed by a growing community of users and contributors just like you. 

Luxon
-----
    The project is primarily developed on Luxon Framework on Python and supports both version 3.5 and 3.6. (3.6 recommended) 

    Luxon forms part of the Tachyonic eco-system of projects. Its intently built to provide a common development interface for all API, WEB and backend systems keeping performance and rapid development in mind.

    Design emphasizes on the MVC pattern (Model, View, Controller) and build on best practice cloud infrastructure design principles. 

Scalable
--------

    Its build on the principle of isolated projects which are responsible for specific functionality and features all using the same framework (Luxon) to provide rapid development and north- and south-bound interfaces. 

    One important feature is that all interfaces into Tachyonic can be publicly exposed and redundantly deployed over several regions, domains and endpoints. All application interfaces are based on the well-known JSON using RESTful API.

Endpoints
---------

    Endpoints provide additional functionality to the system. You may add your own or use some of the endpoints bundled in the Tachyonic Project. Some examples of these are:

    * Netrino - used for orchestration via service templating,
    * InfinityStone - used for AAA (Authentication, Authorization and Accounting),
    * Yoshii - used for Telemetry. 
    * Photonic - a Web UI.

    All endpoints providing services are fully scalable by just adding more hardware and using HA proxies such as F5 or opensource projects.
    Daemons known as minion workers perform tasks such as deploying configurations built using YANG templates and collecting Telemetry data and SNMP counter values.

Databases
---------
    Databases used are

    * SQLite
    * Mariadb.

Object Store
------------
    A controversial subject was finding a way to store large amounts of data in a secure, redundant manner such as those collected and consumed by the Telemetry service. Hence the Katalog and Kiloquad project was initiated.

    It’s a simple object store being strictly built for our purposes.

Sharing objects
---------------
    Sharing data between processes and redundant nodes we use Redis in-memory data structure store. Primarily used for our cache, state-sharing and sessions.

    Redis supports data structures such as strings, hashes, lists, sets, sorted sets with range queries, bitmaps, hyperloglogs and geospatial indexes with radius queries.

Message Bus
-----------
    Tachyonic endpoints and minions/workers utilize AMQ (Advanced Message Queueing Protocol). It was chosen to support RabbitMQ.

    RabbitMQ is lightweight and easy to deploy on premises and in the cloud. It supports multiple messaging protocols. RabbitMQ can be deployed in distributed and federated configurations to meet high-scale, high-availability requirements. 
