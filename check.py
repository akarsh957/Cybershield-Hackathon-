import time
from scapy.all import sniff, IP, UDP, DNS, DNSQR

# --- CONFIGURATION ---
# This is the name of your Wi-Fi adapter from your ipconfig output.
# It's crucial that this name is exactly correct.
NETWORK_INTERFACE = "Intel(R) Wi-Fi 6 AX201 160MHz"
# ---------------------

# A set to keep track of IPs we've already seen to keep the log clean.
seen_udp_ips = set()

def packet_handler(packet):
    """
    This function is called for every packet Scapy captures.
    It checks for DNS queries and UDP traffic and prints the details.
    """
    try:
        # We only care about packets with an IP layer.
        if not packet.haslayer(IP):
            return

        # --- DNS Intelligence Stage ---
        # Check if the packet is a DNS query.
        if packet.haslayer(DNS) and packet.haslayer(DNSQR) and packet[DNS].opcode == 0:
            query_name = packet[DNS][DNSQR].qname.decode('utf-8', 'ignore')
            print(f"[DNS Query] \t Your PC asked for the IP of: {query_name}")

        # --- UDP Traffic Stage ---
        # Check if the packet is using UDP.
        if packet.haslayer(UDP):
            # Get the source and destination IP addresses.
            src_ip = packet[IP].src
            dest_ip = packet[IP].dst

            # We only care about traffic leaving our local network.
            # This ignores traffic between your PC and your router.
            if dest_ip.startswith('192.168.') or dest_ip.startswith('10.'):
                return
            
            # If we haven't seen this destination IP before, print it.
            if dest_ip not in seen_udp_ips:
                timestamp = time.strftime('%H:%M:%S')
                print(f"[{timestamp}] [UDP Packet] \t Sent to IP: {dest_ip}")
                seen_udp_ips.add(dest_ip)

    except Exception as e:
        # This will prevent the script from crashing on weird packets.
        # print(f"Error processing a packet: {e}")
        pass

# --- MAIN SCRIPT EXECUTION ---
if __name__ == '__main__':
    print("--- V.R.I.V.E. Packet Debugger ---")
    print(f"Starting to listen on network interface: {NETWORK_INTERFACE}")
    print("Please start your WhatsApp or Telegram call now...")
    print("-" * 40)

    # The sniff function is the core of Scapy. It captures packets and calls
    # our packet_handler function for each one.
    sniff(prn=packet_handler, store=False, iface=NETWORK_INTERFACE, filter="udp or port 53")

    print("-" * 40)
    print("Debugger stopped.")
