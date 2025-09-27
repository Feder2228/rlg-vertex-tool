import shutil, math
from modules import m3d, util, nlgutil

# SECTION IDENTIFIER CONSTANTS
SECTION_CONTAINER = b'\xb0\x00'
SECTION_MATRIX_DATA = b'\xb0\x02'
SECTION_MODEL_DATA = b'\xb0\x03'
SECTION_MESH_DATA = b'\xb0\x04'
SECTION_VERTEX_ATTRIBUTES = b'\xb0\x05'
SECTION_VERTEX_DATA = b'\xb0\x06'
SECTION_INDEX_DATA = b'\xb0\x07'
SECTION_SKELETON_CONTAINER = b'\xb0\x08'
SECTION_BONE_MESH_HASHES = b'\xb0\x0b'
SECTION_BONE_MATRICES = b'\xb0\x0a'
SECTION_BONE_UNKNOWN = b'\xb0\x0c'
SECTION_MATERIAL_DATA = b'\xb0\x16'

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


# Read rlg file. Returns model3d object
def read_rlg( filepath ):

    print( "DEBUG: " + filepath )

    rlgfile = open( filepath, "rb" )

    section_map = nlgutil.get_map_of_sections( rlgfile )


    # Read general model data (data that is not associated with a mesh in particular)
    matrix = get_matrix_from_rlg( rlgfile, section_map[ SECTION_MATRIX_DATA ][ 0 ] )
    model_data = get_model_data_from_rlg( rlgfile, section_map[ SECTION_MODEL_DATA ][ 0 ] )
    model3d = m3d.Model3d( matrix, model_data, [] )
      
    
    # Read data that is associated to a mesh
    mesh_data = get_mesh_data_from_rlg( rlgfile, section_map[ SECTION_MESH_DATA ][ 0 ] )
    index_data = get_index_data_from_rlg( rlgfile, section_map[ SECTION_INDEX_DATA ][ 0 ] )
    vertex_attributes = get_vertex_attributes_from_rlg_split_by_group( rlgfile, section_map[ SECTION_VERTEX_ATTRIBUTES ][ 0 ] ) 
    vertices = get_vertices_from_rlg_split_by_group( rlgfile, section_map[ SECTION_VERTEX_DATA ][ 0 ], meshes=mesh_data, vaps=vertex_attributes )


    # Loop through groups
    for i, mesh_data_instance in enumerate(mesh_data):

        # Split index data by group
        index_data_end = mesh_data_instance.index_start_offset + ( (mesh_data_instance.index_count) * 2 )
        index_data_of_this_mesh = []

        for j in range( mesh_data_instance.index_start_offset//2, index_data_end//2 ): 

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




# replace part of an rlg file's data with the model3d object data
def patch_rlg( srcpath, dstpath, new_model3d ):

    # get the data of the original rlg file as a model3d object
    old_model3d = read_rlg( srcpath )

    # copy the rlg file and open it
    shutil.copyfile( srcpath, dstpath )
    rlgfile = open( dstpath, "r+b" )

    # get a map of the file's sections
    section_map = nlgutil.get_map_of_sections( rlgfile )

    # get vertex section
    vert_section = section_map[ SECTION_VERTEX_DATA ][ 0 ]


    # loop through every mesh of the file's model
    for i, mesh in enumerate( old_model3d.meshes ):

        # get the offset and vertex count of the vertex section
        #
        # TODO: this heavily relies on the VAPs being ordered in this specific way.
        # rewrite this part of the code.
        # also normals could have stride of 3, so detect the stride and act according to its value.
        # (if it's 12 do a thing, if it's 3 do a different thing)
        #
        offset_for_positions = mesh.vertex_attributes[ 0 ].offset
        offset_for_normals = mesh.vertex_attributes[ 1 ].offset
        offset_for_uvs = mesh.vertex_attributes[ 2 ].offset
        vertex_count = mesh.mesh_data.vertex_count

        # take the new vertices
        new_mesh = new_model3d.get_mesh_by_id( mesh.mesh_data.mesh_hash_id )
        if new_mesh == None:
            print( "WARNING: mesh with hashid {0} not found. Falling back to default mesh order (last to first)".format( hex( mesh.mesh_data.mesh_hash_id ) ) )
            new_mesh = new_model3d.meshes[ 11 - i ]  # TODO: should probably replace the 11 with "len( old_model3d.meshes )"
        new_vertices = new_mesh.vertices


        # VERTEX POSITIONS
        # go to the place where vertex positions are stored
        rlgfile.seek( vert_section.body_location() + offset_for_positions, 0 )

        if util.DEBUG:
            print( "DEBUG: vertex_count={0} len(newverts)={1}".format( vertex_count, len( new_vertices ) ) )
        
        # loop to replace all the vertex positions
        for j in range( vertex_count ):  

            # take a new vertex, then loop on its coordinates and replace all of them
            new_vertex = new_vertices[ j ]

            for coord in new_vertex.position:
                new_bytes = util.float_to_bytes( coord )
                rlgfile.write( new_bytes )


        
        # VERTEX NORMALS
        # go to the place where vertex normals are stored
        rlgfile.seek( vert_section.body_location() + offset_for_normals, 0 )

        # loop to replace all the vertex positions
        for j in range( vertex_count ):  

            # take a new vertex, then loop on its coordinates and replace all of them
            new_vertex = new_vertices[ j ]

            for coord in new_vertex.normal:
                new_bytes = util.float_to_bytes( coord )
                rlgfile.write( new_bytes )



        # UV COORDINATES
        # go to the place where vertex normals are stored
        rlgfile.seek( vert_section.body_location() + offset_for_uvs, 0 )

        # loop to replace all the vertex positions
        for j in range( vertex_count ):  

            # take a new vertex, then loop on its coordinates and replace all of them
            new_vertex = new_vertices[ j ]

            for coord in new_vertex.uv0:

                if ( coord < 0 or coord > 1 ) and util.DEBUG:
                    print( "DEBUG: this uv coord has a value of " + str( coord ) + " ( vertex " + str( j ) + " of mesh " + str( i ) + ")" )

                new_bytes = util.texcoord_to_bytes( coord )
                rlgfile.write( new_bytes )



    rlgfile.close()






#def rlg_get_section_info( rlg, section_identifier ):
#
#    data = rlg_get_data( rlg )
#    location = data.find( section_identifier )       
#
#    # flags      
#    rlg.seek( location, 0 )
#    flags = int.from_bytes( rlg.read(2), "big" )   
#
#    # section size
#    rlg.seek( location + 4, 0 )
#    section_size = int.from_bytes( rlg.read(4), "big" )
#
#    info = {
#        'location' : location,
#        'start_of_data' : location + 8,
#        'flags' : flags,
#        'section_size' : section_size 
#    }
#
#    return info



# Function to read the vertices of a rlg file. Returns a list of Vertex objects
# TODO: rework it completely and do it the proper way. 
# It needs to be more flexible so that it can read any rlg file.
# It currently doesn't check the V.A.Pointer type, it just assumes it.
# It also assumes the stride, which for normals is no good, since it could 
# sometimes be 3 instead of 12 
#
def get_vertices_from_rlg( rlg, section, meshes, vaps ):  # meshes is actually a list of mesh data instances. Renaming this soon.
    

    # we need mesh data and vertex attributes in order to find out how many vertices there are


    # set up some variables for the loop
    vertices = []
    absolute_id = 0

    # repeat for each interval: get all the vertices in the interval
    for i, mesh in enumerate( meshes ):
        
        relative_id = 0

        for j in range( mesh.vertex_count ):  
            
            offset = vaps[ i ][ 0 ].offset  
            rlg.seek( section.body_location() + offset + (j*12), 0 )
            current_byte = rlg.tell() - section.body_location()  # TODO: remove this?
            position = [ util.bytes_to_float( rlg.read(4) ),  
                         util.bytes_to_float( rlg.read(4) ), 
                         util.bytes_to_float( rlg.read(4) ) ]
           
            offset = vaps[ i ][ 1 ].offset
            rlg.seek( section.body_location() + offset + (j*12), 0 )
            normal = [ util.bytes_to_float( rlg.read(4) ),  
                       util.bytes_to_float( rlg.read(4) ), 
                       util.bytes_to_float( rlg.read(4) ) ]
            
            # I'm not sure if I should read the uv coordinates as signed
            # According to KillzXGaming's research it's unsigned,
            # but from my experience reading it as unsigned breaks some textures (even if barely noticeable).
            # 
            offset = vaps[ i ][ 2 ].offset
            rlg.seek( section.body_location() + offset + (j*4), 0 )
            attribute_0xcc = [ int.from_bytes( rlg.read(2), "big", signed=True ) / 1024,
                               int.from_bytes( rlg.read(2), "big", signed=True ) / 1024 ]

            offset = vaps[ i ][ 3 ].offset
            rlg.seek( section.body_location() + offset + (j*4), 0 )
            attribute_0xed = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vaps[ i ][ 4 ].offset
            rlg.seek( section.body_location() + offset + (j*4), 0 )
            attribute_0x52 = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vaps[ i ][ 5 ].offset
            rlg.seek( section.body_location() + offset + (j*4), 0 )
            attribute_0xc0 = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vaps[ i ][ 6 ].offset
            rlg.seek( section.body_location() + offset + (j*4), 0 )
            attribute_0xd6 = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vaps[ i ][ 7 ].offset
            rlg.seek( section.body_location() + offset + (j*4), 0 )
            attribute_0xd7 = [ int.from_bytes( rlg.read(4), "big" ) ]

            offset = vaps[ i ][ 8 ].offset
            rlg.seek( section.body_location() + offset + (j*4), 0 )
            attribute_0xd4 = [ int.from_bytes( rlg.read(1), "big" ),
                               int.from_bytes( rlg.read(1), "big" ),
                               int.from_bytes( rlg.read(1), "big" ),
                               int.from_bytes( rlg.read(1), "big" ) ]

            offset = vaps[ i ][ 9 ].offset
            rlg.seek( section.body_location() + offset + (j*16), 0 )
            attribute_0xb0 = [ util.bytes_to_float( rlg.read(4) ),  
                               util.bytes_to_float( rlg.read(4) ), 
                               util.bytes_to_float( rlg.read(4) ),
                               util.bytes_to_float( rlg.read(4) ) ]

            new_vertex = m3d.Vertex( absolute_id, relative_id, current_byte, i, position, normal,
                                            attribute_0xcc, attribute_0xed, attribute_0x52, attribute_0xc0,
                                            attribute_0xd6, attribute_0xd7, attribute_0xd4, attribute_0xb0)
            vertices.append( new_vertex )

            current_byte = rlg.tell() - section.body_location()

            absolute_id += 1
            relative_id += 1

    return vertices


# TODO: remove these two functions. get_verices_from_rlg should work like this
def get_vertices_from_rlg_split_by_group( rlg, header_location, meshes, vaps ):

    vertices = get_vertices_from_rlg( rlg, header_location, meshes, vaps )
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
def get_vertex_attributes_from_rlg( rlg, section ):  # section size shouldn't be needed. I'll have to rewrite the code tho
    
    # TODO: REWORK THIS CODE IT SUCKS

    # set some variables for the loop
    rlg.seek( section.body_location() ,0)
    vertex_attributes = []
    group = -1

    # read data
    while rlg.tell() < section.end(): 

        offset = int.from_bytes( rlg.read(4), "big" )
        type = int.from_bytes( rlg.read(1), "big" )
        stride = int.from_bytes( rlg.read(1), "big" )
        unknown_0x6 = int.from_bytes( rlg.read(2), "big" )

        if( type == VERTEX_ATTRIBUTE_TYPE_VERTEX ):
            group += 1

        new_vertex_attribute = m3d.VertexAttribute( group, offset, type, stride, unknown_0x6 )

        vertex_attributes.append( new_vertex_attribute )

    return vertex_attributes


# TODO: remove this function. get_vertex_..._rlg should work like this
def get_vertex_attributes_from_rlg_split_by_group( rlg, section ):
    
    vertex_attributes = get_vertex_attributes_from_rlg( rlg, section )

    vertex_attributes_by_group = []
    group = []

    for i, v in enumerate( vertex_attributes ):

        group.append( v )

        # if this is last vertex of a group, put the group into the "vertex_attributes_by_group" list
        if( i >= len(vertex_attributes)-1 or vertex_attributes[i+1].group != v.group ):
            vertex_attributes_by_group.append( group )
            group = []

    return vertex_attributes_by_group




def get_model_data_from_rlg( rlgfile, section ):
    
    # go to where model data starts
    rlgfile.seek( section.body_location(), 0 )

    model_count = section.size//12
    model_data_instances = []

    for i in range( model_count ):

        model_data = m3d.ModelData( int.from_bytes( rlgfile.read(4), "big" ),
                                           int.from_bytes( rlgfile.read(4), "big" ),
                                           int.from_bytes( rlgfile.read(4), "big" ) )

        model_data_instances.append( model_data )
    
    return model_data_instances




def get_mesh_data_from_rlg( rlg, section ):
    
    # go to where data starts
    rlg.seek( section.body_location() , 0 )

    # read data
    mesh_data_instances = []

    while rlg.tell() < section.end(): 
        index_start_offset = int.from_bytes( rlg.read(4), "big" )
        index_format = int.from_bytes( rlg.read(2), "big" )
        index_count = int.from_bytes( rlg.read(2), "big" )
        vertex_count = int.from_bytes( rlg.read(2), "big" )
        unknown_0x0a = int.from_bytes( rlg.read(1), "big" )
        attribute_count = int.from_bytes( rlg.read(1), "big" )
        unknown_0x0c = int.from_bytes( rlg.read(4), "big" )  # I'm pretty sure this is the vertex_attribute instance offset
        material_hash_id = int.from_bytes( rlg.read(4), "big" )
        mesh_hash_id = int.from_bytes( rlg.read(4), "big" )
        unknown_0x18 = int.from_bytes( rlg.read(4), "big" )
        unknown_0x1c = int.from_bytes( rlg.read(4), "big" )
        material_offset = int.from_bytes( rlg.read(4), "big" )
        unknown_0x24 = int.from_bytes( rlg.read(4), "big" )
        unknown_0x28 = int.from_bytes( rlg.read(4), "big" )
        unknown_0x2c = int.from_bytes( rlg.read(4), "big" )

        # TODO: rename variables in MeshData class
        new_mesh_data_instance = m3d.MeshData( index_start_offset=index_start_offset, index_count=index_count, index_format=index_format,
                                               vertex_count=vertex_count, unknown0xA=unknown_0x0a, attribute_count=attribute_count,
                                               unknown0xC=unknown_0x0c, material_hash_id=material_hash_id, unknown0x18=unknown_0x18, 
                                               unknown0x1C=unknown_0x1c, mesh_hash_id=mesh_hash_id, material_offset=material_offset,
                                               unknown_0x24=unknown_0x24, unknown_0x28=unknown_0x28, unknown_0x2C=unknown_0x2c )

        mesh_data_instances.append( new_mesh_data_instance )
  
    return mesh_data_instances
    



# Read data from index section. Return a list of all indices
def get_index_data_from_rlg( rlg, section ):

    # go to where data starts
    rlg.seek( section.body_location(), 0 )

    # read all indices and return a list containing them
    indices = []
    while rlg.tell() < section.end():
        indices.append( int.from_bytes( rlg.read(2), 'big' ) )
    return indices




def get_matrix_from_rlg( rlg, section ):

    rlg.seek( section.body_location(), 0 )

    matrix = []


    for i in range(4):

        matrix_row = []

        for j in range(4):

            matrix_row.append( util.bytes_to_float( rlg.read(4) ) )
        
        matrix.append( matrix_row )


    return matrix