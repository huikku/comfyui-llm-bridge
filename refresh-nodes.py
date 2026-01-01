#!/usr/bin/env python3
"""
ComfyUI Node Compressor for LLM Integration

Fetches node definitions from a running ComfyUI instance, compresses them
into a compact format, and splits them into domain-specific files.

Usage:
    python refresh-nodes.py                    # Auto-detect port, fetch and compress
    python refresh-nodes.py --port 8000        # Use specific port
    python refresh-nodes.py -i object_info.json  # Use local file instead of fetching
"""

import json
import os
import argparse
import fnmatch
from urllib.request import urlopen
from urllib.error import URLError
from pathlib import Path

# --- Configuration ---
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "category-map.json"
OUTPUT_DIR = SCRIPT_DIR / "nodes"

# --- Single-letter type codes ---
TYPE_CODES = {
    "MODEL": "M", "IMAGE": "G", "CONDITIONING": "C", "LATENT": "A",
    "VAE": "V", "CLIP": "P", "STRING": "S", "INT": "I", "FLOAT": "F",
    "BOOLEAN": "B", "MASK": "K", "CONTROL_NET": "T", "LIST": "L",
    "CLIP_VISION_OUTPUT": "O", "CLIP_VISION": "N", "STYLE_MODEL": "Y",
    "UPSCALE_MODEL": "U", "GLIGEN": "H", "*": "*", "BASIC_PIPE": "E",
    "DETAILER_PIPE": "D", "SAM_MODEL": "Q", "BBOX_DETECTOR": "X",
    "SEGM_DETECTOR": "Z", "PK_HOOK": "J", "SCHEDULER_FUNC": "R",
    "GUIDER": "W", "SIGMAS": "0", "NOISE": "1", "AUDIO": "2",
    "SAMPLER": "3", "HOOKS": "4", "COMBO": "L",
}

LEGEND = "# M=MODEL G=IMAGE C=CONDITIONING A=LATENT V=VAE P=CLIP S=STRING I=INT F=FLOAT B=BOOLEAN K=MASK T=CONTROL_NET L=LIST * for any other type"


