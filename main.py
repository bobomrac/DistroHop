from export_flow import export_flow
from import_flow import import_flow
from helpers import clear_screen

def main_menu():
    while True:
        clear_screen()
        print("=== Linux Migration Tool ===")
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
            clear_screen()
            print("📖 Help Information\n")
            print("Export Backup: Creates a backup of your files and applications.")
            print("Import Restore: Restores files and reinstalls applications from a backup.")
            input("\nPress Enter to return.")
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            input("⚠️ Invalid option! Press Enter to continue.")

if __name__ == "__main__":
    main_menu()
