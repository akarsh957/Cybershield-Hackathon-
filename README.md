V.R.I.V.E. - VoIP Real-time Intelligence & Visualization Engine
Submission for the Cyber Shield Hackathon

📖 Introduction
V.R.I.V.E. is a powerful, real-time intelligence and visualization tool designed to trace the geographical origin of Voice over IP (VoIP) calls. In an era where digital communication can be easily anonymized, V.R.I.V.E. provides a critical advantage to security analysts and law enforcement by offering a live, interactive dashboard that monitors, analyzes, and maps VoIP traffic as it happens.

🎥 Demo
Watch the video below to see V.R.I.V.E. in action:

https://youtu.be/tDkbJiLuRIc
![WhatsApp Image 2025-08-31 at 12 03 42_ea9e6db3](https://github.com/user-attachments/assets/f6bfd2a2-4d8b-4638-bd2f-58dcdc035a4d)

![WhatsApp Image 2025-08-31 at 12 04 07_ba53a9b7](https://github.com/user-attachments/assets/f68b97cc-3da8-4960-8897-b8cff7388af8)

![WhatsApp Image 2025-08-31 at 12 04 25_c34a9f24](https://github.com/user-attachments/assets/3bdaefcf-5caa-431b-b416-4f876dbbfb9b)



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

🚀 How to Run V.R.I.V.E.
Important: You must run all commands in a Command Prompt (CMD) with Administrator privileges.

Clone the Repository

git clone [https://github.com/your-username/vrive.git](https://github.com/your-username/vrive.git)
cd vrive

Install Dependencies
Open CMD as Administrator and run:

pip install -r requirements.txt

If the above command doesn't work, try using pip3:

pip3 install -r requirements.txt

Run the Backend Server
In the same Administrator CMD window, run:

python3 analyzer.py

Open the Web Interface
Navigate to the following URL in your web browser:

[http://12.0.0.1:5000](http://12.0.0.1:5000)

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
