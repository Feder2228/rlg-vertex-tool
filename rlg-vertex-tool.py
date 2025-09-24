import os
import modules.dae as dae
import modules.rlg as rlg
import modules.util as util


# CONSTANTS
# DIRECTORY PATHS
DIR_PATH_OUTPUT = "output/"
DIR_PATH_INPUT_NLG_FORMATS = "rlg/"
DIR_PATH_INPUT_COMMON_FORMATS = "obj/"

# PROMPT STRINGS
PROMPT_STR_BASE_COMMANDS = '''-- Select a command --
    e - extract data from .rlg (save as .dae)
    g - generate new .rlg (use original .rlg plus a modified .dae)
    x - exit
    help - more info      
'''
PROMPT_STR_HELP = '''
    REGULAR COMMANDS:

    e
    Takes all the .rlg files it finds in the "rlg" folder, reads their data, then for each of them it creates a .dae file containing the vertices and faces (separated by group).
    For 3D model mods, import this .dae file in a program like blender, move the vertices around (but do NOT add/remove any!), then export it and save it to the "obj" folder, than use the g command
    
    g
    Takes all the .rlg files it finds in the "rlg" folder and for each of them it searches the "obj" folder for an .dae file that has the same name.
    For each file it finds the .dae of, it reads the vertices of the .dae and overwrites the .rlg's vertices with those.
    (Saves the modified .rlg as a copy in the "output" folder. The original .rlg won't be modified)
              
    
    DEV COMMANDS:

    eobjs 
    [disabled in current version, will be re-added in the future] Same as "e" command, but each group (mesh) is saved in a different .obj file (for dev purposes only. Those objs can't be used to recreate an .rlg file)

    d
    Create a .txt file containing various data about each group (mesh) of the .rlg file. The .txt will be saved in the "output" folder.
'''




def __main__():
    while True:
        r = input("\n\n" +PROMPT_STR_BASE_COMMANDS+ "\n\n")

        # Check if response is exit
        if(r == "x"):
            exit()

        rlg_filenames = util.get_all_filenames_of_specified_extension( DIR_PATH_INPUT_NLG_FORMATS, ".rlg" )
        dae_filenames = util.get_all_filenames_of_specified_extension( DIR_PATH_INPUT_COMMON_FORMATS, ".dae" )

        # check response and execute if it's a valid command
        if(r == "d"):
            for rlgname in rlg_filenames:
                rlgpath = DIR_PATH_INPUT_NLG_FORMATS + rlgname
                print_misc_data_to_file( rlgname, rlg.read_rlg( rlgpath ) )

        elif(r == "e"):
            for rlgname in rlg_filenames:
                rlgpath = DIR_PATH_INPUT_NLG_FORMATS + rlgname
                daepath = ( DIR_PATH_OUTPUT + rlgname ).replace( ".rlg", ".dae" )
                dae.create_dae( rlg.read_rlg( rlgpath ), daepath )

        elif(r == "g"):
            for daename in dae_filenames:
                daepath = DIR_PATH_INPUT_COMMON_FORMATS + daename
                dae.read_dae( daepath )
        
        elif(r == "help"):
            print( PROMPT_STR_HELP + "\n")

        else:
            print("invalid input")
            
        input("Press Enter to continue...")




# function that prints data to file
def print_misc_data_to_file( filename, model3d ):

    txtfile = open( DIR_PATH_OUTPUT + filename + "_miscdata.txt", "w" )

    txtfile.write( "4x4 MATRIX:\n" )
    for row in model3d.matrix_data:
        txtfile.write( str( row ) + "\n" )
    txtfile.write( "\n" )

    txtfile.write( "MODEL DATA:\n" )
    txtfile.write( str( model3d.model_data ) + "\n\n" )

    txtfile.write( "ALL MESH DATA:\n" )
    for d in model3d.meshes:
        txtfile.write( str( d.mesh_data ) + "\n" )
    txtfile.write( "\n\n\n\n" )

    for i, d in enumerate( model3d.meshes ):

        txtfile.write( "data[" +str(i)+ "]\n" )
        txtfile.write( "\nMESH DATA:\n" ) # TODO: iterate on the whole dict, and print ints as hex
        txtfile.write( str( d.mesh_data ) + "\n" )

        txtfile.write( "\nINDEX DATA:\n" )
        max_index = 0
        for e in d.index_data:
            txtfile.write( str( hex( e ) ) + " " )
            if( e > max_index ):
                max_index = e
        txtfile.write( "\nbiggest index of mesh: " + str(hex(max_index)) )

        txtfile.write( "\n\nVERTEX ATTRIBUTE:\n" )
        for e in d.vertex_attributes:
            txtfile.write( str( e ) + "\n" )

        txtfile.write( "\nVERTICES:\n" )
        vertex_id = 0x0
        for e in d.vertices:
            txtfile.write( "VERTEX " + hex( vertex_id ) + " " )
            vertex_id += 1
            txtfile.write( str( e.position ) + "\n" )
            txtfile.write( str( e.normal ) + "\n" )
            txtfile.write( str( e.uv0 ) + "\n" )
            txtfile.write( str( e.unknown0xED ) + "\n" )
            txtfile.write( str( e.unknown0x52 ) + "\n" )
            txtfile.write( str( e.unknown0xC0 ) + "\n" )
            txtfile.write( str( e.unknown0xD6 ) + "\n" )
            txtfile.write( str( e.unknown0xD7 ) + "\n" )
            txtfile.write( str( e.bone_ids ) + "\n" )
            txtfile.write( str( e.bone_weights ) + "\n" )
            txtfile.write( "\n" )

        txtfile.write( "\n\nFACES:\n" )
        for e in d.faces:
            txtfile.write( str( e ) + "\n" )
        txtfile.write("\n\n\n\n\n\n\n\n")

    txtfile.close()
    print( filename + "_miscdata.txt file successfully created in output folder" )




if __name__ == "__main__":
    __main__()

