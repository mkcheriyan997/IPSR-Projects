import os
import json
from flask import Flask, render_template, request, jsonify, Response, send_file
from app.database import (
    init_db, save_playbook, get_playbooks, get_playbook,
    create_run, get_runs, get_run
)
from app.generator import generate_playbook, generate_inventory, run_risk_assessment
from app.executor import execute_ansible_async
from app.gitops import push_to_gitops

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize database on startup
init_db()

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """
    Receives JSON containing configuration and task selections.
    Generates Ansible Playbook, Inventory, runs Risk Advisor, and saves to Database.
    """
    try:
        data = request.json or {}
        
        name = data.get('name', 'AutoPlay Server Provisioning')
        target_hosts = data.get('target_hosts', 'all')
        become_privilege = data.get('become_privilege', 'yes')
        
        # Target details for Inventory
        ip = data.get('ip', '')
        user = data.get('user', 'ec2-user')
        key_path = data.get('key_path', '')
        password = data.get('password', '')
        
        # List of configured tasks
        tasks = data.get('tasks', [])
        
        # 1. Generate Playbook YAML
        header_vars = {
            'playbook_name': name,
            'target_hosts': target_hosts,
            'become_privilege': become_privilege
        }
        playbook_yaml = generate_playbook(header_vars, tasks)
        
        # 2. Generate Inventory INI
        inventory_ini = generate_inventory(ip, user, key_path, password, target_hosts)
        
        # 3. Static Security Risk Assessment
        risks = run_risk_assessment(playbook_yaml, tasks)
        
        # 4. Save to Database
        playbook_id = save_playbook(
            name=name,
            target_hosts=target_hosts,
            become_privilege=become_privilege,
            tasks=tasks,
            playbook_yaml=playbook_yaml,
            inventory_ini=inventory_ini
        )
        
        # 5. Push to GitOps repository automatically
        push_to_gitops(playbook_yaml, inventory_ini)
        
        return jsonify({
            'success': True,
            'playbook_id': playbook_id,
            'playbook_yaml': playbook_yaml,
            'inventory_ini': inventory_ini,
            'risks': risks
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/playbook/<int:playbook_id>')
def view_playbook(playbook_id):
    playbook = get_playbook(playbook_id)
    if not playbook:
        return "Playbook not found", 404
    return render_template('preview.html', playbook=playbook)

@app.route('/playbook/<int:playbook_id>/download-playbook')
def download_playbook_file(playbook_id):
    playbook = get_playbook(playbook_id)
    if not playbook:
        return "Playbook not found", 404
    
    filename = f"playbook_{playbook_id}.yml"
    response = Response(playbook['playbook_yaml'], mimetype='text/yaml')
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

@app.route('/playbook/<int:playbook_id>/download-inventory')
def download_inventory_file(playbook_id):
    playbook = get_playbook(playbook_id)
    if not playbook:
        return "Playbook not found", 404
    
    filename = f"inventory_{playbook_id}.ini"
    response = Response(playbook['inventory_ini'], mimetype='text/plain')
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

@app.route('/api/run', methods=['POST'])
def api_run_playbook():
    """
    Executes a saved playbook asynchronously.
    """
    try:
        data = request.json or {}
        playbook_id = data.get('playbook_id')
        ip = data.get('ip', 'localhost')
        private_key = data.get('private_key', '')
        is_dry_run = data.get('is_dry_run', False)
        
        if not playbook_id:
            return jsonify({'success': False, 'error': 'Playbook ID is required'}), 400
            
        playbook = get_playbook(playbook_id)
        if not playbook:
            return jsonify({'success': False, 'error': 'Playbook not found'}), 404
            
        # Create execution record in database
        run_id = create_run(playbook_id, ip)
        
        # Start background Ansible process
        execute_ansible_async(
            run_id=run_id,
            playbook_id=playbook_id,
            ip=ip,
            private_key_content=private_key if private_key else None,
            is_dry_run=is_dry_run
        )
        
        return jsonify({
            'success': True,
            'run_id': run_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/console/<int:run_id>')
def console(run_id):
    run = get_run(run_id)
    if not run:
        return "Execution log not found", 404
    return render_template('console.html', run=run)

@app.route('/api/run/<int:run_id>/logs')
def api_get_logs(run_id):
    run = get_run(run_id)
    if not run:
        return jsonify({'success': False, 'error': 'Run not found'}), 404
        
    return jsonify({
        'success': True,
        'status': run['status'],
        'logs': run['logs']
    })

@app.route('/history')
def history():
    runs = get_runs()
    return render_template('history.html', runs=runs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
