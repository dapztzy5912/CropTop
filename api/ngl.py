import os
import random
import string
import requests
import time
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Enable CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

class NGLSpammer:
    def __init__(self):
        self.active_attacks = {}

    def deviceId(self):
        characters = string.ascii_lowercase + string.digits
        part1 = ''.join(random.choices(characters, k=8))
        part2 = ''.join(random.choices(characters, k=4))
        part3 = ''.join(random.choices(characters, k=4))
        part4 = ''.join(random.choices(characters, k=4))
        part5 = ''.join(random.choices(characters, k=12))
        device_id = f"{part1}-{part2}-{part3}-{part4}-{part5}"
        return device_id

    def UserAgent(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        ]
        return random.choice(user_agents)

    def send_ngl_message(self, nglusername: str, message: str):
        headers = {
            'Host': 'ngl.link',
            'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'x-requested-with': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'user-agent': f'{self.UserAgent()}',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://ngl.link',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': f'https://ngl.link/{nglusername}',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        data = {
            'username': f'{nglusername}',
            'question': f'{message}',
            'deviceId': f'{self.deviceId()}',
            'gameSlug': '',
            'referrer': '',
        }

        try:
            response = requests.post(
                'https://ngl.link/api/submit', 
                headers=headers, 
                data=data, 
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False

spammer = NGLSpammer()

@app.route('/')
def home():
    return jsonify({
        "message": "NGL Spammer API", 
        "status": "active",
        "endpoints": {
            "/api/start": "POST - Start spam",
            "/api/status": "GET - API status"
        }
    })

@app.route('/api/start', methods=['POST', 'OPTIONS'])
def start_spam():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        nglusername = data.get('username', '').strip()
        message = data.get('message', '').strip()
        count = int(data.get('count', 10))
        delay = float(data.get('delay', 1.0))
        
        if not nglusername or not message:
            return jsonify({'error': 'Username dan pesan harus diisi'}), 400
        
        if count > 50:  # Limit untuk Vercel
            return jsonify({'error': 'Maksimal 50 pesan per request'}), 400
        
        # Simpan attack info
        attack_id = str(int(time.time() * 1000))
        spammer.active_attacks[attack_id] = {
            'username': nglusername,
            'message': message,
            'count': count,
            'delay': delay,
            'sent': 0,
            'failed': 0,
            'started_at': time.time()
        }
        
        # Jalankan spam (sync untuk Vercel)
        results = []
        for i in range(count):
            success = spammer.send_ngl_message(nglusername, message)
            results.append({
                'attempt': i + 1,
                'success': success,
                'timestamp': time.time()
            })
            
            if success:
                spammer.active_attacks[attack_id]['sent'] += 1
            else:
                spammer.active_attacks[attack_id]['failed'] += 1
                
            time.sleep(delay)
        
        # Hitung statistik
        stats = spammer.active_attacks[attack_id]
        success_rate = (stats['sent'] / count) * 100 if count > 0 else 0
        
        return jsonify({
            'attack_id': attack_id,
            'message': 'Spam completed',
            'stats': {
                'sent': stats['sent'],
                'failed': stats['failed'],
                'total': count,
                'success_rate': round(success_rate, 2)
            },
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/status/<attack_id>', methods=['GET'])
def get_status(attack_id):
    if attack_id in spammer.active_attacks:
        return jsonify(spammer.active_attacks[attack_id])
    else:
        return jsonify({'error': 'Attack ID tidak ditemukan'}), 404

@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({
        'status': 'active',
        'active_attacks': len(spammer.active_attacks),
        'timestamp': time.time()
    })

# Handler untuk Vercel
def handler(request, context):
    path = request.path
    method = request.method
    
    # Routing manual untuk Vercel serverless
    if path == '/api/start' and method == 'POST':
        return start_spam()
    elif path.startswith('/api/status'):
        if '/api/status/' in path:
            attack_id = path.split('/api/status/')[-1]
            return get_status(attack_id)
        else:
            return api_status()
    else:
        return home()

if __name__ == '__main__':
    app.run(debug=True)
