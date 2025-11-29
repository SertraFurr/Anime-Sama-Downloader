from utils.var import print_status, Colors
import subprocess
import sys
import shutil
import os
import av

def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False