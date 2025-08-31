V.R.I.V.E. - VoIP Real-time Intelligence & Visualization Engine
Submission for the Cyber Shield Hackathon

📖 Introduction
V.R.I.V.E. is a powerful, real-time intelligence and visualization tool designed to trace the geographical origin of Voice over IP (VoIP) calls. In an era where digital communication can be easily anonymized, V.R.I.V.E. provides a critical advantage to security analysts and law enforcement by offering a live, interactive dashboard that monitors, analyzes, and maps VoIP traffic as it happens.

🎥 Demo
Watch the video below to see V.R.I.V.E. in action:

https://youtu.be/tDkbJiLuRIc


🎯 The Problem
Malicious actors, scammers, and criminals frequently exploit the anonymity of encrypted VoIP services (like Telegram, Signal, etc.) to carry out illegal activities without revealing their location. Tracing these calls is a complex and often time-consuming process that requires deep network analysis, usually performed after the fact. This delay allows perpetrators to relocate, making them difficult to apprehend.

💡 Our Solution
V.R.I.V.E. addresses this challenge by providing an all-in-one solution that automates the process of capturing, analyzing, and visualizing VoIP call data in real-time.

When a target VoIP call is initiated, V.R.I.V.E.:

Detects & Captures: It actively monitors network traffic to detect and capture the data packets of the VoIP session.

Analyzes: It extracts the subject's IP address from the captured packets and initiates a traceroute to map the network path.

Visualizes: It geolocates the subject's IP address and plots both the operator's and the subject's location on an interactive world map, calculating the distance and live call duration.

Reports: All session data, including IP hops and location details, is saved in a structured JSON file for post-analysis and evidence collection.

✨ Key Features
Real-time Traffic Analysis: Actively sniffs the network for live VoIP sessions.

Supported Platforms: Currently capable of tracing calls on WhatsApp and Telegram.

IP Geolocation: Accurately estimates the country, city, and ISP of the subject based on their IP address.

Interactive Dashboard: A user-friendly web interface displays key information on a world map.

Dynamic Visualization: Plots the operator's and subject's locations and draws the connection path.

Live Metrics: Displays real-time call duration and the distance between the operator and the subject.

Confidence Score: Provides an estimated confidence level for the traced location.

Automated Logging: Automatically saves detailed forensic data of each session into a JSON file.

🛠️ Technology Stack
Backend: Python, Flask

Packet Analysis: Scapy (or similar packet manipulation library)

Frontend: HTML, CSS, JavaScript

Mapping: Leaflet.js (or a similar mapping library)

IP Intelligence: IP geolocation APIs

HOW THE V.R.I.V.E. LIVE MONITORING WORKS

