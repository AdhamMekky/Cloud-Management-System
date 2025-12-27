import customtkinter as ctk
from tkinter import filedialog, messagebox
import vm_manager
import docker_manager
import threading
import os
import json
import docker

# --- CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CloudManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. WINDOW SETUP (Massive Size)
        self.title("Cloud Management System - Final Presentation")
        self.geometry("1400x900")
        # --- FONTS SETUP ---
        self.font_title = ctk.CTkFont(family="Arial", size=28, weight="bold")
        self.font_header = ctk.CTkFont(family="Arial", size=20, weight="bold")
        self.font_body = ctk.CTkFont(family="Arial", size=16)
        self.font_button = ctk.CTkFont(family="Arial", size=18, weight="bold")
        self.font_code = ctk.CTkFont(family="Consolas", size=16) 
        self.font_log = ctk.CTkFont(family="Courier New", size=14)

        try:
            # This creates the connection to the Docker Engine
            self.docker_client = docker.from_env()
        except Exception as e:
            self.docker_client = None
            print(f"Error connecting to Docker: {e}")

        # 2. DEFINE LARGE FONTS
        self.font_title = ctk.CTkFont(family="Arial", size=32, weight="bold")
        self.font_header = ctk.CTkFont(family="Arial", size=24, weight="bold")
        self.font_body = ctk.CTkFont(family="Arial", size=18)
        self.font_button = ctk.CTkFont(family="Arial", size=20, weight="bold")
        self.font_log = ctk.CTkFont(family="Consolas", size=16)

        # Layout: Sidebar (Left) + Main (Right)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 3. WIDE SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="CLOUD\nMANAGER", font=ctk.CTkFont(size=40, weight="bold"))
        self.logo.grid(row=0, column=0, padx=20, pady=(40, 40))

        # Big Sidebar Buttons
        self.btn_vm = ctk.CTkButton(self.sidebar, text="VM Workstation", height=60, font=self.font_button, command=self.show_vm_frame)
        self.btn_vm.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        
        self.btn_docker = ctk.CTkButton(self.sidebar, text="Docker Operations", height=60, font=self.font_button, command=self.show_docker_frame)
        self.btn_docker.grid(row=2, column=0, padx=20, pady=15, sticky="ew")

        # --- 4. MAIN CONTENT AREA ---
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_rowconfigure(0, weight=1) 
        self.main_area.grid_rowconfigure(1, weight=0) 

        # --- 5. WIDE LOG SYSTEM (Max Width) ---
        # We use padx=0 to make it touch the edges of the screen
        self.console_frame = ctk.CTkFrame(self.main_area, height=250) 
        self.console_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        
        self.console_label = ctk.CTkLabel(self.console_frame, text=" System Logs / Status:", anchor="w", font=self.font_header)
        self.console_label.pack(fill="x", padx=10, pady=(10, 0))
        
        # wrap="none" keeps your table rows straight (scrolling horizontally if needed)
        self.console = ctk.CTkTextbox(self.console_frame, height=200, font=self.font_log, wrap="none")
        self.console.pack(fill="both", expand=True, padx=10, pady=10)
        self.log("System Initialized. Ready for presentation.")

        # Initialize Frames
        self.vm_frame = None
        self.docker_frame = None
        
        self.create_vm_view()
        self.create_docker_view()

        # Start on VM Page
        self.show_vm_frame()

    def log(self, message):
        self.console.insert("end", f">> {message}\n")
        self.console.see("end")

    # =====================================================
    # VIEW: VIRTUAL MACHINE
    # =====================================================
    def create_vm_view(self):
        # 1. Main Frame
        self.vm_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.vm_frame.grid_columnconfigure(0, weight=1)

        # 2. Title
        title = ctk.CTkLabel(self.vm_frame, text="Create New Virtual Machine", font=self.font_title)
        title.pack(pady=30)

        # 3. Content Container (Splits screen into Left and Right)
        content = ctk.CTkFrame(self.vm_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=10)
        
        # Left gets 2/3 space, Right gets 1/3 space
        content.grid_columnconfigure(0, weight=2) 
        content.grid_columnconfigure(1, weight=1) 

        # --- LEFT COLUMN: INPUTS ---
        form = ctk.CTkFrame(content)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=0)
        form.grid_columnconfigure(1, weight=1) # Make input boxes stretch

        # Input Row 1: Name
        ctk.CTkLabel(form, text="VM Name:", font=self.font_header).grid(row=0, column=0, padx=20, pady=20, sticky="e")
        self.entry_vm_name = ctk.CTkEntry(form, placeholder_text="e.g. Ubuntu_Test", height=50, font=self.font_body)
        self.entry_vm_name.grid(row=0, column=1, padx=20, pady=20, sticky="ew")

        # Input Row 2: RAM
        ctk.CTkLabel(form, text="RAM (MB):", font=self.font_header).grid(row=1, column=0, padx=20, pady=20, sticky="e")
        self.entry_ram = ctk.CTkEntry(form, placeholder_text="e.g. 1024", height=50, font=self.font_body)
        self.entry_ram.grid(row=1, column=1, padx=20, pady=20, sticky="ew")

        # Input Row 3: CPU
        ctk.CTkLabel(form, text="CPU Cores:", font=self.font_header).grid(row=2, column=0, padx=20, pady=20, sticky="e")
        self.entry_cpu = ctk.CTkEntry(form, placeholder_text="e.g. 2", height=50, font=self.font_body)
        self.entry_cpu.grid(row=2, column=1, padx=20, pady=20, sticky="ew")

        # Input Row 4: Disk
        ctk.CTkLabel(form, text="Disk Size (GB):", font=self.font_header).grid(row=3, column=0, padx=20, pady=20, sticky="e")
        self.entry_disk = ctk.CTkEntry(form, placeholder_text="e.g. 10", height=50, font=self.font_body)
        self.entry_disk.grid(row=3, column=1, padx=20, pady=20, sticky="ew")

        # Input Row 5: ISO
        ctk.CTkLabel(form, text="ISO Image:", font=self.font_header).grid(row=4, column=0, padx=20, pady=20, sticky="e")
        self.entry_iso = ctk.CTkEntry(form, placeholder_text="Optional path to ISO", height=50, font=self.font_body)
        self.entry_iso.grid(row=4, column=1, padx=20, pady=20, sticky="ew")
        
        btn_browse = ctk.CTkButton(form, text="Browse...", width=120, height=50, font=self.font_button, command=self.browse_iso)
        btn_browse.grid(row=4, column=2, padx=20, pady=20)


        # --- RIGHT COLUMN: ACTIONS (The Buttons!) ---
        actions = ctk.CTkFrame(content) 
        actions.grid(row=0, column=1, sticky="nsew", pady=0)
        
        # Center contents
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_rowconfigure(0, weight=1) # Spacer top
        actions.grid_rowconfigure(5, weight=1) # Spacer bottom

        ctk.CTkLabel(actions, text="Control Panel", font=self.font_header).grid(row=1, column=0, pady=20)

        # 1. GREEN BUTTON (Manual)
        btn_launch = ctk.CTkButton(actions, text="CREATE & LAUNCH\n(Manual Settings)", height=80, font=self.font_button, fg_color="green", command=self.run_vm_logic)
        btn_launch.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        # 2. SEPARATOR
        ctk.CTkLabel(actions, text="- OR -", font=self.font_body).grid(row=3, column=0, pady=10)

        # 3. ORANGE BUTTON (Config)
        btn_config = ctk.CTkButton(actions, text="LAUNCH FROM\nCONFIG FILE", height=80, font=self.font_button, fg_color="#D35400", command=self.run_vm_config)
        btn_config.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

    # =====================================================
    # LOGIC: VM
    # =====================================================
    def browse_iso(self):
        filename = filedialog.askopenfilename(title="Select ISO File", filetypes=[("ISO Files", "*.iso")])
        if filename:
            self.entry_iso.delete(0, "end")
            self.entry_iso.insert(0, filename)

    def run_vm_logic(self):
        name = self.entry_vm_name.get()
        ram = self.entry_ram.get()
        cpu = self.entry_cpu.get()
        disk = self.entry_disk.get()
        iso = self.entry_iso.get()

        if not name or not ram or not cpu or not disk:
            self.log("ERROR: Please fill in Name, RAM, CPU, and Disk Size.")
            return
        
        self.launch_vm_thread(name, ram, cpu, disk, iso)

    def run_vm_config(self):
        choice = messagebox.askyesno("Load Config", "Browse for config file?\n(No = Use default 'vm_config.json')")
        config_path = "vm_config.json"
        if choice:
            config_path = filedialog.askopenfilename(title="Select JSON Config", filetypes=[("JSON Files", "*.json")])
            if not config_path: return
        
        self.log(f"Reading configuration from: {config_path}")
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            name = config.get("vm_name", "config_vm")
            ram = config.get("ram_mb", 2048)
            cpu = config.get("cpu_cores", 2)
            disk = config.get("disk_size_gb", 10)
            iso = config.get("iso_path", "")
            
            self.launch_vm_thread(name, str(ram), str(cpu), str(disk), iso)
        except Exception as e:
            self.log(f"Config Error: {e}")

    def launch_vm_thread(self, name, ram, cpu, disk, iso):
        self.log(f"Starting VM Job: {name}...")
        def task():
            try:
                disk_path = vm_manager.create_disk(name, int(disk))
                if disk_path:
                    self.log(f"Disk Ready: {disk_path}")
                    iso_path = iso if iso and iso.strip() != "" else None
                    vm_manager.launch_vm(int(ram), int(cpu), disk_path, iso_path)
                    self.log("VM Session Ended.")
            except Exception as e:
                self.log(f"VM Error: {e}")
        threading.Thread(target=task).start()

    # =====================================================
    # VIEW: DOCKER
    # =====================================================
    def create_docker_view(self):
        # 1. Main Frame (Using Grid to match System Log)
        self.docker_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.docker_frame.grid(row=0, column=0, sticky="nsew") 
        
        # Expand to fill space
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

        # 2. Create the Tabs
        self.docker_tabs = ctk.CTkTabview(self.docker_frame)
        self.docker_tabs.pack(fill="both", expand=True, padx=20, pady=10)
        
        # --- FIX 1: MAKE TABS BIGGER ---
        # We access the internal button bar to set the font and height
        self.docker_tabs._segmented_button.configure(font=self.font_button, height=40)

        # Create Tab Variables
        tab_manage = self.docker_tabs.add("Manage")
        tab_create = self.docker_tabs.add("Create File")
        tab_build = self.docker_tabs.add("Build Image")
        tab_search = self.docker_tabs.add("Search")

        # ==========================================
        # TAB 1: MANAGE
        # ==========================================
        ctk.CTkLabel(tab_manage, text="Container Management", font=self.font_title).pack(pady=20)
        ctk.CTkButton(tab_manage, text="List All Images", height=50, font=self.font_button, command=self.run_docker_list_images).pack(pady=10, fill="x", padx=150)
        ctk.CTkButton(tab_manage, text="List Running Containers", height=50, font=self.font_button, command=self.run_docker_list_containers).pack(pady=10, fill="x", padx=150)
        
        ctk.CTkFrame(tab_manage, height=2, fg_color="gray").pack(fill="x", pady=30, padx=50)

        ctk.CTkLabel(tab_manage, text="Stop Container (Enter ID):", font=self.font_header).pack(pady=(20, 5))
        stop_frame = ctk.CTkFrame(tab_manage, fg_color="transparent")
        stop_frame.pack(pady=10, fill="x", padx=100) 
        self.entry_stop_id = ctk.CTkEntry(stop_frame, height=60, font=self.font_body, placeholder_text="e.g. a1b2c3d4")
        self.entry_stop_id.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(stop_frame, text="STOP CONTAINER", width=220, height=60, font=self.font_button, fg_color="#C0392B", hover_color="#922B21", command=self.run_docker_stop).pack(side="left", padx=(20, 0))

        # ==========================================
        # TAB 2: CREATE FILE
        # ==========================================
        ctk.CTkLabel(tab_create, text="Create New Docker Project", font=self.font_title).pack(pady=20)

        create_container = ctk.CTkFrame(tab_create, fg_color="transparent")
        create_container.pack(fill="both", expand=True, padx=20, pady=10)
        create_container.grid_columnconfigure(0, weight=3)
        create_container.grid_columnconfigure(1, weight=1)

        left_col = ctk.CTkFrame(create_container, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        self.entry_project_name = ctk.CTkEntry(left_col, placeholder_text="Project Name (Optional)", height=40, font=self.font_body)
        self.entry_project_name.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(left_col, text="Dockerfile Content:", font=self.font_header).pack(anchor="w")
        self.text_dockerfile = ctk.CTkTextbox(left_col, font=self.font_code, wrap="none")
        self.text_dockerfile.pack(fill="both", expand=True, pady=5)

        right_col = ctk.CTkFrame(create_container, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew")
        right_col.grid_rowconfigure(0, weight=1)
        right_col.grid_rowconfigure(2, weight=1)

        ctk.CTkButton(right_col, text="SAVE\nDOCKERFILE", height=80, font=self.font_button, fg_color="#27AE60", hover_color="#1E8449", command=self.save_dockerfile).grid(row=1, column=0, sticky="ew", padx=10)

        # ==========================================
        # TAB 3: BUILD IMAGE
        # ==========================================
        ctk.CTkLabel(tab_build, text="Build Docker Image", font=self.font_title).pack(pady=20)
        ctk.CTkLabel(tab_build, text="Image Tag (Name:Version):", font=self.font_header).pack(pady=(20,5))
        self.entry_build_name = ctk.CTkEntry(tab_build, placeholder_text="e.g. my-app:v1", height=50, font=self.font_body)
        self.entry_build_name.pack(fill="x", padx=150, pady=10)

        ctk.CTkLabel(tab_build, text="Directory Path (Use . for current):", font=self.font_header).pack(pady=(20,5))
        self.entry_build_path = ctk.CTkEntry(tab_build, placeholder_text="e.g. .", height=50, font=self.font_body)
        self.entry_build_path.pack(fill="x", padx=150, pady=10)
        self.entry_build_path.insert(0, ".") 

        ctk.CTkButton(tab_build, text="BUILD IMAGE", height=60, font=self.font_button, fg_color="#8E44AD", hover_color="#71368A", command=self.run_docker_build).pack(pady=30, fill="x", padx=150)

        # ==========================================
        # TAB 4: SEARCH
        # ==========================================
        ctk.CTkLabel(tab_search, text="Search & Pull Images", font=self.font_title).pack(pady=20)
        
        # Search Section
        ctk.CTkLabel(tab_search, text="Search Query:", font=self.font_header).pack(pady=(10,5))
        self.entry_search = ctk.CTkEntry(tab_search, placeholder_text="e.g. python, nginx", height=50, font=self.font_body)
        self.entry_search.pack(fill="x", padx=150, pady=10)
        
        # --- FIX 2: MOVE LOCAL SEARCH HERE ---
        search_btn_frame = ctk.CTkFrame(tab_search, fg_color="transparent")
        search_btn_frame.pack(pady=10)
        
        # Button 1: Search Online
        ctk.CTkButton(search_btn_frame, text="Search Docker Hub", width=200, height=50, font=self.font_button, command=self.run_docker_search).pack(side="left", padx=10)
        # Button 2: Search Local (Moved Up)
        ctk.CTkButton(search_btn_frame, text="Search Local Images", width=200, height=50, font=self.font_button, fg_color="#8E44AD", command=self.run_docker_search_local).pack(side="left", padx=10)
        
        ctk.CTkFrame(tab_search, height=2, fg_color="gray").pack(fill="x", pady=20, padx=50)

        # Pull Section
        ctk.CTkLabel(tab_search, text="Image Name to Pull:", font=self.font_header).pack(pady=(10,5))
        self.entry_pull = ctk.CTkEntry(tab_search, placeholder_text="e.g. ubuntu:latest", height=50, font=self.font_body)
        self.entry_pull.pack(fill="x", padx=150, pady=10)
        
        # Pull Button is now alone at the bottom
        ctk.CTkButton(tab_search, text="Pull Image", width=200, height=50, font=self.font_button, command=self.run_docker_pull).pack(pady=10)

    # --- DOCKER LOGIC ---
    def run_docker_list_images(self):
        self.log("Fetching Images...")
        try:
            # 1. Get list from Docker
            images = docker_manager.client.images.list()
            
            if not images:
                self.log("No images found.")
                return

            # 2. Print Header
            self.log(f"{'REPOSITORY':<25} {'TAG':<15} {'ID':<12} {'SIZE (MB)':<10}")
            self.log("-" * 65)

            # 3. Print Rows
            for img in images:
                # Get size in MB
                size_mb = f"{img.attrs['Size'] / (1024 * 1024):.1f}"
                short_id = img.short_id.split(":")[1][:10]
                
                # Images can have multiple tags, list them all
                tags = img.tags if img.tags else ["<none>:<none>"]
                for tag in tags:
                    if ":" in tag:
                        repo, version = tag.split(":", 1)
                    else:
                        repo, version = tag, "<none>"
                    
                    # Log the row to the GUI
                    self.log(f"{repo:<25} {version:<15} {short_id:<12} {size_mb:<10}")
                    
        except Exception as e:
            self.log(f"Error fetching images: {e}")

    def run_docker_list_containers(self):
        self.log("Fetching Running Containers...")
        try:
            # 1. Get list from Docker
            containers = docker_manager.client.containers.list()
            
            if not containers:
                self.log("No running containers.")
                return

            # 2. Print Header
            self.log(f"{'ID':<12} {'NAME':<20} {'IMAGE':<20} {'STATUS':<15}")
            self.log("-" * 70)

            # 3. Print Rows
            for container in containers:
                cid = container.short_id
                name = container.name
                status = container.status
                
                # Get image name (handle cases where tag is missing)
                image = container.image.tags[0] if container.image.tags else "image_id"
                if len(image) > 18: image = image[:15] + "..." # Shorten if too long
                
                # Log the row to the GUI
                self.log(f"{cid:<12} {name:<20} {image:<20} {status:<15}")
                
        except Exception as e:
            self.log(f"Error fetching containers: {e}")

    def run_docker_stop(self):
        cid = self.entry_stop_id.get()
        if not cid: return
        self.log(f"Stopping {cid}...")
        try:
            docker_manager.client.containers.get(cid).stop()
            self.log("Container Stopped.")
        except Exception as e:
            self.log(f"Error: {e}")

    def run_save_dockerfile(self):
        project = self.entry_project_name.get()
        content = self.text_dockerfile.get("1.0", "end-1c")
        if not project:
            self.log("Error: Enter a project name.")
            return
        full_path = os.path.join(docker_manager.DOCKER_HOME, project)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        file_path = os.path.join(full_path, "Dockerfile")
        try:
            with open(file_path, "w") as f:
                f.write(content)
            self.log(f"Saved Dockerfile to: {file_path}")
        except Exception as e:
            self.log(f"Error saving: {e}")

    def run_docker_build(self):
        # 1. Get Inputs
        tag = self.entry_build_name.get().strip()
        path = self.entry_build_path.get().strip()

        # 2. Input Validation (Instant Feedback)
        if not tag:
            self.log(">> Error: Please enter an Image Tag (e.g., test:v1).")
            return
        if not path:
            self.log(">> Error: Please enter the Directory Path.")
            return
        
        # 3. Path Verification (The most common fix)
        # If user typed just "." but the file is in "Docker_Projects/TestFix1", this catches it.
        if not os.path.exists(path):
            self.log(f">> Error: The folder path does not exist: {path}")
            return
        
        # Check specifically for the Dockerfile
        if not os.path.exists(os.path.join(path, "Dockerfile")):
            self.log(f">> Error: No 'Dockerfile' found inside: {path}")
            return

        # 4. Start the Build Thread
        def thread_target():
            try:
                self.log(f">> Starting build for '{tag}'...")
                self.log(f">> Reading context from: {path}")
                
                # Use low-level API to get real-time stream logs
                response = self.docker_client.api.build(path=path, tag=tag, decode=True)
                
                for chunk in response:
                    if 'stream' in chunk:
                        # Clean up the log line
                        line = chunk['stream'].strip()
                        if line:
                            self.log(f"[Build] {line}")
                    elif 'error' in chunk:
                        self.log(f">> Build Failed: {chunk['error']}")
                        return
                
                self.log(f">> Successfully built image: {tag}")

            except Exception as e:
                self.log(f">> Critical Build Error: {e}")

        threading.Thread(target=thread_target, daemon=True).start()

    def run_docker_search(self):
        term = self.entry_search.get()
        self.log(f"Searching DockerHub for '{term}'...")
        try:
            results = docker_manager.client.images.search(term)
            for r in results[:4]:
                self.log(f"Hub Found: {r['name']} ({r['star_count']} stars)")
        except Exception as e:
            self.log(f"Error: {e}")

    def run_docker_search_local(self):
        # 1. Get the search term
        term = self.entry_search.get().strip().lower()
        
        if not term:
            self.log(">> Please type a name to search locally.")
            return

        def thread_target():
            try:
                self.log(f">> Searching local repositories for '{term}'...")
                images = self.docker_client.images.list()
                
                # Table Header
                output = [f"{'REPOSITORY':<25} {'TAG':<15} {'ID':<12} {'SIZE (MB)':<10}"]
                output.append("-" * 70)
                
                found_count = 0
                for img in images:
                    tags = img.tags if img.tags else ["<none>:<none>"]
                    for tag in tags:
                        # Split into Repo and Version
                        try:
                            repo, version = tag.split(":")
                        except:
                            repo, version = tag, "<none>"
                            
                        # --- THE FIX: STRICT CHECK ---
                        # Only check if 'term' is inside the 'repo' variable.
                        # We ignore the 'version' variable.
                        if term in repo.lower():
                            short_id = img.short_id.split(":")[1][:12]
                            size_mb = f"{img.attrs['Size'] / (1024 * 1024):.1f}"
                            
                            output.append(f"{repo:<25} {version:<15} {short_id:<12} {size_mb:<10}")
                            found_count += 1
                
                if found_count == 0:
                    self.log(f">> No local repositories found matching: '{term}'")
                else:
                    self.log("\n".join(output))

            except Exception as e:
                self.log(f"Error searching local: {e}")

        threading.Thread(target=thread_target, daemon=True).start()

    def run_docker_pull(self):
        img = self.entry_pull.get()
        self.log(f"Pulling {img}...")
        def task():
            try:
                docker_manager.client.images.pull(img)
                self.log("Pull Complete.")
            except Exception as e:
                self.log(f"Error: {e}")
        threading.Thread(target=task).start()

    # --- NAVIGATION ---
    def show_vm_frame(self):
        if self.docker_frame: self.docker_frame.grid_forget()
        self.vm_frame.grid(row=0, column=0, sticky="nsew")

    def show_docker_frame(self):
        self.vm_frame.grid_forget()
        self.docker_frame.grid(row=0, column=0, sticky="nsew")
        
    def save_dockerfile(self):
        # 1. Get Project Name & Content
        project_name = self.entry_project_name.get().strip()
        content = self.text_dockerfile.get("0.0", "end").strip()

        # Validation: Must have a name and content
        if not project_name:
            self.log(">> Error: Please enter a Project Name to create the folder.")
            return
        if not content:
            self.log(">> Error: Dockerfile content is empty.")
            return

        # 2. Define the Path: Docker_Projects / <ProjectName> / Dockerfile
        base_folder = "Docker_Projects"
        project_folder = os.path.join(base_folder, project_name)
        file_path = os.path.join(project_folder, "Dockerfile")

        try:
            # 3. Create the Folder (if it doesn't exist)
            if not os.path.exists(project_folder):
                os.makedirs(project_folder)
                self.log(f">> Created new project folder: {project_folder}")

            # 4. Save the File (Force name 'Dockerfile', no extension)
            # newline='\n' ensures Linux-style line endings even on Windows
            with open(file_path, "w", newline='\n') as f: 
                f.write(content)
            
            self.log(f">> Success! Saved to: {file_path}")

        except Exception as e:
            self.log(f"Error saving file: {e}")

if __name__ == "__main__":
    app = CloudManagerApp()
    app.mainloop()