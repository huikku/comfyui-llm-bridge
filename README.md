# ComfyUI LLM Integration

A portable package that enables LLM-assisted ComfyUI workflow generation with live node discovery.

## Features

- **Port Auto-Detection**: Automatically finds running ComfyUI on ports 8188, 8000, or 8888
- **Node Compression**: Reduces token usage by 80%+ with compact notation
- **Domain Splitting**: Generates focused files for different workflow types
- **Antigravity Integration**: Workflow file for seamless IDE integration

## Quick Start

1. **Copy this folder** to your ComfyUI installation directory

2. **Ensure ComfyUI is running**, then refresh nodes:
   ```bash
   python refresh-nodes.py
   ```

3. **Use with Antigravity**: Open your ComfyUI folder in the IDE and use `/comfyui` workflow

## Usage

### Basic Usage (Auto-detect port)
```bash
python refresh-nodes.py
```

### Specify Port
```bash
python refresh-nodes.py --port 8000
```

### Use Existing JSON File
```bash
python refresh-nodes.py -i object_info.json
```

### Custom Output Directory
```bash
python refresh-nodes.py -o ./my-nodes/
```

## Generated Files

| File | Description |
|------|-------------|
| `nodes/core.txt` | Essential nodes: loaders, samplers, conditioning, latent, image, mask |
| `nodes/video.txt` | Video generation: Wan, LTXV, Cosmos, Hunyuan, VHS |
| `nodes/3d.txt` | 3D models: Tripo, Hy3D, mesh operations |
| `nodes/segmentation.txt` | Segmentation: SAM, BiRefNet, AILab, detectors |
| `nodes/api.txt` | API nodes: Kling, Runway, Veo, OpenAI, Luma |
| `nodes/training.txt` | Training: LoRA, datasets |
| `nodes/advanced.txt` | Advanced model operations |
| `nodes/full.txt` | All nodes (fallback) |

## Node Format

Compressed nodes use this format:
```
@NodeName +required:TYPE ?optional:TYPE -output:TYPE
```

**Type Codes:**
- `M`=MODEL, `G`=IMAGE, `C`=CONDITIONING, `A`=LATENT
- `V`=VAE, `P`=CLIP, `S`=STRING, `I`=INT, `F`=FLOAT
- `B`=BOOLEAN, `K`=MASK, `T`=CONTROL_NET, `L`=LIST

## Configuration

Edit `category-map.json` to customize:
- Which categories go into which files
- Node name patterns for matching
- Port detection order
- Connection timeout

## Requirements

- Python 3.6+
- No external dependencies (uses stdlib only)