STEP 1: OPERATOR INITIALIZATION
- The process begins when the operator opens the web dashboard.
- A "Mission Start" dialog appears, prompting the user to input their current Latitude and Longitude.
- This manual input guarantees a reliable starting point for the trace.

 ![WhatsApp Image 2025-08-31 at 12 05 24_38764b16](https://github.com/user-attachments/assets/441bf9c8-9910-4d1b-8401-f4c36a5798cf)


STEP 2: BACKEND ACTIVATION
- When the operator clicks "Start Tracing", the coordinates are sent to the Python backend via a WebSocket connection.
- Upon receiving this signal, the backend sets the operator's location and immediately activates the core packet sniffing engine on the specified network interface.
- A "LISTENING" status is sent back to the UI, providing visual confirmation that the system is live.

  

STEP 3: LIVE PACKET CAPTURE
- The engine uses the Scapy library to sniff all network traffic in real-time.
- It is specifically configured to filter and analyze two types of packets:
  1. DNS packets (on Port 53)
  2. UDP packets (the protocol used by most real-time voice and video streams)

  ![WhatsApp Image 2025-08-31 at 12 05 39_6c376e3c](https://github.com/user-attachments/assets/2e92d370-3c0e-4da5-bd24-104c286aea5d)


STEP 4: THE HYBRID DETECTION ENGINE
The system uses a two-stage process to intelligently identify VoIP calls from background noise.

- STAGE 1: DNS INTELLIGENCE
  - The engine inspects all outgoing DNS queries. If it sees a request for a known VoIP-related hostname (like 'whatsapp.net', 'telegram.org', or generic services like 'stun' and 'turn'), it reads the IP address from the DNS response.
  - This IP is dynamically flagged as a high-confidence VoIP server. This method allows the tool to find the correct server even if its IP address changes frequently.

- STAGE 2: HEURISTIC ANALYSIS
  - For all other UDP traffic, the engine acts as a profiler. It tracks every external IP address the computer communicates with.
  - It maintains a count of packets sent to each IP within a short time window (e.g., 4 seconds).
  - If the number of packets to a single IP crosses a set threshold (e.g., 25 packets), the system flags it as a "Probable VoIP Stream" based on its high-volume, continuous behavior.

STEP 5: TRIGGERING THE FULL ANALYSIS
- Once an IP is flagged as a VoIP server by either the DNS or Heuristic engine, the system initiates a full forensic analysis on that IP.
- The system is stateful; it understands it's in an "active call" and will treat subsequent IPs from the same service as server hops, not new calls.

STEP 6: DATA ENRICHMENT AND REPORTING
- The flagged IP is sent to the IPinfo.io API to retrieve its metadata:
  - GEOLOCATION: The server's City and Country.
  - OWNERSHIP: The name of the company that owns the IP (e.g., "Telegram Messenger Inc" or "Google LLC").
  - ANONYMITY STATUS: Whether the IP is a known VPN or proxy.
- A TRACEROUTE is performed to map the entire network path from the operator to the server, and each hop is geolocated.
- A CONFIDENCE SCORE is calculated based on the consistency of the traceroute path and the VPN status.
- The system automatically generates a detailed JSON evidence report upon call termination.

STEP 7: REAL-TIME VISUALIZATION
- All the analyzed data is packaged and pushed instantly to the frontend UI via WebSockets.
- The JavaScript in the browser receives this data and updates all dashboard elements without a page refresh:
  - The map plots the full traceroute path.
  - The information panels are populated with location and ownership details.
  - The widgets are updated with the call duration and distance.

![WhatsApp Image 2025-08-31 at 12 03 42_6e6b6a9e](https://github.com/user-attachments/assets/1318ff23-e9ee-4095-9d24-c3ce1522a8a2)

![WhatsApp Image 2025-08-31 at 12 04 07_0413ef6c](https://github.com/user-attachments/assets/7f802ec0-1fb5-465b-a46f-382fd33b8abe)

![WhatsApp Image 2025-08-31 at 12 04 25_60d20614](https://github.com/user-attachments/assets/415932d0-d524-4882-8b60-e869ea2a6987)


STEP 8: SESSION TERMINATION
- The backend continuously monitors the active call.
- If no packets are seen from the VoIP service for a set period (e.g., 10 seconds), the system automatically declares the call has ended.
- It sends a final signal to the UI to stop the timer and clear the map, ready for the next trace.

🧑‍💻 Usage
Once the UI is loaded, enter the operator's current coordinates (Latitude and Longitude).

Click "Start Tracing". The system status will change to "LISTENING FOR VOIP TRAFFIC".

Initiate or receive a WhatsApp or Telegram call on the same network.

V.R.I.V.E. will automatically detect the call, and the dashboard will update in real-time with the subject's estimated location and other metrics.

Once the call ends, the session data will be saved as a .json file in the project directory.

👥 Team Members
Akarsh Mishra
Snehil Shourya 
Atharva Satish Patkar 
Amrita Jadhav 
Jayanth Renganathan 
Built with passion for the Cyber Shield Hackathon.
