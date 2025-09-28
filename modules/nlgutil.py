# N.L.G. Utilities 
# This file is for functions that are related to decoding/encoding NLG file
# formats and are useful to more than one module (i.e. both rlg.py and shier.py)

from modules import util

STRING_SECTION_START = 0x1C8F4  # this is for get_hash_name


class Section:
    def __init__( self, header_location, size, flags ):
        self.header_location = header_location
        self.size = size
        self.flags = flags
    def body_location( self ):
        return self.header_location + 8  # return location of body
    def end( self ):
        return self.header_location + 8 + self.size  # return location of end 



# takes a file object as parameter and returns a dict that maps each found
# section identifier to a list of Section objects.
#
def get_map_of_sections( file ):

    # check size 
    file.seek( 0, 2 )
    filesize = file.tell()
    file.seek( 0, 0 )

    # dict of sections
    section_map = {}

    while file.tell() < filesize:


        if util.DEBUG:
            print( 'found a section at ' + str( file.tell() ) )


        # get header data
        #
        # The first line checks if the section header's first bit is high.
        # If it's high, this should be a container of sections.
        #
        flags = int.from_bytes( file.read(2), 'big' )
        is_section_container = flags & 0x8000

        section_type = file.read(2)

        section_size = int.from_bytes( file.read(4), 'big' )

        header_location = file.tell() - 8


        if util.DEBUG:
            print( 'type: {0}  location: {1}  container: {2}  size: {3}'.format( 
                section_type, header_location, is_section_container, section_size ) )
            

        
        # create Section object
        new_section = Section( header_location, section_size, flags )


        # add new found section to map
        if section_type not in section_map:
            section_map.update( { section_type : [ new_section ] } )
        else:
            section_map[ section_type ].append( new_section )


        # Move on to the next section's header.
        # If the last found section was a section container, don't do anything,
        # the file object thing is pointing to the first byte of header 
        # already.
        # Otherwise, move forward by <section_size> bytes
        #
        if not is_section_container:
            file.seek( section_size, 1 )

        # align by 4
        while not file.tell() % 4 == 0:
            file.seek( 1, 1 )  # move forward by 1 until you're aligned

        
    return section_map
            




# function that maps an hash to its name. Requires hashid.bin path to work.
# binpath: filepath (str); hash: hash (integer)
# return string containing the name associated to the hash
#
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