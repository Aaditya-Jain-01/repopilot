import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ADAPTION_API_KEY", "")
ENDPOINT = os.getenv("ADAPTION_ENDPOINT", "https://api.prod.adaptionlabs.ai/api/v1/responses")
MODEL_NAME = os.getenv("ADAPTION_MODEL", "stack:deepseek-v4-flash-1")

def query_adaption(prompt: str) -> str:
    """Sends a completion request to Adaption's live inference stack."""
    if not API_KEY or "pt_live" not in API_KEY:
        raise ValueError("Missing or invalid ADAPTION_API_KEY in .env file.")

    headers = {
        "Authorization": f"Bearer {API_KEY.strip()}",
        "Content-Type": "application/json",
        "User-Agent": "RepoPilot/1.0"
    }
    payload = {
        "model": MODEL_NAME.strip(),
        "input": prompt
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(ENDPOINT.strip(), data=data_bytes, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, dict):
                if "output_text" in data and data["output_text"]:
                    return str(data["output_text"])
                for k in ["output", "text", "response", "content"]:
                    if k in data and data[k]:
                        return str(data[k])
            return str(data)
    except urllib.error.HTTPError as e:
        error_detail = e.read().decode("utf-8")
        print(f"\n[Adaption API HTTP {e.code}]: {error_detail}")
        raise
    except Exception as e:
        print(f"\n[Adaption Connection Error]: {e}")
        raise

def audit_code(file_name: str, code_content: str) -> dict:
    """Performs an AST-level security, logic, and performance review."""
    prompt = (
        "You are an elite automated security and code quality review agent.\n"
        "Analyze the provided code thoroughly. Output ONLY a valid JSON object with a single key 'issues', "
        "which is a list of objects containing: "
        "'line' (int or str), 'severity' ('CRITICAL', 'WARNING', or 'INFO'), "
        "'title' (short summary), and 'recommendation' (concise fix advice).\n"
        "Do not include conversational preamble. Return valid JSON only.\n\n"
        f"File: {file_name}\n\n```python\n{code_content}\n```"
    )

    raw = query_adaption(prompt).strip()
    clean = raw
    if "```json" in clean:
        clean = clean.split("```json")[1].split("```")[0].strip()
    elif "```" in clean:
        clean = clean.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(clean)
    except Exception:
        start = clean.find("{")
        end = clean.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(clean[start:end+1])
            except Exception:
                pass
        return {
            "issues": [
                {"line": "1", "severity": "INFO", "title": "Model Analysis", "recommendation": raw}
            ]
        }

def generate_patch(file_name: str, code_content: str) -> str:
    """Generates corrected source code."""
    prompt = (
        "You are an autonomous patching agent. Rewrite and fix all security vulnerabilities, "
        "resource leaks, and logic bugs in the code.\n"
        "Output ONLY the complete, corrected version of the code. "
        "Do NOT include conversational explanation or markdown backticks.\n\n"
        f"File: {file_name}\n\n```python\n{code_content}\n```"
    )

    raw = query_adaption(prompt).strip()
    if "```python" in raw:
        return raw.split("```python")[1].split("```")[0].strip()
    elif "```" in raw:
        return raw.split("```")[1].split("```")[0].strip()
    return raw

def generate_unit_tests(file_name: str, code_content: str) -> str:
    """Generates a comprehensive pytest test suite covering edge cases."""
    prompt = (
        "You are an automated QA test engineer. Write a complete pytest test suite "
        "for the provided code. Include tests for boundary conditions, exceptions, and valid cases.\n"
        "Use standard library 'unittest.mock' (MagicMock, patch) for mocking databases or external I/O instead of custom mock classes.\n"
        "Return ONLY runnable Python test code without preamble or backticks.\n\n"
        f"File: {file_name}\n\n```python\n{code_content}\n```"
    )

    raw = query_adaption(prompt).strip()
    if "```python" in raw:
        return raw.split("```python")[1].split("```")[0].strip()
    elif "```" in raw:
        return raw.split("```")[1].split("```")[0].strip()
    return raw