import os
import subprocess
import json
import tarfile
import platform
from datetime import datetime

def clear_screen():
    os.system('clear')

def get_usb_drives():
    try:
        result = subprocess.run(['lsblk', '-J'], capture_output=True, text=True)
        devices = json.loads(result.stdout)
        return [
            {
                'name': device.get('label', 'NO_LABEL'),
                'mount': device['mountpoint'],
                'size': device['size']
            }
            for device in devices['blockdevices'] 
            if device['rm'] and device['mountpoint']
        ]
    except Exception as e:
        return []

def get_free_space(path):
    try:
        result = subprocess.run(['df', '-h', path], capture_output=True, text=True)
        return result.stdout.split('\n')[1].split()[3]
    except:
        return "Unknown"

def get_common_files():
    home = os.path.expanduser('~')
    common = [
        'Documents', 'Pictures', 'Music', 'Downloads',
        '.bashrc', '.vimrc', '.config', '.ssh'
    ]
    return [os.path.join(home, f) for f in common if os.path.exists(os.path.join(home, f))]

def get_installed_apps():
    apps = []
    managers = detect_package_managers()
    
    if 'apt' in managers:
        result = subprocess.run(['apt', 'list', '--installed'], capture_output=True, text=True)
        apps.extend([line.split('/')[0] for line in result.stdout.split('\n') if '/' in line])
    
    if 'dnf' in managers or 'yum' in managers:
        pm = 'dnf' if 'dnf' in managers else 'yum'
        result = subprocess.run([pm, 'list', 'installed'], capture_output=True, text=True)
        apps.extend([line.split()[0] for line in result.stdout.split('\n')[2:] if line])
    
    if 'pacman' in managers:
        result = subprocess.run(['pacman', '-Q'], capture_output=True, text=True)
        apps.extend([line.split()[0] for line in result.stdout.split('\n') if line])
    
    if 'flatpak' in managers:
        result = subprocess.run(['flatpak', 'list'], capture_output=True, text=True)
        apps.extend([line.split('\t')[0] for line in result.stdout.split('\n') if '\t' in line])
    
    return list(set(apps))

def create_backup(selected_files, apps_list, destination):
    manifest = {
        'created': datetime.now().isoformat(),
        'files': selected_files,
        'apps': apps_list,
        'system': platform.platform()
    }
    
    backup_name = f"migration_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.tar.gz"
    backup_path = os.path.join(destination, backup_name)
    
    try:
        with tarfile.open(backup_path, "w:gz") as tar:
            for file in selected_files:
                tar.add(file, arcname=os.path.basename(file))
            
            manifest_path = '/tmp/manifest.json'
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f)
            tar.add(manifest_path, arcname='manifest.json')
        
        return True, backup_path
    except Exception as e:
        return False, str(e)

def detect_package_managers():
    managers = []
    for pm in ['apt', 'dnf', 'yum', 'pacman', 'zypper']:
        if subprocess.run(['which', pm], capture_output=True).returncode == 0:
            managers.append(pm)
    if subprocess.run(['which', 'flatpak'], capture_output=True).returncode == 0:
        managers.append('flatpak')
    return managers

def check_package_exists(package_manager, app_name):
    try:
        if package_manager == 'apt':
            result = subprocess.run(['apt-cache', 'show', app_name], capture_output=True, text=True)
            return result.returncode == 0
        elif package_manager in ['dnf', 'yum']:
            result = subprocess.run([package_manager, 'info', app_name], capture_output=True)
            return result.returncode == 0
        elif package_manager == 'pacman':
            result = subprocess.run(['pacman', '-Si', app_name], capture_output=True)
            return result.returncode == 0
        elif package_manager == 'flatpak':
            result = subprocess.run(['flatpak', 'search', app_name], capture_output=True, text=True)
            return any(app_name in line for line in result.stdout.split('\n'))
        return False
    except Exception as e:
        return False

def install_package(package_manager, app_name):
    try:
        if package_manager == 'apt':
            subprocess.run(['sudo', 'apt', 'install', '-y', app_name], check=True)
        elif package_manager in ['dnf', 'yum']:
            subprocess.run(['sudo', package_manager, 'install', '-y', app_name], check=True)
        elif package_manager == 'pacman':
            subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', app_name], check=True)
        elif package_manager == 'flatpak':
            subprocess.run(['flatpak', 'install', '-y', 'flathub', app_name], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
