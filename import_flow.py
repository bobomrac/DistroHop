from helpers import *

def import_flow():
    clear_screen()
    print("=== Import Restore ===")
    
    # USB Detection
    usb_drives = get_usb_drives()
    if not usb_drives:
        input("No USB drives detected! Press Enter to return.")
        return
    
    print("Detected USB Drives:")
    for idx, drive in enumerate(usb_drives, 1):
        print(f"{idx}. {drive['name']} ({drive['mount']})")
    
    selection = input("Select USB drive (number): ")
    try:
        selected = usb_drives[int(selection)-1]
    except:
        input("Invalid selection! Press Enter to return.")
        return
    
    # Find backup files
    backup_files = [f for f in os.listdir(selected['mount']) if f.startswith('migration_backup')]
    if not backup_files:
        input("No backup files found! Press Enter to return.")
        return
    
    print("\nAvailable backups:")
    for idx, file in enumerate(backup_files, 1):
        print(f"{idx}. {file}")
    
    selection = input("Select backup (number): ")
    try:
        backup_file = os.path.join(selected['mount'], backup_files[int(selection)-1])
    except:
        input("Invalid selection! Press Enter to return.")
        return
    
    # Extract backup
    print("\nRestoring files...")
    try:
        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall(os.path.expanduser('~'))
        print("Files restored successfully!")
    except Exception as e:
        print(f"Error restoring files: {e}")
    
    # Application Reinstallation
    print("\n=== Application Installation ===")
    
    # Read backup manifest
    manifest_path = os.path.join(os.path.expanduser('~'), 'manifest.json')
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        apps_list = manifest.get('apps', [])
        os.remove(manifest_path)
    except Exception as e:
        print(f"Error reading manifest: {e}")
        apps_list = []
    
    if apps_list:
        # Detect available package managers
        managers = detect_package_managers()
        native_managers = [pm for pm in managers if pm != 'flatpak']
        flatpak_available = 'flatpak' in managers
        
        # Installation priority selection
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
            
            # Try preferred method first
            if priority == 'native':
                for pm in native_managers:
                    if check_package_exists(pm, app):
                        print(f"Found in {pm}, installing...")
                        if install_package(pm, app):
                            success_count += 1
                            installed = True
                            break
                # Fallback to Flatpak
                if not installed and flatpak_available:
                    if check_package_exists('flatpak', app):
                        print("Found in Flatpak, installing...")
                        if install_package('flatpak', app):
                            success_count += 1
                            installed = True
            else:
                if flatpak_available:
                    if check_package_exists('flatpak', app):
                        print("Found in Flatpak, installing...")
                        if install_package('flatpak', app):
                            success_count += 1
                            installed = True
                # Fallback to native
                if not installed:
                    for pm in native_managers:
                        if check_package_exists(pm, app):
                            print(f"Found in {pm}, installing...")
                            if install_package(pm, app):
                                success_count += 1
                                installed = True
                                break
            
            if not installed:
                failed_apps.append(app)
                print(f"Failed to install {app}")

        # Installation summary
        print("\n=== Installation Summary ===")
        print(f"Successfully installed: {success_count}/{len(apps_list)}")
        if failed_apps:
            print("\nFailed applications:")
            for app in failed_apps:
                print(f"- {app}")
            print("\nNote: Some applications might have different names in repositories")

    input("\nPress Enter to return to menu.")
