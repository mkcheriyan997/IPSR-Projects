# Project Report: Automated LEMP Stack with WordPress, SFTP, and phpMyAdmin

## 1. Automation with Ansible (Core Requirement)
The entire infrastructure and application stack has been automated using **Ansible** to ensure a reproducible, documented, and professional deployment.
- **Location:** `~/ansible-setup/`
- **Playbook:** `setup_wordpress.yml`
- **Idempotency:** The playbook is designed to be run multiple times without causing errors. It includes custom logic to handle existing WordPress installations and configurations gracefully.
- **Key Modules Used:** `dnf`, `systemd`, `user`, `file`, `mysql_db`, `mysql_user`, `get_url`, and `shell` (with `creates` and `failed_when` guards).

## 2. Infrastructure & Package Installation
The following stack was deployed on Amazon Linux 2023:
- **Web Server:** Nginx (v1.30.1)
- **Database:** MariaDB (v10.11.15)
- **Runtime:** PHP (v8.2.31) with `fpm`, `mysqlnd`, `gd`, `intl`, `mbstring`, `xml`, and `zip`.
- **Automation Support:** `ansible-core`, `community.mysql` collection, and `PyMySQL` Python driver.

## 3. User & Security Configuration
- **Web User:** Created `wpadmin` with home directory `/home/wpadmin`.
- **Web Root:** Set to `/home/wpadmin/MyWebsiteProject/public` as requested.
- **SFTP Chroot Jail:** 
    - Configured in `/etc/ssh/sshd_config` to restrict the `sftp_users` group.
    - User `wpadmin` is chrooted to their home directory for maximum security.
    - Shell access is disabled (`/sbin/nologin`) to ensure the user can only manage files via SFTP.
- **Permissions:** Home directory is owned by `root:root` (required for chroot), while web files are owned by `wpadmin:wpadmin`.

## 4. phpMyAdmin Configuration
- **Installation:** Deployed latest phpMyAdmin to `/home/wpadmin/MyWebsiteProject/public/phpmyadmin`.
- **Configuration:** Secured with a unique Blowfish secret and configured for secure HTTPS-only access.
- **URL:** [https://mlolad.xyz/phpmyadmin/](https://mlolad.xyz/phpmyadmin/)

## 5. SSL/TLS Certificate & Network Security
- **Trusted SSL:** Implemented a real **Let's Encrypt** SSL certificate once DNS was verified.
- **HTTPS Enforcement:** Nginx is configured to force all HTTP (Port 80) traffic to HTTPS (Port 443) using a 301 redirect.
- **AWS Firewall:** Security Group rules were updated to allow public inbound traffic on Ports 80 and 443.

## 6. WordPress Installation & Content
- **Deployment:** Automated via **WP-CLI** within the Ansible playbook.
- **Database:** Dedicated `wordpress_db` database with `wp_user` account.
- **Personal Blog Post:** Automatically created a post titled **"About Me"** documenting the administrator's interest in technology and server management.

---

## Final Project Credentials

### SFTP Credentials
- **Host:** `13.63.155.95`
- **Username:** `wpadmin`
- **Password:** `wpadmin123`

### phpMyAdmin Credentials
- **URL:** `https://mlolad.xyz/phpmyadmin`
- **Username:** `wp_user`
- **Password:** `wp_password123`

### WordPress Credentials
- **Admin URL:** `https://mlolad.xyz/wp-admin`
- **Username:** `wpadmin`
- **Password:** `AdminPass123!`

---

## Verification Guide for Invigilator
1. **Frontend:** Visit [https://mlolad.xyz](https://mlolad.xyz) (Verify Green Lock & "About Me" post).
2. **Backend:** Visit [https://mlolad.xyz/wp-admin](https://mlolad.xyz/wp-admin) and log in.
3. **Database:** Visit [https://mlolad.xyz/phpmyadmin](https://mlolad.xyz/phpmyadmin) and log in.
4. **Ansible:** Run `ansible-playbook -i ~/ansible-setup/inventory.ini ~/ansible-setup/setup_wordpress.yml` to see the automated state management in action.
5. **Security:** Attempt an SSH login as `wpadmin` (should be denied) or an SFTP login (should be restricted to home).
