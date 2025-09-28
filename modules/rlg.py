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

# VERTEX ATTRIBUTE POINTER CONSTANTS
# positions
VAP_POSITION_A = 0x67
VAP_POSITION_B = 0x0  # can have stride of 6 sometimes. Never seen this personally
# normals
VAP_NORMAL_A = 0xfe
VAP_NORMAL_B = 0x1  # can have stride of 3 sometimes. Never seen this personally
# uv coords
VAP_UV0_A = 0xcc  # idk what's the difference between these three. I've only seen the first
VAP_UV0_B = 0x3
VAP_UV0_C = 0x26
VAP_UV1_A = 0x17  # no idea what this is really. Comes from switch-toolbox source
# unknown
VAP_UNK0 = 0xed
VAP_UNK1 = 0x52
VAP_UNK2 = 0xc0
VAP_UNK3 = 0xd6
VAP_UNK4 = 0xd7
# bones
VAP_BONE_INDICES_A = 0xd4
VAP_BONE_WEIGHTS_A = 0xb0


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
    index_data = get_index_data_from_rlg( rlgfile, section_map[ SECTION_INDEX_DATA ][ 0 ], mesh_data )
    vertex_attributes = get_vaps( rlgfile, section_map[ SECTION_VERTEX_ATTRIBUTES ][ 0 ] ) 
    print( vertex_attributes )
    vertices = get_vertices( rlgfile, section_map[ SECTION_VERTEX_DATA ][ 0 ], meshes=mesh_data, vaps=vertex_attributes )


    # Loop through groups
    for i, mesh_data_instance in enumerate(mesh_data):


        index_data_of_this_mesh = index_data[ i ]


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
def get_vertices( rlg, section, meshes, vaps ):  # meshes is actually a list of mesh data instances. Renaming this soon.
    

    # we need mesh data and vertex attributes in order to find out how many vertices there are


    # set up some variables for the loop
    vertices = []
    absolute_id = 0

    # repeat for each interval: get all the vertices in the interval
    for i, mesh in enumerate( meshes ):
        
        relative_id = 0

        vertices_of_mesh = []

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
            vertices_of_mesh.append( new_vertex )

            current_byte = rlg.tell() - section.body_location()

            absolute_id += 1
            relative_id += 1


        vertices.append( vertices_of_mesh )


    return vertices



# returns a list of lists of VertexAttribute objects. Each dict is a vertex attribute instance
# each list is for a different mesh
def get_vaps( rlg, section ):  
    
    # TODO: REWORK THIS CODE IT SUCKS

    # set some variables for the loop
    rlg.seek( section.body_location() ,0)
    vertex_attributes = []
    group = -1

    vertex_attributes_of_mesh = []

    # read data
    while rlg.tell() < section.end(): 

        offset = int.from_bytes( rlg.read(4), "big" )
        type = int.from_bytes( rlg.read(1), "big" )
        stride = int.from_bytes( rlg.read(1), "big" )
        unknown_0x6 = int.from_bytes( rlg.read(2), "big" )

        if( type == VAP_POSITION_A ):
            group += 1
            if group > 0:  # this garbage piece of code will be gone soon
                vertex_attributes.append( vertex_attributes_of_mesh )
            vertex_attributes_of_mesh = []

        new_vertex_attribute = m3d.VertexAttribute( group, offset, type, stride, unknown_0x6 )

        vertex_attributes_of_mesh.append( new_vertex_attribute )


    vertex_attributes.append( vertex_attributes_of_mesh )

    return vertex_attributes




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
        new_mesh_data_instance = m3d.MeshData( index_offset=index_start_offset, index_count=index_count, index_format=index_format,
                                               vertex_count=vertex_count, unknown0xA=unknown_0x0a, attribute_count=attribute_count,
                                               unknown0xC=unknown_0x0c, material_hash_id=material_hash_id, unknown0x18=unknown_0x18, 
                                               unknown0x1C=unknown_0x1c, mesh_hash_id=mesh_hash_id, material_offset=material_offset,
                                               unknown_0x24=unknown_0x24, unknown_0x28=unknown_0x28, unknown_0x2C=unknown_0x2c )

        mesh_data_instances.append( new_mesh_data_instance )
  
    return mesh_data_instances
    



# Read data from index section. Return a list containing one list per mesh.
# Each of these lists contains the indices of the mesh
def get_index_data_from_rlg( rlgfile, section, mesh_data ):

    # go to where data starts
    rlgfile.seek( section.body_location(), 0 )

    # Read all indices and return a list containing lists of indices.
    # One list per mesh
    indices = []

    # iterate through every mesh
    for mesh_data_instance in mesh_data:

        indices_of_mesh = []

        rlgfile.seek( section.body_location() + mesh_data_instance.index_offset, 0 )

        # get indices of this mesh
        for i in range( mesh_data_instance.index_count ):
            indices_of_mesh.append( int.from_bytes( rlgfile.read(2), 'big' ) )


        # append this meshes indices to the list of all meshes
        indices.append( indices_of_mesh )


    return indices




def get_matrix_from_rlg( rlgfile, section ):

    rlgfile.seek( section.body_location(), 0 )

    matrix = []


    for i in range(4):

        matrix_row = []

        for j in range(4):

            matrix_row.append( util.bytes_to_float( rlgfile.read(4) ) )
        
        matrix.append( matrix_row )


    return matrix