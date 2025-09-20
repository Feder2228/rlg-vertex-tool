import os, struct, math, shutil, glob, re


# CONSTANTS
# SECTION IDENTIFIER CONSTANTS
SECTION_MATRIX_DATA = b'\x00\x01\xb0\x02'
SECTION_MODEL_DATA = b'\x00\x01\xb0\x03'
SECTION_MESH_DATA = b'\x00\x01\xb0\x04'
SECTION_VERTEX_ATTRIBUTES = b'\x00\x01\xb0\x05'
SECTION_VERTEX_DATA = b'\x00\x01\xb0\x06'
SECTION_INDEX_DATA = b'\x00\x01\xb0\x07'
SECTION_SKELETON_DATA = b'\x00\x01\xb0\x08'
SECTION_BONE_MESH_HASHES = b'\x00\x01\xb0\x0b'
SECTION_BONE_DATA = b'\x00\x01\xb0\x0a'
SECTION_UNKNOWN_DATA = b'\x00\x01\xb0\x0c'
SECTION_MATERIAL_DATA = b'\x00\x01\xb0\x16'

# VERTEX ATTRIBUTE CONSTANTS
VERTEX_ATTRIBUTE_TYPE_VERTEX = 0x67
VERTEX_ATTRIBUTE_TYPE_2 = 0xfe
VERTEX_ATTRIBUTE_TYPE_3 = 0xcc
VERTEX_ATTRIBUTE_TYPE_4 = 0xed
VERTEX_ATTRIBUTE_TYPE_5 = 0x52
VERTEX_ATTRIBUTE_TYPE_6 = 0xc0
VERTEX_ATTRIBUTE_TYPE_7 = 0xd6
VERTEX_ATTRIBUTE_TYPE_8 = 0xd7
VERTEX_ATTRIBUTE_TYPE_9 = 0xd4
VERTEX_ATTRIBUTE_TYPE_10 = 0xb0


# RLG UTILITY FUNCTIONS
def rlg_get_size(rlg):
    rlg.seek(0,2)
    return rlg.tell()

def rlg_get_data(rlg):
    size = rlg_get_size( rlg )
    rlg.seek(0,0)
    return rlg.read( size )

def rlg_get_section_info( rlg, section_identifier ):
    a = []
    data = rlg_get_data( rlg )
    location = data.find( section_identifier )

    # location of section
    a.append( location )        

    # flags      
    rlg.seek( location, 0 )
    flags = rlg.read(2)
    flags = int.from_bytes( flags, "big" )
    a.append( flags )           

    # section size
    rlg.seek( location + 4, 0 )
    section_size = rlg.read(4)
    section_size = int.from_bytes( section_size, "big" )
    a.append( section_size )          
    return a




# MISC UTILITY FUNCTIONS
# Function to convert a bytearray into a string where the each byte corresponds to two hexadecimal digits (in ascii)
def byte_hex_str(bytes):
    string = ""
    for i in bytes:
        string += byte_hex(i)
    return string

def byte_hex(byte):
    upper4 = (byte & 0xf0) >> 4 
    lower4 = byte & 0x0f
    chars = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    return (chars[upper4] + chars[lower4])

# Function that scans the rlg folder for files and returns a list containing all the file names
def get_all_rlg_filenames():

    filenames_r = glob.glob("./rlg/*.rlg")
    filenames = []

    print("found", str(len(filenames_r)), "rlg files:")
    for i in filenames_r:
        file = re.split("\\\\", i)[1]
        print(file)
        filenames.append(file)
    return filenames

def bytes_to_float(bytes):
    return struct.unpack( '!f', bytes )[0]




