import json
import io
import base64
from collections import deque
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import requests
from flask import Flask, render_template_string, url_for
from apscheduler.schedulers.background import BackgroundScheduler

# --- Загрузка конфигурации ---
def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "server_location": "Unknown Location",
            "check_interval_minutes": 1, 
            "retention_hours": 72, 
            "targets": [{"name": "Google", "url": "https://google.com"}]
        }

config = load_config()
MAX_POINTS = config['retention_hours'] * 60
targets = config['targets']
# Извлекаем локацию для отображения
LOCATION = config.get('server_location', 'Default Server')
data_store = {t['name']: deque(maxlen=MAX_POINTS) for t in targets}

app = Flask(__name__)

def check_availability():
    timestamp = datetime.now()
    for target in targets:
        try:
            response = requests.get(target['url'], timeout=5)
            status = 1 if response.status_code == 200 else 0
        except:
            status = 0
        data_store[target['name']].append((timestamp, status))

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_availability, trigger="interval", minutes=config['check_interval_minutes'])
scheduler.start()

def generate_plot():
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 7))
    
    for i, (name, data) in enumerate(data_store.items()):
        if not data: continue
        times, statuses = zip(*data)
        offset = i * 0.04
        ax.step(times, [s + offset for s in statuses], where='post', label=name, linewidth=2.5)

    ax.set_ylim(-0.1, 1.5)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['OFFLINE', 'ONLINE'], fontsize=10, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.1)
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), 
              ncol=min(len(targets), 4), frameon=True, facecolor='#1a1d2b', fontsize=10)
    
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', transparent=True, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return plot_url

@app.route('/')
def index():
    plot_url = generate_plot()
    
    all_online = all(d[-1][1] == 1 for d in data_store.values() if d)
    uptime_text = "System Operational" if all_online else "Issues Detected"
    status_color = "#28a745" if all_online else "#dc3545"

    html = f'''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>{LOCATION} | Monitor</title>
        <link rel="icon" href="{{{{ url_for('static', filename='favicon.ico') }}}}">
        <meta http-equiv="refresh" content="60">
        <style>
            :root {{ --main-bg: #0f111a; --card-bg: #1a1d2b; --accent: #007bff; }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: var(--main-bg); color: #e1e1e1; margin: 0; }}
            
            header {{ background: var(--card-bg); padding: 20px 50px; display: flex; align-items: center; border-bottom: 4px solid var(--accent); }}
            .logo {{ height: 60px; margin-right: 25px; }}
            .brand-name {{ font-size: 26px; font-weight: 800; color: #fff; text-transform: uppercase; letter-spacing: 1px; }}
            .location-tag {{ font-size: 18px; color: orange; margin-left: auto; font-weight: bold; border: 1px solid orange; padding: 5px 15px; border-radius: 5px; }}
            
            .container {{ max-width: 1200px; margin: 40px auto; padding: 0 20px; }}
            .card {{ background: var(--card-bg); border-radius: 15px; padding: 35px; box-shadow: 0 15px 40px rgba(0,0,0,0.6); }}
            
            .status-bar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 20px; }}
            .indicator {{ padding: 8px 20px; border-radius: 30px; font-size: 13px; font-weight: bold; background: {status_color}; color: white; box-shadow: 0 0 15px {status_color}55; }}
            
            .graph-area {{ margin-top: 30px; text-align: center; }}
            img.main-plot {{ width: 100%; border-radius: 10px; }}
            
            footer {{ margin-top: 60px; text-align: center; color: #444; font-size: 12px; padding-bottom: 30px; border-top: 1px solid #222; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <header>
            <img src="{{{{ url_for('static', filename='logo.png') }}}}" class="logo" alt="TriolCorp Logo">
            <div class="brand-name">TriolCorp <span style="font-weight: 300; color: var(--accent);">Network Intelligence</span></div>
            <div class="location-tag">{LOCATION}</div>
        </header>

        <div class="container">
            <div class="card">
                <div class="status-bar">
                    <div>
                        <h2 style="margin:0; letter-spacing: 0.5px;">Connectivity Retrospective</h2>
                        <div style="color: #666; font-size: 14px; margin-top: 8px;">Analysis Window: {config['retention_hours']} Hours</div>
                    </div>
                    <div class="indicator">{uptime_text}</div>
                </div>
                
                <div class="graph-area">
                    <img src="data:image/png;base64,{plot_url}" class="main-plot">
                </div>
            </div>

            <footer>
                &copy; {datetime.now().year} TriolCorp Monitoring Service. Current Time: {datetime.now().strftime('%H:%M:%S')}
            </footer>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    check_availability()
    app.run(host='0.0.0.0', port=5000, debug=False)
