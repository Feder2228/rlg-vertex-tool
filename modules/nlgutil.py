from modules import util

# N.L.G. Utilities 
# This file is for functions that are related to decoding/encoding NLG file
# formats and are useful to more than one module (i.e. both rlg.py and shier.py)

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
            


