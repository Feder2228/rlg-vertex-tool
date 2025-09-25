# RLG Vertex Tool
RLG Vertex Tool allows you to read data and extract vertices from rlg files. It also allows you to edit the files and make some VERY BASIC mods.  
You can extract part of the data of an .rlg file into a .dae, but for now it's just the vertices, faces and uv mapping.
You can edit the .dae you extracted to make a 3d model edit, but only vertex positions, uv mapping and (supposedly) normals will be read by the tool. Anything else is ignored for now.

## How to make your 3d model mod with this tool:
1. Put your .rlg file in the rlg folder
2. Run the script and use the e command to generate a .dae file
3. In the output folder you'll find the newly created .dae file, import it in a 3D model editor (such as blender). Here you can move the vertices around, but **DO NOT** add or delete any.
4. Once you're done with the edit, export the .dae file into the obj folder (make sure to name it the same way as the file that was outputed by the script)
5. Run the script and use the g command to generate a new .rlg (the original .rlg still needs to be in the rlg folder). The script will replace the original rlg's vertices with the ones that are found in the .dae file
6. If everything went right, you'll find your new rlg in the output folder. Enjoy!
