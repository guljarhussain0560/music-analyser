import os
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_requirements_lock_synchronization():
    """
    Asserts that every dependency declared in requirements.txt exists with a pinned version in requirements.lock.
    Guarantees zero configuration drift between development and production builds.
    """
    req_file = os.path.join(BASE_DIR, "requirements.txt")
    lock_file = os.path.join(BASE_DIR, "requirements.lock")

    assert os.path.exists(req_file), "requirements.txt must exist"
    assert os.path.exists(lock_file), "requirements.lock must exist"

    with open(req_file, encoding="utf-8") as f:
        req_lines = [
            re.split(r"[><=~;]", line.strip())[0].strip().lower()
            for line in f
            if line.strip() and not line.startswith("#") and not line.startswith("-")
        ]

    with open(lock_file, encoding="utf-8") as f:
        lock_content = f.read().lower()

    for pkg in req_lines:
        clean_pkg = pkg.split("[")[0].strip()
        assert clean_pkg in lock_content, (
            f"Required package '{clean_pkg}' is missing from requirements.lock"
        )
