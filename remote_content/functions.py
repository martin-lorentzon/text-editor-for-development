import subprocess
from pathlib import Path


SUCCESS = 0
GENERIC_ERROR = 1
GIT_NOT_FOUND_ERROR = 2


GIT_NOT_FOUND_MSG = "Git is not installed or not found in PATH"
GIT_AVAILABLE_MSG = "Git is available: {result}"
GIT_FAILED_MSG = "Git command failed: {error}"
GIT_SUCCEEDED_MSG = "Successfully cloned remote repository to: {local_path}"
DIRECTORY_NOT_EMPTY_MSG = "Failed to clone remote repository: The specified local directory has items inside and needs to be empty"
UNEXPECTED_ERROR_MSG = "Unexpected error: {error}"


def is_git_installed():
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        return SUCCESS, GIT_AVAILABLE_MSG.format(result=result.stdout.strip())
    except FileNotFoundError:
        return GIT_NOT_FOUND_ERROR, GIT_NOT_FOUND_MSG
    except subprocess.CalledProcessError as e:
        return GENERIC_ERROR, GIT_FAILED_MSG.format(error=e.stderr.strip())
    except Exception as e:
        return GENERIC_ERROR, UNEXPECTED_ERROR_MSG.format(error=e)


def clone_git_repo(repo_url: str, local_path: Path | str):
    local_path = Path(local_path)

    if not local_path.exists():
        local_path.mkdir(parents=True, exist_ok=True)

    if any(local_path.iterdir()):
        return GENERIC_ERROR, DIRECTORY_NOT_EMPTY_MSG

    try:
        subprocess.run(
            ["git", "clone", repo_url, str(local_path)],
            check=True
        )
        return SUCCESS, GIT_SUCCEEDED_MSG.format(local_path=local_path)
    except FileNotFoundError:
        return GIT_NOT_FOUND_ERROR, GIT_NOT_FOUND_MSG
    except subprocess.CalledProcessError as e:
        return GENERIC_ERROR, GIT_FAILED_MSG.format(error=e.stderr.strip())
    except Exception as e:
        return GENERIC_ERROR, UNEXPECTED_ERROR_MSG.format(error=e)
