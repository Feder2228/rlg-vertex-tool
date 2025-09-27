from modules import util

# This module contains a function that reads hashid.py, which is a file found
# in MSC's ROM and associates hashes to names

STRING_SECTION_START = 0x1C8F4


# binpath: filepath (str); hash: hash (integer)
# return string containing the name associated to the hash
def get_hash_name( binpath, hash ):

    binfile = open( binpath, 'rb' )


    # look for the hash, start from the beginning of the file
    binfile.seek( 0, 0 )

    string_offset = -1

    # loop until the hash section ends
    while binfile.tell() < STRING_SECTION_START:

        binfile.read(4)  # skip 4
        scanned_hash = binfile.read(4)

        if scanned_hash == hash.to_bytes( 4, 'big' ):
            string_offset = int.from_bytes( binfile.read(4), 'big' )
            break
    

    # if you couldn't find the hash, return None
    if string_offset == -1:
        return None
    

    # go to where the string is
    binfile.seek( STRING_SECTION_START + string_offset , 0)
        
    hash_string = ''    

    # read the bytes
    while True:

        next_byte = binfile.read(1)

        if next_byte == b'\x00':
            return hash_string
        
        hash_string += next_byte.decode( 'ascii' ) 

