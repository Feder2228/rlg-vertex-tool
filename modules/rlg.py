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
    matrix = get_matrix( rlgfile, section_map[ SECTION_MATRIX_DATA ][ 0 ] )
    model_data = get_modeldata( rlgfile, section_map[ SECTION_MODEL_DATA ][ 0 ] )
    model3d = m3d.Model3d( matrix, model_data, [] )
      
    
    # Read data that is associated to a mesh
    mesh_datas = get_meshdata( rlgfile, section_map[ SECTION_MESH_DATA ][ 0 ] )
    index_data = get_indices( rlgfile, section_map[ SECTION_INDEX_DATA ][ 0 ], mesh_datas )
    vertex_attributes = get_vaps( rlgfile, section_map[ SECTION_VERTEX_ATTRIBUTES ][ 0 ], mesh_datas ) 
    vertices = get_vertices( rlgfile, section_map[ SECTION_VERTEX_DATA ][ 0 ], mesh_datas=mesh_datas, vaps=vertex_attributes )


    # Loop through meshes
    for i, mesh_data_instance in enumerate( mesh_datas ):


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


        # take the new vertices
        new_mesh = new_model3d.get_mesh_by_id( mesh.mesh_data.mesh_hash_id )
        if new_mesh == None:
            print( "WARNING: mesh with hashid {0} not found. Falling back to default mesh order (last to first)".format( hex( mesh.mesh_data.mesh_hash_id ) ) )
            new_mesh = new_model3d.meshes[ len( old_model3d.meshes ) - i ]  # TODO: should probably replace the 11 with "len( old_model3d.meshes )"
        new_vertices = new_mesh.vertices



        for j, vap in enumerate( mesh.vertex_attributes ):

            # go to the place indicated by the VAP
            rlgfile.seek( vert_section.body_location() + vap.offset, 0 )


            if vap.type in [ VAP_POSITION_A, VAP_POSITION_B ]:
                if vap.stride == 12:
                    for k in range( mesh.mesh_data.vertex_count ):  
                        rlgfile.write( util.float_to_bytes4( new_vertices[ k ].position[0] ) )
                        rlgfile.write( util.float_to_bytes4( new_vertices[ k ].position[1] ) )
                        rlgfile.write( util.float_to_bytes4( new_vertices[ k ].position[2] ) )
                elif vap.stride == 6:
                    for k in range( mesh.mesh_data.vertex_count ):  
                        rlgfile.write( util.float_to_bytes1( new_vertices[ k ].position[0] ) )
                        rlgfile.write( util.float_to_bytes1( new_vertices[ k ].position[1] ) )
                        rlgfile.write( util.float_to_bytes1( new_vertices[ k ].position[2] ) )
                else:
                    print( 'huh, pos stride is ' + str( vap.stride ) )  # this shouldn't happen
            

            elif vap.type in [ VAP_NORMAL_A, VAP_NORMAL_B ]:
                if vap.stride == 12:
                    for k in range( mesh.mesh_data.vertex_count ):  
                        rlgfile.write( util.float_to_bytes4( new_vertices[ k ].normal[0] ) )
                        rlgfile.write( util.float_to_bytes4( new_vertices[ k ].normal[1] ) )
                        rlgfile.write( util.float_to_bytes4( new_vertices[ k ].normal[2] ) )
                elif vap.stride == 3:
                    for k in range( mesh.mesh_data.vertex_count ):  
                        rlgfile.write( util.float_to_bytes2( new_vertices[ k ].normal[0] ) )
                        rlgfile.write( util.float_to_bytes2( new_vertices[ k ].normal[1] ) )
                        rlgfile.write( util.float_to_bytes2( new_vertices[ k ].normal[2] ) )
                else:
                    print( 'huh, normal stride is ' + str( vap.stride ) )  # this shouldn't happen


            elif vap.type in [ VAP_UV0_A, VAP_UV0_B, VAP_UV0_C ]:
                if vap.stride == 4:
                    for k in range( mesh.mesh_data.vertex_count ):  
                        rlgfile.write( util.float_to_bytes2( new_vertices[ k ].uv0[0] ) )
                        rlgfile.write( util.float_to_bytes2( new_vertices[ k ].uv0[1] ) )
                else:
                    print( 'huh, uv0 stride is ' + str( vap.stride ) )  # this shouldn't happen


    rlgfile.close()




