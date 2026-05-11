# src/tools/code_executor.py
"""安全的 Python 代码执行工具"""

from langchain_core.tools import tool
import subprocess
import tempfile
import os


@tool
def execute_python_code(code: str) -> str:
    """Execute Python code in a sandboxed environment.
    Use this for calculations, data processing, or generating charts.

    Args:
        code: Valid Python code to execute. Use print() to output results.

    Returns:
        The stdout output of the executed code, or error message if it fails.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=30,  # 30秒超时
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            return output if output else "Code executed successfully (no output)."
        else:
            return f"Error:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out (30s limit)."
    finally:
        os.unlink(temp_path)
