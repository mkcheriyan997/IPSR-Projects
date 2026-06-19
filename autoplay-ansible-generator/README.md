# AutoPlay: Python-Based Ansible Playbook Generator

AutoPlay is a containerized Python web application that allows users to dynamically generate, preview, analyze, and execute Ansible playbooks directly from an interactive web interface. 

With AutoPlay, administrators and DevOps engineers can select common Linux automation tasks, input host parameters, run a real-time security risk assessment on the configuration, compile the playbook and inventory, and trigger remote execution with streamed logs.

---

## 🚀 Key Features

1. **Web-Based Task Builder**: Select from standard task templates (Nginx installation, Docker setup, user management, container deployment, firewall updates, and custom shell scripts).
2. **Dynamic Playbook & Inventory Generation**: AutoPlay uses Jinja2 template compiling to dynamically render structured YAML playbooks and ini-compliant inventory configurations.
3. **Interactive Security Risk Advisor**: Static code analyzer parses target playbooks for high-risk patterns like `rm -rf`, piped web curls, database ports (`3306`, `5432`) opened to `0.0.0.0/0`, or redundant root escalations.
4. **Asynchronous Execution Engine**: Executes `ansible-playbook` commands in the background using multi-threaded Python subprocesses, logging outputs in real-time.
5. **Logs Terminal & Run History**: A retro-style console dashboard polling stdout to stream terminal outputs live. Runs are persisted in a local SQLite database for historical compliance and audit logging.
6. **Containerized Architecture**: The entire platform is dockerized with built-in Ansible-core and system dependencies (`sshpass`, `openssh-client`), ready for cross-platform execution.

---

## 🛠️ Tech Stack
* **Frontend**: HTML5, CSS3, Bootstrap 5, Bootstrap Icons
* **Backend**: Python 3.11, Flask
* **Database**: SQLite3
* **Automation/YAML compilation**: Ansible Core, Jinja2, PyYAML
* **Containerization**: Docker & Docker Compose
* **CI/CD**: GitHub Actions

---

## 📁 Folder Structure
```text
autoplay-ansible-generator/
│
├── app/
│   ├── app.py                  # Main Flask application routes
│   ├── generator.py            # Jinja2 template compiling & Risk Engine
│   ├── executor.py             # Asynchronous subprocess execution runner
│   ├── database.py             # SQLite helper functions
│   │
│   ├── templates/              # Jinja2 HTML templates
│   │   ├── base.html           # Main base layout with imports
│   │   ├── dashboard.html      # Playbook constructor dashboard
│   │   ├── preview.html        # Playbook details and run trigger page
│   │   ├── console.html        # Real-time console terminal output logs
│   │   └── history.html        # Persistence run dashboard
│   │
│   ├── static/                 # Static assets (styling & scripts)
│   │   ├── style.css           # Custom dark theme with glassmorphism
│   │   └── script.js            # Frontend DOM interaction, AJAX, API calls
│   │
│   └── playbook_templates/     # Ansible task blocks J2 files
│       ├── header.yml.j2
│       ├── install_nginx.yml.j2
│       ├── install_docker.yml.j2
│       ├── create_user.yml.j2
│       ├── deploy_container.yml.j2
│       ├── firewall.yml.j2
│       └── custom_command.yml.j2
│
├── ansible-deploy/             # Deployment configurations
│   ├── inventory.ini
│   └── deploy_autoplay.yml     # Playbook deploying AutoPlay to EC2
│
├── tests/                      # Unit testing suite
│   └── test_generator.py
│
├── .github/
│   └── workflows/
│       └── cicd.yml            # CI/CD deployment configuration
│
├── Dockerfile                  # Builds container image
├── docker-compose.yml          # Local container run orchestrator
├── requirements.txt            # Python libraries list
└── README.md                   # This project manual
```

---

## ⚙️ Quick Start

### Prerequisites
* Docker and Docker Compose installed.
* Target servers accessible via SSH (if deploying to remote environments).

### Running Locally with Docker
1. Clone the project directory.
2. Build and start the container:
   ```bash
   docker compose up -d --build
   ```
3. Open your browser and navigate to `http://localhost:5000`.

### Running Locally without Docker
1. Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install ansible-core
   ```
3. Run the Flask application:
   ```bash
   python app/app.py
   ```
4. Access `http://localhost:5000`.

---

## 🛡️ Security Best Practices
* **Volatile Temporary Storage**: SSH Private Keys entered for remote authentication are stored in memory or in a temp folder with `0600` permissions and are securely overwritten (`0` padding) and deleted immediately after the subprocess starts.
* **Non-Interactive Execution**: Connections use `-o StrictHostKeyChecking=no` automatically to prevent prompts blocking execution inside headless containers.
* **Global Privilege Checks**: Security advisor warns users if `become: yes` is enabled globally without any task needing root capabilities, encouraging the principle of least privilege.
