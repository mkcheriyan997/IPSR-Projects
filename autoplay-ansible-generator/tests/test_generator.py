import sys
import os
import unittest
import yaml

# Adjust path to import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.generator import generate_playbook, generate_inventory, run_risk_assessment

class TestPlaybookGenerator(unittest.TestCase):

    def test_generate_inventory_local(self):
        result = generate_inventory('', 'ec2-user')
        self.assertIn('localhost ansible_connection=local', result)

    def test_generate_inventory_remote(self):
        result = generate_inventory('13.60.20.10', 'admin', '/path/to/key.pem')
        self.assertIn('13.60.20.10', result)
        self.assertIn('ansible_user=admin', result)
        self.assertIn('ansible_ssh_private_key_file=/path/to/key.pem', result)

    def test_run_risk_assessment_rm_rf(self):
        tasks = [
            {
                'type': 'custom_command',
                'custom_command_name': 'Remove temp files',
                'custom_command_body': 'rm -rf /tmp/test'
            }
        ]
        playbook_yaml = "become: yes\ntasks:\n  - name: Remove temp files\n    ansible.builtin.shell: rm -rf /tmp/test"
        risks = run_risk_assessment(playbook_yaml, tasks)
        
        # Verify rm -rf was flagged as High risk
        high_risks = [r for r in risks if r['risk'] == 'High' and 'rm -rf' in r['task']]
        self.assertTrue(len(high_risks) > 0)

    def test_run_risk_assessment_firewall(self):
        tasks = [
            {
                'type': 'firewall',
                'firewall_port': '3306',
                'firewall_protocol': 'tcp'
            }
        ]
        playbook_yaml = "tasks:\n  - name: Open Port 3306\n    ansible.builtin.firewalld:\n      port: 3306/tcp"
        risks = run_risk_assessment(playbook_yaml, tasks)
        
        # Verify mysql database port is flagged
        db_risks = [r for r in risks if r['risk'] == 'High' and '3306' in r['task']]
        self.assertTrue(len(db_risks) > 0)

    def test_deploy_container_env_parsing(self):
        tasks = [
            {
                'type': 'deploy_container',
                'container_name': 'test-app',
                'container_image': 'nginx:alpine',
                'container_ports': '8080:80',
                'container_env': 'ENV_VAR1=value1\nENV_VAR2=value2'
            }
        ]
        result = generate_playbook({'playbook_name': 'Test Env', 'target_hosts': 'all', 'become_privilege': 'yes'}, tasks)
        self.assertIn('-e "ENV_VAR1=value1"', result)
        self.assertIn('-e "ENV_VAR2=value2"', result)

    def test_sanitize_hosts_group_ip(self):
        # 127.0.0.1 should become hosts_127_0_0_1
        result_inv = generate_inventory('172.31.21.64', 'ec2-user', target_hosts='127.0.0.1')
        self.assertIn('[hosts_127_0_0_1]', result_inv)
        
        result_pb = generate_playbook({'playbook_name': 'Test IP Env', 'target_hosts': '127.0.0.1'}, [])
        self.assertIn('hosts: hosts_127_0_0_1', result_pb)

    def test_sanitize_hosts_group_localhost(self):
        # localhost should become hosts_localhost
        result_inv = generate_inventory('172.31.21.64', 'ec2-user', target_hosts='localhost')
        self.assertIn('[hosts_localhost]', result_inv)
        
        result_pb = generate_playbook({'playbook_name': 'Test Localhost Env', 'target_hosts': 'localhost'}, [])
        self.assertIn('hosts: hosts_localhost', result_pb)

    def test_all_task_templates_generate_valid_yaml(self):
        tasks = [
            {'type': 'install_nginx'},
            {'type': 'install_apache'},
            {'type': 'install_mariadb'},
            {'type': 'install_docker'},
            {'type': 'manage_packages', 'package_names': 'curl\ngit', 'package_state': 'present'},
            {'type': 'manage_service', 'service_name': 'nginx', 'service_state': 'started', 'service_enabled': 'yes'},
            {'type': 'system_update', 'update_mode': 'all', 'update_reboot': 'no'},
            {'type': 'create_user', 'user_name': 'webadmin', 'user_group': 'devops', 'user_shell': '/bin/bash'},
            {'type': 'create_directory', 'directory_path': '/opt/demo', 'directory_owner': 'root', 'directory_group': 'root', 'directory_mode': '0755'},
            {'type': 'write_file', 'file_path': '/tmp/demo.txt', 'file_mode': '0644', 'file_content': 'Managed by AutoPlay'},
            {'type': 'git_clone', 'git_repo': 'https://github.com/example/project.git', 'git_dest': '/opt/project', 'git_version': 'main'},
            {'type': 'host_entry', 'host_ip': '127.0.0.1', 'host_names': 'app.internal app', 'host_state': 'present'},
            {'type': 'cron_job', 'cron_name': 'disk report', 'cron_minute': '0', 'cron_hour': '2', 'cron_job': '/usr/bin/df -h', 'cron_state': 'present'},
            {'type': 'set_hostname', 'hostname_name': 'autoplay-node'},
            {'type': 'configure_timezone', 'timezone_name': 'UTC'},
            {'type': 'firewall', 'firewall_port': '80', 'firewall_protocol': 'tcp'},
            {'type': 'deploy_container', 'container_name': 'demo', 'container_image': 'nginx:alpine', 'container_ports': '8080:80'},
            {'type': 'custom_command', 'custom_command_name': 'Show uptime', 'custom_command_body': 'uptime'},
        ]

        for task in tasks:
            with self.subTest(task=task['type']):
                result = generate_playbook(
                    {'playbook_name': 'Catalog Test', 'target_hosts': 'all', 'become_privilege': 'yes'},
                    [task.copy()]
                )
                parsed = yaml.safe_load(result)
                self.assertIsInstance(parsed, list)
                self.assertTrue(parsed[0]['tasks'])

if __name__ == '__main__':
    unittest.main()
