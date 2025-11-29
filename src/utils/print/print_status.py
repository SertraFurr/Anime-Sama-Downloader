from utils.var import print_status, Colors
import subprocess
import sys
import shutil
import os
import av

def print_status(message, status_type="info"):
    prefix = {
        "info": "[*]",
        "success": "[+]",
        "error": "[-]",
        "loading": "[...]"
    }.get(status_type.lower(), "[*]")
    print(f"{prefix} {message}")