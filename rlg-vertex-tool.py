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
                daename = rlgname + ".dae"
                daepath = DIR_PATH_OUTPUT + daename
                dae.create_dae( rlg.read_rlg( rlgpath ), daepath )

        elif(r == "g"):
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
        
        elif(r == "help"):
            print( PROMPT_STR_HELP + "\n")

        else:
            print("invalid input")
            
        input("Press Enter to continue...")




# function that prints data to file
def print_misc_data_to_file( filename, model3d ):

    txtfile = open( DIR_PATH_OUTPUT + filename + "_miscdata.txt", "w" )

    txtfile.write( str( model3d ) )

    txtfile.close()
    print( filename + "_miscdata.txt file successfully created in output folder" )




if __name__ == "__main__":
    __main__()

