import threading
import time
import subprocess
import re
import json
from datetime import datetime
from scapy.all import sniff, IP, UDP
import requests
from flask import Flask, render_template
from flask_socketio import SocketIO
from math import radians, cos, sin, asin, sqrt
from ipaddress import ip_address, AddressValueError

# --- CONFIGURATION ---
IPINFO_API_KEY = "4f17f099350515" # Your key

VOIP_PREFIXES = {
    "Telegram": ("91.108.",),
    "WhatsApp/Facebook": ("157.240.", "163.70.")
}

SESSION_TIMEOUT_SECONDS = 10
# --- END CONFIGURATION ---

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-hackathon-key-final-stable!'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- GLOBAL STATE ---
operator_location_info = {}
ip_cache = {}
data_lock = threading.Lock()
sniffer_thread = None
is_sniffer_running = False
seen_debug_ips = set()

# New state management for calls
current_call = {
    "active": False,
    "service": None,
    "start_time": None,
    "last_seen": 0,
    "all_subject_ips": set(),
    "initial_traceroute": None,
    "current_subject_ip": None
}

def get_ip_details(ip):
    if ip in ip_cache: return ip_cache[ip]['data']
    try:
        response = requests.get(f"https://ipinfo.io/{ip}?token={IPINFO_API_KEY}", timeout=5)
        response.raise_for_status()
        data = response.json()
        if 'org' in data: data['owner'] = data['org'].split(' ', 1)[1] if ' ' in data['org'] else data['org']
        ip_cache[ip] = {'timestamp': time.time(), 'data': data}
        return data
    except requests.RequestException as e:
        print(f"Error fetching details for {ip}: {e}")
        return {'ip': ip, 'error': str(e)}

def haversine_distance(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    dlon = lon2 - lon1; dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)); r = 6371
    return int(c * r)

def run_traceroute(ip):
    print(f"[{ip}] Running traceroute for initial evidence...")
    command = ["tracert", "-d", "-w", "1000", ip]
    path = []
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        for line in iter(process.stdout.readline, ''):
            match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
            if match:
                hop_ip = match.group(1)
                try:
                    ip_obj = ip_address(hop_ip)
                    if not ip_obj.is_private: path.append(hop_ip)
                except AddressValueError: continue
        process.stdout.close(); process.wait()
    except Exception as e:
        print(f"Error running traceroute for {ip}: {e}")
    print(f"[{ip}] Traceroute complete. Found {len(path)} hops.")
    return [get_ip_details(hop) for hop in path]

def analyze_and_emit(dest_ip, service):
    global current_call
    with data_lock:
        is_new_call = not current_call["active"]
        current_call["active"] = True
        current_call["service"] = service
        current_call["all_subject_ips"].add(dest_ip)
        current_call["last_seen"] = time.time()
        current_call["current_subject_ip"] = dest_ip

        if is_new_call:
            current_call["start_time"] = time.time()
            print(f"\n--- New {service} Session Detected to {dest_ip} ---")
        else:
            print(f"--- {service} Session Hopped to New IP: {dest_ip} ---")

    dest_details = get_ip_details(dest_ip)
    
    traceroute_path = []
    if is_new_call:
        traceroute_path = run_traceroute(dest_ip)
        with data_lock:
            current_call["initial_traceroute"] = traceroute_path

    distance_km = None
    if dest_details.get('loc') and operator_location_info.get('loc'):
        op_lat, op_lon = operator_location_info['loc']
        sub_lat, sub_lon = dest_details['loc'].split(',')
        distance_km = haversine_distance(op_lat, op_lon, sub_lat, sub_lon)

    confidence = 70
    if dest_details.get('country') and traceroute_path:
        matching_hops = sum(1 for hop in traceroute_path[-3:] if hop.get('country') == dest_details['country'])
        confidence += matching_hops * 5
    if dest_details.get('bogon') or dest_details.get('vpn'):
        confidence -= 40; dest_details['owner'] = "VPN / Anonymizer"
    
    final_data = {
        'destination_details': dest_details, 'traceroute_path': traceroute_path,
        'distance_km': distance_km, 'confidence_score': max(0, min(100, confidence)),
        'is_new_call': is_new_call
    }
    socketio.emit('update_data', final_data)
    print(f"[{dest_ip}] Analysis complete. Emitted {'full' if is_new_call else 'light'} update.")

