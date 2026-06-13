import os
import subprocess
import sys

# --- CONFIGURATION ---
# Change this to your GitHub Repository URL
REPO_URL = "https://github.com/Pranavrai207/web-studio.git" 
GITHUB_USERNAME = "Pranavrai207"
REPO_NAME = "web-studio"


def run_git(commands):
    """Executes a list of git commands."""
    for cmd in commands:
        try:
            print(f"Running: {cmd}")
            subprocess.run(cmd, check=True, shell=True, cwd="clients")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {cmd}: {e}")
            return False
    return True

def deploy(client_folder):
    """Adds, commits, and pushes a specific client folder."""
    if not os.path.exists(os.path.join("clients", client_folder)):
        print(f"Error: Folder '{client_folder}' not found in clients directory.")
        return

    # 1. Check if remote is set
    result = subprocess.run("git remote", capture_output=True, text=True, shell=True, cwd="clients")
    if "origin" not in result.stdout:
        if "REPLACE_WITH" in REPO_URL:
            print("\n!!! ACTION REQUIRED !!!")
            print("Please edit deploy.py and set your REPO_URL first.")
            return
        subprocess.run(f"git remote add origin {REPO_URL}", shell=True, cwd="clients")

    # 2. Git Workflow
    msg = f"Add pitch for {client_folder}"
    commands = [
        f"git add {client_folder}",
        f'git commit -m "{msg}"',
        "git push -u origin main"
    ]
    
    if run_git(commands):
        live_url = f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/{client_folder}/"
        print("\n" + "="*50)
        print("🚀 DEPLOYMENT SUCCESSFUL!")
        print(f"Client: {client_folder}")
        print(f"Live URL: {live_url}")
        print("="*50)
    else:
        print("\n❌ Deployment Failed. Check your internet connection or GitHub permissions.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy.py [folder_name]")
        print("Example: python deploy.py reflections_cafe")
    else:
        deploy(sys.argv[1])
