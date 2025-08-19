import subprocess
from pathlib import Path


GIT_NOT_FOUND_MSG = "Git is not installed or not found in PATH."
GIT_AVAILABLE_MSG = "Git is available: {result}"
GIT_FAILURE_MSG = "Git command failed: {error}"
GIT_SUCCEEDED_MSG = "Git successfully cloned remote contents to: {local_path}"
DIRECTORY_NOT_EMPTY_MSG = "Failed to clone remote contents: The specified local directory has items inside"
UNEXPECTED_ERROR_MSG = "Unexpected error: {error}"


def is_git_installed():
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(GIT_AVAILABLE_MSG.format(result=result.stdout.strip()))
        return True
    except FileNotFoundError:
        print(GIT_NOT_FOUND_MSG)
        return False
    except subprocess.CalledProcessError as e:
        print(GIT_FAILURE_MSG.format(error=e.stderr.strip()))
        return False
    except Exception as e:
        print(UNEXPECTED_ERROR_MSG.format(error=e))
        return False


def clone_git_repo(repo_url: str, local_path: Path | str):
    local_path = Path(local_path)

    if not local_path.exists():
        local_path.mkdir(parents=True, exist_ok=True)

    if any(local_path.iterdir()):
        message = DIRECTORY_NOT_EMPTY_MSG
        return False, message

    try:
        subprocess.run(
            ["git", "clone", repo_url, str(local_path)],
            check=True
        )
        message = GIT_SUCCEEDED_MSG.format(local_path=local_path)
        return True, message
    except FileNotFoundError:
        message = GIT_NOT_FOUND_MSG
        return False, message
    except subprocess.CalledProcessError as e:
        message = GIT_FAILURE_MSG.format(error=e.stderr.strip())
        return False, message
    except Exception as e:
        message = UNEXPECTED_ERROR_MSG.format(error=e)
        return False, message