# Function to read the vertices of a rlg file. Returns a list which contains lists of Vertex object.
# One list per each matrix.
#
def get_vertices( rlgfile, section, mesh_datas, vaps ): 
    

    # we need mesh data and vertex attributes in order to find out how many vertices there are


    # set up some variables for the loop
    vertices = []


    # iterate through all mesh_data instances
    for i, mesh_data in enumerate ( mesh_datas ):


        # Intialize vertices, with default values. 
        # These values are invalid, but will be changed later.
        #
        mesh_vertices = []
        for j in range( mesh_data.vertex_count ):
            mesh_vertices.append( m3d.Vertex( relative_id=j ) )


        # iterate through all VAPs of the mesh
        for vap in vaps[ i ]:

            # go to the offset that is indicated by the VAP
            rlgfile.seek( section.body_location() + vap.offset, 0 )


            # Now, act accordingly to what kind of data this is.
            #
            # If it's vertex positions...
            if vap.type in [ VAP_POSITION_A, VAP_POSITION_B ]:
                if vap.stride == 12:
                    for k in range( mesh_data.vertex_count ):
                        mesh_vertices[ k ].position = [ util.bytes_to_float( rlgfile.read(4) ),  
                                                        util.bytes_to_float( rlgfile.read(4) ), 
                                                        util.bytes_to_float( rlgfile.read(4) ) ]
                elif vap.stride == 6:
                    for k in range( mesh_data.vertex_count ):
                        mesh_vertices[ k ].position = [ int.from_bytes( rlgfile.read(2), 'big', signed=True ) / 1024,
                                                        int.from_bytes( rlgfile.read(2), 'big', signed=True ) / 1024,
                                                        int.from_bytes( rlgfile.read(2), 'big', signed=True ) / 1024 ]
                else:
                    print( 'huh, pos stride is ' + str( vap.stride ) )  # this shouldn't happen


            # If it's normals...
            elif vap.type in [ VAP_NORMAL_A, VAP_NORMAL_B ]:
                if vap.stride == 12:
                    for k in range( mesh_data.vertex_count ):
                        mesh_vertices[ k ].normal = [ util.bytes_to_float( rlgfile.read(4) ),  
                                                      util.bytes_to_float( rlgfile.read(4) ), 
                                                      util.bytes_to_float( rlgfile.read(4) ) ]
                elif vap.stride == 3:
                    for k in range( mesh_data.vertex_count ):
                        mesh_vertices[ k ].normal = [ int.from_bytes( rlgfile.read(1), 'big', signed=True ) / 255,
                                                      int.from_bytes( rlgfile.read(1), 'big', signed=True ) / 255,
                                                      int.from_bytes( rlgfile.read(1), 'big', signed=True ) / 255 ]
                else:
                    print( 'huh, normal stride is ' + str( vap.stride ) )  # this shouldn't happen


            # If it's uv coordinates (0)...
            elif vap.type in [ VAP_UV0_A, VAP_UV0_B, VAP_UV0_C ]:
                if vap.stride == 4:
                    for k in range( mesh_data.vertex_count ):
                        mesh_vertices[ k ].uv0 = [ int.from_bytes( rlgfile.read(2), 'big', signed=True ) / 1024,
                                                      int.from_bytes( rlgfile.read(2), 'big', signed=True ) / 1024 ]
                else:
                    print( 'huh, uv0 stride is: ' + str( vap.stride ) )  # this shouldn't happen


            # If it's uv coordinates (1)...
            elif vap.type == VAP_UV1_A:
                print( 'uv1 detected. What even is uv1 though?' )  # I have no idea what to do with this for now. 
                # I'll just put this print message here so that when we open a file that has vap type 0x17 we notice it


            # If it's the list of bone indices...
            elif vap.type == VAP_BONE_INDICES_A:
                if vap.stride == 4:
                    for k in range( mesh_data.vertex_count ):
                        mesh_vertices[ k ].bone_ids = [ int.from_bytes( rlgfile.read(1), 'big' ),
                                                      int.from_bytes( rlgfile.read(1), 'big' ),
                                                      int.from_bytes( rlgfile.read(1), 'big' ),
                                                      int.from_bytes( rlgfile.read(1), 'big' ) ]
                else:
                    print( 'huh, bone indices stride is: ' + vap.stride )  # this shouldn't happen


            # If it's the list of bone weights...
            elif vap.type == VAP_BONE_WEIGHTS_A:
                if vap.stride == 16:
                    for k in range( mesh_data.vertex_count ):
                        mesh_vertices[ k ].bone_weights = [ util.bytes_to_float( rlgfile.read(4) ),  
                                                      util.bytes_to_float( rlgfile.read(4) ),
                                                      util.bytes_to_float( rlgfile.read(4) ),  
                                                      util.bytes_to_float( rlgfile.read(4) ) ]
                else:
                    print( 'huh, bone weights stride is: ' + vap.stride )  # this shouldn't happen


            # If it's one of the unknown values...
            elif vap.type == VAP_UNK0:
                for k in range( mesh_data.vertex_count ):
                    mesh_vertices[ k ].unknown0xED = rlgfile.read( vap.stride )

            elif vap.type == VAP_UNK1:
                for k in range( mesh_data.vertex_count ):
                    mesh_vertices[ k ].unknown0x52 = rlgfile.read( vap.stride )

            elif vap.type == VAP_UNK2:
                for k in range( mesh_data.vertex_count ):
                    mesh_vertices[ k ].unknown0xC0 = rlgfile.read( vap.stride )

            elif vap.type == VAP_UNK3:
                for k in range( mesh_data.vertex_count ):
                    mesh_vertices[ k ].unknown0xD6 = rlgfile.read( vap.stride )

            elif vap.type == VAP_UNK4:
                for k in range( mesh_data.vertex_count ):
                    mesh_vertices[ k ].unknown0xD7 = rlgfile.read( vap.stride )


        vertices.append( mesh_vertices )


    return vertices




