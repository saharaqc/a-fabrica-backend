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
app.config['MAIL_SERVER'] = 'smtp.ionos.es'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_IONOS')
app.config['MAIL_PASSWORD'] = os.environ.get('PASS_IONOS')
app.config['MAIL_DEFAULT_SENDER'] = ('A Fábrica', os.environ.get('EMAIL_IONOS'))

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
            'muebles': 'Solo Mobiliario',
            'consulta': 'Consulta General'
        }
        
        budgets = {
            '5k-15k': '500€ - 3.000€',
            '15k-30k': '3.000€ - 7.000€',
            '30k-50k': '7.000€ - 15.000€',
            '50k+': 'Más de 15.000€',
            'consultar': 'Prefiero consultar'
        }
        
        # 🔧 LÍNEA CORREGIDA - eliminar caracteres problemáticos
        admin_email_body = f"""Nueva consulta desde el sitio web de A Fábrica

DATOS DEL CLIENTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nombre: {data['name']}
Email: {data['email']}
Teléfono: {data.get('phone', 'No proporcionado')}

DETALLES DEL PROYECTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tipo de proyecto: {project_types.get(data['projectType'], data['projectType'])}
Presupuesto: {budgets.get(data.get('budget', ''), data.get('budget', 'No especificado'))}
Fecha deseada de inicio: {data.get('startDate', 'No especificada')}

MENSAJE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data['message']}

ENVIADO EL: {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}
        """
        
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            try:
                # 1. Enviar email al administrador
                admin_msg = Message(
                    subject=subject,
                    recipients=[ADMIN_EMAIL],
                    body=admin_email_body,
                    sender=('A Fábrica', app.config['MAIL_USERNAME'])
                )
                mail.send(admin_msg)
                print(f"✅ Email enviado a {ADMIN_EMAIL}")
                
                # 2. Enviar email de confirmación al cliente con HTML
                client_subject = "Confirmación - Hemos recibido tu consulta"
                
                # 🎨 TEMPLATE HTML CORREGIDO con colores de marca
                client_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirmación A Fábrica</title>
    <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;700&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
