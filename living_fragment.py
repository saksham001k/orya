import numpy as np
import hashlib
from PIL import Image, ImageDraw
import io

def generate_living_fragment(seed_hash, frame=0, user_id="living"):
    """Generates an animated/evolving fragment that changes over time."""
    
    # Use hash + frame to get different but related parameters each time
    combined_hash = hashlib.sha256(f"{seed_hash}_{frame}".encode()).hexdigest()
    
    # Convert to parameters
    params = []
    for i in range(0, len(combined_hash), 6):
        chunk = combined_hash[i:i+6]
        params.append(int(chunk, 16) / 0xffffff)
    
    # Create image
    size = 800
    img = Image.new('RGB', (size, size), color='black')
    draw = ImageDraw.Draw(img)
    
    # Draw evolving patterns based on frame
    center_x, center_y = size // 2, size // 2
    
    for i in range(50):
        # Parameters evolve with frame number
        radius = params[i % len(params)] * 300 + (frame * 2)
        angle = (i * 0.125 + frame * 0.01) * 2 * np.pi
        
        # Pulsing effect
        pulse = np.sin(frame * 0.1 + i * 0.5) * 20
        
        x = center_x + (radius + pulse) * np.cos(angle)
        y = center_y + (radius + pulse) * np.sin(angle)
        
        # Color evolves too
        r = int(100 + 155 * abs(np.sin(params[0] + frame * 0.05)))
        g = int(100 + 155 * abs(np.sin(params[1] + frame * 0.03)))
        b = int(100 + 155 * abs(np.sin(params[2] + frame * 0.07)))
        
        radius_point = 5 + params[i % len(params)] * 10
        draw.ellipse([x-radius_point, y-radius_point, x+radius_point, y+radius_point],
                    fill=(r, g, b))
    
    filename = f"fragments/{user_id}_{seed_hash[:12]}_frame{frame:03d}.png"
    img.save(filename)
    return filename, combined_hash

def create_animation_frames(seed_hash, num_frames=10):
    """Create multiple frames for an animation"""
    frames = []
    for frame in range(num_frames):
        filename, _ = generate_living_fragment(seed_hash, frame)
        frames.append(filename)
    return frames

if __name__ == "__main__":
    # Test with a hash
    test_hash = hashlib.sha256(b"living_test").hexdigest()
    frames = create_animation_frames(test_hash, 5)
    print(f"Created living fragment frames: {frames}")