def packet_handler(packet):
    if not packet.haslayer(IP) or not packet.haslayer(UDP): return
    try:
        dest_ip_obj = ip_address(packet[IP].dst)
    except AddressValueError: return
    if dest_ip_obj.is_private or dest_ip_obj.is_multicast: return
    dest_ip = str(dest_ip_obj)

    if dest_ip not in seen_debug_ips:
        print(f"  [Packet Log] New UDP connection to: {dest_ip}")
        seen_debug_ips.add(dest_ip)
    
    with data_lock:
        if current_call["active"] and dest_ip in current_call["all_subject_ips"]:
            current_call["last_seen"] = time.time()
            return

    for service, prefixes in VOIP_PREFIXES.items():
        if any(dest_ip.startswith(p) for p in prefixes):
            threading.Thread(target=analyze_and_emit, args=(dest_ip, service)).start()
            return

def session_cleanup_thread():
    global current_call
    while True:
        time.sleep(5)
        with data_lock:
            if current_call["active"] and (time.time() - current_call["last_seen"]) > SESSION_TIMEOUT_SECONDS:
                print(f"\n--- {current_call['service']} call has ended (timeout). ---")
                
                # Save evidence file
                duration_seconds = int(time.time() - current_call["start_time"])
                m, s = divmod(duration_seconds, 60)
                h, m = divmod(m, 60)
                duration_str = f"{h:02d}h{m:02d}m{s:02d}s"
                date_str = datetime.utcfromtimestamp(current_call["start_time"]).strftime('%Y-%m-%d')
                
                report = {
                    "case_id": f"VRIVE_{int(time.time())}",
                    "service_provider": current_call["service"],
                    "call_start_timestamp_utc": datetime.utcfromtimestamp(current_call["start_time"]).isoformat() + "Z",
                    "call_duration": duration_str,
                    "operator_details": {
                        "public_ip": operator_location_info.get("public_ip", "N/A"),
                        "latitude": operator_location_info.get('loc', ('N/A','N/A'))[0],
                        "longitude": operator_location_info.get('loc', ('N/A','N/A'))[1]
                    },
                    "subject_details": {
                        "server_ips_used": list(current_call["all_subject_ips"]),
                    },
                    "initial_network_path": {
                        "traced_ip": current_call["initial_traceroute"][0]['ip'] if current_call.get("initial_traceroute") else "N/A",
                        "hops": current_call.get("initial_traceroute", [])
                    }
                }
                
                filename = f"{current_call['service']}_{date_str}_{duration_str}.json"
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=4)
                print(f"[+] Evidence report saved to: {filename}")

                socketio.emit('call_ended', {})
                # Reset call state
                current_call = {
                    "active": False, "service": None, "start_time": None, "last_seen": 0,
                    "all_subject_ips": set(), "initial_traceroute": None, "current_subject_ip": None
                }

def run_sniffer_process():
    global is_sniffer_running
    is_sniffer_running = True
    print("\n--- Network Sniffer is now LIVE ---")
    socketio.emit('sniffer_status', {'status': 'listening'})
    sniff(prn=packet_handler, store=False, filter="udp", iface="Intel(R) Wi-Fi 6 AX201 160MHz")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_tracing')
def handle_start_tracing(data):
    global operator_location_info, sniffer_thread
    operator_location_info['loc'] = (data.get('lat'), data.get('lon'))
    try:
        # Get operator's public IP
        operator_location_info['public_ip'] = requests.get('https://api.ipinfo.io/ip', timeout=5).text.strip()
    except:
        operator_location_info['public_ip'] = "Detection Failed"

    print(f"Operator location set by UI: Lat={data.get('lat')}, Lon={data.get('lon')}")
    socketio.emit('operator_location', operator_location_info)
    if sniffer_thread is None:
        sniffer_thread = threading.Thread(target=run_sniffer_process, daemon=True)
        sniffer_thread.start()

if __name__ == '__main__':
    print("--- V.R.I.V.E. Backend Starting ---")
    threading.Thread(target=session_cleanup_thread, daemon=True).start()
    print("Starting web server on http://127.0.0.1:5000")
    print("Waiting for operator to start trace from UI...")
    socketio.run(app, host='127.0.0.1', port=5000)

