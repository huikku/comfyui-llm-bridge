---
description: Refresh ComfyUI node definitions and generate workflows
---
# ComfyUI Workflow Generation

Use this workflow to generate valid ComfyUI workflows with live node discovery.

## Steps

// turbo
1. Run the node refresh script to get current node definitions:
   ```bash
   python llm-integration/refresh-nodes.py
   ```

2. Read the appropriate node definition file based on the task:
   - For basic image generation: read `llm-integration/nodes/core.txt`
   - For video workflows: also read `llm-integration/nodes/video.txt`
   - For 3D model generation: also read `llm-integration/nodes/3d.txt`
   - For segmentation/masking: also read `llm-integration/nodes/segmentation.txt`
   - For API-based generation: also read `llm-integration/nodes/api.txt`
   - For training workflows: also read `llm-integration/nodes/training.txt`
   - If unsure, read `llm-integration/nodes/full.txt`

3. Generate a ComfyUI workflow JSON using ONLY nodes from the loaded definitions.

4. Validate that all node connections match compatible input/output types.

5. Save the workflow to `workflows/<descriptive-name>.json`

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
