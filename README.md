# RLG Tool
RLG Tool is a program for **decoding and manipulating Mario Strikers Charged Football's .rlg files**. 

## How to make your own 3D model mod:
1. with the src directory as your present working directory, run **python -m rlgtool.cli dec src.rlg**
where src.rlg is the path of your rlg file. This will create a dae file in the same directory as the rlg file
2. import that file into blender, there you can edit the model. Just **don't add or rename any meshes**. You can remove all meshes except for one if you want. Also don't mind bones. They don't do anything for now.
3. after you're done with the blender part, export as .dae (legacy), then run the command **python -m rlgtool.cli patch src.rlg dst.rlg src.dae** and the rlg will get patched with the data found in the **src.dae** file
4. put the new .rlg file into the game, and, if everything goes right, enjoy!

## Credits:
Huge thanks to:
* DIP for helping me out and also letting me use [pyGLT](https://github.com/MCMANIRX/pyGLT)'s code in my project (rlt module)
* KillzXGaming for [researching the file formats](https://github.com/KillzXGaming/NLG_Research/wiki/Mario-Strikers-GLG-and-RLG) and for [switch-toolbox](https://github.com/KillzXGaming/Switch-Toolbox/blob/master/File_Format_Library/FileFormats/NLG/MarioStrikers/StrikersRLG.cs)

## See also:
* strikers-re: https://github.com/Rocci1212/strikers-re/blob/main/game%20files%20research/3d%20models

## Known bugs and issues:
### Face indices don't work correctly + game crash
Right now trying to decode mario.rlg and patching it with the dae file you obtain with that process (mario.rlg.dae) creates a file that makes the game crash.
This is because of the fact that this program encodes indices in a very unoptimized way and it makes the file bigger than it should be. Apparently there is a limit to how much bigger the file can get, so the game crashes when trying to load the file.
Because of this, the only possible mods for now are mods with less faces than the original file.  

### Blender crash
Some files crash blender when trying to load them. This happens with ball.rlg and a few other objects

### UV mapping
UV mapping is messy. RLG files don't allow a vertex to have an coordinates for each face. To fix this I am gonna have to split the vertices of the input dae file into multiple vertices, grouped by UV coords. Before I do this though, I should optimize the indices.  

### Bones
Bones don't work. This is mainly due to me not knowing how bone works in 3D graphics in general, but it is also because of the weird way they're stored in the game's filesystem. Part of the data is stored in the rlg files, part of it in the shier files.  

### (Material textures)
For now, this tool only extracts one texture per material, but most RLG file have like 6 (reflections, ice, mud...)

### (Vertex colors)
Vertex colors are not implemented yet. They're used only in some objects, so it's not really the priority.

### (patch command ignores materials)
patch command does not edit materials for now. Will implement this soon, at least for changing the first texture of each material


