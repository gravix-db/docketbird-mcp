#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import json
from termcolor import colored

# Add parent directory to path to import from docketbird_mcp if needed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# CONFIGURATION VARIABLES
SERVER_IP = os.getenv(
    "SERVER_IP", "165.227.221.151"
)  # Default from README-Deployment.md
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", "~/.ssh/do_droplet")  # Path to SSH key
SSH_USER = os.getenv("SSH_USER", "root")  # Default SSH user
DOCKETBIRD_API_KEY = os.getenv(
    "DOCKETBIRD_API_KEY", "dummy_key_for_testing"
)  # Default dummy key for testing


def print_colored(message, color="white", status=None):
    """Print a colored message with optional status prefix."""
    status_prefix = ""
    if status == "info":
        status_prefix = colored("[INFO] ", "blue")
    elif status == "success":
        status_prefix = colored("[SUCCESS] ", "green")
    elif status == "error":
        status_prefix = colored("[ERROR] ", "red")
    elif status == "warning":
        status_prefix = colored("[WARNING] ", "yellow")

    print(f"{status_prefix}{colored(message, color)}")


def check_environment_variables():
    """Check if required environment variables are set."""
    print_colored("Checking environment variables...", status="info")

    missing_vars = []
    if not SERVER_IP:
        missing_vars.append("SERVER_IP")

    if missing_vars:
        print_colored(
            f"Missing required environment variables: {', '.join(missing_vars)}",
            status="error",
        )
        print_colored("Please set them before running this script:", status="info")
        print_colored("export SERVER_IP=your_droplet_ip", "yellow")
        sys.exit(1)

    print_colored("Environment variables are properly set.", status="success")
    print_colored(f"Using SERVER_IP: {SERVER_IP}", status="info")
    print_colored(f"Using SSH_KEY_PATH: {SSH_KEY_PATH}", status="info")

    if DOCKETBIRD_API_KEY == "dummy_key_for_testing":
        print_colored(
            "DOCKETBIRD_API_KEY not set, using dummy key for testing", status="warning"
        )
    else:
        print_colored(
            f"DOCKETBIRD_API_KEY is set (first 5 chars): {DOCKETBIRD_API_KEY[:5]}...",
            status="info",
        )


def run_ssh_command(command):
    """Run a command on the remote server via SSH."""
    ssh_command = [
        "ssh",
        "-i",
        os.path.expanduser(SSH_KEY_PATH),
        f"{SSH_USER}@{SERVER_IP}",
        command,
    ]
    try:
        result = subprocess.run(ssh_command, capture_output=True, text=True)
        if result.returncode != 0:
            print_colored(
                f"SSH command failed with error: {result.stderr}", status="error"
            )
            return None
        return result.stdout.strip()
    except Exception as e:
        print_colored(f"Failed to run SSH command: {str(e)}", status="error")
        return None


def test_docker_container():
    """Test if the Docker container is running."""
    print_colored("\nChecking if Docker container is running...", status="info")

    # Check if the container exists and is running
    container_status = run_ssh_command(
        "docker ps | grep docketbird-mcp || echo 'Container not found'"
    )

    if not container_status or "Container not found" in container_status:
        print_colored("Container is not running or doesn't exist", status="error")
        return False

    print_colored("Container is running:", status="success")
    print_colored(container_status, "green")

    # Check container logs
    print_colored("\nChecking container logs...", status="info")
    container_logs = run_ssh_command("docker logs docketbird-mcp")

    if not container_logs:
        print_colored("Failed to retrieve container logs", status="error")
        return False

    print_colored("Container logs:", status="success")
    for line in container_logs.split("\n"):
        print_colored(f"  {line}", "cyan")

    # Check if API key is properly set in the container
    if "API Key set" in container_logs:
        print_colored("API key is properly set in the container", status="success")
    else:
        print_colored(
            "API key might not be properly set in the container", status="warning"
        )

    return True


def main():
    """Main test function."""
    print_colored("=" * 70, "cyan")
    print_colored("DocketBird MCP Server Deployment Test", "cyan")
    print_colored("=" * 70, "cyan")

    # Step 1: Check environment variables
    check_environment_variables()

    # Step 2: Test Docker container
    container_success = test_docker_container()

    # Summary
    print_colored("\n" + "=" * 70, "cyan")
    if container_success:
        print_colored("✅ DEPLOYMENT TEST PASSED!", "green", status="success")
        print_colored(
            "The DocketBird MCP server appears to be running correctly.",
            status="success",
        )
        print_colored(
            "Note: This test only confirms the container is running, not that it's accessible.",
            status="info",
        )
        print_colored(
            "The MCP server might be designed to be accessed differently than direct TCP connections.",
            status="info",
        )
    else:
        print_colored("❌ DEPLOYMENT TEST FAILED!", "red", status="error")
        print_colored("Please check the server logs and configuration.", status="error")

    print_colored("=" * 70, "cyan")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\nTest interrupted by user.", status="warning")
        sys.exit(1)
    except Exception as e:
        print_colored(f"An unexpected error occurred: {str(e)}", status="error")
        sys.exit(1)
