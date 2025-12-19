import docker
import os

# This connects Python to the Docker Service we fixed earlier
try:
    client = docker.from_env()
except Exception as e:
    print(f"Error connecting to Docker: {e}")
    print("Did you run 'sudo service docker start'?")

def list_images():
    """Lists all Docker images downloaded on this system."""
    print("\n--- Local Docker Images ---")
    try:
        images = client.images.list()
        if not images:
            print("No images found. Try pulling one first!")
        
        for img in images:
            # Images can have multiple tags, we print the first one
            tags = img.tags if img.tags else ["<no-tag>"]
            print(f"ID: {img.short_id} | Tags: {', '.join(tags)}")
    except Exception as e:
        print(f"Error listing images: {e}")

def list_containers():
    """Lists currently running containers."""
    print("\n--- Running Containers ---")
    try:
        containers = client.containers.list()
        if not containers:
            print("No containers are currently running.")
            
        for container in containers:
            print(f"ID: {container.short_id} | Name: {container.name} | Status: {container.status}")
    except Exception as e:
        print(f"Error listing containers: {e}")

def pull_image():
    """Downloads an image from Docker Hub."""
    image_name = input("Enter image name to pull (e.g., 'ubuntu', 'nginx', 'python'): ")
    print(f"Pulling '{image_name}'... (This might take a moment)")
    
    try:
        client.images.pull(image_name)
        print(f"Successfully pulled {image_name}!")
    except docker.errors.ImageNotFound:
        print(f"Error: Image '{image_name}' not found on DockerHub.")
    except Exception as e:
        print(f"Error: {e}")

def stop_container():
    """Stops a specific running container."""
    container_id = input("Enter Container ID or Name to stop: ")
    try:
        # We need to 'get' the container object first, then stop it
        container = client.containers.get(container_id)
        print(f"Stopping container {container_id}...")
        container.stop()
        print(f"Container {container_id} stopped successfully!")
    except docker.errors.NotFound:
        print(f"Error: Container '{container_id}' not found.")
    except Exception as e:
        print(f"Error: {e}")

def search_dockerhub():
    """Searches Docker Hub for images."""
    term = input("Enter image name to search on Docker Hub: ")
    print(f"Searching for '{term}'...")
    
    try:
        # The Docker API returns a list of dictionaries
        results = client.images.search(term)
        
        print(f"\n--- Search Results for '{term}' ---")
        # Let's show the top 5 results so we don't spam the screen
        for result in results[:5]: 
            # Some descriptions are very long, so we cut them off at 50 characters
            description = result['description'][:50] + "..." if result['description'] else "No description"
            print(f"Name: {result['name']} | Star Count: {result['star_count']} | Desc: {description}")
            
    except Exception as e:
        print(f"Error searching Docker Hub: {e}")  

def create_dockerfile():
    """Creates a Dockerfile based on user input."""
    print("\n--- Create Dockerfile ---")
    
    # 1. Ask where to save it
    folder = input("Enter a folder name to save this project (e.g., 'my_website'): ")
    
    # Create the folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created folder: {folder}")
    
    # 2. Get the content
    print("Enter Dockerfile instructions one by one.")
    print("Type 'DONE' when you are finished.")
    print("Example: FROM ubuntu")
    
    lines = []
    while True:
        line = input("Instruction: ")
        if line.strip().upper() == 'DONE':
            break
        lines.append(line)
    
    # 3. Write the file
    file_path = os.path.join(folder, "Dockerfile")
    try:
        with open(file_path, "w") as f:
            for instruction in lines:
                f.write(instruction + "\n")
        print(f"Dockerfile successfully saved at: {file_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

def build_image():
    """Builds a Docker image from a directory containing a Dockerfile."""
    print("\n--- Build Docker Image ---")
    
    # 1. Ask for the folder containing the Dockerfile
    path = input("Enter path to the folder with Dockerfile (e.g., 'my_website'): ")
    
    if not os.path.exists(path):
        print("Error: That folder does not exist.")
        return

    # 2. Ask for a name for the new image
    tag_name = input("Enter a name for your new image (e.g., 'my-custom-app:v1'): ")
    
    print("Building image... please wait...")
    
    try:
        # docker build -t tag_name path
        image, build_logs = client.images.build(path=path, tag=tag_name)
        
        # Optional: Print build logs if you want to see details
        # for chunk in build_logs:
        #     if 'stream' in chunk:
        #         print(chunk['stream'], end='')
                
        print(f"\nSuccess! Image '{tag_name}' built successfully.")
        print(f"Image ID: {image.short_id}")
        
    except docker.errors.BuildError as e:
        print(f"Build failed: {e}")
        # Print the build log to see why it failed
        for line in e.build_log:
            if 'stream' in line:
                print(line['stream'], end='')
    except Exception as e:
        print(f"Error: {e}")