import os
from modules import m3d, util

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



# Function to read the vertices of a rlg file. Returns a list of Vertex objects
def get_vertices_from_rlg( rlg ):
    
    # get section info
    section_info = rlg_get_section_info( rlg, SECTION_VERTEX_DATA )

    # get mesh data and vertex attributes, we need it in order to find out how many vertices there are
    meshes = get_mesh_data_from_rlg( rlg )
    vertex_attributes = get_vertex_attributes_from_rlg( rlg )

    # set up some variables for the loop
    start_of_data = section_info['start_of_data']
    vertices = []
    absolute_id = 0

    # repeat for each interval: get all the vertices in the interval
    for i, mesh in enumerate( meshes ):
        
        relative_id = 0

        for j in range( int( mesh.vertex_count, 16 ) ):  # TODO: I shouldn't have to cast vertex_count to int here
            
            offset = vertex_attributes[ i*10 ].offset  
            rlg.seek( start_of_data + offset + (j*12), 0 )
            current_byte = rlg.tell() - start_of_data  # TODO: remove this?
            position = [ util.bytes_to_float( rlg.read(4) ),  
                         util.bytes_to_float( rlg.read(4) ), 
                         util.bytes_to_float( rlg.read(4) ) ]
           
            offset = vertex_attributes[ i*10 + 1 ].offset
            rlg.seek( start_of_data + offset + (j*12), 0 )
            normal = [ util.bytes_to_float( rlg.read(4) ),  
                       util.bytes_to_float( rlg.read(4) ), 
                       util.bytes_to_float( rlg.read(4) ) ]
            
            offset = vertex_attributes[ i*10 + 2 ].offset
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xcc = [ int.from_bytes( rlg.read(2), "big" ) / 1024,
                               int.from_bytes( rlg.read(2), "big" ) / 1024 ]

            offset = vertex_attributes[ i*10 + 3 ].offset
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xed = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vertex_attributes[ i*10 + 4 ].offset
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0x52 = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vertex_attributes[ i*10 + 5 ].offset
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xc0 = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vertex_attributes[ i*10 + 6 ].offset
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xd6 = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vertex_attributes[ i*10 + 7 ].offset
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xd7 = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vertex_attributes[ i*10 + 8 ].offset
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xd4 = [ int.from_bytes( rlg.read(1), "big" ),
                               int.from_bytes( rlg.read(1), "big" ),
                               int.from_bytes( rlg.read(1), "big" ),
                               int.from_bytes( rlg.read(1), "big" ) ]

            offset = vertex_attributes[ i*10 + 9 ].offset
            rlg.seek( start_of_data + offset + (j*16), 0 )
            attribute_0xb0 = [ util.bytes_to_float( rlg.read(4) ),  
                               util.bytes_to_float( rlg.read(4) ), 
                               util.bytes_to_float( rlg.read(4) ),
                               util.bytes_to_float( rlg.read(4) ) ]

            new_vertex = m3d.Vertex( absolute_id, relative_id, current_byte, i, position, normal,
                                            attribute_0xcc, attribute_0xed, attribute_0x52, attribute_0xc0,
                                            attribute_0xd6, attribute_0xd7, attribute_0xd4, attribute_0xb0)
            vertices.append( new_vertex )

            current_byte = rlg.tell() - start_of_data

            absolute_id += 1
            relative_id += 1

    return vertices


def get_vertices_from_rlg_split_by_group( rlg ):

    vertices = get_vertices_from_rlg( rlg )
    return split_vertices_by_group( vertices )
    

def split_vertices_by_group( vertices ):

    vertices_by_group = []
    group = []

    for i, v in enumerate( vertices ):

        group.append( v )

        # if this is last vertex of a group, put the group into the "vertices_by_group" list
        if( i >= len(vertices)-1 or vertices[i+1].group != v.group ):
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
    vertex_attributes = []
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

        new_vertex_attribute = m3d.VertexAttribute( group, offset, type, stride, unknown_0x6 )

        vertex_attributes.append( new_vertex_attribute )

    return vertex_attributes


def get_vertex_attributes_from_rlg_split_by_group(rlg):
    
    vertex_attributes = get_vertex_attributes_from_rlg( rlg )

    vertex_attributes_by_group = []
    group = []

    for i, v in enumerate( vertex_attributes ):

        group.append( v )

        # if this is last vertex of a group, put the group into the "vertex_attributes_by_group" list
        if( i >= len(vertex_attributes)-1 or vertex_attributes[i+1].group != v.group ):
            vertex_attributes_by_group.append( group )
            group = []

    return vertex_attributes_by_group




def get_model_data_from_rlg(rlg):
    
    section_info = rlg_get_section_info( rlg, SECTION_MODEL_DATA )
    start_of_data = section_info['start_of_data']
    section_size = section_info['section_size']

    # go to where model data starts
    rlg.seek( start_of_data, 0 )

    model_count = section_size//12
    model_data_instances = []

    for i in range( model_count ):

        model_data = m3d.ModelData( int.from_bytes( rlg.read(4), "big" ),
                                           int.from_bytes( rlg.read(4), "big" ),
                                           int.from_bytes( rlg.read(4), "big" ) )

        model_data_instances.append( model_data )
    
    return model_data_instances




def get_mesh_data_from_rlg(rlg):
    
    section_info = rlg_get_section_info( rlg, SECTION_MESH_DATA )
    start_of_data = section_info['start_of_data']
    section_size = section_info['section_size']

    # go to where data starts
    rlg.seek( start_of_data , 0 )
    start_of_data = rlg.tell()

    # read data
    mesh_data_instances = []

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

        new_mesh_data_instance = m3d.MeshData( index_start_offset, index_flags & 0xffffff, index_flags >> 24, hex(vertex_count),  # TODO: nuh-uh
                 unknown_0x0a, material_hash_id, unknown_0x16, unknown_0x1a, mesh_hash_id,  material_offset, unknown_0x22,
                 unknown_0x26, unknown_0x2a,   
        )

        mesh_data_instances.append( new_mesh_data_instance )
  
    return mesh_data_instances
    



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





# Read rlg file. Returns model3d object
def read_rlg( filepath ):

    rlgfile = open( filepath, "rb" )

    model3d = m3d.Model3d( get_matrix_from_rlg( rlgfile ), get_model_data_from_rlg( rlgfile ), [] )
      
    
    # Read data
    mesh_data = get_mesh_data_from_rlg( rlgfile )
    index_data = get_index_data_from_rlg( rlgfile )
    vertex_attributes = get_vertex_attributes_from_rlg_split_by_group( rlgfile )
    vertices = get_vertices_from_rlg_split_by_group( rlgfile )


    # Loop through groups
    for i, mesh_data_instance in enumerate(mesh_data):

        # Split index data by group
        index_data_end = mesh_data_instance.index_start_offset + ( (mesh_data_instance.index_count) * 2 )
        index_data_of_this_mesh = []

        for j in range( mesh_data_instance.index_start_offset//2, index_data_end//2 ): 

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

                confirmed_tri = m3d.Face( tri )

                faces_of_this_mesh.append( confirmed_tri )


        new_mesh = m3d.Mesh( mesh_data_instance, index_data, vertex_attributes[ i ], vertices[ i ], faces_of_this_mesh )

        # Add data to array
        model3d.meshes.append( new_mesh )

    rlgfile.close()
    return model3d