def load_config():
    """Load category mapping configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "output_files": {},
        "full_output": "full.txt",
        "default_port_order": [8188, 8000, 8888],
        "connection_timeout": 2
    }


def detect_comfyui_port(ports, timeout=2):
    """Try to find a running ComfyUI instance on common ports."""
    for port in ports:
        try:
            url = f"http://localhost:{port}/object_info"
            response = urlopen(url, timeout=timeout)
            if response.status == 200:
                print(f"[OK] Found ComfyUI on port {port}")
                return port, response.read().decode('utf-8')
        except (URLError, TimeoutError, ConnectionRefusedError):
            print(f"  Port {port}: not responding")
            continue
    return None, None


def get_type_code(type_name):
    """Get compact type code for a type name."""
    if not isinstance(type_name, str):
        return "*"
    return TYPE_CODES.get(type_name, type_name)


def format_enum(values, max_options=10):
    """Format enum values inline if short enough, otherwise return L."""
    if not isinstance(values, list):
        return "L"
    if len(values) <= max_options:
        # Short enum - expand inline
        return "[" + "|".join(str(v) for v in values) + "]"
    else:
        # Long enum - just mark as list
        return "L"


def compress_node(node_name, node_data):
    """Compress a single node definition to compact format."""
    node_line = f"@{node_name}"
    
    # Process inputs
    if 'input' in node_data and isinstance(node_data['input'], dict):
        # Required inputs
        required = node_data['input'].get('required', {})
        if isinstance(required, dict):
            for input_name, input_info in required.items():
                type_name = "UNKNOWN"
                type_str = None
                if isinstance(input_info, list) and len(input_info) > 0:
                    potential_type = input_info[0]
                    if isinstance(potential_type, list):
                        # This is a COMBO/dropdown - try to expand short enums
                        type_str = format_enum(potential_type)
                    elif isinstance(potential_type, str):
                        type_name = potential_type
                if type_str is None:
                    type_str = get_type_code(type_name)
                node_line += f" +{input_name}:{type_str}"
        
        optional = node_data['input'].get('optional', {})
        if isinstance(optional, dict):
            for input_name, input_info in optional.items():
                type_name = "UNKNOWN"
                type_str = None
                if isinstance(input_info, list) and len(input_info) > 0:
                    potential_type = input_info[0]
                    if isinstance(potential_type, list):
                        # This is a COMBO/dropdown - try to expand short enums
                        type_str = format_enum(potential_type)
                    elif isinstance(potential_type, str):
                        type_name = potential_type
                if type_str is None:
                    type_str = get_type_code(type_name)
                node_line += f" ?{input_name}:{type_str}"
    
    # Process outputs
    output_names = node_data.get('output_name', [])
    output_types = node_data.get('output', [])
    for i in range(min(len(output_names), len(output_types))):
        node_line += f" -{output_names[i]}:{get_type_code(output_types[i])}"
    
    return node_line


def matches_patterns(node_name, patterns):
    """Check if node name matches any of the given patterns."""
    if not patterns:
        return False
    for pattern in patterns:
        if fnmatch.fnmatch(node_name, pattern):
            return True
    return False


def compress_and_split(json_data, config):
    """Compress node definitions and split into category files."""
    if not isinstance(json_data, dict):
        print("Error: Input data is not a valid JSON object.")
        return None
    
    # Group nodes by category
    nodes_by_category = {}
    node_to_category = {}  # Track which category each node belongs to
    
    for node_name, node_data in json_data.items():
        category = node_data.get('category', 'other').split('/')[0]
        if category not in nodes_by_category:
            nodes_by_category[category] = []
        
        compressed = compress_node(node_name, node_data)
        nodes_by_category[category].append(compressed)
        node_to_category[node_name] = category
    
    # Build full output
    full_lines = [LEGEND]
    for category in sorted(nodes_by_category.keys()):
        full_lines.append(f"# {category}")
        full_lines.extend(nodes_by_category[category])
        full_lines.append("")
    
    full_output = "\n".join(full_lines)
    
    # Build split outputs based on config
    split_outputs = {}
    output_files = config.get("output_files", {})
    
    for split_name, split_config in output_files.items():
        split_lines = [LEGEND]
        categories = split_config.get("categories", [])
        patterns = split_config.get("node_patterns", [])
        
        # Add nodes from matching categories
        added_nodes = set()
        for category in categories:
            if category in nodes_by_category:
                split_lines.append(f"# {category}")
                split_lines.extend(nodes_by_category[category])
                split_lines.append("")
                for node_line in nodes_by_category[category]:
                    node_name = node_line.split()[0][1:]  # Remove @ prefix
                    added_nodes.add(node_name)
        
        # Add nodes matching patterns (from any category)
        if patterns:
            pattern_nodes = []
            for node_name, node_data in json_data.items():
                if node_name not in added_nodes and matches_patterns(node_name, patterns):
                    pattern_nodes.append(compress_node(node_name, node_data))
            
            if pattern_nodes:
                split_lines.append("# pattern-matched")
                split_lines.extend(pattern_nodes)
                split_lines.append("")
        
        split_outputs[split_config["filename"]] = "\n".join(split_lines)
    
    # Add full output
    split_outputs[config.get("full_output", "full.txt")] = full_output
    
    return split_outputs


def main():
    parser = argparse.ArgumentParser(description='Fetch and compress ComfyUI node definitions')
    parser.add_argument('-i', '--input', help='Input JSON file (skip fetching)')
    parser.add_argument('-p', '--port', type=int, help='ComfyUI port (skip auto-detection)')
    parser.add_argument('-o', '--output-dir', help='Output directory for compressed files')
    args = parser.parse_args()
    
    config = load_config()
    output_dir = Path(args.output_dir) if args.output_dir else OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get node data
    json_data = None
    
    if args.input:
        # Load from file
        print(f"Loading from file: {args.input}")
        with open(args.input, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    else:
        # Fetch from running ComfyUI
        if args.port:
            ports = [args.port]
        else:
            ports = config.get("default_port_order", [8188, 8000, 8888])
        
        print("Detecting ComfyUI instance...")
        port, content = detect_comfyui_port(ports, config.get("connection_timeout", 2))
        
        if port is None:
            print("\n[ERROR] Could not find running ComfyUI instance.")
            print("  Make sure ComfyUI is running, or use -i to specify a JSON file.")
            return 1
        
        json_data = json.loads(content)
    
    # Compress and split
    print(f"\nProcessing {len(json_data)} nodes...")
    outputs = compress_and_split(json_data, config)
    
    if not outputs:
        print("Error: Failed to compress nodes.")
        return 1
    
    # Write output files
    print(f"\nWriting to {output_dir}/")
    for filename, content in outputs.items():
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        lines = len([l for l in content.split('\n') if l.strip()])
        print(f"  {filename}: {len(content):,} bytes, {lines} lines")
    
    # Stats for full output
    full_file = config.get("full_output", "full.txt")
    if full_file in outputs:
        full_content = outputs[full_file]
        print(f"\nTotal: {len(full_content):,} bytes (~{len(full_content)//4:,} tokens)")
    
    print("\n[OK] Done!")
    return 0


if __name__ == "__main__":
    exit(main())
