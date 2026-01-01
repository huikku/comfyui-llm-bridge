# ComfyUI Workflow Generation Rules

When working with ComfyUI workflows in this project:

## Always Reference Node Definitions

1. **Before generating or modifying any ComfyUI workflow**, read the appropriate node definition file(s):
   - `nodes/core.txt` - Always read this for essential nodes
   - `nodes/video.txt` - For video generation workflows
   - `nodes/3d.txt` - For 3D model generation
   - `nodes/segmentation.txt` - For segmentation/masking
   - `nodes/api.txt` - For API-based generation
   - `nodes/full.txt` - When unsure or for comprehensive workflows

2. **Only use nodes that exist** in the loaded node files. Never invent node names.

3. **Match input/output types exactly**. Use the type codes to ensure connections are valid:
   - `M`=MODEL, `G`=IMAGE, `C`=CONDITIONING, `A`=LATENT
   - `V`=VAE, `P`=CLIP, `S`=STRING, `I`=INT, `F`=FLOAT

4. **For dropdown parameters**, use only values shown in `[opt1|opt2|...]` format.

## When Nodes Are Missing

- If a needed node doesn't exist, inform the user and suggest installing it
- After new nodes are installed, remind user to run `python refresh-nodes.py`
- Never generate workflows using nodes not in the definition files

## Refresh When Needed

Run `python refresh-nodes.py` to update node definitions after:
- Installing new custom nodes
- Updating ComfyUI
- Starting work in a new ComfyUI installation
