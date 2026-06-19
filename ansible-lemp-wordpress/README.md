# Automated LEMP Stack with WordPress, SFTP, and phpMyAdmin

This project automates the deployment of a professional-grade web hosting environment on Amazon Linux 2023 using Ansible.

## Project Structure
- `ansible-setup/`: Idempotent playbook, remote inventory and safe credential example.
- `documentation/`: Verified Task #49310 completion and instance-migration reports.
- `scripts/`: Supporting AWS security-group utility.

## Key Features
- **LEMP Stack:** Nginx, MariaDB 10.11, and PHP 8.2.
- **SSL/TLS:** Automated certificate issuance via Let's Encrypt (Certbot).
- **Security:** SFTP Chroot jail for web admins and restricted shell access.
- **Database Management:** Secured phpMyAdmin installation.
- **WordPress:** Automated installation and configuration via WP-CLI.

## Automation
Create the private variables file before the first run:

```bash
cd ansible-setup
cp credentials.yml.example credentials.yml
chmod 600 credentials.yml
# Replace every placeholder, then preferably run: ansible-vault encrypt credentials.yml
```

Deploy from the controller instance:

```bash
ansible-playbook setup_wordpress.yml
```

The repository intentionally excludes `credentials.yml` and the task credential
sheet. No operational passwords or private keys should be committed.

---
*Updated on: June 19, 2026*
