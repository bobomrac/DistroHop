from helpers import *
import os

def export_flow():
    clear_screen()
    print("=== Export Backup ===")
    
    # USB Detection
    usb_drives = get_usb_drives()
    if not usb_drives:
        input("No USB drives detected! Press Enter to return.")
        return
    
    print("Detected USB Drives:")
    for idx, drive in enumerate(usb_drives, 1):
        free_space = get_free_space(drive['mount'])
        print(f"{idx}. {drive['name']} ({drive['mount']}, Free: {free_space})")
    
    # USB Selection
    try:
        selection = int(input("\nSelect USB drive (number): ")) - 1
        selected = usb_drives[selection]
    except (ValueError, IndexError):
        input("Invalid selection! Press Enter to return.")
        return
    
    # File Selection
    default_files = get_common_files()
    print(f"\nRecommended files:\n{', '.join([os.path.basename(f) for f in default_files])}")
    
    if input("Use recommended files? [Y/n]: ").lower() != 'n':
        selected_files = default_files
    else:
        selected_files = []
        for file in default_files:
            if input(f"Include {os.path.basename(file)}? [Y/n]: ").lower() != 'n':
                selected_files.append(file)
    
    # Application Selection
    apps = get_installed_apps()
    print(f"\nFound {len(apps)} installed applications")
    
    if input("Include all applications? [Y/n]: ").lower() != 'n':
        selected_apps = apps
    else:
        selected_apps = []
        for app in apps:
            if input(f"Include {app}? [Y/n]: ").lower() != 'n':
                selected_apps.append(app)
    
    # Confirmation
    print("\n=== Summary ===")
    print(f"Files: {len(selected_files)} items")
    print(f"Applications: {len(selected_apps)} items")
    print(f"Destination: {selected['mount']}")
    
    if input("\nStart backup? [Y/n]: ").lower() == 'n':
        return
    
    # Create Backup
    success, path = create_backup(selected_files, selected_apps, selected['mount'])
    if success:
        print(f"\n✅ Backup created: {path}")
    else:
        print(f"\n❌ Error creating backup: {path}")
    
    input("\nPress Enter to return to menu.")
