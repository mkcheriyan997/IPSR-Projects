import os
import subprocess
import threading

def push_to_gitops(playbook_yaml, inventory_ini):
    """
    Spawns a background thread to save the playbook/inventory configuration
    and push it to the GitHub repository using the GitHub PAT.
    """
    thread = threading.Thread(target=_execute_gitops_push, args=(playbook_yaml, inventory_ini))
    thread.daemon = True
    thread.start()

def _execute_gitops_push(playbook_yaml, inventory_ini):
    try:
        # 1. Define paths inside the container workspace
        app_dir = '/app'
        gitops_dir = os.path.join(app_dir, 'gitops')
        os.makedirs(gitops_dir, exist_ok=True)
        
        # 2. Write files
        with open(os.path.join(gitops_dir, 'playbook.yml'), 'w', encoding='utf-8') as f:
            f.write(playbook_yaml)
        with open(os.path.join(gitops_dir, 'inventory.ini'), 'w', encoding='utf-8') as f:
            f.write(inventory_ini)
            
        # 3. Configure local Git identity in container if not set
        subprocess.run(['git', 'config', 'user.name', 'AutoPlay GitOps'], cwd=app_dir)
        subprocess.run(['git', 'config', 'user.email', 'gitops@autoplay.local'], cwd=app_dir)
        
        # 4. Set remote URL with token for pushing securely
        token = os.environ.get('GITHUB_PAT', '')
        if not token:
            print("GitOps warning: GITHUB_PAT env var is not set. Push might fail.")
        repo_url = f"https://{token}@github.com/mkcheriyan997/IPSR-Projects.git"
        subprocess.run(['git', 'remote', 'set-url', 'origin', repo_url], cwd=app_dir)
        
        # 5. Git workflow commands
        subprocess.run(['git', 'add', 'gitops/'], cwd=app_dir)
        subprocess.run(['git', 'commit', '-m', 'GitOps: Auto-update generated playbook config'], cwd=app_dir)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=app_dir)
        
        # 6. Revert remote URL to standard HTTP for security
        subprocess.run(['git', 'remote', 'set-url', 'origin', 'https://github.com/mkcheriyan997/IPSR-Projects.git'], cwd=app_dir)
        
        print("GitOps push completed successfully.")
    except Exception as e:
        print(f"GitOps push failed: {str(e)}")
