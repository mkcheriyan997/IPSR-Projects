import os
import subprocess
import threading
import shutil
import tempfile
from app.database import update_run_status, append_run_logs, get_playbook

# Create generated dirs
GENERATED_DIR = os.path.join(os.path.dirname(__file__), 'generated')
PLAYBOOKS_DIR = os.path.join(GENERATED_DIR, 'playbooks')
INVENTORIES_DIR = os.path.join(GENERATED_DIR, 'inventories')
KEYS_DIR = os.path.join(GENERATED_DIR, 'keys')

for d in [PLAYBOOKS_DIR, INVENTORIES_DIR, KEYS_DIR]:
    os.makedirs(d, exist_ok=True)

def execute_ansible_async(run_id, playbook_id, ip, private_key_content=None, is_dry_run=False):
    """
    Spawns a background thread to execute the Ansible playbook.
    """
    thread = threading.Thread(
        target=_run_ansible_subprocess,
        args=(run_id, playbook_id, ip, private_key_content, is_dry_run)
    )
    thread.daemon = True
    thread.start()

def _run_ansible_subprocess(run_id, playbook_id, ip, private_key_content=None, is_dry_run=False):
    """
    Executes ansible-playbook via subprocess, streaming logs directly into the SQLite database.
    Handles temporary file management for playbooks, inventories, and secure SSH keys.
    """
    # 1. Fetch playbook data
    playbook_data = get_playbook(playbook_id)
    if not playbook_data:
        update_run_status(run_id, 'failed', "Error: Playbook data could not be retrieved from database.\n")
        return

    playbook_yaml = playbook_data['playbook_yaml']
    inventory_ini = playbook_data['inventory_ini']

    # 2. Setup temporary paths
    playbook_path = os.path.join(PLAYBOOKS_DIR, f"playbook_{run_id}.yml")
    inventory_path = os.path.join(INVENTORIES_DIR, f"inventory_{run_id}.ini")
    key_path = None

    try:
        # Write playbook and inventory files
        with open(playbook_path, 'w', encoding='utf-8') as f:
            f.write(playbook_yaml)

        # Write SSH Private Key if provided, securing permissions (chmod 600)
        if private_key_content:
            key_path = os.path.join(KEYS_DIR, f"key_{run_id}.pem")
            with open(key_path, 'w', encoding='utf-8') as f:
                f.write(private_key_content.strip() + "\n")
            # Apply restricted permissions
            os.chmod(key_path, 0o600)
            
            # Inject key_path into the inventory content
            if "ansible_ssh_private_key_file=" in inventory_ini:
                import re
                inventory_ini = re.sub(
                    r"ansible_ssh_private_key_file=\S+",
                    f"ansible_ssh_private_key_file={key_path}",
                    inventory_ini
                )
            else:
                lines = []
                for line in inventory_ini.splitlines():
                    if line.strip() and not line.startswith('[') and 'ansible_user=' in line:
                        line = f"{line} ansible_ssh_private_key_file={key_path}"
                    lines.append(line)
                inventory_ini = '\n'.join(lines) + '\n'

        with open(inventory_path, 'w', encoding='utf-8') as f:
            f.write(inventory_ini)

        # 3. Build command
        cmd = ["ansible-playbook", "-i", inventory_path, playbook_path]
        if is_dry_run:
            cmd.append("--check")

        log_msg = f"Executing Command: {' '.join(cmd)}\n"
        if is_dry_run:
            log_msg += "Mode: DRY RUN (Check-Mode)\n"
        log_msg += "-" * 60 + "\n"
        append_run_logs(run_id, log_msg)

        # 4. Run Subprocess with clean environment
        env = os.environ.copy()
        # Ensure Ansible does not block on SSH host key verification
        env["ANSIBLE_HOST_KEY_CHECKING"] = "False"
        # Force color output (can parse or display nicely in retro-terminal)
        env["ANSIBLE_FORCE_COLOR"] = "True"

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Merge stderr into stdout to capture all messages chronologically
            text=True,
            env=env
        )

        # 5. Read output line by line and stream to DB
        while True:
            line = process.stdout.readline()
            if not line:
                break
            append_run_logs(run_id, line)

            # Ensure execution hasn't completed and closed pipe
            if process.poll() is not None:
                # Read remaining lines
                for rem_line in process.stdout.readlines():
                    append_run_logs(run_id, rem_line)
                break

        process.wait()
        exit_code = process.returncode

        # 6. Final Status Update
        if exit_code == 0:
            append_run_logs(run_id, "\n" + "="*60 + "\nPLAYBOOK EXECUTION COMPLETED SUCCESSFULLY.\n")
            update_run_status(run_id, 'success', None) # Maintains current logs and sets status
        else:
            append_run_logs(run_id, f"\n" + "="*60 + f"\nPLAYBOOK EXECUTION FAILED. Exit Code: {exit_code}\n")
            update_run_status(run_id, 'failed', None)

    except Exception as e:
        error_msg = f"\nExecution exception encountered:\n{str(e)}\n"
        append_run_logs(run_id, error_msg)
        update_run_status(run_id, 'failed', None)

    finally:
        # 7. Secure Cleanup of sensitive temporary resources
        if os.path.exists(playbook_path):
            os.remove(playbook_path)
        if os.path.exists(inventory_path):
            os.remove(inventory_path)
        if key_path and os.path.exists(key_path):
            # Overwrite private key data before deletion for extra security
            try:
                with open(key_path, 'w') as f:
                    f.write("0" * 1024)
            except IOError:
                pass
            os.remove(key_path)
