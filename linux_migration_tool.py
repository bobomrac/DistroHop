#!/usr/bin/env python3
"""
Linux Migration Tool

This tool helps you export a backup of your common files/directories along with a list
of installed applications, saving the backup to a connected USB drive.
It also allows you to import (restore) the backup and automatically reinstall
applications on a new system.
"""

import os
import sys
import subprocess
import json
import tarfile
import platform
import shutil
from io import BytesIO
from datetime import datetime

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def get_usb_drives():
    """
    Detect USB drives using `lsblk -J`.
    Looks for devices marked as removable (rm) that are mounted.
    """
    try:
        # Request specific columns for clarity
        result = subprocess.run(
            ['lsblk', '-J', '-o', 'NAME,LABEL,RM,MOUNTPOINT,SIZE'],
            capture_output=True, text=True, check=True
        )
        devices = json.loads(result.stdout)
        usb_drives = []
        for device in devices.get('blockdevices', []):
            # Check top-level device
            if device.get('rm') and device.get('mountpoint'):
                usb_drives.append({
                    'name': device.get('label') or device.get('name'),
                    'mount': device.get('mountpoint'),
                    'size': device.get('size')
                })
            # Also check children (e.g. partitions)
            if 'children' in device:
                for child in device['children']:
                    if child.get('rm') and child.get('mountpoint'):
                        usb_drives.append({
                            'name': child.get('label') or child.get('name'),
                            'mount': child.get('mountpoint'),
                            'size': child.get('size')
                        })
        return usb_drives
    except Exception as e:
        print(f"Error detecting USB drives: {e}")
        return []

def get_free_space(path):
    """
    Return free space at `path` in a human-friendly format (in GB).
    """
    try:
        total, used, free = shutil.disk_usage(path)
        free_gb = free / (1024 ** 3)
        return f"{free_gb:.2f}G"
    except Exception:
        return "Unknown"

def get_common_files():
    """
    Returns a list of common directories and files (if they exist) in the user's home directory.
    """
    home = os.path.expanduser('~')
    common = [
        'Documents', 'Pictures', 'Music', 'Downloads',
        '.bashrc', '.vimrc', '.config', '.ssh'
    ]
    return [os.path.join(home, f) for f in common if os.path.exists(os.path.join(home, f))]

def detect_package_managers():
    """
    Check for available package managers.
    """
    managers = []
    for pm in ['apt', 'dnf', 'yum', 'pacman', 'zypper']:
        if subprocess.run(['which', pm], capture_output=True).returncode == 0:
            managers.append(pm)
    if subprocess.run(['which', 'flatpak'], capture_output=True).returncode == 0:
        managers.append('flatpak')
    return managers

def get_installed_apps():
    """
    Attempt to retrieve a list of installed applications from various package managers.
    """
    apps = []
    managers = detect_package_managers()
    
    if 'apt' in managers:
        try:
            result = subprocess.run(
                ['apt', 'list', '--installed'],
                capture_output=True, text=True, check=True
            )
            apps.extend([line.split('/')[0] for line in result.stdout.splitlines() if '/' in line])
        except subprocess.CalledProcessError:
            pass

    if 'dnf' in managers or 'yum' in managers:
        pm = 'dnf' if 'dnf' in managers else 'yum'
        try:
            result = subprocess.run(
                [pm, 'list', 'installed'],
                capture_output=True, text=True, check=True
            )
            lines = result.stdout.splitlines()[1:]  # Skip header
            apps.extend([line.split()[0] for line in lines if line])
        except subprocess.CalledProcessError:
            pass

    if 'pacman' in managers:
        try:
            result = subprocess.run(
                ['pacman', '-Q'],
                capture_output=True, text=True, check=True
            )
            apps.extend([line.split()[0] for line in result.stdout.splitlines() if line])
        except subprocess.CalledProcessError:
            pass

    if 'flatpak' in managers:
        try:
            result = subprocess.run(
                ['flatpak', 'list'],
                capture_output=True, text=True, check=True
            )
            apps.extend([line.split('\t')[0] for line in result.stdout.splitlines() if '\t' in line])
        except subprocess.CalledProcessError:
            pass

    return list(set(apps))  # Remove duplicates

def create_backup(selected_files, apps_list, destination):
    """
    Create a compressed tar.gz backup containing the selected files and a manifest
    listing the applications and other metadata.
    """
    manifest = {
        'created': datetime.now().isoformat(),
        'files': selected_files,
        'apps': apps_list,
        'system': platform.platform()
    }
    backup_name = f"migration_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
    backup_path = os.path.join(destination, backup_name)

    try:
        with tarfile.open(backup_path, "w:gz") as tar:
            # Add each file/directory preserving relative path from the home directory.
            home = os.path.expanduser('~')
            for file in selected_files:
                if os.path.exists(file):
                    arcname = os.path.relpath(file, home)
                    tar.add(file, arcname=arcname)
            # Write manifest.json directly into the archive without a temporary file.
            manifest_data = json.dumps(manifest, indent=4)
            manifest_bytes = manifest_data.encode('utf-8')
            info = tarfile.TarInfo(name="manifest.json")
            info.size = len(manifest_bytes)
            info.mtime = datetime.now().timestamp()
            tar.addfile(tarinfo=info, fileobj=BytesIO(manifest_bytes))
        return True, backup_path
    except Exception as e:
        return False, str(e)

