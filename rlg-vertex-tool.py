import os
import modules.daelib as daelib
import modules.rlglib as rlglib
import modules.objlib as objlib
import modules.util as util


# CONSTANTS
# DIRECTORT PATHS
DIR_PATH_OUTPUT = "output/"
DIR_PATH_INPUT_NLG_FORMATS = "rlg/"
DIR_PATH_INPUT_COMMON_FORMATS = "obj/"

# PROMPT STRINGS
PROMPT_STR_BASE_COMMANDS = '''-- Select a command --
    e - extract data from .rlg (save as .obj)
    g - generate new .rlg (use original .rlg plus a modified .obj)
    x - exit
    help - more info      
'''
PROMPT_STR_HELP = '''
    REGULAR COMMANDS:

    e
    Takes all the .rlg files it finds in the "rlg" folder, reads their data, then for each of them it creates a .obj file containing the vertices and faces (separated by group).
    For 3D model mods, import this .obj file in a program like blender, move the vertices around (but do NOT add/remove any!), then export it and save it to the obj folder, than use the g command
    
    g
    Takes all the .rlg files it finds in the "rlg" folder and for each of them it searches the "obj" folder for an .obj file that has the same name.
    For each file it finds the .obj of, it reads the vertices of the .obj and overwrites the .rlg's vertices with those.
    (Saves the modified .rlg as a copy in the "output" folder. The original .rlg won't be modified)
              
    
    DEV COMMANDS:

    es 
    Same as "e" command, but each group (mesh) is saved in a different .obj file (for dev purposes only. Those objs can't be used to recreate an .rlg file)

    dae
    Similar to "e", except it creates a .dae file instead of .obj (currently WIP)

    d
    Create a .txt file containing various data about each group (mesh) of the .rlg file. The .txt will be saved in the "output" folder.
'''




# function that prints data to file
def print_misc_data_to_file(rlg):

    filename = os.path.basename(rlg.name)
    data = rlglib.read_rlg(rlg)

    txt = open( DIR_PATH_OUTPUT + filename + "_miscdata.txt", "w" )

    txt.write( "4x4 MATRIX:\n" )
    for row in data['matrix']:
        txt.write( str( row ) + "\n" )
    txt.write( "\n" )

    txt.write( "MODEL DATA:\n" )
    txt.write( str( data['model_data'] ) + "\n\n" )

    txt.write( "ALL MESH DATA:\n" )
    for d in data['meshes']:
        txt.write( str(d['mesh_data'] ) + "\n" )
    txt.write( "\n\n\n\n" )

    for i, d in enumerate( data['meshes'] ):

        txt.write( "data[" +str(i)+ "]\n" )
        txt.write( "\nMESH DATA:\n" ) # TODO: iterate on the whole dict, and print ints as hex
        txt.write( str( d['mesh_data'] ) + "\n" )

        txt.write( "\nINDEX DATA:\n" )
        max_index = 0
        for e in d['index_data']:
            txt.write( str(hex(e)) + " " )
            if( e > max_index ):
                max_index = e
        txt.write( "\nbiggest index of mesh: " + str(hex(max_index)) )

        txt.write( "\n\nVERTEX ATTRIBUTE:\n" )
        for e in d['vertex_attributes']:
            txt.write( str(e) + "\n" )

        txt.write( "\nVERTICES:\n" )
        vertex_id = 0x0
        for e in d['vertices']:
            txt.write( "VERTEX " + hex( vertex_id ) + " " )
            vertex_id += 1
            txt.write( str( e['position'] ) + "\n" )
            txt.write( str( e['normal'] ) + "\n" )
            txt.write( str( e['uv0'] ) + "\n" )
            txt.write( str( e['attribute_0xed'] ) + "\n" )
            txt.write( str( e['attribute_0x52'] ) + "\n" )
            txt.write( str( e['attribute_0xc0'] ) + "\n" )
            txt.write( str( e['attribute_0xd6'] ) + "\n" )
            txt.write( str( e['attribute_0xd7'] ) + "\n" )
            txt.write( str( e['bone_ids'] ) + "\n" )
            txt.write( str( e['bone_weights'] ) + "\n" )
            txt.write( "\n" )

        txt.write( "\n\nFACES:\n" )
        for e in d['faces']:
            txt.write( str(e) + "\n" )
        txt.write("\n\n\n\n\n\n\n\n")

    txt.close()
    print(filename+"_miscdata.txt file successfully created in output folder")



# START OF CODE
while True:
    r = input("\n\n" +PROMPT_STR_BASE_COMMANDS+ "\n\n")

    # Check if response is exit
    if(r == "x"):
        exit()

    rlg_filenames = util.get_all_filenames_of_specified_extension( DIR_PATH_INPUT_NLG_FORMATS, ".rlg" )
    dae_filenames = util.get_all_filenames_of_specified_extension( DIR_PATH_INPUT_COMMON_FORMATS, ".dae" )

    # check response and execute if it's a valid command
    if(r == "eobj"):
        for i in rlg_filenames:
            rlg = open( DIR_PATH_INPUT_NLG_FORMATS + i, "rb" )
            objlib.create_obj( rlg )
            rlg.close()

    elif(r == "gobj"):
        for i in rlg_filenames:
            rlg = open( DIR_PATH_INPUT_NLG_FORMATS + i, "rb" )
            rlglib.generate_new_rlg( rlg )
            rlg.close()

    elif(r == "eobjs"):
        for i in rlg_filenames:
            rlg = open( DIR_PATH_INPUT_NLG_FORMATS + i, "rb" )
            objlib.create_obj( rlg, split_files_by_group=True )
            rlg.close()
        
    elif(r == "d"):
        for i in rlg_filenames:
            rlg = open( DIR_PATH_INPUT_NLG_FORMATS + i, "rb" )
            print_misc_data_to_file( rlg )
            rlg.close()

    elif(r == "e"):
        for i in rlg_filenames:
            rlg = open( DIR_PATH_INPUT_NLG_FORMATS + i, "rb" )
            daelib.create_dae( rlglib.read_rlg(rlg), i.split(".")[0] )

    elif(r == "g"):
        for i in dae_filenames:
            dae = open( DIR_PATH_INPUT_COMMON_FORMATS + i, "r" )
            daelib.read_dae( dae )
    
    elif(r == "help"):
        print( PROMPT_STR_HELP + "\n")

    else:
        print("invalid input")
        
    input("Press Enter to continue...")