import os
import modules.dae as dae
import modules.rlg as rlg
import modules.util as util


# CONSTANTS
# DIRECTORY PATHS
DIR_PATH_OUTPUT = "output/"
DIR_PATH_INPUT_NLG_FORMATS = "input rlg/"
DIR_PATH_INPUT_COMMON_FORMATS = "input dae/"

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
    Takes all the .rlg files it finds in the "input rlg" folder, reads their data, then for each of them it creates a .dae file containing the vertices and faces (separated by group).
    For 3D model mods, import this .dae file in a program like blender, move the vertices around (but do NOT add/remove any!), then export it and save it to the "input dae" folder, than use the g command
    
    g
    Takes all the .rlg files it finds in the "input rlg" folder and for each of them it searches the "input dae" folder for an .dae file that has the same name.
    For each file it finds the .dae of, it reads the vertices of the .dae and overwrites the .rlg's vertices with those.
    (Saves the modified .rlg as a copy in the "output" folder. The original .rlg won't be modified)
              
    x
    exit

    help
    show this message
    
    
    DEV COMMANDS:

    ge
    Does the g command thing, then for each .rlg file it creates, it exports it as .dae again.
    You'll find both an .rlg and its .dae equivalent in the output folder.
    Nice QoL feature for testing.

    d
    Create a .txt file containing various data about each group (mesh) of the .rlg file. The .txt will be saved in the "output" folder.
'''




def __main__():
    while True:
        r = input("\n\n" +PROMPT_STR_BASE_COMMANDS+ "\n\n")

        # Check if response is exit
        if( r == "x" ):
            exit()

        rlg_filenames = util.get_all_filenames_of_specified_extension( DIR_PATH_INPUT_NLG_FORMATS, ".rlg" )
        dae_filenames = util.get_all_filenames_of_specified_extension( DIR_PATH_INPUT_COMMON_FORMATS, ".dae" )

        # check response and execute if it's a valid command
        if( r == "d" ):
            print_misc_data_to_file( rlg_filenames )

        elif( r == "e" ):
            export_rlg_as_dae( rlg_filenames )

        elif( r == "g" ):
            generate_rlg_from_rlg_and_dae( rlg_filenames, dae_filenames )

        elif( r == "ge" ):
            generate_rlg_from_rlg_and_dae( rlg_filenames, dae_filenames, auto_export=True )
        
        elif( r == "help" ):
            print( PROMPT_STR_HELP + "\n")

        else:
            print("invalid input")
            
        input("Press Enter to continue...")


def export_rlg_as_dae( rlg_filenames ):
    for rlgname in rlg_filenames:
        rlgpath = DIR_PATH_INPUT_NLG_FORMATS + rlgname
        daename = rlgname + ".dae"
        daepath = DIR_PATH_OUTPUT + daename
        dae.create_dae( rlg.read_rlg( rlgpath ), daepath )
        print( 'created dae file at {0}'.format( daepath ) )


def generate_rlg_from_rlg_and_dae( rlg_filenames, dae_filenames, auto_export=False ):
    for rlgname in rlg_filenames:
        daename = rlgname + ".dae"

        if daename not in dae_filenames:
            print( rlgname + ".dae not found" )
            continue
        print( "found " + daename )

        src_rlg_path = DIR_PATH_INPUT_NLG_FORMATS + rlgname
        dst_rlg_path = DIR_PATH_OUTPUT + rlgname
        daepath = DIR_PATH_INPUT_COMMON_FORMATS + daename

        rlg.patch_rlg( src_rlg_path, dst_rlg_path, dae.read_dae( daepath ) )
        print( 'created rlg file at {0}'.format( dst_rlg_path ) )

        # automatic exportation: automatically export the newly generated rlg to dae.
        # This is QoL for testing.
        # In the output folder you won't only find your new .rlg, but also the .dae
        # equivalent of that .rlg, ready to be imported in blender and be checked for
        # inaccuracies.
        #
        if auto_export:
            auto_export_dae_path = DIR_PATH_OUTPUT + daename
            dae.create_dae( rlg.read_rlg( dst_rlg_path ), auto_export_dae_path )
            print( 'created dae file at {0}'.format( auto_export_dae_path ) )



def print_misc_data_to_file( rlg_filenames ):

    for rlgname in rlg_filenames:

        rlgpath = DIR_PATH_INPUT_NLG_FORMATS + rlgname
        model = rlg.read_rlg( rlgpath )

        txtfile = open( DIR_PATH_OUTPUT + rlgname + "_miscdata.txt", "w" )
        txtfile.write( str( model ) )
        txtfile.close()

        print( rlgname + "_miscdata.txt file successfully created in output folder" )




if __name__ == "__main__":
    __main__()