# returns a list of lists of VertexAttribute objects. Each dict is a vertex attribute instance
# each list is for a different mesh
# VAP stands for "vertex attribute pointer"
#
def get_vaps( rlg, section, mesh_datas ):  
    
    # set sup ome variables for the loop
    vaps = []


    # iterate through every mesh
    for i, mesh_data in enumerate( mesh_datas ):

        # go to the location of this meshes' VAPs 
        rlg.seek( section.body_location() + mesh_data.unknown0xC, 0 )  # unknown0xC is vap offset.
        mesh_vaps = []

        # repeat VAP_count times, read the next VAP 
        # (read all the Vertex Attribute Pointers of the mesh)
        #
        for j in range( mesh_data.attribute_count ):

            offset = int.from_bytes( rlg.read(4), 'big' )
            type = int.from_bytes( rlg.read(1), 'big' )
            stride = int.from_bytes( rlg.read(1), 'big' )
            unknown_0x6 = int.from_bytes( rlg.read(2), 'big' )  # RLG only

            if util.DEBUG:
                print( 'iter {0} {1}  offset {2}  type {3}  stride {4}'.format( i,j,offset,type,stride ) )

            mesh_vaps.append( m3d.VertexAttribute( group=i, offset=offset, type=type, stride=stride, unknown0x6=unknown_0x6 )  )

    
        vaps.append( mesh_vaps )


    return vaps 




def get_modeldata( rlgfile, section ):
    
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




def get_meshdata( rlg, section ):
    
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
        vap_count = int.from_bytes( rlg.read(1), "big" )
        vap_offset = int.from_bytes( rlg.read(4), "big" )  # I'm pretty sure this is the vertex_attribute instance offset
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
                                               vertex_count=vertex_count, unknown0xA=unknown_0x0a, attribute_count=vap_count,
                                               unknown0xC=vap_offset, material_hash_id=material_hash_id, unknown0x18=unknown_0x18, 
                                               unknown0x1C=unknown_0x1c, mesh_hash_id=mesh_hash_id, material_offset=material_offset,
                                               unknown_0x24=unknown_0x24, unknown_0x28=unknown_0x28, unknown_0x2C=unknown_0x2c )

        mesh_data_instances.append( new_mesh_data_instance )
  
    return mesh_data_instances
    



# Read data from index section. Return a list containing one list per mesh.
# Each of these lists contains the indices of the mesh
def get_indices( rlgfile, section, mesh_data ):

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




def get_matrix( rlgfile, section ):

    rlgfile.seek( section.body_location(), 0 )

    matrix = []


    for i in range(4):

        matrix_row = []

        for j in range(4):

            matrix_row.append( util.bytes_to_float( rlgfile.read(4) ) )
        
        matrix.append( matrix_row )


    return matrix