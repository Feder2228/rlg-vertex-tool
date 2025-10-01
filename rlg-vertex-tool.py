import os
import modules.dae as dae
import modules.rlg as rlg
import modules.util as util
import sys

# CONSTANTS
# DIRECTORY PATHS
DIR_PATH_OUTPUT = "output/"
DIR_PATH_INPUT_NLG_FORMATS = "input rlg/"
DIR_PATH_INPUT_COMMON_FORMATS = "input dae/"

# PROMPT STRINGS
PROMPT_STR_BASE_COMMANDS = '''-- Select a command --
    dec - decode (part of) a .rlg file (save as .dae)
    enc - encode .rlg (use original .rlg plus a modified .dae)
    exit - exit
    help - more info      
'''
PROMPT_STR_HELP = '''
    REGULAR COMMANDS:

    dec (d)
    Takes all the .rlg files it finds in the "input rlg" folder, reads their data, then for each of them it creates a .dae file containing the vertices and faces (separated by group).
    For 3D model mods, import this .dae file in a program like blender, move the vertices around (but do NOT add/remove any!), then export it and save it to the "input dae" folder, than use the enc command
    
    enc (e)
    Takes all the .rlg files it finds in the "input rlg" folder and for each of them it searches the "input dae" folder for an .dae file that has the same name.
    For each file it finds the .dae of, it reads the vertices of the .dae and overwrites the .rlg's vertices with those.
    (Saves the modified .rlg as a copy in the "output" folder. The original .rlg won't be modified)

    help (h)
    show this message
    
    
    DEV COMMANDS:

    enc2 (e2)
    Does the enc command thing, then for each .rlg file it creates, it exports it as .dae again.
    You'll find both an .rlg and its .dae equivalent in the output folder.
    Nice QoL feature for testing.

    txt (t)
    Create a .txt file containing various data about each group (mesh) of the .rlg file. The .txt will be saved in the "output" folder.
'''




def __main__():

    if sys.argv[ 1 ] in ( 'help', 'h' ):
        print( PROMPT_STR_HELP )
        exit()

    # CLI arguments
    filepath = sys.argv[ 1 ]
    action = sys.argv[ 2 ]  # enc, dec, enc2, txt

    # check if extension is correct
    extension = filepath.split( '.' )[ -1 ]

    if extension not in [ 'rlg', 'glg', 'dae' ]:
        print( 'unsupported file extension ' + extension )
        exit()

    # path variables
    rlgpath = ''
    daepath = ''

    if extension in [ 'rlg', 'glg' ]:
        rlgpath = filepath
        daepath = filepath + '.dae'
    elif extension == 'dae':
        rlgpath = filepath[ :-4 ]
        daepath = filepath


    # check response and execute if it's a valid command
    if( action in [ 'txt', 't' ] ):
        print_misc_data_to_file( rlgpath )

    elif( action in [ 'dec', 'd' ] ):
        export_rlg_as_dae( rlgpath, daepath )

    elif( action in [ 'enc', 'e', 'enc2', 'e2' ] ):
        if not os.path.isfile( daepath ):
            print( daepath + ' not found' )
            exit()
        auto_export = True if action in [ 'enc2', 'e2' ] else False
        generate_rlg_from_rlg_and_dae( rlgpath, daepath, auto_export )

    else:
        print('invalid command. Use "rlg-vertex-tool help" to see a list of commands')
        


def export_rlg_as_dae( rlgpath, daepath ):
    dae.create_dae( rlg.read_rlg( rlgpath ), daepath )
    print( 'created dae file at {0}'.format( daepath ) )


def generate_rlg_from_rlg_and_dae( rlgpath, daepath, auto_export=False ):
    src_rlg_path = rlgpath
    dst_rlg_path = DIR_PATH_OUTPUT + rlgpath.split( '/' )[ -1 ]  # tmp

    rlg.patch_rlg( src_rlg_path, dst_rlg_path, dae.read_dae( daepath ) )
    print( 'created rlg file at {0}'.format( dst_rlg_path ) )

    # automatic exportation: automatically export the newly generated rlg to dae.
    # This is QoL for testing.
    # In the output folder you won't only find your new .rlg, but also the .dae
    # equivalent of that .rlg, ready to be imported in blender and be checked for
    # inaccuracies.
    #
    #if auto_export:
    #    auto_export_dae_path = DIR_PATH_OUTPUT + daename
    #    dae.create_dae( rlg.read_rlg( dst_rlg_path ), auto_export_dae_path )
    #    print( 'created dae file at {0}'.format( auto_export_dae_path ) )



def print_misc_data_to_file( rlgpath ):

    model = rlg.read_rlg( rlgpath )

    txtfile = open( DIR_PATH_OUTPUT + "_miscdata.txt", "w" )
    txtfile.write( str( model ) )
    txtfile.close()

    print( "_miscdata.txt file successfully created in output folder" )


if __name__ == "__main__":
    __main__()

