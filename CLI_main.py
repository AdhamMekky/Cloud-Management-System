import sys
import os
import docker_manager
import vm_manager  

def print_header():
    print("=" * 40)
    print("   Cloud Management System   ")
    print("=" * 40)

def main_menu():
    while True:
        print_header()
        print("1. VM Operations (QEMU)")
        print("2. Docker Operations")
        print("0. Exit")
        print("-" * 40)
        
        choice = input("Enter your choice: ")

        if choice == '1':
            vm_menu()
        elif choice == '2':
            docker_menu()
        elif choice == '0':
            print("Exiting system. Goodbye!")
            sys.exit()
        else:
            print("Invalid choice, please try again.")

def vm_menu():
    print("\n--- VM Operations ---")
    print("1. Create VM (Interactive)")
    print("2. Create VM (From Config File)")
    print("0. Back to Main Menu")
    
    choice = input("Select operation: ")
    if choice == '1':
        vm_manager.create_vm_interactive()
    elif choice == '2':
        vm_manager.create_vm_from_config()  
    elif choice == '0':
        return
    else:
        print("Invalid choice.")

def docker_menu():
    print("\n--- Docker Operations ---")
    print("1. Create Dockerfile")          
    print("2. Build Docker Image")
    print("3. List Docker Images")
    print("4. List Running Containers")
    print("5. Stop a Container")            
    print("6. Search Image (DockerHub)")
    print("7. Pull Image")
    print("0. Back to Main Menu")
    
    choice = input("Select operation: ")

    if choice == '1':                      
        docker_manager.create_dockerfile()
    elif choice == '2':                    
        docker_manager.build_image()
    elif choice == '3':
        docker_manager.list_images()
    elif choice == '4':
        docker_manager.list_containers()
    elif choice == '5':                     
        docker_manager.stop_container()
    elif choice == '6':                     
        docker_manager.search_dockerhub()
    elif choice == '7':
        docker_manager.pull_image()
    elif choice == '0':
        return
    else:
        print("Feature coming in the next step!")

if __name__ == "__main__":
    main_menu()