# CORE FUNCTIONS
# Function to read the vertices of a rlg file. Returns a list containing all the vertices
def get_vertices_from_rlg( rlg, vertex_attributes ):
    
    # get section info
    section_info = rlg_get_section_info( rlg, SECTION_VERTEX_DATA )
    location = section_info[0]

    # in order to determine on which intervals we can find vertices, we need to scan the vertex attributes
    # find the intervals
    intervals = []
    for i, instance in enumerate(vertex_attributes):
        if( instance['type'] == VERTEX_ATTRIBUTE_TYPE_VERTEX ):
            intervals.append({
                'start': instance['offset'],
                'end': vertex_attributes[i+1]['offset']
            })
    print( "DEBUG" + str(intervals) )

    # set up some variables for the loop
    start_of_data = location + 8
    a = []
    absolute_id = 0

    # repeat for each interval: get all the vertices in the interval
    for group, interval in enumerate(intervals):

        rlg.seek( start_of_data + interval['start'] )
        current_byte = rlg.tell() - start_of_data

        relative_id = 0

        while current_byte < interval['end']:

            a.append( {
                "absolute_id" : absolute_id,       # id
                "relavtive_id" : relative_id,      # id (relative to the start of the group)
                "offset" : current_byte,
                "type" : VERTEX_ATTRIBUTE_TYPE_VERTEX, 
                "group" : group,
                "values" : [ bytes_to_float( rlg.read(4) ),  
                             bytes_to_float( rlg.read(4) ), 
                             bytes_to_float( rlg.read(4) ) ]
            } )

            current_byte = rlg.tell() - start_of_data

            absolute_id += 1
            relative_id += 1

    return a


def get_vertices_from_rlg_split_by_group( rlg ):

    vertices = get_vertices_from_rlg( rlg, get_vertex_attributes_from_rlg(rlg) )
    return split_vertices_by_group( vertices )
    

def split_vertices_by_group( vertices ):

    vertices_by_group = []
    group = []

    for i, v in enumerate( vertices ):

        group.append( v )

        # if this is last vertex of a group, put the group into the "vertices_by_group" list
        if( i >= len(vertices)-1 or vertices[i+1]['group'] != v['group'] ):
            vertices_by_group.append( group )
            group = []

    return vertices_by_group




# returns an array of dicts. Each dict is a vertex attribute instance
def get_vertex_attributes_from_rlg(rlg):
    
    section_info = rlg_get_section_info( rlg, SECTION_VERTEX_ATTRIBUTES )
    location = section_info[0]
    section_size = section_info[2]
    start_of_data = location + 8

    # set some variables for the loop
    rlg.seek( start_of_data ,0)
    a = []
    end_of_section = start_of_data + section_size
    group = -1

    # read data
    while rlg.tell() < end_of_section: 

        offset = int.from_bytes( rlg.read(4), "big" )
        type = int.from_bytes( rlg.read(1), "big" )
        stride = int.from_bytes( rlg.read(1), "big" )
        unknown_0x6 = int.from_bytes( rlg.read(2), "big" )

        if( type == VERTEX_ATTRIBUTE_TYPE_VERTEX ):
            group += 1

        a.append( {
            "group" : group,
            "offset" : offset,
            "type" : type,         # types are ordered like this: 67 fe cc ed 52 c0 d6 d7 d4 b0
            "stride" : stride,
            "0x6" : unknown_0x6
        } )
    return a


def get_vertex_attributes_from_rlg_split_by_group(rlg):
    
    vertex_attributes = get_vertex_attributes_from_rlg( rlg )

    vertex_attributes_by_group = []
    group = []

    for i, v in enumerate( vertex_attributes ):

        group.append( v )

        # if this is last vertex of a group, put the group into the "vertex_attributes_by_group" list
        if( i >= len(vertex_attributes)-1 or vertex_attributes[i+1]['group'] != v['group'] ):
            vertex_attributes_by_group.append( group )
            group = []

    return vertex_attributes_by_group




def read_model_data(rlg):
    
    section_info = rlg_get_section_info( rlg, SECTION_MODEL_DATA )
    location = section_info[0]
    section_size = section_info[2]

    # go to where model data starts
    rlg.seek( location + 8, 0 )

    # loop on it and read stuff idk
    model_count = section_size//12
    for i in range(0, model_count):
        rlg.read(4)
        mesh_count = int.from_bytes( rlg.read(4), "big" )
        print("mesh count: " +str(mesh_count))
        rlg.read(4)




