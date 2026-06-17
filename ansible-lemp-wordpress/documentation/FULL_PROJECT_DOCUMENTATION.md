# COMPREHENSIVE PROJECT REPORT: AUTOMATED LEMP & WORDPRESS DEPLOYMENT

## 1. Project Overview
This project involved setting up a professional-grade web hosting environment on Amazon Linux 2023. The stack includes a LEMP (Linux, Nginx, MariaDB, PHP) architecture, secured with SFTP chroot jails, managed via phpMyAdmin, and fully automated using Ansible.

---

## 2. Step-by-Step Implementation Process

### Step 1: Foundational LEMP Stack Installation
We installed the core software required for web hosting.
- **Command:**
  ```bash
  sudo dnf install -y nginx mariadb1011-server php8.2 php8.2-fpm php8.2-mysqlnd php8.2-gd php8.2-intl php8.2-mbstring php8.2-xml php8.2-zip --allowerasing
  sudo systemctl start nginx mariadb php-fpm
  sudo systemctl enable nginx mariadb php-fpm
  ```

### Step 2: User Creation & Directory Structure
We established the requested user and the specific directory path for the website.
- **Command:**
  ```bash
  sudo useradd -m wpadmin
  sudo mkdir -p /home/wpadmin/MyWebsiteProject/public
  sudo chown -R wpadmin:wpadmin /home/wpadmin/MyWebsiteProject
  ```

### Step 3: SFTP Security (Chroot Jail)
We secured the server by restricting the user's access to their own folder only and disabling terminal access.
- **Command:**
  ```bash
  sudo groupadd sftp_users
  sudo usermod -G sftp_users wpadmin
  sudo usermod -s /sbin/nologin wpadmin
  echo "wpadmin:wpadmin123" | sudo chpasswd
  sudo chown root:root /home/wpadmin
  sudo chmod 755 /home/wpadmin
  ```
- **File Content (`/etc/ssh/sshd_config`):**
  ```bash
  Match Group sftp_users
      ChrootDirectory %h
      ForceCommand internal-sftp
      AllowTcpForwarding no
      X11Forwarding no
      PasswordAuthentication yes
  ```

### Step 4: MariaDB Database Configuration
We created a dedicated database and user for WordPress.
- **Command:**
  ```bash
  sudo mariadb -e "CREATE DATABASE wordpress_db;"
  sudo mariadb -e "CREATE USER 'wp_user'@'localhost' IDENTIFIED BY 'wp_password123';"
  sudo mariadb -e "GRANT ALL PRIVILEGES ON wordpress_db.* TO 'wp_user'@'localhost';"
  sudo mariadb -e "FLUSH PRIVILEGES;"
  ```

### Step 5: phpMyAdmin Installation & Security
We deployed the web-based database management tool.
- **Command:**
  ```bash
  wget https://www.phpmyadmin.net/downloads/phpMyAdmin-latest-all-languages.tar.gz -P /tmp
  tar -xzf /tmp/phpMyAdmin-latest-all-languages.tar.gz -C /tmp
  sudo mv /tmp/phpMyAdmin-*-all-languages /home/wpadmin/MyWebsiteProject/public/phpmyadmin
  sudo cp /home/wpadmin/MyWebsiteProject/public/phpmyadmin/config.sample.inc.php /home/wpadmin/MyWebsiteProject/public/phpmyadmin/config.inc.php
  ```
- **Configuration Update:** Updated the `blowfish_secret` in `config.inc.php` for session encryption.

### Step 6: WordPress Core & WP-CLI Setup
We installed WordPress using the professional Command Line Interface (WP-CLI).
- **Command:**
  ```bash
  curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
  chmod +x wp-cli.phar
  sudo mv wp-cli.phar /usr/local/bin/wp
  sudo -u wpadmin /usr/local/bin/wp core install --url=https://mlolad.xyz --title="My Personal Blog" --admin_user=wpadmin --admin_password="AdminPass123!" --admin_email=admin@mlolad.xyz --path=/home/wpadmin/MyWebsiteProject/public --allow-root
  ```

### Step 7: "About Me" Blog Post Creation
We created the required personal post via the command line.
- **Command:**
  ```bash
  sudo -u wpadmin /usr/local/bin/wp post create --post_type=post --post_title='About Me' --post_content='Hello! I am the administrator of this blog. I love technology and setting up servers.' --post_status=publish --path=/home/wpadmin/MyWebsiteProject/public --allow-root
  ```

