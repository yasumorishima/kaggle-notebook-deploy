"""Shared utilities for kaggle-notebook-deploy."""


def normalize_path(path_str: str) -> str:
    """Convert Git Bash-style paths (/c/Users/...) to Windows paths (C:/Users/...).

    Git Bash on Windows converts paths to /c/Users/... format, which Python
    does not understand. This function detects and converts them.
    """
    if len(path_str) >= 3 and path_str[0] == '/' and path_str[1].isalpha() and path_str[2] == '/':
        return path_str[1].upper() + ':' + path_str[2:]
    return path_str