def get_mesh_data_from_rlg(rlg):

    # get the filename and strip the extention
    filename = os.path.basename(rlg.name)
    print("Reading mesh data of: " +filename)
    
    section_info = rlg_get_section_info( rlg, SECTION_MESH_DATA )
    location = section_info[0]
    section_size = section_info[2]

    # go to where data starts
    rlg.seek( location+8 , 0 )
    start_of_data = rlg.tell()

    # read data
    a = []
    while rlg.tell() < start_of_data+section_size:  # TODO: edit the condition to make it more readable
        index_start_offset = int.from_bytes( rlg.read(4), "big" )
        index_flags = int.from_bytes( rlg.read(4), "big" )
        vertex_count = int.from_bytes( rlg.read(2), "big" )
        unknown_0x0a = int.from_bytes( rlg.read(4), "big" )
        material_hash_id = int.from_bytes( rlg.read(4), "big" )
        mesh_hash_id = int.from_bytes( rlg.read(4), "big" )
        unknown_0x16 = int.from_bytes( rlg.read(4), "big" )
        unknown_0x1a = int.from_bytes( rlg.read(4), "big" )
        material_offset = int.from_bytes( rlg.read(4), "big" )
        unknown_0x22 = int.from_bytes( rlg.read(4), "big" )
        unknown_0x26 = int.from_bytes( rlg.read(4), "big" )
        unknown_0x2a = int.from_bytes( rlg.read(6), "big" )

        a.append( { 
                "index_start_offset" : index_start_offset,
                "index_count" : index_flags & 0xffffff,
                "index_format" : index_flags >> 24,
                "vertex_count" : hex(vertex_count),
                "0x0a" : unknown_0x0a,
                "material_hash_id" : material_hash_id,
                "0x16" : unknown_0x16,
                "0x1a" : unknown_0x1a,
                "mesh_hash_id" : mesh_hash_id,
                "material_offset" : material_offset,
                "0x22" : unknown_0x22,
                "0x26" : unknown_0x26,
                "0x2a" : unknown_0x2a,
            } )
  
    return a
    



# Read data from index section. Return a list of all indices
def get_index_data_from_rlg(rlg):
    
    section_info = rlg_get_section_info( rlg, SECTION_INDEX_DATA )
    section_size = section_info[2]

    # go to where data starts
    start_of_data = section_info[0] + 8
    rlg.seek( start_of_data, 0 )
    end_of_section = start_of_data + section_size

    # read all indices and return a list containing them
    indices = []
    while rlg.tell() < end_of_section:
        indices.append( int.from_bytes( rlg.read(2), 'big' ) )
    return indices




