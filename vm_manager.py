import os
import subprocess
import json



VM_Folder = "VM_Storage"
if not os.path.exists(VM_Folder):
    os.makedirs(VM_Folder)

def create_disk(disk_name, size_gb):
    """
    Creates a virtual hard drive using qemu-img.
    Command: qemu-img create -f qcow2 <name> <size>
    """
    print(f"\n[1/2] Creating Hard Drive: {disk_name} ({size_gb} GB)...")
    
    # Ensure the name ends with .qcow2
    if not disk_name.endswith('.qcow2'):
        disk_name += '.qcow2'
    disk_name = os.path.join(VM_Folder, disk_name)
        
    try:
        # We use subprocess to run the shell command
        subprocess.run(
            ["qemu-img", "create", "-f", "qcow2", disk_name, f"{size_gb}G"], 
            check=True
        )
        print(f"Success! Disk created at: {os.path.abspath(disk_name)}")
        return disk_name
    except subprocess.CalledProcessError as e:
        print(f"Error creating disk: {e}")
        return None

def launch_vm(ram_mb, cpu_cores, disk_path, iso_path=None):
    """
    Launches the VM using qemu-system-x86_64.
    """
    print(f"\n[2/2] Launching Virtual Machine...")
    print(f"Configuration: {ram_mb}MB RAM | {cpu_cores} Cores")
    
    # Build the massive QEMU command
    cmd = [
        "qemu-system-x86_64",
        "-m", str(ram_mb),              # RAM size
        "-smp", str(cpu_cores),         # Number of CPU cores
        "-hda", disk_path,              # The hard drive we just created
        "-enable-kvm",                  # Use KVM acceleration (faster)
        "-display", "gtk"               # Try to open a GUI window
    ]
    
    # If the user provided an OS installer (ISO), attach it to the CD-ROM
    if iso_path:
        cmd.extend(["-cdrom", iso_path, "-boot", "d"])
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        # We don't use check=True here because closing the VM window might look like an 'error' to Python
        subprocess.run(cmd)
    except Exception as e:
        print(f"Failed to launch QEMU: {e}")
        print("Tip: If you are on WSL without a GUI, try adding '-nographic' to the command.")

def create_vm_interactive():
    """Objective 1: Interactive User Input"""
    print("\n--- Create Virtual Machine (Interactive) ---")
    
    # 1. Get User Input
    vm_name = input("Enter VM Name (for disk file): ")
    try:
        ram = int(input("Enter RAM size (MB) [e.g., 512, 1024, 2048]: "))
        cpu = int(input("Enter number of CPU cores [e.g., 1, 2]: "))
        disk_size = int(input("Enter Disk Size (GB): "))
    except ValueError:
        print("Error: Please enter numbers only for RAM, CPU, and Disk.")
        return

    # 2. Create the Disk
    disk_path = create_disk(vm_name, disk_size)
    
    if disk_path:
        # 3. Ask for an ISO (Optional)
        use_iso = input("Do you have an ISO file (OS Installer)? (y/n): ").lower()
        iso_path = None
        if use_iso == 'y':
            iso_path = input("Enter full path to ISO file: ")
        
        # 4. Launch
        launch_vm(ram, cpu, disk_path, iso_path) 

def create_vm_from_config():
    """Objective 1b: Create VM from Configuration File"""
    print("\n--- Create VM (From Config File) ---")
    
    config_file = input("Enter configuration file path (default: vm_config.json): ")
    if not config_file:
        config_file = "vm_config.json"
        
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        print(f"Loaded configuration: {config}")
        
        # Extract values
        name = config.get("vm_name", "default_vm")
        ram = config.get("ram_mb", 2048)
        cpu = config.get("cpu_cores", 4)
        disk_size = config.get("disk_size_gb", 10)
        iso = config.get("iso_path", "ISO_Images/ubuntu-20.04.6-desktop-amd64.iso")
        
        # Run the standard creation process
        disk_path = create_disk(name, disk_size)
        
        if disk_path:
            launch_vm(ram, cpu, disk_path, iso if iso else None)
            
    except FileNotFoundError:
        print(f"Error: File '{config_file}' not found.")
    except json.JSONDecodeError:
        print(f"Error: '{config_file}' is not a valid JSON file.")
    except Exception as e:
        print(f"Error: {e}")