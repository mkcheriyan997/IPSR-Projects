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
        app_dir = '/app'
        gitops_dir = os.path.join(app_dir, 'gitops')
        token = os.environ.get('GITHUB_PAT', '')
        
        if not token:
            print("GitOps warning: GITHUB_PAT env var is not set. Push will fail.")
            return

        # 1. Initialize Git repository inside the container if it does not exist
        if not os.path.exists(os.path.join(app_dir, '.git')):
            print("No .git folder found inside container. Initializing local repository...")
            repo_url = f"https://{token}@github.com/mkcheriyan997/IPSR-Projects.git"
            
            subprocess.run(['git', 'init'], cwd=app_dir)
            subprocess.run(['git', 'remote', 'add', 'origin', repo_url], cwd=app_dir)
            subprocess.run(['git', 'fetch', 'origin', 'main'], cwd=app_dir)
            # Force checkout main branch files from origin
            subprocess.run(['git', 'checkout', '-f', 'main'], cwd=app_dir)
        else:
            # Update remote URL with token securely in case it changed
            repo_url = f"https://{token}@github.com/mkcheriyan997/IPSR-Projects.git"
            subprocess.run(['git', 'remote', 'set-url', 'origin', repo_url], cwd=app_dir)

        # 2. Write the generated files
        os.makedirs(gitops_dir, exist_ok=True)
        with open(os.path.join(gitops_dir, 'playbook.yml'), 'w', encoding='utf-8') as f:
            f.write(playbook_yaml)
        with open(os.path.join(gitops_dir, 'inventory.ini'), 'w', encoding='utf-8') as f:
            f.write(inventory_ini)
            
        # 3. Configure local Git identity inside the container
        subprocess.run(['git', 'config', 'user.name', 'AutoPlay GitOps'], cwd=app_dir)
        subprocess.run(['git', 'config', 'user.email', 'gitops@autoplay.local'], cwd=app_dir)
        
        # 4. Commit and push the playbook configs
        subprocess.run(['git', 'add', 'gitops/'], cwd=app_dir)
        subprocess.run(['git', 'commit', '-m', 'GitOps: Auto-update generated playbook config'], cwd=app_dir)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=app_dir)
        
        # 5. Revert remote URL to standard HTTP for security
        subprocess.run(['git', 'remote', 'set-url', 'origin', 'https://github.com/mkcheriyan997/IPSR-Projects.git'], cwd=app_dir)
        
        print("GitOps push completed successfully.")
    except Exception as e:
        print(f"GitOps push failed: {str(e)}")