# Get a dict with various data from an rlg file
# Still WIP. Currently structured like this:
# List of dicts. Each dict contains data of a mesh. mesh_data, index_data, vertex_attributes, vertices, faces
# For more info look at the comments next to the last "append" in this function
def get_rlg_dict(rlg):

    data = []
    read_model_data(rlg)   # TODO ???
    
    # Read data
    mesh_data = get_mesh_data_from_rlg(rlg)
    index_data = get_index_data_from_rlg(rlg)
    vertex_attributes = get_vertex_attributes_from_rlg_split_by_group(rlg)
    vertices = get_vertices_from_rlg_split_by_group(rlg)


    # Loop through groups
    for i, m in enumerate(mesh_data):

        # Split index data by group
        index_data_end = m['index_start_offset'] + ( (m['index_count']) * 2 )
        index_data_of_this_mesh = []

        for j in range( m['index_start_offset']//2, index_data_end//2 ): 

            print( "DEBUG:" + str(i) + ", " + str(j) )
            index_data_of_this_mesh.append( index_data[j] )


        # Faces
        faces_of_this_mesh = []

        for j, index in enumerate( index_data_of_this_mesh ):

            if( j < 2 ):
                continue
            
            # check if three adjacent indices are all different. If so, that's a face
            tri = index_data_of_this_mesh[ (j - 2) : (j + 1) ]
            if( tri[0] != tri[1] and tri[1] != tri[2] and tri[0] != tri[2] ):

                faces_of_this_mesh.append( tri )


        # Add data to array
        data.append({
            "mesh_data" : m,                                    # raw mesh data
            "index_data" : index_data_of_this_mesh,             # raw index data (0 based, vertex ids are relative to beginning of mesh/group)
            "vertex_attribute" : vertex_attributes[ i ],        # raw vertex attribute data
            "vertices" : vertices[ i ],                         # processed vertices
            "faces" : faces_of_this_mesh                        # processed faces (0 based, vertex ids are relative to beginning of mesh/group)
        })
    return data




def create_obj(filename, vertices, indices=[]):
    # Remove .rlg from the filename
    filename = re.split(".rlg", filename)[0]
    # Create file
    obj = open("output/" +filename+ ".obj", "w")
    curr_group = -1

    # Now write the vertices
    for v in vertices:
        # Write the group of the vertices
        if(v["group"] != curr_group):

            curr_group = v["group"]
            line = "g group" + str( v["group"] ) + "\n"
            obj.write(line)
        # Write the vertex
        line = "v " + str( v["values"][0] ) + " " + str( v["values"][1] ) + " " + str( v["values"][2] ) + "\n"
        obj.write(line)

    print(filename + ".obj was successfully created in output folder")
    obj.close()




def create_obj_that_has_indices(filename, vertices, indices=[]):
    # Remove .rlg from the filename
    filename = re.split(".rlg", filename)[0]
    # Create file
    obj = open("output/" +filename+ ".obj", "w")

    vertices_by_group = split_vertices_by_group( vertices )

    mesh_data = get_mesh_data_from_rlg(rlg)

    first_vertex_identifier_of_group = 0

    for group, vertices in enumerate( vertices_by_group ):

        # Write the number of group
        obj.write( "g group " + str( group ) + "\n" )

        # Write the vertices of the group
        for vertex in vertices:
            obj.write( "v " + str( vertex["values"][0] ) + " " + str( vertex["values"][1] ) + " " + str( vertex["values"][2] ) + "\n" )
        

        # Write the faces of this group 
        index_array_start_offset = mesh_data[group]['index_start_offset']//2
        index_count = mesh_data[group]['index_count']
        index_end = (index_array_start_offset + index_count)

        indices_of_this_group = indices[ index_array_start_offset : index_end ]
        tri = []

        print( "DEBUG g=" + str(group) + " indices=" + str(len(indices_of_this_group)) )

        for i, index in enumerate( indices_of_this_group ):

            if( i < 2 ):
                continue
            
            # check if three adjacent indices are all different
            tri = indices_of_this_group[ (i - 2) : (i + 1) ]
            if( tri[0] != tri[1] and tri[1] != tri[2] and tri[0] != tri[2] ):
                # write face
                obj.write( "f " )      
                for tri_index in tri:    
                    absolute_index = first_vertex_identifier_of_group + tri_index + 1
                    obj.write( str( absolute_index ) + " " )
                obj.write( "\n" )
        

        # Update the vertex counter
        print( "DEBUG g=" + str(group) + " first_v_id=" + str(first_vertex_identifier_of_group) + "\n" )
        first_vertex_identifier_of_group += len(vertices)


    print(filename + ".obj was successfully created in output folder")
    obj.close()




def create_obj_for_each_group(filename, vertices):
    # Remove .rlg from the filename
    filename = re.split(".rlg", filename)[0]
    curr_group = 0
    group_filename = filename + "_0"
    obj = open("output/" +group_filename+ ".obj", "w")

    for v in vertices:
        # Switch file
        if(v["group"] != curr_group):
            curr_group = v["group"]
            # Create file
            group_filename = filename + "_" + str(v["group"])
            obj.close()
            obj = open("output/" +group_filename+ ".obj", "w")
            line = "g group" + str( v["group"] ) + "\n"
            obj.write(line)
        # Write the vertex
        line = "v " + str( v["values"][0] ) + " " + str( v["values"][1] ) + " " + str( v["values"][2] ) + "\n"
        obj.write(line)
    print("files created in output folder")
    obj.close()




def get_vertices_from_obj(filename):
    print("filename: " +filename)
    obj = open("obj/" + filename + ".obj", "r")
    # find the file size
    obj.seek(0,2)
    file_size = obj.tell()
    # read the data
    obj.seek(0,0)
    data = obj.read( file_size )

    # read the vertices of the obj file and convert them to array
    array_of_vertices = []
    vertex = []
    num_str = ''
    ignore = False
    column = 0
    for i in data:
        # If first character of row is not v, ignore the whole row
        if(i != 'v' and column == 0):
            ignore = True
        # If second character of row is not whitespace, ignore the whole row
        if(i != ' ' and column == 1):
            ignore = True
        # If current character is a comment ignore until new line
        if(i == '#'):
            ignore = True
        # If current character is part of a number, store it
        if(i in ['0','1','2','3','4','5','6','7','8','9','-','.','e']):
            num_str += i
        #  Increment the column
        column += 1
        # At the end of a number, parse the number
        if( (i == " " and len(num_str) != 0) or i == "\n"):
            if(not ignore):
                num = float(num_str)
                vertex.append(num)
            num_str = ''
            # Check if it's newline
            if(i == "\n"):
                if(len(vertex) > 0):
                    array_of_vertices.append(vertex)
                vertex = []
                ignore = False
                column = 0
        
    obj.close()
    return array_of_vertices




def generate_new_rlg(original_rlg):

    # Get the rlg filename (without extension)
    filename = os.path.basename(original_rlg.name)
    filename = re.split(".rlg", filename)[0]

    # Get the data from both the rlg and the obj
    try:
        new_vertices = get_vertices_from_obj(filename)
    except:
        print("Error: .obj file not found")
        return
    
    # check if files have the same amount of vertices. Throw a warning if not
    old_vertices = get_vertices_from_rlg( original_rlg, get_vertex_attributes_from_rlg(original_rlg) )
    print("Found " + str(len(new_vertices)) + " Vertices in given obj file")
    print("Found " + str(len(old_vertices)) + " Vertices in given rlg file")
    if( len(new_vertices) != len(old_vertices)):
        print("Warning: The vertex count of the two files doesn't match. This may lead to errors, or the output rlg file might be incorrect")

    # open the file and find the start of the section we need
    rlg = open("rlg/"+filename+".rlg", "rb")
    section_info = rlg_get_section_info( rlg, SECTION_VERTEX_DATA )
    location = section_info[0]  
    start_of_data = location+8
    rlg.close()

    # copy the rlg file to the output folder and replace its vertices 
    shutil.copyfile('./rlg/'+filename+'.rlg', './output/'+filename+'.rlg')
    rlg = open("output/"+filename+'.rlg', "r+b")
    vertex_num = 0

    for i in old_vertices:
        offset = i['offset']
        curr_location = start_of_data+offset
        rlg.seek(curr_location,0)
        for j in new_vertices[ vertex_num ]:
            j_hexstr = hex(struct.unpack('<I', struct.pack('<f', j))[0])
            if(j_hexstr != "0x0"):
                j_bytes = bytes.fromhex(j_hexstr[2:])
            else:
                j_bytes = b'\x00\x00\x00\x00'
            rlg.write( j_bytes )
        vertex_num += 1
    print(filename+".rlg file successfully created in output folder")
    



# PROCEDURES FOR CONVERTING FILES
# Function to convert a .rlg file to .obj that only contains vertices.
def extract_rlg_vertices_to_obj_file( rlg ):
    vertex_attributes = get_vertex_attributes_from_rlg(rlg)
    vertices = get_vertices_from_rlg(rlg, vertex_attributes)
    create_obj(i, vertices)


# Function to convert a .rlg file to multiple .obj that only contains vertices. Each obj is a group
def extract_rlg_vertices_to_multiple_obj_files_separate_by_group( rlg ):
    vertex_attributes = get_vertex_attributes_from_rlg(rlg)
    vertices = get_vertices_from_rlg(rlg, vertex_attributes)
    create_obj_for_each_group(i, vertices)
    rlg.close()


# WIP function to convert a .rlg file to .obj that contains vertices and faces.
def extract_rlg_vertices_and_faces_to_obj_file( rlg ):
    vertex_attributes = get_vertex_attributes_from_rlg(rlg)
    vertices = get_vertices_from_rlg(rlg, vertex_attributes)
    indices = get_index_data_from_rlg(rlg)
    create_obj_that_has_indices(i, vertices, indices)




# FUNCTIONS THAT PRINT DATA TO TXT FILE
def print_misc_data_to_file(rlg):

    filename = os.path.basename(rlg.name)
    data = get_rlg_dict(rlg)

    txt = open("output/" +filename+ "_miscdata.txt", "w")

    txt.write( "ALL MESH DATA:\n" )
    for d in data:
        txt.write( str(d['mesh_data'] ) + "\n" )
    txt.write( "\n\n\n\n" )

    for i, d in enumerate(data):

        txt.write( "data[" +str(i)+ "]\n" )
        txt.write( "\nMESH DATA:\n" ) # TODO: iterate on the whole dict, and print ints as hex
        txt.write( str( d['mesh_data'] ) + "\n" )

        txt.write( "\nINDEX DATA:\n" )
        max_index = 0
        for e in d['index_data']:
            txt.write( str(hex(e)) + " " )
            if( e > max_index ):
                max_index = e
        txt.write( "\nbiggest index of mesh: " + str(hex(max_index)) )

        txt.write( "\n\nVERTEX ATTRIBUTE:\n" )
        for e in d['vertex_attribute']:
            txt.write( str(e) + "\n" )

        txt.write( "\nVERTICES:\n" )
        vertex_id = 0x0
        for e in d['vertices']:
            txt.write( "VERTEX " + hex( vertex_id ) + " " )
            vertex_id += 1
            txt.write( str( e['values'] ) )
            txt.write( "\n" )

        txt.write( "\n\nFACES:\n" )
        for e in d['faces']:
            txt.write( str(e) + "\n" )
        txt.write("\n\n\n\n\n\n\n\n")

    txt.close()
    print(filename+"_miscdata.txt file successfully created in output folder")


def print_vertex_attributes_to_file(rlg):
    # Read vertex attributes
    vertex_attribute = get_vertex_attributes_from_rlg(rlg)
    for a in vertex_attribute:
        print(a)
    # Print vertex attribute on text file
    txt = open("output/" +i+ "_vertexattribute.txt", "w")
    txt.write( str(len(vertex_attribute)) +" attributes found\n\n")
    for a in vertex_attribute:
        for j in a:
            txt.write( j +" : "+ hex(a.get(j)) )
            txt.write("\n")
        txt.write("------------------------------------------------\n")
    txt.close


def print_mesh_data_to_file(rlg):
    # Read mesh data
    mesh_data = get_mesh_data_from_rlg(rlg)
    for m in mesh_data:
        print(m)
    rlg.close()
    # Print mesh data on text file
    txt = open("output/" +i+ "_meshdata.txt", "w")
    txt.write( str(len(mesh_data)) +" mesh data found\n\n")
    for m in mesh_data:
        for j in m:
            txt.write( j +" : "+ hex(m.get(j)) )
            txt.write("\n")
        txt.write("------------------------------------------------\n")
    txt.close


def print_index_data_to_file(rlg):
    # Read index data
    bytestr = get_index_data_from_rlg(rlg)
    rlg.close()
    # Print index data on text file
    txt = open("output/" +i+ "_indexdata.txt", "w")
    string = byte_hex_str(bytestr)
    for j in range(0, len(string)):
        txt.write(string[j])
        if(j%12 == 11):
            txt.write("\n")
    txt.close()
    print("Created txt file containing index data of " +i+ " in output folder")




# START OF CODE
while True:
    r = input('''\n\n-- Select a command --
              
    COMMANDS FOR EXPORTING/IMPORTING FILES:
    e - Extract vertices and faces from .rlg file and save them in .obj format
    ev - Extract only vertices from .rlg file and save them in .obj format
    g - Generate new .rlg (by starting from an original .rlg and replacing its vertices with the ones of an obj)
              
    DEV STUFF:
    es - Extract vertices from rlg file and put them in separate OBJs (by group) (for dev purposes only. Those objs won't be useful to recreate an .rlg file)
    data - print misc data about each mesh of the .rlg file. Data will go into a txt file in the output folder
    va - print vertex attributes to txt file
    mesh - print mesh data to txt file
    index - print index data to txt file
    
    x - Exit\n\n''')

    # Check if response is exit
    if(r == "x"):
        exit()

    filenames = get_all_rlg_filenames()
    

    for i in filenames:
        rlg = open("rlg/" + i, "rb")
        print("\n================================================================")

        if(r == "ev"):
            extract_rlg_vertices_to_obj_file( rlg )

        #TODO test
        elif(r == "e"):
            extract_rlg_vertices_and_faces_to_obj_file( rlg )

        elif(r == "g"):
            generate_new_rlg(rlg)

        elif(r == "es"):
            extract_rlg_vertices_to_multiple_obj_files_separate_by_group(rlg)

        elif(r == "va"):
            print_vertex_attributes_to_file(rlg)

        elif(r == "mesh"):
            print_mesh_data_to_file(rlg)

        elif(r == "index"):
            print_index_data_to_file(rlg)
            
        elif(r == "data" or r == "d"):
            print_misc_data_to_file(rlg)

        else:
            print("invalid input")
            break
        print("================================================================")
        rlg.close()
    rlg.close()
    input("Press Enter to continue...")