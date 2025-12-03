from entropy_harvester import capture_entropy_snapshot
from fragment_generator import generate_fragment
import hashlib

def create_personal_fragment():
    # Step 1: Capture YOUR system's entropy
    print("Capturing your digital essence...")
    snapshot, seed_hash = capture_entropy_snapshot()
    
    print(f"Your unique seed: {seed_hash[:16]}...")
    
    # Step 2: Generate YOUR fragment
    print("Generating your Orya fragment...")
    filename, full_hash = generate_fragment(seed_hash, "orya_user")
    
    print(f"\n✨ Fragment created: {filename}")
    print(f"📊 Entropy sources:")
    for key, value in snapshot.items():
        print(f"   - {key}: {value}")
    
    return filename, seed_hash

if __name__ == "__main__":
    create_personal_fragment()