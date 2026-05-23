# N.L.G. Utilities 
# This file is for functions that are related to decoding/encoding NLG file
# formats and are useful to more than one module (i.e. both rlg.py and shier.py)

STRING_SECTION_START = 0x1C8F4  # this is for get_hash_name


class Section:
    def __init__(self, header_location : int, size : int, flags : int, type : bytes):
        self.header_location = header_location
        self.size = size
        self.flags = flags
        self.type = type
        self.children = list()
    def body_location(self):
        return self.header_location + 8  # return location of body
    def end(self):
        return self.header_location + 8 + self.size  # return location of end 
    def get_children_of_type(self, type : bytes):
        """Get the list of the child section of a certain type. 

        Args:
            type: type of section to get the 
        """
        children_of_that_type = []
        for child in self.children:
            if child.type==type:
                children_of_that_type.append(child)
        return children_of_that_type




def get_section_tree(file, align4=True):
    """Reads a NLG file and returns a tree of its section

    Known supported file formats: .rlg .shier .glg

    Args:
        file: the file to read the sections from
    Return:
        list of Section objects
    """
    # check size 
    file.seek(0, 2)
    filesize = file.tell()
    file.seek(0, 0)

    level_one_sections = []
    section_stack = []

    while file.tell() < filesize:
        # create Section object
        new_section = Section(flags=int.from_bytes(file.read(2), 'big'),
                                type=file.read(2),
                                size=int.from_bytes(file.read(4), 'big'),
                                header_location=file.tell() - 8)
        if len(section_stack) == 0:
            level_one_sections.append(new_section)
        # pop the stack if we got out of a container section
        while len(section_stack) > 0 and file.tell() >= section_stack[-1].end():
            section_stack.pop()
        # append the new section to its parent
        if len(section_stack) > 0:
            parent_section = section_stack[-1]
            parent_section.children.append(new_section)
        # push the stack if this is a new container section
        if new_section.flags & 0x8000:
            section_stack.append(new_section)
        # If it's NOT a container, move to the end of the section
        else:
            file.seek(new_section.end(), 0)
        # align by 4
        if align4:
            while not file.tell() % 4 == 0:
                file.seek(1, 1)  # move forward by 1 until you're aligned
    return level_one_sections
            



def get_hash_name(binfile, hash : int) -> str:
    """Read hashid.bin file and tell what the given hash is

    Args:
        binfile: the hashid.bin file
        hash: hash that you want to know the name of
    Return:
        string containing the name associated with the hash
    """
    # look for the hash, start from the beginning of the file
    binfile.seek(0, 0)
    string_offset = -1

    # loop until the hash section ends
    while binfile.tell() < STRING_SECTION_START:
        binfile.read(4)  # skip 4
        scanned_hash = binfile.read(4)
        if scanned_hash == hash.to_bytes(4, 'big'):
            string_offset = int.from_bytes(binfile.read(4), 'big')
            break

    # if you couldn't find the hash, return None
    if string_offset == -1:
        return None
    
    # go to where the string is
    binfile.seek(STRING_SECTION_START + string_offset, 0)
    hash_string = ''    

    # read the bytes
    while True:
        next_byte = binfile.read(1)
        if next_byte == b'\x00':
            return hash_string
        hash_string += next_byte.decode('ascii') 



    
def write_section_header(rlgfile, section : Section): 
    """Write the header of an NLG file section
    """
    rlgfile.write(section.flags.to_bytes(2, 'big'))
    rlgfile.write(section.type)  # 2 bytes
    rlgfile.write(section.size.to_bytes(4, 'big'))




def copy_section(src, dst, section):
    """Copy a section of a NLG binary file to another file

    Args:
        src: source file
        dst: destination file
        section: section of source file to be copied
    """
    src.seek(section.header_location, 0)
    header = src.read(8)
    dst.write(header)
    content = src.read(section.size)
    dst.write(content)
    # align by 4
    while not dst.tell() % 4 == 0:
        dst.seek(1, 1)  # move forward by 1 until you're aligned




def update_section_size_and_go_to_end(file, section : Section):
    """Update the Section object's size and also the file's section's size.

    The file pointer MUST point to the new end of the section.

    Args:
        file: file
        section: section
    """
    section.size = file.tell() - section.body_location()
    file.seek(section.header_location + 4, 0)
    file.write(section.size.to_bytes(4, 'big'))
    # go to end of the section
    file.seek(section.end(), 0)
    while not file.tell() % 4 == 0:
        file.seek(1, 1)




def section_tree_str(root : Section, level=0) -> str:
    INDENT = '.   '
    s = ''
    s += hex(int.from_bytes(root.type))
    s += '\n'
    for section in root.children:
        s += (INDENT * level)
        s += section_tree_str(root=section, level=level+1)
    return s