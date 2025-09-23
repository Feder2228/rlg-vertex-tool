import os, util

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


def rlg_get_size(rlg):
    rlg.seek(0,2)
    return rlg.tell()

def rlg_get_data(rlg):
    size = rlg_get_size( rlg )
    rlg.seek(0,0)
    return rlg.read( size )

def rlg_get_section_info( rlg, section_identifier ):

    data = rlg_get_data( rlg )
    location = data.find( section_identifier )       

    # flags      
    rlg.seek( location, 0 )
    flags = int.from_bytes( rlg.read(2), "big" )   

    # section size
    rlg.seek( location + 4, 0 )
    section_size = int.from_bytes( rlg.read(4), "big" )

    info = {
        'location' : location,
        'start_of_data' : location + 8,
        'flags' : flags,
        'section_size' : section_size 
    }

    return info



# Function to read the vertices of a rlg file. Returns a list containing all the vertices
def get_vertices_from_rlg( rlg ):
    
    # get section info
    section_info = rlg_get_section_info( rlg, SECTION_VERTEX_DATA )

    # get mesh data and vertex attributes, we need it in order to find out how many vertices there are
    meshes = get_mesh_data_from_rlg( rlg )
    vertex_attributes = get_vertex_attributes_from_rlg( rlg )

    # set up some variables for the loop
    start_of_data = section_info['start_of_data']
    a = []
    absolute_id = 0

    # repeat for each interval: get all the vertices in the interval
    for i, mesh in enumerate( meshes ):
        
        relative_id = 0

        for j in range( int( mesh['vertex_count'], 16 ) ):  # TODO: I shouldn't have to cast vertex_count to int here
            
            offset = vertex_attributes[ i*10 ]['offset']  # TODO: move this inside the loop?
            rlg.seek( start_of_data + offset + (j*12), 0 )
            current_byte = rlg.tell() - start_of_data  # TODO: remove this?
            position = [ util.bytes_to_float( rlg.read(4) ),  
                         util.bytes_to_float( rlg.read(4) ), 
                         util.bytes_to_float( rlg.read(4) ) ]
           
            offset = vertex_attributes[ i*10 + 1 ]['offset']
            rlg.seek( start_of_data + offset + (j*12), 0 )
            normal = [ util.bytes_to_float( rlg.read(4) ),  
                       util.bytes_to_float( rlg.read(4) ), 
                       util.bytes_to_float( rlg.read(4) ) ]
            
            offset = vertex_attributes[ i*10 + 2 ]['offset']
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xcc = [ int.from_bytes( rlg.read(2), "big" ) / 1024,
                               int.from_bytes( rlg.read(2), "big" ) / 1024 ]

            offset = vertex_attributes[ i*10 + 3 ]['offset']
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xed = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vertex_attributes[ i*10 + 4 ]['offset']
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0x52 = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vertex_attributes[ i*10 + 5 ]['offset']
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xc0 = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vertex_attributes[ i*10 + 6 ]['offset']
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xd6 = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vertex_attributes[ i*10 + 7 ]['offset']
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xd7 = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vertex_attributes[ i*10 + 8 ]['offset']
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xd4 = [ int.from_bytes( rlg.read(1), "big" ),
                               int.from_bytes( rlg.read(1), "big" ),
                               int.from_bytes( rlg.read(1), "big" ),
                               int.from_bytes( rlg.read(1), "big" ) ]

            offset = vertex_attributes[ i*10 + 9 ]['offset']
            rlg.seek( start_of_data + offset + (j*16), 0 )
            attribute_0xb0 = [ util.bytes_to_float( rlg.read(4) ),  
                               util.bytes_to_float( rlg.read(4) ), 
                               util.bytes_to_float( rlg.read(4) ),
                               util.bytes_to_float( rlg.read(4) ) ]

            a.append( {
                "absolute_id" : absolute_id,       # id
                "relavtive_id" : relative_id,      # id (relative to the start of the group)
                "offset" : current_byte,           # TODO: should I remove this?
                "group" : i,
                "position" : position,
                "normal" : normal,
                "uv0" : attribute_0xcc,
                "attribute_0xed" : attribute_0xed,
                "attribute_0x52" : attribute_0x52,
                "attribute_0xc0" : attribute_0xc0,
                "attribute_0xd6" : attribute_0xd6,
                "attribute_0xd7" : attribute_0xd7,
                "bone_ids" : attribute_0xd4,
                "bone_weights" : attribute_0xb0,
            } )

            current_byte = rlg.tell() - start_of_data

            absolute_id += 1
            relative_id += 1

    return a


