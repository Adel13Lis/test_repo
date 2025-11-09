import os
import subprocess
import shutil

def run_git_command(command, cwd=REPO_DIR):
    """Utility function to run a git command and handle errors."""
    try:
        # We use check=True to raise an error if the command fails
        result = subprocess.run(
            ['git'] + command.split(),
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Executed: git {command}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"🚨 Git command failed: git {command}")
        print(f"Stderr: {e.stderr}")
        raise

def create_file(path, content):
    """Utility function to write content to a file."""
    full_path = os.path.join(REPO_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

def setup_repo():
    """Initializes the repository structure."""
    if os.path.exists(REPO_DIR):
        print(f"🗑️ Removing existing directory: {REPO_DIR}")
        shutil.rmtree(REPO_DIR)

    os.makedirs(REPO_DIR)
    print(f"📁 Created repository directory: {REPO_DIR}")

    run_git_command("init -b main", cwd=REPO_DIR)
    run_git_command("config user.email 'tester@example.com'", cwd=REPO_DIR)
    run_git_command("config user.name 'Scanner Tester'", cwd=REPO_DIR)

def create_initial_commit():
    """First commit: a clean, working file."""
    print("\n--- Creating Commit 1: Initial Setup ---")
    content = "# Initial Python configuration file\nDEBUG = False\n"
    create_file("settings.py", content)
    run_git_command("add settings.py")
    run_git_command("commit -m 'Initial project setup and settings file.'")

def create_secret_leak_commit():
    """Second commit: Leaking an API key in the source code."""
    print("\n--- Creating Commit 2: Hardcoded API Key Leak (HIGH SEVERITY) ---")
    content = (
        "# Initial Python configuration file\n"
        "DEBUG = False\n"
        f"OPENAI_KEY = '{API_KEY}'  # WARNING: Hardcoded API key!\n"
    )
    create_file("settings.py", content)
    run_git_command("add settings.py")
    run_git_command("commit -m 'feat: Add OpenAI integration settings'")

def create_password_leak_commit():
    """Third commit: Leaking a password in a separate config file."""
    print("\n--- Creating Commit 3: Hardcoded Password Leak ---")
    content = (
        f"db.url={DB_URL}\n"
        "server.port=8080\n"
        "# This file should have been in .gitignore!\n"
    )
    create_file("app.config", content)
    run_git_command("add app.config")
    run_git_command("commit -m 'fix: Update application config parameters'")

def create_leak_in_message_commit():
    """Fourth commit: Leaking a password in the commit message only."""
    print("\n--- Creating Commit 4: Leak in Commit Message ---")
    content = "A random public file."
    create_file("README.md", content)
    run_git_command("add README.md")
    # Secret included in the message body
    commit_message = (
        "docs: Update README for better navigation.\n\n"
        "NOTE: Old password was {}. It is now rotated, but this history still exists.".format(PASSWORD)
    )
    run_git_command(f"commit -m \"{commit_message}\"")

def create_remdiation_commit():
    """Fifth commit: The file is corrected, but the secret is still in the history."""
    print("\n--- Creating Commit 5: Remediation (Secret Removed from HEAD) ---")
    content = (
        "# Initial Python configuration file\n"
        "DEBUG = False\n"
        "OPENAI_KEY = os.getenv('OPENAI_KEY')  # Use environment variable\n"
    )
    create_file("settings.py", content)
    
    # Add app.config to gitignore (but the file history remains)
    create_file(".gitignore", "*.config\n")
    
    run_git_command("add settings.py .gitignore")
    run_git_command("commit -m 'fix: Remove hardcoded secrets and use environment variables for settings'")
    
    # Clean up the app.config file in the working directory
    os.remove(os.path.join(REPO_DIR, "app.config"))
    print("🗑️ app.config deleted from working directory (still in history).")

def display_confirm():
    print("\n=======================================================")
    print(f"Repository setup complete in: ./{REPO_DIR}")
    print("This repository now contains several simulated secrets ")
    print("across its commit history for your scanning program to find.")
    print("=======================================================")

def main():
    """Main execution function."""
    print("--- Git Repository Creation Script Started ---")

    try:
        setup_repo()
        create_initial_commit()
        create_secret_leak_commit()
        create_password_leak_commit()
        create_leak_in_message_commit()
        create_remdiation_commit()

        display_confirm()

    except Exception as e:
        print(f"\nScript encountered a fatal error: {e}")
        shutil.rmtree(REPO_DIR, ignore_errors=True)
        print(f"Cleaned up partial directory {REPO_DIR}.")

if __name__ == "__main__":
    main()
