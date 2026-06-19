import os
import re
import yaml
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'playbook_templates')
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True, lstrip_blocks=True)

def generate_playbook(header_vars, tasks_list):
    """
    Generates an Ansible Playbook (YAML string) from header variables and a list of task configurations.
    
    header_vars: dict with keys like 'playbook_name', 'target_hosts', 'become_privilege'
    tasks_list: list of dicts, each representing a task:
                e.g., {'type': 'install_nginx', 'nginx_service_state': 'started', ...}
    """
    try:
        # 1. Render the header
        header_template = env.get_template('header.yml.j2')
        playbook_content = header_template.render(header_vars)
        if not playbook_content.endswith('\n'):
            playbook_content += '\n'
        
        # 2. Append tasks
        for task in tasks_list:
            task_type = task.get('type')
            
            # Preprocess tasks to avoid list rendering issues in templates
            if task_type == 'deploy_container':
                env_str = task.get('container_env', '')
                if isinstance(env_str, str):
                    task['container_env'] = [line.strip() for line in env_str.splitlines() if line.strip()]
                    
            template_filename = f"{task_type}.yml.j2"
            
            try:
                task_template = env.get_template(template_filename)
                rendered_task = task_template.render(task)
                playbook_content += rendered_task + "\n"
            except Exception as e:
                playbook_content += f"    # [ERROR rendering task '{task_type}': {str(e)}]\n\n"
                
        return playbook_content
    except Exception as e:
        return f"# Error generating playbook: {str(e)}"

def generate_inventory(ip, user, key_path=None, password=None, target_hosts='target_servers'):
    """
    Generates an Ansible inventory INI content.
    """
    if not ip:
        return "[servers]\nlocalhost ansible_connection=local"
        
    line = f"{ip} ansible_user={user}"
    if key_path:
        line += f" ansible_ssh_private_key_file={key_path}"
    if password:
        line += f" ansible_ssh_pass={password}"
        
    # Standard connection option to avoid host key checking prompts
    line += " ansible_ssh_extra_args='-o StrictHostKeyChecking=no'"
    
    group_name = 'target_servers' if target_hosts == 'all' else target_hosts
    content = f"[{group_name}]\n{line}\n"
    return content

def run_risk_assessment(playbook_yaml, tasks_list):
    """
    Analyzes the tasks list and the generated playbook YAML for potential security and configuration risks.
    Returns a list of dicts: [{'task': '...', 'risk': 'High/Medium/Low', 'reason': '...', 'suggestion': '...'}]
    """
    risks = []
    
    # 1. Check for become: yes without critical packages
    if "become: yes" in playbook_yaml or "become: true" in playbook_yaml:
        # Verify if become is generally justified
        has_privileged_task = False
        for task in tasks_list:
            if task.get('type') in ['install_nginx', 'install_docker', 'create_user', 'firewall']:
                has_privileged_task = True
                break
        if not has_privileged_task:
            risks.append({
                'task': 'Global Become Privilege',
                'risk': 'Low',
                'reason': 'The playbook is run with global "become: yes" (root access), but no package installs or user creations are explicitly selected.',
                'suggestion': 'Disable global become privilege if all tasks can be executed under a normal unprivileged user.'
            })

    # 2. Check for unsafe custom commands
    for task in tasks_list:
        if task.get('type') == 'custom_command':
            cmd = task.get('custom_command_body', '')
            cmd_lower = cmd.lower()
            
            # Critical/High risks
            if 'rm -rf' in cmd:
                risks.append({
                    'task': 'Custom Command: rm -rf',
                    'risk': 'High',
                    'reason': f'Custom command contains "rm -rf". This could lead to accidental or catastrophic file deletion.',
                    'suggestion': 'Ensure the target path is strictly correct and never uses unvalidated path variables.'
                })
            if 'chmod 777' in cmd or 'chmod -r 777' in cmd_lower:
                risks.append({
                    'task': 'Custom Command: chmod 777',
                    'risk': 'Medium',
                    'reason': 'Setting full read-write-execute permissions (777) creates a significant security vulnerability.',
                    'suggestion': 'Use restrictive permissions like 755 for directories and 644 for files.'
                })
            if 'curl' in cmd_lower and ('| sh' in cmd_lower or '| bash' in cmd_lower):
                risks.append({
                    'task': 'Custom Command: Piping Curl to Shell',
                    'risk': 'High',
                    'reason': 'Downloading scripts directly from the web and executing them without inspection is a major remote code execution risk.',
                    'suggestion': 'Download the script to a temp file, inspect/verify its checksum, and run it locally, or use official packages.'
                })
            if 'passwd' in cmd_lower:
                risks.append({
                    'task': 'Custom Command: Password Modification',
                    'risk': 'Medium',
                    'reason': 'Modifying passwords via direct custom script commands can expose credentials in process lists or logs.',
                    'suggestion': 'Use Ansible\'s built-in "user" module with a salted/hashed password.'
                })

        # 3. Firewall checking
        elif task.get('type') == 'firewall':
            port_str = str(task.get('firewall_port', '80'))
            
            # Common database/management ports
            db_ports = {
                '3306': 'MySQL',
                '5432': 'PostgreSQL',
                '27017': 'MongoDB',
                '6379': 'Redis'
            }
            sec_ports = {
                '22': 'SSH',
                '23': 'Telnet',
                '3389': 'RDP'
            }
            
            if port_str in db_ports:
                risks.append({
                    'task': f'Firewall: Open {db_ports[port_str]} Port ({port_str})',
                    'risk': 'High',
                    'reason': f'Opening database port {port_str} to the public network allows brute-force and zero-day exposure.',
                    'suggestion': f'Restrict access to {db_ports[port_str]} to private VPC IP ranges or secure VPN IPs only.'
                })
            elif port_str in sec_ports:
                risks.append({
                    'task': f'Firewall: Open {sec_ports[port_str]} Port ({port_str})',
                    'risk': 'Medium',
                    'reason': f'Opening administrative {sec_ports[port_str]} port globally poses an intelligence and exploitation target.',
                    'suggestion': f'Use specialized security groups or host firewalls that restrict ingress to trusted bastion/office CIDRs.'
                })

    return risks
