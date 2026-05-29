from flask import Flask, jsonify
import os
import requests


app = Flask(__name__)


def get_summary_url():
    return os.getenv('DJANGO_SYSTEM_SUMMARY_URL', 'http://monolito_django:8000/api/system/summary/')


@app.get('/api/v1/reports/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'micro_reportes'}), 200


@app.get('/api/v1/reports/summary')
def reports_summary():
    try:
        response = requests.get(
            get_summary_url(),
            timeout=8,
            headers={'Host': 'localhost'},
        )
        response.raise_for_status()
        summary = response.json()
    except Exception as exc:
        return jsonify({
            'error': 'No fue posible consultar el resumen desde Django.',
            'details': str(exc),
        }), 503

    return jsonify({
        'source': 'django-summary',
        'summary': summary,
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)