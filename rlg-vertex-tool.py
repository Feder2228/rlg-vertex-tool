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

    # check that file exists
    if not os.path.isfile( filepath ):
        print( filepath + ' not found' )

    # check if extension is correct
    extension = filepath.split( '.' )[ -1 ]

    if extension not in [ 'rlg', 'glg', 'dae' ]:
        print( 'unsupported file extension ' + extension )
        exit()



    # check response and execute if it's a valid command
    # txt command
    if( action in [ 'txt', 't' ] ):
        if extension == 'rlg':
            print_misc_data_to_file( filepath )
        elif extension == 'glg':
            print_misc_data_to_file( filepath, is_glg=True )
        else:
            print( 'this command supports rlg/glg file formats only. Given: ' + extension )

    # dec command
    elif( action in [ 'dec', 'd' ] ):
        if extension == 'rlg':
            export_rlg_as_dae( filepath )
        elif extension == 'glg':
            export_rlg_as_dae( filepath, is_glg=True )
        else:
            print( 'this command supports rlg/glg file formats only. Given: ' + extension )

    # enc command
    elif( action in [ 'enc', 'e', 'enc2', 'e2' ] ):

        rlgpath = ''
        daepath = ''

        # if user gave dae file, find the rlg equivalent (or vice versa)
        if extension == 'dae':
            daepath = filepath
            rlgpath = util.check_rlgpath( filepath )
            if rlgpath == None:
                print( rlgpath + ' not found' )
                exit()
            extension = rlgpath.split( '.' )[ -1 ]
        elif extension in [ 'rlg', 'glg' ]:
            rlgpath = filepath
            daepath = util.check_daepath( filepath )
            if daepath == None:
                print( daepath + ' not found' )
                exit()
        else:
            print( 'this command supports rlg/glg/dae file formats only. Given: ' + extension )
            exit()

        is_glg = True if extension == 'glg' else False
        auto_export = True if action in [ 'enc2', 'e2' ] else False

        generate_rlg_from_rlg_and_dae( rlgpath, daepath, is_glg=is_glg, auto_export=auto_export )

    else:
        print('invalid command. Use "python rlg-vertex-tool help" to see a list of commands')
        


def export_rlg_as_dae( rlgpath, is_glg=False ):

    daepath = rlgpath + '.dae'  # path of new file to create

    dae.create_dae( rlg.read_rlg( rlgpath, is_glg=is_glg ), daepath )
    print( 'created dae file at {0}'.format( daepath ) )


def generate_rlg_from_rlg_and_dae( rlgpath, daepath, is_glg=False, auto_export=False ):

    rlg.patch_rlg( rlgpath, rlgpath, dae.read_dae( daepath ), is_glg=is_glg )
    print( 'created rlg file at {0}'.format( rlgpath ) )
    
    if auto_export:
        dae.create_dae( rlg.read_rlg( rlgpath, is_glg=is_glg ), daepath )
        print( 'created dae file at {0}'.format( daepath ) )



def print_misc_data_to_file( rlgpath, is_glg=False ):

    model = rlg.read_rlg( rlgpath, is_glg=is_glg )

    txtpath = rlgpath + "_miscdata.txt"
    txtfile = open( txtpath, "w" )
    txtfile.write( str( model ) )
    txtfile.close()

    print( "_miscdata.txt file successfully created at " + txtpath )


if __name__ == "__main__":
    __main__()

