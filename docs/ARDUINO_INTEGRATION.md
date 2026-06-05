# 🔌 Intégration Arduino - Prototype IoT de Maintenance Prédictive

## 1. Concept et Faisabilité

### Vue d'ensemble
Ce prototype transforme MinePredict en un système **IoT réel** où un Arduino/ESP32 capture des mesures de capteurs physiques et les envoie en temps réel à l'API FastAPI pour prédiction de pannes.

### Architecture globale
```
[Capteurs Physiques] 
    ↓
[Arduino/ESP32]  ← Microcontrôleur
    ↓ (USB/Wi-Fi)
[PC/Raspberry Pi] ← Passerelle bridge (Python)
    ↓ (HTTP/REST)
[FastAPI Backend] ← Prédiction ML
    ↓ (WebSocket/REST)
[React Dashboard] ← Affichage temps réel
```

### Matériel Nécessaire

#### Option 1 : Arduino + Capteurs Analogiques (Basique - 30€)
- **Arduino Uno** ou **Arduino Mega** (15-25€)
- **Capteur Vibration** (analogique, piezo) : 3-5€
  - Broche : `A0` (Analog 0)
  - Fréquence : 0-10 kHz
  - Sortie : 0-5V → Convertir en mm/s pour comparaison
- **Capteur Température** (DHT22 ou LM35) : 5-10€
  - DHT22 : `D2` (Digital 2, protocole 1-wire)
  - LM35 : `A1` (linéaire, 0V = -50°C, 2.5V = 75°C)
- **Capteur Pression** (optionnel) : 8-15€
  - BMP280 ou BMP390 : `I2C (A4, A5)` ou `SPI`
- **Câble USB A-B** (pour communication série) : 3-5€

#### Option 2 : ESP32 + Wi-Fi (Recommandé - 40-60€)
- **ESP32 Dev Board** : 20-40€
  - Double cœur 240 MHz
  - Wi-Fi 802.11 b/g/n
  - Bluetooth LE
  - ADC 12-bit multi-canaux
  - I2C, SPI, UART
- **Même capteurs** que Option 1
- **Avantage** : Pas besoin de PC comme passerelle, envoi direct HTTP/MQTT vers le backend

---

## 2. Montage Électronique Détaillé

### Schéma Arduino Uno + 3 Capteurs

```
                         +5V ───┬─────────┬───────┬──────┐
                              │        │       │      │
                             R1       R2      │    DHT22
                           10kΩ     10kΩ     │    (D2)
                              │        │       │      │
         Piezo Vibration ──A0──┘        │       │      └─ GND
         (Analog Input)                 │       │
                                    BMP280   Vref  
                                    (I2C)    (A2)
                               A4 → SDA     
                               A5 → SCL     
         
         
                        ┌─── ARDUINO ───┐
                        │               │
                    GND ├───────────────┤ 5V
                    GND ├───────────────┤ 3.3V
                     D0 ├───────────────┤ AREF
                     D1 ├───────────────┤ A0 ←── Vibration
                     D2 ├───────────────┤ A1 ←── Température (LM35)
                     D3 ├───────────────┤ A2
                     D4 ├───────────────┤ A3
                     D5 ├───────────────┤ A4 → I2C SDA
                     D6 ├───────────────┤ A5 → I2C SCL
                     D7 ├───────────────┤
                     D8 ├───────────────┤
                     D9 ├───────────────┤
                    D10 ├───────────────┤
                    D11 ├───────────────┤
                    D12 ├───────────────┤
                    D13 ├───────────────┤
                        └───────────────┘
```

### Connexions Pin par Pin

#### 1. Capteur Vibration (Piezo)
```
Piezo Sensor
├─ Signal (Central) → Arduino A0 (via Resistor Divider)
├─ GND → Arduino GND
└─ + → Arduino 5V (optionnel pour stabilité)

Resistor Divider (protège A0 vs voltages > 5V):
5V ──┬── R1 (10kΩ) ──┬── A0
     │               │
    GND             R2 (10kΩ)
                     │
                    GND
```

**Code à tester** :
```cpp
int vibrationPin = A0;

void setup() {
  Serial.begin(9600);
  pinMode(vibrationPin, INPUT);
}

void loop() {
  int raw = analogRead(vibrationPin);
  float voltage = raw * (5.0 / 1023.0);
  float vibration_mm_per_s = voltage * 10.0;  // Étalonnage empirique
  
  Serial.print("Vibration: ");
  Serial.print(vibration_mm_per_s);
  Serial.println(" mm/s");
  
  delay(500);
}
```

