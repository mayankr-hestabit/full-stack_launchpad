import subprocess
import sys
import tempfile
from pathlib import Path


def execute_python_code(code: str, timeout: int = 10) -> dict:
    """
    Execute Python code in a temporary file.

    Returns:
        {
            "success": bool,
            "stdout": str,
            "stderr": str
        }
    """

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name

        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Execution timed out.",
        }

    except Exception as error:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(error),
        }

    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)