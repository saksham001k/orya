import matplotlib.pyplot as plt
import numpy as np
import hashlib
import json
import time
from PIL import Image, ImageDraw
import io
from datetime import datetime
from entropy_harvester import capture_entropy_snapshot  # Add this import

def hash_to_params(seed_hash):
    """Converts a hash string into deterministic parameters for generation."""
    # Use parts of the hash as parameters
    num_params = 10
    params = []
    for i in range(0, len(seed_hash), 8):
        chunk = seed_hash[i:i+8]
        params.append(int(chunk, 16) / 0xffffffff)  # Normalize to 0-1
    
    return params[:num_params]

def generate_fragment(seed_hash, user_id="user"):
    """Generates a visual fragment from a seed hash."""
    params = hash_to_params(seed_hash)
    
    # Create a deterministic but chaotic visual
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='black')
    ax.set_facecolor('black')
    ax.axis('off')
    
    # Use params to draw something unique
    n_points = 500
    # Use the hash to seed the random state for reproducibility
    random_seed = int(seed_hash[:8], 16)
    rng = np.random.RandomState(random_seed)
    
    angles = np.cumsum(rng.randn(n_points) * 0.5)
    radii = np.linspace(0.1, 2, n_points)
    
    for i in range(min(5, len(params))):
        offset = params[i] * 2 * np.pi
        x = radii * np.cos(angles + offset + params[i])
        y = radii * np.sin(angles + offset + params[i])
        color = (params[5], params[6], params[7], 0.7)
        ax.plot(x, y, color=color, linewidth=0.5 + params[i])
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    
    # Create final image
    img = Image.open(buf)
    draw = ImageDraw.Draw(img)
    
    # Optional: add tiny hash text in corner (uncomment if wanted)
    # draw.text((10, img.height-20), f"#{seed_hash[:8]}", fill=(255,255,255,100))
    
    filename = f"fragments/{user_id}_{seed_hash[:12]}.png"
    img.save(filename)
    return filename, seed_hash

def generate_fragment_with_personality(seed_hash, user_id="user"):
    """Generates a fragment with personality traits based on entropy."""
    snapshot, _ = capture_entropy_snapshot()  # Get actual entropy data
    
    # Determine personality based on entropy patterns
    personality = {
        'chaos': snapshot.get('cpu_jitter', 10) / 100.0,  # Use .get() for safety
        'calm': 1.0 - (snapshot.get('cpu_jitter', 10) / 100.0),
        'complexity': snapshot.get('process_count', 100) / 1000.0,
        'age': (time.time() - snapshot.get('boot_time', time.time())) / 86400.0,  # days since boot
        'energy': snapshot.get('memory_free', 8000000000) / (1024**3) / 16.0  # GB free
    }
    
    # Generate fragment with personality
    filename, seed = generate_fragment(seed_hash, user_id)
    
    # Add personality metadata
    personality_file = f"fragments/{user_id}_{seed[:12]}_personality.json"
    with open(personality_file, 'w') as f:
        json.dump({
            'hash': seed,
            'personality': personality,
            'timestamp': datetime.now().isoformat(),
            'traits': describe_personality(personality)
        }, f, indent=2)
    
    return filename, seed, personality

def describe_personality(personality):
    """Create a poetic description of the fragment's personality."""
    traits = []
    
    if personality['chaos'] > 0.7:
        traits.append("chaotic")
    elif personality['calm'] > 0.7:
        traits.append("serene")
    
    if personality['complexity'] > 0.5:
        traits.append("intricate")
    else:
        traits.append("minimal")
    
    if personality['age'] > 7:
        traits.append("ancient")
    elif personality['age'] < 1:
        traits.append("newborn")
    
    if personality['energy'] > 0.7:
        traits.append("energetic")
    elif personality['energy'] < 0.3:
        traits.append("dormant")
    
    return traits

if __name__ == "__main__":
    # Test basic fragment
    test_hash = hashlib.sha256(b"test").hexdigest()
    filename, seed = generate_fragment(test_hash)
    print(f"Basic fragment generated: {filename}")
    print(f"Seed: {seed}")
    
    # Test personality fragment
    print("\n--- Testing Personality Fragment ---")
    try:
        filename2, seed2, personality = generate_fragment_with_personality(test_hash, "test_user")
        print(f"Personality fragment generated: {filename2}")
        print(f"Personality traits: {describe_personality(personality)}")
        print(f"Personality data: {personality}")
    except Exception as e:
        print(f"Error generating personality fragment: {e}")
        print("Make sure entropy_harvester.py is in the same directory")