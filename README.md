# ComfyUI LLM Bridge

**A portable integration layer that enables [Antigravity IDE](https://antigravity.google) agents to generate valid ComfyUI workflows using live node discovery.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

---

## What This Does

ComfyUI exposes every installed node via its `/object_info` API—but this JSON is **massive** (10MB+ with custom nodes) and structurally complex. When LLMs try to generate workflows directly from this data, they:

- ❌ Hallucinate non-existent node names
- ❌ Misconnect incompatible types  
- ❌ Burn context window on verbose schemas
- ❌ Miss your custom nodes entirely

**This bridge solves all of that:**

- ✅ **Live Discovery** — Fetches node definitions directly from your running ComfyUI
- ✅ **80%+ Compression** — Converts verbose JSON to compact, LLM-optimized notation
- ✅ **Domain Splitting** — Organizes nodes by task (video, 3D, segmentation, etc.)
- ✅ **Antigravity Workflow** — Ready-to-use `/comfyui` slash command for seamless generation

---

## Designed for Antigravity IDE

This project is built specifically for **[Google Antigravity](https://antigravity.google)**—the agent-first IDE that enables autonomous AI agents to handle complex software development tasks.

### Why Antigravity?

Antigravity's agent architecture is uniquely suited for ComfyUI workflow generation:

| Capability | How It Helps |
|------------|--------------|
| **Terminal Access** | Agents can run `refresh-nodes.py` to fetch live node definitions |
| **File System Access** | Agents read compressed node files and write workflow JSON |
| **Browser Control** | Agents can verify workflows load correctly in ComfyUI's web UI |
| **Task Planning** | Complex multi-node workflows benefit from Antigravity's planning artifacts |
| **Knowledge Persistence** | Node definitions and workflow patterns persist across sessions |

### The `/comfyui` Workflow

Drop this bridge into any ComfyUI installation and the included Antigravity workflow handles everything:

1. **Auto-refresh** — Runs `refresh-nodes.py` to get current node definitions
2. **Smart file selection** — Loads only the domain files needed for your task
3. **Validated generation** — Creates workflows using **only your installed nodes**
4. **Type checking** — Validates all connections match compatible input/output types

---

## Quick Start

### Prerequisites

- [Antigravity IDE](https://antigravity.google) (free download for Windows, macOS, Linux)
- ComfyUI running locally
- Python 3.6+

### Installation

```bash
# Clone into your ComfyUI directory
cd /path/to/ComfyUI
git clone https://github.com/huikku/comfyui-llm-bridge.git

# Copy the .agent folder to ComfyUI root (required for Antigravity to detect workflows)
cp -r comfyui-llm-bridge/.agent .
```

### Recommended Workflow

**Open your ComfyUI folder in Antigravity IDE** — this gives the agent access to your models, custom nodes, and the bridge together in one workspace.

```
ComfyUI/
├── .agent/                     ← Workflows must be at root level
│   └── workflows/
│       └── comfyui.md
├── models/
├── custom_nodes/
├── comfyui-llm-bridge/
│   ├── nodes/
│   └── refresh-nodes.py
└── ...
```

> **Note:** Antigravity only detects `.agent/workflows/` at the workspace root, which is why we copy it up from the cloned repo.

### Usage

1. **Open ComfyUI folder** in Antigravity IDE as your workspace
2. **Ensure ComfyUI is running** (the bridge needs to query it)
3. **Type `/comfyui`** in the chat to invoke the workflow
4. **Describe what you want** — the agent handles the rest

**Example prompts:**
- "Generate an img2img workflow with ControlNet depth"
- "Create a video generation workflow using Wan 2.1"
- "Build a LoRA training workflow for SDXL"

---

## How Compression Works

### Before: 847 bytes of JSON
```json
{
  "KSampler": {
    "input": {
      "required": {
        "model": ["MODEL"],
        "positive": ["CONDITIONING"],
        "negative": ["CONDITIONING"],
        "latent_image": ["LATENT"],
        "seed": ["INT", {"default": 0}],
        "steps": ["INT", {"default": 20}],
        "cfg": ["FLOAT", {"default": 8.0}],
        "sampler_name": [["euler", "euler_ancestral", "heun", ...]],
        "scheduler": [["normal", "karras", "exponential", ...]]
      }
    },
    "output": ["LATENT"],
    "output_name": ["LATENT"]
  }
}
```

### After: 142 bytes (~83% reduction)
```
@KSampler +model:M +positive:C +negative:C +latent_image:A +seed:I +steps:I +cfg:F +sampler_name:[euler|euler_ancestral|heun|...] +scheduler:[normal|karras|...] -LATENT:A
```

---

## Node Notation Reference

```
@NodeName +required:TYPE ?optional:TYPE -output:TYPE
```

### Prefixes
| Symbol | Meaning |
|--------|---------|
| `@` | Node class name |
| `+` | Required input |
| `?` | Optional input |
| `-` | Output |

### Type Codes
| Code | Type | Code | Type |
|------|------|------|------|
| `M` | MODEL | `G` | IMAGE |
| `C` | CONDITIONING | `A` | LATENT |
| `V` | VAE | `P` | CLIP |
| `S` | STRING | `I` | INT |
| `F` | FLOAT | `B` | BOOLEAN |
| `K` | MASK | `T` | CONTROL_NET |
| `L` | LIST/COMBO | `*` | Any other type |

### Inline Enums

Short dropdowns (≤10 options) are expanded inline for better generation accuracy:

```
+scheduler:[normal|karras|exponential|sgm_uniform]
```

---

## Generated Files

Node definitions are split by domain to minimize context usage:

| File | Contents |
|------|----------|
| `nodes/core.txt` | Loaders, samplers, conditioning, latent, image, mask |
| `nodes/video.txt` | Wan, LTXV, Cosmos, Hunyuan, VHS |
| `nodes/3d.txt` | Tripo, Hy3D, mesh operations |
| `nodes/segmentation.txt` | SAM, BiRefNet, detectors |
| `nodes/api.txt` | Kling, Runway, Veo, OpenAI, Luma |
| `nodes/training.txt` | LoRA, datasets |
| `nodes/advanced.txt` | Advanced model operations |
| `nodes/full.txt` | Complete reference (fallback) |

---

## CLI Reference

### Auto-detect port
```bash
python refresh-nodes.py
```

### Specify port
```bash
python refresh-nodes.py --port 8000
```

### Use local JSON file
```bash
python refresh-nodes.py -i object_info.json
```

### Custom output directory
```bash
python refresh-nodes.py -o ./my-nodes/
```

---

## Agent Capabilities

With this bridge, Antigravity agents can:

### 1. Generate Valid Workflows
Using only nodes that exist in your local installation—no hallucinations.

### 2. Recommend Node Packs
When your workflow needs functionality you don't have:
- Informs you about the missing node pack
- Asks for permission before suggesting installation
- Provides ComfyUI Manager or git clone instructions
- Reminds you to restart and re-run `refresh-nodes.py`

### 3. Write Custom Nodes
When no existing node fits your needs:
- Proposes the node design and gets approval
- Creates the Python node in `custom_nodes/`
- Includes proper `INPUT_TYPES`, `RETURN_TYPES`, and registration
- Verifies the node appears after refresh

---

## Workflow JSON Format

ComfyUI workflows use numbered node objects with connection links:

```json
{
  "1": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {
      "ckpt_name": "v1-5-pruned.safetensors"
    }
  },
  "2": {
    "class_type": "KSampler",
    "inputs": {
      "model": ["1", 0],
      "positive": ["3", 0],
      "negative": ["4", 0],
      "latent_image": ["5", 0],
      "seed": 42,
      "steps": 20,
      "cfg": 7.5,
      "sampler_name": "euler",
      "scheduler": "normal"
    }
  }
}
```

Links use the format `["source_node_id", output_index]`.

---

## Configuration

Edit `category-map.json` to customize domain splitting:

```json
{
  "output_files": {
    "core": {
      "filename": "core.txt",
      "categories": ["loaders", "sampling", "conditioning", "latent", "image", "mask"]
    },
    "video": {
      "filename": "video.txt", 
      "categories": ["video"],
      "node_patterns": ["*Wan*", "*LTXV*", "*VHS*"]
    }
  },
  "default_port_order": [8188, 8000, 8888],
  "connection_timeout": 2
}
```

---

## Requirements

- **Python 3.6+** (no external dependencies—stdlib only)
- **ComfyUI** running locally
- **[Antigravity IDE](https://antigravity.google)** for the full agent experience

---

## Related Projects

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) — The node-based Stable Diffusion interface
- [Antigravity IDE](https://antigravity.google) — Google's agent-first development environment

---

## License

MIT — See [LICENSE](./LICENSE)
