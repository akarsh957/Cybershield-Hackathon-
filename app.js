// Global variables
let map;
let operatorMarker, subjectMarker;
let pathLine;
let callStartTime = null;
let durationInterval = null;
let socket;

// UI Element References
const opLat = document.getElementById('op-lat');
const opLon = document.getElementById('op-lon');
const subCountry = document.getElementById('sub-country');
const subCity = document.getElementById('sub-city');
const subIp = document.getElementById('sub-ip');
const subOwner = document.getElementById('sub-owner');
const subConfidence = document.getElementById('sub-confidence');
const distanceValue = document.getElementById('distance-value');
const durationValue = document.getElementById('duration-value');
const startModalBackdrop = document.getElementById('start-modal-backdrop');
const startTracingBtn = document.getElementById('start-tracing-btn');
const latInput = document.getElementById('lat-input');
const lonInput = document.getElementById('lon-input');
const modalError = document.getElementById('modal-error');
const statusPanel = document.getElementById('status-panel');
const statusText = document.getElementById('status-text');

function initializeDashboard() {
    map = L.map('map').setView([20.5937, 78.9629], 4);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    setupSocketIO();
}

startTracingBtn.addEventListener('click', () => {
    const lat = parseFloat(latInput.value);
    const lon = parseFloat(lonInput.value);
    if (isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
        modalError.textContent = "Invalid coordinates."; return;
    }
    modalError.textContent = "";
    startModalBackdrop.style.display = 'none';
    socket.emit('start_tracing', { lat: lat, lon: lon });
});

function setupSocketIO() {
    socket = io();
    socket.on('connect', () => console.log('Connected to backend server.'));
    
    socket.on('operator_location', (data) => {
        if (!data || !data.loc) return;
        const [lat, lon] = data.loc;
        opLat.textContent = lat.toFixed(4);
        opLon.textContent = lon.toFixed(4);
        
        const opPosition = [lat, lon];
        map.setView(opPosition, 10);
        if (operatorMarker) operatorMarker.setLatLng(opPosition);
        else operatorMarker = L.marker(opPosition).addTo(map).bindPopup(`<b>Your Location</b>`);
    });

    socket.on('sniffer_status', (data) => {
        if (data.status === 'listening') {
            statusPanel.classList.add('listening');
            statusText.textContent = 'LISTENING FOR VOIP TRAFFIC';
        }
    });

    socket.on('update_data', (data) => {
        if (!callStartTime) {
            callStartTime = new Date();
            if(durationInterval) clearInterval(durationInterval);
            durationInterval = setInterval(updateCallDuration, 1000);
        }
        const dest = data.destination_details;
        subCountry.textContent = dest.country || 'N/A';
        subCity.textContent = dest.city || 'N/A';
        subIp.textContent = dest.ip;
        subOwner.textContent = dest.owner || 'N/A';
        subConfidence.textContent = data.confidence_score;
        distanceValue.textContent = data.distance_km ? data.distance_km.toLocaleString('en-IN') : '--';

        const subjectCoords = dest.loc ? dest.loc.split(',').map(Number) : null;
        if (subjectCoords) {
             const redIcon = new L.Icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
            });
            if (subjectMarker) subjectMarker.setLatLng(subjectCoords);
            else subjectMarker = L.marker(subjectCoords, {icon: redIcon}).addTo(map);
            subjectMarker.bindPopup(`<b>Subject (Est.):</b><br>${dest.city || ''}, ${dest.country || ''}<br>IP: ${dest.ip}`);
            
            const pathCoords = [];
            if (operatorMarker) {
                const opLatLng = operatorMarker.getLatLng();
                pathCoords.push([opLatLng.lat, opLatLng.lng]);
            }
            // Add traceroute hops to the path
            data.traceroute_path.forEach(hop => {
                if (hop.loc) {
                    pathCoords.push(hop.loc.split(',').map(Number));
                }
            });
            pathCoords.push(subjectCoords);
            
            if (pathLine) pathLine.setLatLngs(pathCoords);
            else pathLine = L.polyline(pathCoords, { color: '#e94560', weight: 3 }).addTo(map);
            
            map.fitBounds(L.latLngBounds(pathCoords).pad(0.2));
        }
    });

    socket.on('call_ended', (data) => {
        console.log(`Call with ${data.ip} ended.`);
        clearInterval(durationInterval);
        callStartTime = null;
        durationInterval = null;
        
        // Reset UI elements
        subCountry.textContent = '--';
        subCity.textContent = '--';
        subIp.textContent = '--';
        subOwner.textContent = '--';
        subConfidence.textContent = '--';
        distanceValue.textContent = '--';
        
        if(subjectMarker) {
            map.removeLayer(subjectMarker);
            subjectMarker = null;
        }
        if(pathLine) {
            map.removeLayer(pathLine);
            pathLine = null;
        }
    });
}

function updateCallDuration() {
    if (!callStartTime) return;
    const now = new Date();
    const diff = now - callStartTime;
    const seconds = Math.floor((diff / 1000) % 60).toString().padStart(2, '0');
    const minutes = Math.floor((diff / (1000 * 60)) % 60).toString().padStart(2, '0');
    const hours = Math.floor((diff / (1000 * 60 * 60)) % 24).toString().padStart(2, '0');
    durationValue.textContent = `${hours}:${minutes}:${seconds}`;
}

window.onload = initializeDashboard;

