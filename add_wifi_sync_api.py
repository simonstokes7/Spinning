with open(r"c:\Data_Projects\Spinning\spinning_server.py", "r", encoding="utf-8") as f:
    server_code = f.read()

# Add /api/server/ip route
ip_route = """import socket

def get_local_wifi_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

@app.route('/api/server/ip', methods=['GET'])
def get_server_ip():
    ip = get_local_wifi_ip()
    return jsonify({
        'ip': ip,
        'port': 8080,
        'url': f"http://{ip}:8080/Latest_Spin_Class_Workout.html",
        'cockpit_url': f"http://{ip}:8080/"
    })
"""

if 'def get_local_wifi_ip():' not in server_code:
    server_code = server_code.replace("app = Flask(__name__, static_folder='.', static_url_path='')", "app = Flask(__name__, static_folder='.', static_url_path='')\n\n" + ip_route)

with open(r"c:\Data_Projects\Spinning\spinning_server.py", "w", encoding="utf-8") as f:
    f.write(server_code)

print("SUCCESS: Added /api/server/ip to spinning_server.py!")
