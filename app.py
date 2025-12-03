from flask import Flask, render_template, request, send_file, jsonify
from entropy_harvester import capture_entropy_snapshot
from fragment_generator import generate_fragment
from living_fragment import create_animation_frames
import os
import json
from datetime import datetime
import hashlib
import time
import glob  # Add this import

app = Flask(__name__)

# Store fragments metadata
FRAGMENTS_DB = []

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate a new fragment"""
    snapshot, seed_hash = capture_entropy_snapshot()
    filename, full_hash = generate_fragment(seed_hash, "web_user")
    
    # Also create personality data for this fragment
    create_personality_data(seed_hash, snapshot, "web_user")
    
    # Store metadata
    fragment_data = {
        'filename': os.path.basename(filename),
        'hash': full_hash,
        'timestamp': datetime.now().isoformat(),
        'entropy_sources': snapshot,
        'type': 'static'
    }
    FRAGMENTS_DB.append(fragment_data)
    
    return jsonify({
        'filename': os.path.basename(filename),
        'hash': full_hash,
        'message': 'Fragment created successfully'
    })

@app.route('/generate_living', methods=['POST'])
def generate_living():
    """Generate a living (animated) fragment"""
    snapshot, seed_hash = capture_entropy_snapshot()
    frames = create_animation_frames(seed_hash, num_frames=5)
    
    # Also create personality data for this fragment
    create_personality_data(seed_hash, snapshot, "living_user")
    
    # Store metadata
    fragment_data = {
        'filename': [os.path.basename(f) for f in frames],
        'hash': seed_hash,
        'timestamp': datetime.now().isoformat(),
        'entropy_sources': snapshot,
        'type': 'living'
    }
    FRAGMENTS_DB.append(fragment_data)
    
    return jsonify({
        'frames': [os.path.basename(f) for f in frames],
        'hash': seed_hash,
        'message': 'Living fragment created with 5 frames'
    })

@app.route('/fragment/<filename>')
def get_fragment(filename):
    """Serve the fragment image"""
    return send_file(f'fragments/{filename}', mimetype='image/png')

@app.route('/gallery')
def gallery():
    """Show all generated fragments"""
    return render_template('gallery.html', fragments=FRAGMENTS_DB[-20:])

@app.route('/fragment/<hash>/info')
def fragment_info(hash):
    """Get personality info about a fragment"""
    # Search for personality file with this hash
    pattern = f"fragments/*_{hash[:12]}_personality.json"
    files = glob.glob(pattern)
    
    if not files:
        # Try with full hash pattern
        pattern = f"fragments/*_{hash}_personality.json"
        files = glob.glob(pattern)
    
    if files:
        with open(files[0], 'r') as f:
            data = json.load(f)
        return jsonify(data)
    
    return jsonify({'error': 'Fragment personality data not found'})

@app.route('/merge', methods=['POST'])
def merge_fragments():
    """Merge two fragments into a new one"""
    data = request.json
    hash1 = data.get('hash1', '').strip()
    hash2 = data.get('hash2', '').strip()
    
    if not hash1 or not hash2:
        return jsonify({'error': 'Missing fragment hashes'})
    
    # Create merged hash
    merged_hash = hashlib.sha256(f"{hash1}{hash2}".encode()).hexdigest()
    
    # Generate new fragment from merged hash
    filename, seed = generate_fragment(merged_hash, "merged")
    
    # Create merge metadata
    merge_file = f"fragments/merged_{seed[:12]}_info.json"
    with open(merge_file, 'w') as f:
        json.dump({
            'merged_hash': seed,
            'parent_hashes': [hash1[:12], hash2[:12]],
            'timestamp': datetime.now().isoformat(),
            'message': f'Merged from {hash1[:12]} and {hash2[:12]}'
        }, f, indent=2)
    
    return jsonify({
        'filename': os.path.basename(filename),
        'hash': seed,
        'parent_hashes': [hash1[:12], hash2[:12]],
        'message': 'Fragments merged successfully'
    })

def create_personality_data(seed_hash, snapshot, user_id):
    """Create personality JSON file for a fragment"""
    # Calculate personality traits
    personality = {
        'chaos': snapshot.get('cpu_jitter', 10) / 100.0,
        'calm': 1.0 - (snapshot.get('cpu_jitter', 10) / 100.0),
        'complexity': snapshot.get('process_count', 100) / 1000.0,
        'age': (time.time() - snapshot.get('boot_time', time.time())) / 86400.0,
        'energy': snapshot.get('memory_free', 8000000000) / (1024**3) / 16.0
    }
    
    # Determine traits
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
    
    # Create personality file
    personality_file = f"fragments/{user_id}_{seed_hash[:12]}_personality.json"
    with open(personality_file, 'w') as f:
        json.dump({
            'hash': seed_hash,
            'personality': personality,
            'timestamp': datetime.now().isoformat(),
            'traits': traits
        }, f, indent=2)
    
    return personality_file

if __name__ == '__main__':
    # Ensure fragments directory exists
    os.makedirs('fragments', exist_ok=True)
    app.run(debug=True, port=5000)