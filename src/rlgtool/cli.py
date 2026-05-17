from . import rlgtool as rlgtool
from . import nlgutil
import sys
import os


# PROMPT STRINGS
PROMPT_STR_HELP = '''Commands:

dec <source rlg file> 
decodes a .rlg file into a .dae file

patch <source rlg file> <dest rlg file> <source dae file>
patches source .rlg file with the data of the source .dae file. The new rlg file will be created at "dest rlg file"
'''

# commands
COMMAND_DEC = ['dec', 'd']
COMMAND_DECSHIER = ['decshier', 'ds']
COMMAND_PATCH = ['patch']
COMMAND_TRI = ['tri']
COMMAND_CUBE = ['cube']


def __main__():
    if sys.argv[1] in ('help', 'h'):
        print(PROMPT_STR_HELP)
        exit()

    if(sys.argv[1] in COMMAND_DEC):
        if get_file_extension(sys.argv[2]) != 'rlg':
            raise Exception('this command supports rlg file format only.')
        rlgtool.export_rlg_as_dae(sys.argv[2])

    elif(sys.argv[1] in COMMAND_DECSHIER):
        if get_file_extension(sys.argv[2]) != 'rlg':
            raise Exception('first argument must be a file of type rlg')
        if get_file_extension(sys.argv[3]) != 'shier':
            raise Exception('second argument must be a file of type shier')
        rlgtool.export_rlg_as_dae(rlgpath=sys.argv[2], shierpath=sys.argv[3])

    elif(sys.argv[1] in COMMAND_PATCH):
        if get_file_extension(sys.argv[2]) != 'rlg':
            raise Exception('first argument must be a file of type rlg')
        if get_file_extension(sys.argv[3]) != 'rlg':
            raise Exception('second argument must be a file of type rlg')
        if get_file_extension(sys.argv[4]) != 'dae':
            raise Exception('third argument must be a file of type dae')
        rlgtool.generate_rlg_from_rlg_and_dae(srcrlgpath=sys.argv[2], dstrlgpath=sys.argv[3], daepath=sys.argv[4])

    elif(sys.argv[1] in COMMAND_CUBE):
        rlgtool.cube(source_rlg_path=sys.argv[2], destination_rlg_path=sys.argv[3])

    else:
        print('unknown command')




def get_file_extension(filepath):
    return filepath.split( '.' )[ -1 ]


__main__()