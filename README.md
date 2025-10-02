# RLG Vertex Tool
RLG Vertex Tool allows you to **read data and extract vertices from rlg files**. It also allows you to edit the files and make some VERY BASIC mods.  
You can extract part of the data of an .rlg file into a .dae, but for now it's just the vertices, faces and uv mapping.
You can edit the .dae you extracted to make a **3d model edit**, but **only vertex positions**, **uv mapping** and (supposedly) **normals** will be read by the tool. Anything else is ignored for now.

## How to make your 3d model mod with this tool:
1. run the command "python rlg-vertex-tool (rlgfile) dec", you'll find a new .dae file in the directory of the rlg file.
2. import that file into blender, there you can move vertices and uv positions, but you cannot add vertices/faces (for now)
3. export the .dae file and overwrite the old one (it must have the same name and it must be in the same directory as the rlg file)
4. run the command "python rlg-vertex-tool (rlgfile) enc" and the rlg will get patched with the data found in the .dae file
5. enjoy!