#### 2. Capteur Température (DHT22)
```
DHT22 Sensor
├─ VCC → Arduino 5V (pas de condensateur recommandé, USB power OK)
├─ GND → Arduino GND
├─ NC (broche 2) → pas utilisée
└─ DATA → Arduino D2 (avec resistor pull-up 10kΩ optionnel)

Connexion directe OK pour distances < 20cm
```

**Installation Librairie** :
```bash
Arduino IDE → Sketch → Include Library → Manage Libraries
Chercher : "DHT sensor library"
Installer : DHT sensor library by Adafruit
```

**Code** :
```cpp
#include "DHT.h"

#define DHTPIN 2
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Erreur DHT22");
    return;
  }
  
  Serial.print("Temp: ");
  Serial.print(temperature);
  Serial.print(" °C, Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");
  
  delay(2000);
}
```

#### 3. Capteur Pression (BMP280 - I2C)
```
BMP280 I2C
├─ VCC → Arduino 5V (ou 3.3V)
├─ GND → Arduino GND
├─ SCL → Arduino A5 (Clock)
└─ SDA → Arduino A4 (Data)

Note: Ajouter capacitors 100nF de stabilisation (optionnel mais recommandé)
```

**Installation Librairie** :
```bash
Installer : Adafruit BMP280 Library
```

**Code** :
```cpp
#include <Adafruit_BMP280.h>

Adafruit_BMP280 bmp280;

void setup() {
  Serial.begin(9600);
  if (!bmp280.begin(0x77)) {  // I2C address 0x76 ou 0x77
    Serial.println("BMP280 not found!");
    while (1);
  }
}

void loop() {
  float pressure = bmp280.readPressure() / 100.0F;  // En hPa
  float temperature = bmp280.readTemperature();
  
  Serial.print("Pressure: ");
  Serial.print(pressure);
  Serial.print(" hPa, Temp: ");
  Serial.print(temperature);
  Serial.println(" °C");
  
  delay(1000);
}
```

---

## 3. Code Arduino Complet (Tri-capteurs)

Fichier : `arduino_sketch/minepredict_sensor.ino`

```cpp
#include "DHT.h"

// Pin Configuration
#define VIBRATION_PIN A0
#define DHT_PIN 2
#define DHTTYPE DHT22

DHT dht(DHT_PIN, DHTTYPE);

// Calibration factors
const float VIBRATION_SCALE = 10.0;  // Raw → mm/s
const float PRESSURE_SCALE = 1.0;    // Direct read

struct SensorReading {
  float vibration;    // mm/s
  float temperature;  // °C
  float humidity;     // %
  unsigned long timestamp;
};

void setup() {
  Serial.begin(9600);
  pinMode(VIBRATION_PIN, INPUT);
  dht.begin();
  
  Serial.println("MinePredict Arduino Sensor Node - Starting");
  delay(2000);
}

void loop() {
  SensorReading reading;
  
  // Read Vibration (Analog)
  int raw_vibration = analogRead(VIBRATION_PIN);
  float voltage = raw_vibration * (5.0 / 1023.0);
  reading.vibration = voltage * VIBRATION_SCALE;
  
  // Read Temperature + Humidity
  reading.humidity = dht.readHumidity();
  reading.temperature = dht.readTemperature();
  
  // Timestamp
  reading.timestamp = millis();
  
  // Validate readings
  if (!isnan(reading.temperature) && !isnan(reading.humidity)) {
    // Send as JSON via Serial
    sendJSON(reading);
  } else {
    Serial.println("{\"error\": \"DHT22 read failed\"}");
  }
  
  delay(1000);  // 1 reading per second
}

void sendJSON(const SensorReading& reading) {
  Serial.print("{");
  Serial.print("\"vibration\": ");
  Serial.print(reading.vibration, 2);
  Serial.print(", \"temperature\": ");
  Serial.print(reading.temperature, 2);
  Serial.print(", \"humidity\": ");
  Serial.print(reading.humidity, 2);
  Serial.print(", \"timestamp\": ");
  Serial.print(reading.timestamp);
  Serial.println("}");
}
```

---

## 4. Passerelle Python (Serial → HTTP)

Fichier : `backend/arduino_bridge.py`