</head>
<body style="margin: 0; padding: 0; font-family: 'Rubik', sans-serif; background-color: #F5F5F5;">
    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #F5F5F5;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table cellpadding="0" cellspacing="0" border="0" width="600" style="background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #084D4B 0%, #62A4A1 100%); padding: 30px; text-align: center; border-radius: 12px 12px 0 0;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: 700; font-family: 'Playfair Display', serif;">
                                <span style="color: #CF5138;">A</span> F<span style="color: #CF5138;">á</span>brica
                            </h1>
                            <p style="color: #ffffff; margin: 10px 0 0 0; opacity: 0.9; font-family: 'Rubik', sans-serif; font-size: 16px;">Centro de diseño y producción de mobiliario, carpintería e interiorismo</p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="color: #084D4B; margin: 0 0 20px 0; font-size: 28px; font-family: 'Playfair Display', serif; font-weight: 700;">Hola <span style="color: #CF5138;">{data['name']}</span>,</h2>
                            
                            <p style="color: #2C2C2C; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0; font-family: 'Rubik', sans-serif;">
                                <strong>Gracias por contactar con <span style="font-family: 'Playfair Display', serif;"><span style="color: #CF5138;">A</span> F<span style="color: #CF5138;">á</span>brica</span>.</strong> Hemos recibido tu consulta y nos pondremos en contacto contigo en las próximas <strong style="color: #CF5138;">24 horas</strong>.
                            </p>
                            
                            <!-- Project Details Box -->
                            <div style="background-color: #F5F5F5; padding: 25px; border-radius: 8px; border-left: 4px solid #CF5138; margin: 25px 0;">
                                <h3 style="color: #084D4B; margin: 0 0 15px 0; font-size: 20px; font-family: 'Playfair Display', serif; font-weight: 700;">Detalles de tu consulta:</h3>
                                <p style="color: #2C2C2C; margin: 8px 0; font-size: 15px; font-family: 'Rubik', sans-serif;"><strong>Proyecto:</strong> {project_types.get(data['projectType'], data['projectType'])}</p>
                                <p style="color: #2C2C2C; margin: 8px 0; font-size: 15px; font-family: 'Rubik', sans-serif;"><strong>Fecha de solicitud:</strong> {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</p>
                            </div>
                            
                            <div style="background: linear-gradient(135deg, #F5F5F5 0%, #ffffff 100%); padding: 20px; border-radius: 8px; border: 1px solid #62A4A1; margin: 25px 0;">
                                <p style="color: #2C2C2C; font-size: 16px; line-height: 1.6; margin: 0; font-family: 'Rubik', sans-serif; font-style: italic;">
                                    En <span style="font-family: 'Playfair Display', serif;"><span style="color: #CF5138;">A</span> F<span style="color: #CF5138;">á</span>brica</span>, cada proyecto es una historia contada en forma, función y detalle. 
                                    <strong style="color: #CF5138;">Estamos emocionados de escucharte, enseñarte y acompañarte</strong> 
                                    a hacer realidad tu proyecto.
                                </p>
                            </div>
                            
                            <p style="color: #2C2C2C; font-size: 16px; line-height: 1.6; margin: 30px 0 0 0; font-family: 'Rubik', sans-serif;">
                                <strong>Lo hacemos simple, bien y contigo,</strong><br>
                                <span style="color: #084D4B; font-weight: 500;">El equipo de <span style="font-family: 'Playfair Display', serif;"><span style="color: #CF5138;">A</span> F<span style="color: #CF5138;">á</span>brica</span></span>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #2C2C2C; padding: 30px; border-radius: 0 0 12px 12px;">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="text-align: center;">
                                        <h3 style="color: #ffffff; margin: 0 0 20px 0; font-size: 20px; font-family: 'Playfair Display', serif; font-weight: 700;">
                                            <span style="color: #CF5138;">A</span> F<span style="color: #CF5138;">á</span>brica
                                        </h3>
                                        <p style="color: #BAA88F; margin: 8px 0; font-size: 14px; font-family: 'Rubik', sans-serif;">
                                            <strong>Web:</strong> <a href="https://a-fabrica.es" style="color: #CF5138; text-decoration: none;">a-fabrica.es</a>
                                        </p>
                                        <p style="color: #BAA88F; margin: 8px 0; font-size: 14px; font-family: 'Rubik', sans-serif;">
                                            <strong>Email:</strong> <a href="mailto:info@a-fabrica.es" style="color: #CF5138; text-decoration: none;">info@a-fabrica.es</a>
                                        </p>
                                        <p style="color: #BAA88F; margin: 8px 0; font-size: 14px; font-family: 'Rubik', sans-serif;">
                                            <strong>Teléfono:</strong> <a href="tel:+34604200388" style="color: #CF5138; text-decoration: none;">+34 604 200 388</a>
                                        </p>
                                        <p style="color: #62A4A1; margin: 15px 0 0 0; font-size: 13px; font-family: 'Rubik', sans-serif; font-style: italic;">
                                            Vigo, España
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

                # Versión texto como fallback
                client_text = f"""Hola {data['name']},

Gracias por contactar con A Fábrica. Hemos recibido tu consulta y nos pondremos en contacto contigo en las próximas 24 horas.

Detalles de tu consulta:
• Proyecto: {project_types.get(data['projectType'], data['projectType'])}
• Fecha de solicitud: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}

En A Fábrica, cada proyecto es una historia contada en forma, función y detalle. Estamos emocionados de escucharte, enseñarte y acompañarte a hacer realidad tu proyecto.

Lo hacemos simple, bien y contigo,
El equipo de A Fábrica

---
A Fábrica - Centro de diseño y producción de mobiliario, carpintería e interiorismo
Web: https://a-fabrica.es
Email: info@a-fabrica.es
Teléfono: +34 604 200 388
Vigo, España
"""
                
                confirmation_msg = Message(
                    subject=client_subject,
                    recipients=[data['email']],
                    html=client_html,
                    body=client_text,
                    sender=('A Fábrica', app.config['MAIL_USERNAME'])
                )
                mail.send(confirmation_msg)
                print(f"✅ Email de confirmación HTML enviado a {data['email']}")
                
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
