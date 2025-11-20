# Chatbot de Reservas - Restaurante Inventado

Pequeña aplicación Flask que simula un chatbot para gestionar reservas vía mensajes (pensado para integrarse con Twilio/WhatsApp). Guarda reservas en `reservas.txt`.

**Requisitos**:
- Python 3.8+
- `flask`
- `twilio`

## Instalación rápida (Windows PowerShell)
1. Crear y activar entorno virtual:
```powershell
python -m venv venv
.\venv\Scripts\activate
```
2. Instalar dependencias:
```powershell
pip install flask twilio
```

## Ejecutar la aplicación
```powershell
# activar el entorno si no está activo
.\venv\Scripts\activate
python .\main.py
```
La aplicación arranca en `http://127.0.0.1:5000` por defecto.

## Exponer con ngrok (para Twilio webhook)
Si usas ngrok en otra terminal (cmd), ejecuta:
```powershell
ngrok http 5000
```
Copia la URL pública que te dé ngrok (por ejemplo `https://abcd1234.ngrok.io`) y configura en Twilio el webhook de mensajes entrantes a:
```
https://<tu-ngrok>.ngrok.io/bot
```

## Flujo de reserva (ejemplo)
1. Enviar `reservar` o `mesa`.
2. Responder número de personas (1-4).
3. Responder fecha en `DD/MM/AAAA`.
4. Responder hora en formato 24h `HH:MM` (dentro del horario de apertura).
5. Proporcionar nombre.

## Archivo de reservas
- Las reservas se añaden en texto plano al archivo `reservas.txt` junto con la fecha/hora del registro.

## Notas y recomendaciones
- Si quieres persistencia más robusta, considera usar JSON, SQLite o una base de datos.

## Conversión rápida a JSON (fácil)
Si prefieres guardar las reservas en un archivo JSON en lugar de `reservas.txt`, sustituye la función `guardar_reserva_en_archivo` por algo así:

```python
import json
from pathlib import Path

RESERVAS_JSON = Path('reservas.json')

def guardar_reserva_json(datos_reserva):
	data = []
	if RESERVAS_JSON.exists():
		try:
			with RESERVAS_JSON.open('r', encoding='utf-8') as f:
				data = json.load(f)
		except (ValueError, json.JSONDecodeError):
			data = []
	data.append(datos_reserva)
	with RESERVAS_JSON.open('w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=2)

# Llamar a guardar_reserva_json en lugar de guardar_reserva_en_archivo
```

Esto mantiene un array de reservas en `reservas.json` y es fácil de leer/editar.

## Conversión rápida a SQLite (más robusto)
Para usar SQLite (archivo local) con consultas sencillas, crea una pequeña utilidad usando el módulo `sqlite3` incluido en la stdlib:

```python
import sqlite3
from pathlib import Path

DB_PATH = Path('reservas.db')

def init_db():
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	c.execute('''
		CREATE TABLE IF NOT EXISTS reservas (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			nombre TEXT,
			personas INTEGER,
			fecha TEXT,
			hora TEXT,
			creado_en TEXT
		)
	''')
	conn.commit()
	conn.close()

def guardar_reserva_sqlite(datos_reserva):
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	c.execute(
		'INSERT INTO reservas (nombre, personas, fecha, hora, creado_en) VALUES (?,?,?,?,?)',
		(datos_reserva.get('nombre'), datos_reserva.get('personas'), datos_reserva.get('fecha'), datos_reserva.get('hora'), datos_reserva.get('creado_en'))
	)
	conn.commit()
	conn.close()

# Ejecutar init_db() al arrancar la app y llamar a guardar_reserva_sqlite cuando confirmes la reserva
```