```python
#!/usr/bin/env python3
"""
Arduino Serial Bridge - Reads sensors from Arduino, sends to FastAPI backend.
Runs on PC/Raspberry Pi as intermediary.
"""

import serial
import json
import requests
import time
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
SERIAL_PORT = "COM3"  # Windows: COM3, Linux: /dev/ttyUSB0, Mac: /dev/tty.usbserial-*
BAUD_RATE = 9600
API_BASE_URL = "http://localhost:8000"
EQUIPMENT_ID = "arduino_sensor_01"

# Calibration & thresholds
VIBRATION_ALERT_THRESHOLD = 50.0  # mm/s
TEMPERATURE_ALERT_THRESHOLD = 80.0  # °C


def read_arduino(ser):
    """Read JSON data from Arduino serial port."""
    if ser.in_waiting > 0:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith('{'):
                return json.loads(line)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Parse error: {e}")
    return None


def send_to_backend(reading):
    """Send sensor reading to FastAPI backend for prediction."""
    payload = {
        "equipment_id": EQUIPMENT_ID,
        "values": {
            "vibration": reading["vibration"],
            "temperature": reading["temperature"],
            "humidity": reading["humidity"],
            "timestamp": reading["timestamp"],
        }
    }
    
    try:
        # Predict failure
        response = requests.post(
            f"{API_BASE_URL}/predict/failure",
            json=payload,
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Prediction: {result}")
            
            # Check alerts
            if result.get("probability", 0) > 0.7:
                logger.warning(f"🚨 ALERT: High failure risk ({result['probability']*100:.1f}%)")
            
            return result
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
    
    return None


def main():
    """Main loop: Read Arduino, predict, repeat."""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        logger.info(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud")
        
        time.sleep(2)  # Wait for Arduino initialization
        
        while True:
            reading = read_arduino(ser)
            
            if reading:
                logger.info(f"Reading: {reading}")
                result = send_to_backend(reading)
                
                # Local alerts
                if reading["vibration"] > VIBRATION_ALERT_THRESHOLD:
                    logger.warning(f"⚠️ High vibration: {reading['vibration']:.1f} mm/s")
                
                if reading["temperature"] > TEMPERATURE_ALERT_THRESHOLD:
                    logger.warning(f"⚠️ High temperature: {reading['temperature']:.1f} °C")
            
            time.sleep(0.1)
    
    except serial.SerialException as e:
        logger.error(f"Serial connection error: {e}")
        logger.info("Retrying in 5 seconds...")
        time.sleep(5)
        main()
    
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        ser.close()


if __name__ == "__main__":
    main()
```

**Installation & Lancement** :
```bash
# Installer pyserial
pip install pyserial requests

# Détecter le port COM
python -m serial.tools.list_ports

# Lancer le bridge
python backend/arduino_bridge.py
```

---

## 5. Intégration Backend FastAPI

Ajouter endpoint pour recevoir et traiter les données Arduino :

Fichier : `backend/app/routes/arduino.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path

router = APIRouter(tags=["arduino"])

# Stockage local des readings (en prod : base de données)
ARDUINO_DATA_FILE = Path(__file__).parent.parent.parent / "data" / "arduino_readings.jsonl"


class ArduinoReading(BaseModel):
    equipment_id: str
    values: dict  # {vibration, temperature, humidity, timestamp}


@router.post("/arduino/reading")
async def store_arduino_reading(reading: ArduinoReading):
    """Store Arduino sensor reading in JSONL file."""
    try:
        # Enrich data
        enriched = {
            "timestamp": datetime.now().isoformat(),
            "equipment_id": reading.equipment_id,
            "source": "arduino",
            **reading.values
        }
        
        # Append to JSONL
        ARDUINO_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(ARDUINO_DATA_FILE, "a") as f:
            f.write(json.dumps(enriched) + "\n")
        
        return {"status": "stored", "timestamp": enriched["timestamp"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/arduino/readings")
async def get_arduino_readings(limit: int = 100):
    """Retrieve latest Arduino readings."""
    if not ARDUINO_DATA_FILE.exists():
        return []
    
    readings = []
    with open(ARDUINO_DATA_FILE, "r") as f:
        for line in f.readlines()[-limit:]:
            readings.append(json.loads(line))
    
    return readings
```

**Ajouter dans** `backend/app/main.py` :
```python
from backend.app.routes import arduino

app.include_router(arduino.router)
```

---

## 6. Dashboard - Affichage Temps Réel Arduino

Modifier `frontend/src/api.js` :
```javascript
export async function storeArduinoReading(equipmentId, values) {
  const { data } = await api.post("/arduino/reading", {
    equipment_id: equipmentId,
    values
  });
  return data;
}

export async function getArduinoReadings(limit = 100) {
  const { data } = await api.get(`/arduino/readings?limit=${limit}`);
  return data;
}
```

Créer page Arduino : `frontend/src/pages/Arduino.jsx`

