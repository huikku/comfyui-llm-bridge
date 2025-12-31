---
description: Refresh ComfyUI node definitions and generate workflows
---
# ComfyUI Workflow Generation

Use this workflow to generate valid ComfyUI workflows with live node discovery.

## Steps

// turbo
1. Run the node refresh script to get current node definitions:
   ```bash
   python comfyui-llm-bridge/refresh-nodes.py
   ```

2. Read the appropriate node definition file based on the task:
   - For basic image generation: read `comfyui-llm-bridge/nodes/core.txt`
   - For video workflows: also read `comfyui-llm-bridge/nodes/video.txt`
   - For 3D model generation: also read `comfyui-llm-bridge/nodes/3d.txt`
   - For segmentation/masking: also read `comfyui-llm-bridge/nodes/segmentation.txt`
   - For API-based generation: also read `comfyui-llm-bridge/nodes/api.txt`
   - For training workflows: also read `comfyui-llm-bridge/nodes/training.txt`
   - If unsure, read `comfyui-llm-bridge/nodes/full.txt`

3. Generate a ComfyUI workflow JSON using ONLY nodes from the loaded definitions.

4. Validate that all node connections match compatible input/output types.

5. Save the workflow to `workflows/<descriptive-name>.json`

## Custom Node Recommendations

If a user's workflow would benefit from nodes that aren't currently installed:

1. **Inform the user** about the missing node pack and what it provides
2. **Ask for permission** before suggesting installation
3. **Provide installation instructions** (e.g., ComfyUI Manager, git clone, etc.)
4. **After installation**, remind user to restart ComfyUI and run:
   ```bash
   python refresh-nodes.py
   ```
5. **Wait for refresh** before generating workflows using the new nodes

Common useful node packs:
- ComfyUI-VideoHelperSuite (VHS) - Video loading/saving
- ComfyUI-Impact-Pack - Face detection, segmentation
- ComfyUI-AnimateDiff - Animation generation
- ComfyUI-WD14-Tagger - Image tagging

## Creating New Custom Nodes

If no existing node provides the required functionality, you can write a new custom node:

1. **Propose the node** - Explain what it will do and why it's needed
2. **Get user approval** before writing any code
3. **Create the node** in `custom_nodes/<node_pack_name>/`:
   - `__init__.py` with NODE_CLASS_MAPPINGS
   - Node class with INPUT_TYPES, RETURN_TYPES, FUNCTION, CATEGORY
4. **Restart ComfyUI** to load the new node
5. **Run refresh-nodes.py** to update the node definitions
6. **Verify the node appears** in the refreshed files before using it in workflows

Example node structure:
```python
class MyCustomNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE",)}}
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process"
    CATEGORY = "custom"
    
    def process(self, image):
        # Your logic here
        return (image,)

NODE_CLASS_MAPPINGS = {"MyCustomNode": MyCustomNode}
```

## Node Format Reference

The compressed node format is:
```
@NodeName +required_input:TYPE ?optional_input:TYPE -output:TYPE
```

Type codes:
- M=MODEL, G=IMAGE, C=CONDITIONING, A=LATENT, V=VAE, P=CLIP
- S=STRING, I=INT, F=FLOAT, B=BOOLEAN, K=MASK, T=CONTROL_NET
- L=LIST/COMBO, * for other types

## Workflow JSON Format

ComfyUI workflows use this structure:
```json
{
  "1": {
    "class_type": "NodeName",
    "inputs": {
      "input_name": value_or_link
    }
  },
  "2": {
    "class_type": "AnotherNode",
    "inputs": {
      "connected_input": ["1", 0]  // Links to node 1, output index 0
    }
  }
}
```
