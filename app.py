# app.py - Backend Flask para A Fábrica
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import os
from datetime import datetime
import json

app = Flask(__name__)

# Configuración CORS
if os.environ.get('ENVIRONMENT') == 'production':
    CORS(app, origins=[
        'https://a-fabrica.es', 
        'https://www.a-fabrica.es',
        'http://localhost:5173',
        'http://localhost:3000'
    ])
else:
    CORS(app)

# Configuración de email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER')

mail = Mail(app)

# Email de destino
ADMIN_EMAIL = 'info@a-fabrica.es'

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'A Fábrica Contact API - Funcionando correctamente',
        'status': 'active',
        'endpoints': {
            'contact': '/api/contact [POST]',
            'health': '/api/health [GET]'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'OK', 
        'message': 'API funcionando correctamente',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/contact', methods=['POST'])
def handle_contact():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False, 
                'message': 'No se recibieron datos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['name', 'email', 'projectType', 'message']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False, 
                'message': f'Campos requeridos faltantes: {", ".join(missing_fields)}'
            }), 400
        
        # Preparar email para el administrador
        subject = f"Nueva consulta de {data['name']} - A Fábrica"
        
        project_types = {
            'residencial': 'Residencial',
            'comercial': 'Comercial', 
            'institucional': 'Institucional',
            'muebles': 'Solo Muebles',
            'consulta': 'Consulta General'
        }
        
        budgets = {
            '5k-15k': '500€ - 3.000€',
            '15k-30k': '3.000€ - 7.000€',
            '30k-50k': '7.000€ - 15.000€',
            '50k+': 'Más de 15.000€',
            'consultar': 'Prefiero consultar'
        }
        
        admin_email_body = f"""
Nueva consulta desde el sitio web de A Fábrica

📋 DATOS DEL CLIENTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nombre: {data['name']}
Email: {data['email']}
Teléfono: {data.get('phone', 'No proporcionado')}

📦 DETALLES DEL PROYECTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tipo de proyecto: {project_types.get(data['projectType'], data['projectType'])}
Presupuesto: {budgets.get(data.get('budget', ''), data.get('budget', 'No especificado'))}
Fecha deseada de inicio: {data.get('startDate', 'No especificada')}

💬 MENSAJE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data['message']}

⏰ ENVIADO EL: {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}
        """
        
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            try:
                # 1. Enviar email al administrador
                admin_msg = Message(
                    subject=subject,
                    recipients=[ADMIN_EMAIL],
                    body=admin_email_body
                )
                mail.send(admin_msg)
                print(f"✅ Email enviado a {ADMIN_EMAIL}")
                
                # 2. Enviar email de confirmación al cliente
                client_subject = "Bienvenido al espacio donde tu historia comienza"
                client_body = f"""Hola {data['name']},

Gracias por contactar con A Fábrica. Hemos recibido tu consulta y nos pondremos en contacto contigo en un plazo máximo de 24 horas.

Detalles de tu consulta:
• Proyecto: {project_types.get(data['projectType'], data['projectType'])}
• Fecha de solicitud: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}

En A Fábrica, cada proyecto es una historia contada en forma, función y detalle. 
Estamos emocionados de escucharte, enseñarte y acompañarte a hacerlo realidad.

Estamos ansiosos por conocerte,
El equipo de A Fábrica

---
A Fábrica - Centro de diseño y producción de mobiliario, carpintería e interiorismo
Web: https://a-fabrica.es
Email: info@a-fabrica.es
Teléfono: +34 604 200 388
"""
                
                confirmation_msg = Message(
                    subject=client_subject,
                    recipients=[data['email']],
                    body=client_body
                )
                mail.send(confirmation_msg)
                print(f"✅ Email de confirmación enviado a {data['email']}")
                
            except Exception as email_error:
                print(f"❌ Error enviando emails: {email_error}")
                # No fallar si hay error de email, pero log it
        
        # Guardar en logs
        print(f"📝 NUEVO CONTACTO: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        return jsonify({
            'success': True,
            'message': 'Mensaje enviado correctamente. Te contactaremos pronto.'
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor. Inténtalo más tarde.'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('ENVIRONMENT') != 'production'

    app.run(host='0.0.0.0', port=port, debug=debug)
