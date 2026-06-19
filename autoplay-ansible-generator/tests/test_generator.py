import sys
import os
import unittest

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

if __name__ == '__main__':
    unittest.main()
