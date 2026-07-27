from huggingface_hub import list_repo_files, hf_hub_download
import os

repo_id = "unsloth/Llama-3.1-8B-Instruct-GGUF"
print(f"Listing files in {repo_id}...")

try:
    files = list_repo_files(repo_id=repo_id)
    # Find the Q4_K_M gguf
    target_file = next((f for f in files if "Q4_K_M" in f.upper() and f.endswith(".gguf")), None)
    
    if not target_file:
        print("Could not find a Q4_K_M model. Available files:")
        for f in files:
            print(f" - {f}")
    else:
        print(f"Found target file: {target_file}")
        print("Starting robust download to C: drive...")
        
        c_drive_dir = "C:/Users/plumb/models"
        os.makedirs(c_drive_dir, exist_ok=True)
        
        file_path = hf_hub_download(
            repo_id=repo_id,
            filename=target_file,
            local_dir=c_drive_dir
        )
        expected_path = os.path.join(c_drive_dir, "llama3-8b.gguf")
        if file_path != expected_path:
            if os.path.exists(expected_path):
                os.remove(expected_path)
            os.rename(file_path, expected_path)
            
        print(f"Download complete! Saved to {expected_path}")
        
except Exception as e:
    print(f"Error: {e}")
