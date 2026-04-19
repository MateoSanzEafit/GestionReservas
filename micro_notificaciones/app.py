from flask import Flask, request, jsonify
import uuid
import datetime

app = Flask(__name__)

@app.route('/api/v2/notificaciones/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "micro_notificaciones"}), 200

@app.route('/api/v2/notificaciones/send', methods=['POST'])
def send_notification():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    required_fields = ['usuario_id', 'mensaje']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
            
    # Simulación de envío
    notification_id = str(uuid.uuid4())
    print(f"[NOTIF] Enviando mensaje a {data['usuario_id']}: {data['mensaje']}")
    
    return jsonify({
        "id": notification_id,
        "status": "ENVIADO",
        "timestamp": datetime.datetime.now().isoformat(),
        "details": {
            "usuario_id": data['usuario_id'],
            "mensaje": data['mensaje'],
            "reserva_id": data.get('reserva_id')
        }
    }), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