def check_package_exists(package_manager, app_name):
    """
    Check if the package manager can find the given application.
    """
    try:
        if package_manager == 'apt':
            result = subprocess.run(['apt-cache', 'show', app_name], capture_output=True, text=True)
            return result.returncode == 0 and bool(result.stdout.strip())
        elif package_manager in ['dnf', 'yum']:
            result = subprocess.run([package_manager, 'info', app_name], capture_output=True)
            return result.returncode == 0
        elif package_manager == 'pacman':
            result = subprocess.run(['pacman', '-Si', app_name], capture_output=True)
            return result.returncode == 0
        elif package_manager == 'flatpak':
            result = subprocess.run(['flatpak', 'search', app_name], capture_output=True, text=True)
            return app_name.lower() in result.stdout.lower()
        elif package_manager == 'zypper':
            result = subprocess.run(['zypper', 'info', app_name], capture_output=True, text=True)
            return result.returncode == 0
        return False
    except Exception:
        return False

def install_package(package_manager, app_name):
    """
    Install the application using the specified package manager.
    """
    try:
        if package_manager == 'apt':
            subprocess.run(['sudo', 'apt', 'install', '-y', app_name], check=True)
        elif package_manager in ['dnf', 'yum']:
            subprocess.run(['sudo', package_manager, 'install', '-y', app_name], check=True)
        elif package_manager == 'pacman':
            subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', app_name], check=True)
        elif package_manager == 'flatpak':
            subprocess.run(['sudo', 'flatpak', 'install', '-y', 'flathub', app_name], check=True)
        elif package_manager == 'zypper':
            subprocess.run(['sudo', 'zypper', 'install', '-y', app_name], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def export_flow():
    """Handles the backup/export flow."""
    clear_screen()
    print("=== Export Backup ===\n")
    
    usb_drives = get_usb_drives()
    if not usb_drives:
        input("No USB drives detected! Press Enter to return.")
        return

    print("Detected USB Drives:")
    for idx, drive in enumerate(usb_drives, 1):
        free_space = get_free_space(drive['mount'])
        print(f"{idx}. {drive['name']} (Mount: {drive['mount']}, Free: {free_space}, Size: {drive['size']})")
    
    try:
        selection = int(input("\nSelect USB drive (number): "))
        if selection < 1 or selection > len(usb_drives):
            raise ValueError
        selected = usb_drives[selection - 1]
    except ValueError:
        input("Invalid selection! Press Enter to return.")
        return

    default_files = get_common_files()
    if default_files:
        print("\nRecommended files/directories:")
        for f in default_files:
            print(f"- {os.path.basename(f)}")
    else:
        print("\nNo recommended files found.")
    
    use_recommended = input("\nUse recommended files? [Y/n]: ").strip().lower()
    if use_recommended in ["", "y", "yes"]:
        selected_files = default_files
    else:
        selected_files = []
        for file in default_files:
            choice = input(f"Include {os.path.basename(file)}? [Y/n]: ").strip().lower()
            if choice in ["", "y", "yes"]:
                selected_files.append(file)

    apps = get_installed_apps()
    print(f"\nFound {len(apps)} installed applications.")
    
    include_all_apps = input("Include all applications in the backup? [Y/n]: ").strip().lower()
    if include_all_apps in ["", "y", "yes"]:
        selected_apps = apps
    else:
        selected_apps = []
        for app in apps:
            choice = input(f"Include {app}? [Y/n]: ").strip().lower()
            if choice in ["", "y", "yes"]:
                selected_apps.append(app)

    print("\n=== Summary ===")
    print(f"Files to backup: {len(selected_files)} item(s)")
    print(f"Applications to backup: {len(selected_apps)} item(s)")
    print(f"Destination USB: {selected['mount']}")
    
    proceed = input("\nStart backup? [Y/n]: ").strip().lower()
    if proceed not in ["", "y", "yes"]:
        return

    print("\nCreating backup, please wait...")
    success, backup_path = create_backup(selected_files, selected_apps, selected['mount'])
    if success:
        print(f"\n✅ Backup created successfully: {backup_path}")
    else:
        print(f"\n❌ Error creating backup: {backup_path}")
    
    input("\nPress Enter to return to the main menu.")

def import_flow():
    """Handles the restore/import flow."""
    clear_screen()
    print("=== Import Restore ===\n")
    
    usb_drives = get_usb_drives()
    if not usb_drives:
        input("No USB drives detected! Press Enter to return.")
        return

    print("Detected USB Drives:")
    for idx, drive in enumerate(usb_drives, 1):
        print(f"{idx}. {drive['name']} (Mount: {drive['mount']})")
    
    try:
        selection = int(input("\nSelect USB drive (number): "))
        if selection < 1 or selection > len(usb_drives):
            raise ValueError
        selected = usb_drives[selection - 1]
    except ValueError:
        input("Invalid selection! Press Enter to return.")
        return

    try:
        backup_files = [
            f for f in os.listdir(selected['mount'])
            if f.startswith('migration_backup') and f.endswith('.tar.gz')
        ]
    except Exception as e:
        input(f"Error accessing drive: {e}\nPress Enter to return.")
        return

    if not backup_files:
        input("No backup files found on the selected USB drive! Press Enter to return.")
        return

    print("\nAvailable Backups:")
    for idx, file in enumerate(backup_files, 1):
        print(f"{idx}. {file}")
    
    try:
        selection = int(input("\nSelect backup (number): "))
        if selection < 1 or selection > len(backup_files):
            raise ValueError
        backup_file = os.path.join(selected['mount'], backup_files[selection - 1])
    except ValueError:
        input("Invalid selection! Press Enter to return.")
        return

    print("\nRestoring files...")
    try:
        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall(path=os.path.expanduser('~'))
        print("Files restored successfully!")
    except Exception as e:
        print(f"Error restoring files: {e}")
    
    # Application reinstallation
    print("\n=== Application Reinstallation ===")
    manifest_path = os.path.join(os.path.expanduser('~'), 'manifest.json')
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        apps_list = manifest.get('apps', [])
        os.remove(manifest_path)  # Clean up the extracted manifest
    except Exception as e:
        print(f"Error reading manifest: {e}")
        apps_list = []

    if apps_list:
        managers = detect_package_managers()
        native_managers = [pm for pm in managers if pm != 'flatpak']
        flatpak_available = 'flatpak' in managers

        print("\nChoose installation priority:")
        print("1. Native packages (system package manager)")
        print("2. Flatpak packages")
        choice = input("Enter your choice (1/2): ").strip()
        priority = 'native' if choice == '1' else 'flatpak'

        success_count = 0
        failed_apps = []
        for app in apps_list:
            installed = False
            print(f"\nAttempting to install: {app}")
            if priority == 'native':
                for pm in native_managers:
                    if check_package_exists(pm, app):
                        print(f"Found in {pm}. Installing...")
                        if install_package(pm, app):
                            success_count += 1
                            installed = True
                            break
                if not installed and flatpak_available:
                    if check_package_exists('flatpak', app):
                        print("Found in Flatpak. Installing...")
                        if install_package('flatpak', app):
                            success_count += 1
                            installed = True
            else:
                if flatpak_available:
                    if check_package_exists('flatpak', app):
                        print("Found in Flatpak. Installing...")
                        if install_package('flatpak', app):
                            success_count += 1
                            installed = True
                if not installed:
                    for pm in native_managers:
                        if check_package_exists(pm, app):
                            print(f"Found in {pm}. Installing...")
                            if install_package(pm, app):
                                success_count += 1
                                installed = True
                                break
            
            if not installed:
                failed_apps.append(app)
                print(f"Failed to install {app}")

        print("\n=== Installation Summary ===")
        print(f"Successfully installed: {success_count} out of {len(apps_list)}")
        if failed_apps:
            print("\nFailed installations:")
            for app in failed_apps:
                print(f"- {app}")
            print("\nNote: Some application names might differ in repositories.")
    else:
        print("\nNo applications to reinstall based on the backup manifest.")

    input("\nPress Enter to return to the main menu.")

def show_help():
    """Display help information."""
    clear_screen()
    help_text = """
    📖 Help Information

    Export Backup:
      - Creates a backup of your selected files/directories and a list of installed applications.
      - The backup is saved as a compressed tar.gz file on a connected USB drive.
    
    Import Restore:
      - Restores files from a selected backup archive to your home directory.
      - Reinstalls applications listed in the backup manifest using available package managers.
    
    Make sure you have a USB drive connected and mounted.
    """
    print(help_text)
    input("\nPress Enter to return to the main menu.")

def main_menu():
    """Main menu loop."""
    while True:
        clear_screen()
        print("=== Linux Migration Tool ===\n")
        print("1. Export Backup")
        print("2. Import Restore")
        print("3. Help")
        print("4. Exit")
        choice = input("\nSelect an option: ").strip()
        if choice == '1':
            export_flow()
        elif choice == '2':
            import_flow()
        elif choice == '3':
            show_help()
        elif choice == '4':
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            input("⚠️ Invalid option! Press Enter to try again.")

if __name__ == "__main__":
    main_menu()