```jsx
import { useQuery } from "@tanstack/react-query";
import { getArduinoReadings } from "../api";
import { Header } from "./Dashboard";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export function Arduino() {
  const { data: readings } = useQuery({
    queryKey: ["arduino-readings"],
    queryFn: () => getArduinoReadings(50),
    refetchInterval: 1000,  // Poll every second
  });

  const chartData = (readings || []).map((r) => ({
    time: new Date(r.timestamp).toLocaleTimeString(),
    vibration: r.vibration,
    temperature: r.temperature,
    humidity: r.humidity,
  }));

  return (
    <div className="space-y-6">
      <Header 
        title="Capteurs Arduino" 
        subtitle="Flux temps réel du prototype IoT" 
      />
      <section className="panel p-5">
        <h3 className="font-semibold mb-4">Vibrations (mm/s)</h3>
        <div className="h-72">
          <ResponsiveContainer>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="vibration" stroke="#ef4444" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}
```

---

## 7. Schéma de Déploiement Complet

```
┌─────────────────────────────────────────────────────────┐
│                   ARCHITECTURE GLOBALE                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Arduino + Capteurs] ──USB───┐                        │
│                                ↓                        │
│                      [PC/Raspberry Pi]                  │
│                           ↓                             │
│                    [Python Bridge]                      │
│                  (arduino_bridge.py)                    │
│                           ↓ HTTP                        │
│  ┌──────────────────────────────────────┐              │
│  │     [FastAPI Backend]                │              │
│  │  - POST /arduino/reading             │              │
│  │  - POST /predict/failure             │              │
│  │  - GET /arduino/readings             │              │
│  └──────────────────────────────────────┘              │
│             ↓ WebSocket/HTTP                           │
│  ┌──────────────────────────────────────┐              │
│  │    [React Frontend]                  │              │
│  │  - Page Arduino avec flux temps réel │              │
│  │  - Alertes et prédictions            │              │
│  └──────────────────────────────────────┘              │
│                                                         │
└─────────────────────────────────────────────────────────┘

Timeline:
- Arduino lit 1 mesure/sec
- Bridge envoie à API toutes les 1-2 sec
- API stocke + prédit
- Dashboard rafraîchit toutes les 1-2 sec
- Alertes générées en temps réel si risque > seuil
```

---

## 8. Test et Validation

### Phase 1 : Test Arduino seul
```bash
# Ouvrir Serial Monitor Arduino IDE
# Settings → Baud Rate 9600
# Vérifie que le JSON s'affiche correctement
```

### Phase 2 : Test Bridge local
```bash
# Lancer Arduino
# Lancer Backend FastAPI
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# Dans un autre terminal, lancer le bridge
python backend/arduino_bridge.py

# Vérifier les logs
```

### Phase 3 : Test Frontend
```bash
# Lancer Frontend
cd frontend && npm run dev

# Aller sur http://localhost:3000/arduino
# Vérifier l'affichage temps réel
```

---

## 9. Points d'Amélioration Future

1. **Persistance** : Remplacer JSONL par TimescaleDB pour historique
2. **MQTT** : Remplacer HTTP par MQTT pour moins de latence
3. **Firmware OTA** : Mise à jour Arduino over-the-air
4. **Calibration Auto** : Auto-étalonnage des capteurs
5. **Alertes Push** : Email/SMS si anomalie détectée
6. **Clustering** : Plusieurs Arduino → même API
7. **Edge ML** : Modèle léger sur Arduino lui-même

---

## 10. Fiche Technique Résumée

| Aspect | Détail |
|--------|--------|
| **Microcontrôleur** | Arduino Uno/Mega ou ESP32 |
| **Capteurs** | Vibration (analogique), Température (DHT22), Pression (BMP280) |
| **Transmission** | USB serial (Arduino) ou Wi-Fi HTTP (ESP32) |
| **Cadence** | 1 mesure/sec (configurable) |
| **Budget** | ~50-100€ materiel |
| **Intégration backend** | 200 lignes Python (bridge) + 100 lignes FastAPI |
| **Affichage** | Page React avec graphiques temps réel |
| **Complexité** | Moyenne - requiert soudure basique et connaissance électronique |

---

## Conclusion

Ce prototype transforme MinePredict d'une application basée sur datasets en un **système IoT réel et fonctionnel**. C'est un excellent argument pour une soutenance : "J'ai non seulement construit un modèle ML, mais j'ai aussi créé un pipeline IoT end-to-end capable d'ingérer des données réelles de capteurs et de générer des prédictions temps réel."
