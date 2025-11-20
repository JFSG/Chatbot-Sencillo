from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import re
from datetime import datetime

app = Flask(__name__)

# Base de datos simple de reservas
reservas = {}

#Horario de apertura formato 24h
HORARIO_APERTURA = "09:00"  # 09:00 
HORARIO_CIERRE = "23:00"    # 23:00 

#menu inventado
MENU = (
    "🍕🍕 Menú del Restaurante inventado 🍕🍕\n"
    "1. Margarita - 8€\n"
    "2. Pepperoni - 10€\n"
    "3. Hawaiana - 9€\n"
    "4. 4 Quesos - 11€\n"
    "5. Ensalada César - 7€\n"
)

#Función para guardar la reserva en un archivo de texto
def guardar_reserva_en_archivo(datos_reserva):
    with open("reservas.txt", "a", encoding="utf-8") as archivo:
        registro = (
            f"Reserva - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -\n "
            f"Datos de la reserva: {datos_reserva['nombre']}\n"
            f"Personas: {datos_reserva['personas']}\n"
            f"Fecha: {datos_reserva['fecha']}\n"
            f"Hora: {datos_reserva['hora']}\n"
            "-----------------------------\n"
           
        )
        archivo.write(registro)


@app.route('/bot', methods=['POST'])
def bot():
    incomin_msg = request.values.get('Body', '').strip()
    numero_usuario = request.values.get('From', '')
    return generar_respuesta(incomin_msg, numero_usuario)

def generar_respuesta(mensaje, numero_usuario):
    resp = MessagingResponse()
    mensaje_lower = mensaje.lower()
    

    # Respuestas generales antes de procesar reservas
    if 'hola' in mensaje_lower:
        respuesta = "¡Hola! Bienvenido(a) al Restaurante Inventado. ¿En qué puedo ayudarte hoy?"

    elif 'menu' in mensaje_lower or 'menú' in mensaje_lower:
        respuesta = MENU
    
    #si no hay reserva iniciada, detectar intención de reserva
    elif numero_usuario not in reservas:
        if 'reservar' in mensaje_lower or 'mesa' in mensaje_lower:
            reservas[numero_usuario] = {"esperando_personas" : True}
            respuesta = "¡Perfecto! ¿Para cuántas personas quieres reservar? (1-4)"
        else:
            respuesta = "Para hacer una reserva, por favor escribe 'reservar' o 'mesa', para ver el menú, por favor escriba 'menú'."
    #paso 1: esperando número de personas
    elif reservas[numero_usuario].get("esperando_personas", False):
        try:
            num_personas = int(mensaje)
            if 1 <= num_personas <= 4:
                # Actualizar el dict en lugar de sobrescribirlo y pasar al siguiente paso
                reservas[numero_usuario].update({
                    "personas": num_personas,
                    "esperando_fecha": True
                })
                reservas[numero_usuario].pop("esperando_personas", None)
                respuesta = "¡Genial!, ¿Para qué fecha quieres la reserva? (formato: DD/MM/AAAA)"
            else:
                respuesta = "❌ Máximo 4 personas. Escribe un número (1-4):"
        except ValueError:
            respuesta = "❌ Por favor, escribe un número válido de personas (1-4):"
    
    # Paso 2: Esperando Fecha
    elif reservas[numero_usuario].get('esperando_fecha', False):
        try:
            # Comparar solo fechas (sin hora) para permitir reservas el mismo día
            fecha = datetime.strptime(mensaje, "%d/%m/%Y").date()
            if fecha >= datetime.now().date():
                reservas[numero_usuario]['fecha'] = mensaje
                reservas[numero_usuario]['esperando_hora'] = True
                reservas[numero_usuario].pop('esperando_fecha', None)
                respuesta = "Perfecto. ¿A qué hora quieres reservar? (formato 24h, ej: 20:30)"
            else:
                respuesta = "❌ La fecha no puede ser en el pasado. Por favor, ingresa una fecha válida (DD/MM/AAAA):"
        except ValueError:
            respuesta = "❌ Formato de fecha inválido. Usa DD/MM/AAAA:"
    
    # Paso 3: Esperando Hora con validación de horario
    elif reservas[numero_usuario].get('esperando_hora', False):
        if re.match(r'^(?:[01]\d|2[0-3]):[0-5]\d$', mensaje):
            # Parsear horas para comparar correctamente con el horario de apertura/cierre
            hora_reserva_time = datetime.strptime(mensaje, "%H:%M").time()
            apertura = datetime.strptime(HORARIO_APERTURA, "%H:%M").time()
            cierre = datetime.strptime(HORARIO_CIERRE, "%H:%M").time()
            if apertura <= hora_reserva_time <= cierre:
                reservas[numero_usuario].update({
                    'hora': mensaje,
                    'esperando_nombre': True
                })
                reservas[numero_usuario].pop('esperando_hora', None)
                respuesta = "Casi listo. ¿Podrías proporcionarme tu nombre para la reserva?"
            else:
                respuesta = f"❌ Lo siento, nuestro horario de atención es de {HORARIO_APERTURA} a {HORARIO_CIERRE}. Por favor, elige una hora dentro de este rango:"
        else:
            respuesta = "❌ Hora inválida. Usa formato 24h (ej: 20:30):"
    
    # Paso 4: Esperando Nombre
    elif reservas[numero_usuario].get('esperando_nombre', False):
        reservas[numero_usuario]['nombre'] = mensaje
        del reservas[numero_usuario]['esperando_nombre']

        #Mostrar resumen de la reserva
        resumen = (
        "✅ ¡Reserva confirmada!\n"
        f"Nombre: {reservas[numero_usuario]['nombre']}\n"
        f"Personas: {reservas[numero_usuario]['personas']}\n"
        f"Fecha: {reservas[numero_usuario]['fecha']}\n"
        f"Hora: {reservas[numero_usuario]['hora']}\n"
        "Gracias por elegir Restaurante Inventado. ¡Te esperamos!"
        )
        respuesta = resumen
        #Guardar reserva en archivo antes de eliminarla
        guardar_reserva_en_archivo(reservas[numero_usuario])
        #Eliminar reserva completada
        del reservas[numero_usuario]

    else:
        respuesta = "Para hacer una reserva, por favor escribe 'reservar' o 'mesa', para ver el menú, por favor escriba 'menú'."
    
    resp.message(respuesta)
    return str(resp)
            

if __name__ == '__main__':
    app.run(port=5000)