def get_vertices_from_rlg_split_by_group( rlg ):

    vertices = get_vertices_from_rlg( rlg )
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
    start_of_data = section_info['start_of_data']
    section_size = section_info['section_size']

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




# TODO: WIP, need to split by model. For now only works if the file contains one model
def get_model_data_from_rlg(rlg):
    
    section_info = rlg_get_section_info( rlg, SECTION_MODEL_DATA )
    start_of_data = section_info['start_of_data']
    section_size = section_info['section_size']

    # go to where model data starts
    rlg.seek( start_of_data, 0 )

    model_count = section_size//12
    model_data = []

    for i in range( model_count ):

        model_data.append( {
            'hash_id' : int.from_bytes( rlg.read(4), "big"),
            'mesh_count' : int.from_bytes( rlg.read(4), "big" ),
            '0x8' : int.from_bytes( rlg.read(4), "big" )
        })
    
    return model_data




def get_mesh_data_from_rlg(rlg):

    # get the filename and strip the extention
    filename = os.path.basename(rlg.name)
    print("Reading mesh data of: " +filename)
    
    section_info = rlg_get_section_info( rlg, SECTION_MESH_DATA )
    start_of_data = section_info['start_of_data']
    section_size = section_info['section_size']

    # go to where data starts
    rlg.seek( start_of_data , 0 )
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
    start_of_data = section_info['start_of_data']
    section_size = section_info['section_size']

    # go to where data starts
    rlg.seek( start_of_data, 0 )
    end_of_section = start_of_data + section_size

    # read all indices and return a list containing them
    indices = []
    while rlg.tell() < end_of_section:
        indices.append( int.from_bytes( rlg.read(2), 'big' ) )
    return indices




def get_matrix_from_rlg(rlg):

    section_info = rlg_get_section_info( rlg, SECTION_MATRIX_DATA )
    start_of_data = section_info['start_of_data']

    rlg.seek( start_of_data, 0 )

    matrix = []


    for i in range(4):

        matrix_row = []

        for j in range(4):

            matrix_row.append( util.bytes_to_float( rlg.read(4) ) )
        
        matrix.append( matrix_row )


    return matrix





# Get a dict with various data from an rlg file
# Still WIP. Currently structured like this:
# Dict that has the following keys: "model_data", "meshes"
# "meshes" is a list of dicts, each of which contain data of a group/mesh: "mesh_data", "index_data", "vertex_attributes", "vertices", "faces"
# For more info look at the comments next to the last "append" in this function
def read_rlg(rlg):

    data = {
        'matrix' : get_matrix_from_rlg(rlg),
        'model_data' : get_model_data_from_rlg(rlg), 
        'meshes' : []
    }
      
    
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
        data['meshes'].append({
            "mesh_data" : m,                                    # raw mesh data
            "index_data" : index_data_of_this_mesh,             # raw index data (0 based, vertex ids are relative to beginning of mesh/group)
            "vertex_attributes" : vertex_attributes[ i ],        # raw vertex attribute data
            "vertices" : vertices[ i ],                         # processed vertices
            "faces" : faces_of_this_mesh                        # processed faces (0 based, vertex ids are relative to beginning of mesh/group)
        })
    return data



# TODO: nuke this
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
    old_vertices = get_vertices_from_rlg( original_rlg )
    print("Found " + str(len(new_vertices)) + " Vertices in given obj file")
    print("Found " + str(len(old_vertices)) + " Vertices in given rlg file")
    if( len(new_vertices) != len(old_vertices)):
        print("Warning: The vertex count of the two files doesn't match. This may lead to errors, or the output rlg file might be incorrect")

    # open the file and find the start of the section we need
    rlg = open( DIR_PATH_INPUT_NLG_FORMATS + filename + ".rlg", "rb" )
    section_info = rlg_get_section_info( rlg, SECTION_VERTEX_DATA )
    start_of_data = section_info['start_of_data']  
    rlg.close()

    # copy the rlg file to the output folder and replace its vertices 
    shutil.copyfile( DIR_PATH_INPUT_NLG_FORMATS + filename + '.rlg', './' + DIR_PATH_OUTPUT + filename + '.rlg')
    rlg = open( DIR_PATH_OUTPUT + filename + '.rlg', "r+b" )
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
    