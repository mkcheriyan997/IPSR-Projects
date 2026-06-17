# Automated LEMP Stack with WordPress, SFTP, and phpMyAdmin

This project automates the deployment of a professional-grade web hosting environment on Amazon Linux 2023 using Ansible.

## Project Structure
- `ansible-setup/`: Contains the Ansible playbooks, inventory, and roles used to automate the stack installation.
- `documentation/`: Detailed implementation reports and step-by-step guides.
- `scripts/`: Utility scripts, including `open_ports.py` for AWS Security Group management.

## Key Features
- **LEMP Stack:** Nginx, MariaDB 10.11, and PHP 8.2.
- **SSL/TLS:** Automated certificate issuance via Let's Encrypt (Certbot).
- **Security:** SFTP Chroot jail for web admins and restricted shell access.
- **Database Management:** Secured phpMyAdmin installation.
- **WordPress:** Automated installation and configuration via WP-CLI.

## Automation
The entire stack can be deployed by running the Ansible playbook:
```bash
ansible-playbook -i ansible-setup/inventory.ini ansible-setup/setup_wordpress.yml
```

---
*Created on: Wednesday, June 17, 2026*
