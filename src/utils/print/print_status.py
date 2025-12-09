def print_status(message, status_type="info"):
    prefix = {
        "info": "[*]",
        "success": "[+]",
        "error": "[-]",
        "loading": "[...]"
    }.get(status_type.lower(), "[*]")
    print(f"{prefix} {message}")