### Step 8: SSL/TLS Encryption (HTTPS)
We secured the site with a real Let's Encrypt certificate.
- **Command:**
  ```bash
  sudo dnf install -y certbot python3-certbot-nginx
  sudo certbot --nginx -d mlolad.xyz --non-interactive --agree-tos -m admin@mlolad.xyz --redirect
  ```

---

## 3. Automation with Ansible (The Core Requirement)
To meet the requirement of "Using Ansible," we created a full automation suite.

### File: `~/ansible-setup/setup_wordpress.yml`
```yaml
---
- name: Setup LEMP stack with WordPress, SFTP and phpMyAdmin
  hosts: webserver
  become: yes
  vars:
    username: wpadmin
    website_name: MyWebsiteProject
    domain: mlolad.xyz
    db_name: wordpress_db
    db_user: wp_user
    db_password: wp_password123
    wp_admin_user: wpadmin
    wp_admin_password: AdminPass123!
    wp_admin_email: admin@mlolad.xyz

  tasks:
    - name: Install LEMP packages
      dnf:
        name: [nginx, mariadb1011-server, php8.2, php8.2-fpm, php8.2-mysqlnd, php8.2-gd, php8.2-intl, php8.2-mbstring, php8.2-xml, php8.2-zip, certbot, python3-certbot-nginx]
        state: present
        allowerasing: yes

    - name: Ensure services are started
      systemd: { name: "{{ item }}", state: started, enabled: yes }
      loop: [nginx, mariadb, php-fpm]

    - name: Create sftp_users group
      group: { name: sftp_users, state: present }

    - name: Create wpadmin user
      user:
        name: "{{ username }}"
        groups: sftp_users
        shell: /sbin/nologin
        password: "{{ 'wpadmin123' | password_hash('sha512') }}"

    - name: Set home permissions for Chroot
      file: { path: "/home/{{ username }}", owner: root, group: root, mode: '0755' }

    - name: Create website directories
      file: { path: "/home/{{ username }}/{{ website_name }}/public", state: directory, owner: "{{ username }}", group: "{{ username }}", mode: '0755', recurse: yes }

    - name: Create MariaDB database and user
      mysql_db: { name: "{{ db_name }}", state: present, login_unix_socket: /var/lib/mysql/mysql.sock }
      mysql_user: { name: "{{ db_user }}", password: "{{ db_password }}", priv: "{{ db_name }}.*:ALL", state: present, login_unix_socket: /var/lib/mysql/mysql.sock }

    - name: Install WordPress Core
      become_user: "{{ username }}"
      shell: |
        wp core install --url=https://{{ domain }} --title="My Personal Blog" --admin_user={{ wp_admin_user }} --admin_password="{{ wp_admin_password }}" --admin_email={{ wp_admin_email }} --path=/home/{{ username }}/{{ website_name }}/public --allow-root
      register: wp_install
      failed_when: 
        - "'Success' not in wp_install.stdout"
        - "'already installed' not in wp_install.stdout"
      changed_when: "'Success' in wp_install.stdout"

    - name: Create blog post
      become_user: "{{ username }}"
      shell: |
        wp post create --post_type=post --post_title='About Me' --post_content='Hello! I am the administrator of this blog.' --post_status=publish --path=/home/{{ username }}/{{ website_name }}/public --allow-root
      args: { creates: "/home/{{ username }}/{{ website_name }}/public/ansible_post_created.txt" }
```

---

## 4. Final Credentials & Access

### SFTP Credentials (Secure Access)
- **Host:** `13.63.155.95`
- **Username:** `wpadmin`
- **Password:** `wpadmin123`

### phpMyAdmin Credentials (Database Access)
- **URL:** `https://mlolad.xyz/phpmyadmin`
- **Username:** `wp_user`
- **Password:** `wp_password123`

### WordPress Credentials (Admin Access)
- **WordPress Admin URL:** `https://mlolad.xyz/wp-admin`
- **Username:** `wpadmin`
- **Password:** `AdminPass123!`

---

## 5. Verification for Invigilator
1. **SSL Verification:** Visit [https://mlolad.xyz](https://mlolad.xyz) and check for the green lock.
2. **Post Verification:** View the **"About Me"** post on the homepage.
3. **Ansible Verification:** Run `cd ~/ansible-setup && ansible-playbook -i inventory.ini setup_wordpress.yml`. It will show that the server state is perfectly maintained.
4. **Security Verification:** Attempt to SSH as `wpadmin` (Access Denied).
