from modules import m3d, util, rlgtool_xml

# DAE STRINGS
DAE_STR_HEADER = '''<?xml version="1.0" encoding="utf-8"?>
<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <asset/>
  <library_images/>'''
DAE_STR_GEOMETRY_TEMPLATE = '<geometry id="{0}" name="{1}">'
DAE_STR_SOURCE_TEMPLATE = '<source id="{0}">'
DAE_STR_FLOAT_ARRAY_TEMPLATE = '<float_array id="{0}" count="{1}">'
DAE_STR_ACCESSOR_TEMPLATE = '<accessor source="{0}" count="{1}" stride="{2}">'
DAE_STR_PARAM_TEMPLATE = '<param name="{0}" type="{1}"/>'
DAE_STR_NODE_TEMPLATE = '<node id="{0}" name="{1}" type="{2}">'
DAE_STR_INSTANCE_GEOMETRY_TEMPLATE = '<instance_geometry url="{0}" name="{1}"/>'
DAE_STR_INPUT_TEMPLATE = '<input semantic="{0}" source="{1}"/>'
DAE_STR_INPUT_TEMPLATE_OFFSET = '<input semantic="{0}" source="{1}" offset="{2}"/>'
DAE_STR_INPUT_TEMPLATE_OFFSET_SET = '<input semantic="{0}" source="{1}" offset="{2}" set="{3}"/>'
DAE_STR_VERTICES_TEMPLATE = '<vertices id="{0}">'
DAE_STR_TRIANGLES_TEMPLATE = '<triangles count="{0}">'


def create_dae( model, filepath ):

    filename_root = filepath.split( "/" )[-1].split(".")[0]
    print( "DEBUG: filename_root= {0} filepath= {1}".format( filename_root, filepath ) )

    daefile = open( filepath, "w" ) 

    daefile.write( DAE_STR_HEADER + '\n' )

    TAB = "  "
    tab_count = 1
    


    # LIBRARY_GEOMETRIES
    daefile.write( ( TAB * tab_count ) + '<library_geometries>\n' )
    tab_count += 1

    for i, geometry in enumerate( model.meshes ):

        # open geometry tag
        geometry_name = filename_root + "_" + str(i)
        id = geometry_name + '-mesh'
        daefile.write( ( TAB * tab_count ) + DAE_STR_GEOMETRY_TEMPLATE.format( id, geometry_name ) + '\n' )
        tab_count += 1
        
        # open mesh tag
        daefile.write( ( TAB * tab_count ) + '<mesh>\n' )
        tab_count += 1

        # iteration 0 is for positions, 1 is for normals, 2 is for vertex colors, 3 is for uv coords
        for j in range(4):
            
            # open source tag
            id = geometry_name + ['-mesh-position', '-mesh-normal', '-mesh-color', '-mesh-texcoord' ][j]
            daefile.write( ( TAB * tab_count ) + DAE_STR_SOURCE_TEMPLATE.format( id ) + '\n' )
            tab_count += 1

            # open and close float array tag
            id = geometry_name + ['-mesh-position', '-mesh-normal', '-mesh-color', '-mesh-texcoord' ][j] + '-array'

            if j in [0,1]:
                float_count = int( geometry.mesh_data.vertex_count, 16 ) * 3  # TODO: strides won't always work like this. Fix in the future
            elif j == 2:
                float_count = int( geometry.mesh_data.vertex_count, 16 ) * 4
            else:
                float_count = int( geometry.mesh_data.vertex_count, 16 ) * 2

            daefile.write( ( TAB * tab_count ) + DAE_STR_FLOAT_ARRAY_TEMPLATE.format( id, float_count ) )

            for k, vertex in enumerate( geometry.vertices ):

                if j == 0:
                    daefile.write( '{0} {1} {2} '.format( vertex.position[0], vertex.position[1], vertex.position[2] ) )
                elif j == 1:
                    daefile.write( '{0} {1} {2} '.format( vertex.normal[0], vertex.normal[1], vertex.normal[2] ) )
                elif j == 2:
                    daefile.write( '1 1 1 1 ' )
                else:
                    daefile.write( '{0} {1} '.format( vertex.uv0[0], 1 - vertex.uv0[1] ) )  # the v coordinate is flipped

            daefile.write( '</float_array>\n' )

            # open technique_common tag
            daefile.write( ( TAB * tab_count ) + '<technique_common>\n' )
            tab_count += 1

            # open accessor tag
            source = "#" + geometry_name + [ "-mesh-position-array", "-mesh-normal-array", "-mesh-color-array", "-texcoord-array" ][j]
            count = int( geometry.mesh_data.vertex_count, 16 )

            stride = [ 3, 3, 4, 2 ][j]

            daefile.write( ( TAB * tab_count ) + DAE_STR_ACCESSOR_TEMPLATE.format( source, count, stride ) + '\n' )
            tab_count += 1

            # param tag
            if j in [0,1]:
                daefile.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "X", "float" ) + '\n')
                daefile.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "Y", "float" ) + '\n')
                daefile.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "Z", "float" ) + '\n')
            elif j == 2:
                daefile.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "R", "float" ) + '\n')
                daefile.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "G", "float" ) + '\n')
                daefile.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "B", "float" ) + '\n')
                daefile.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "A", "float" ) + '\n')
            else:
                daefile.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "S", "float" ) + '\n')
                daefile.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "T", "float" ) + '\n')

            # close accessor tag
            tab_count -= 1
            daefile.write( ( TAB * tab_count ) + '</accessor>\n' )

            # close technique_common tag
            tab_count -= 1
            daefile.write( ( TAB * tab_count ) + '</technique_common>\n' )

            # close source tag (positions)
            tab_count -= 1
            daefile.write( ( TAB * tab_count ) + '</source>\n' )

        
        # vertices
        id = geometry_name + '-mesh-vertex'
        daefile.write( ( TAB * tab_count ) + DAE_STR_VERTICES_TEMPLATE.format( id ) + '\n' )
        tab_count += 1

        source = '#' + geometry_name + '-mesh-position'
        daefile.write( ( TAB * tab_count ) + DAE_STR_INPUT_TEMPLATE.format( "POSITION", source ) + '\n' )

        tab_count -= 1
        daefile.write( ( TAB * tab_count ) + '</vertices>\n' )


        # triangles
        daefile.write( ( TAB * tab_count ) + DAE_STR_TRIANGLES_TEMPLATE.format( len( geometry.faces ) ) + '\n' )
        tab_count += 1

        source = '#' + geometry_name + '-mesh-vertex'
        daefile.write( ( TAB * tab_count ) + DAE_STR_INPUT_TEMPLATE_OFFSET.format( "VERTEX", source, 0 ) + '\n' )
        source = '#' + geometry_name + '-mesh-normal'
        daefile.write( ( TAB * tab_count ) + DAE_STR_INPUT_TEMPLATE_OFFSET.format( "NORMAL", source, 1 ) + '\n' )
        source = '#' + geometry_name + '-mesh-color'
        daefile.write( ( TAB * tab_count ) + DAE_STR_INPUT_TEMPLATE_OFFSET_SET.format( "COLOR", source, 2, 0 ) + '\n' )
        source = '#' + geometry_name + '-mesh-texcoord'
        daefile.write( ( TAB * tab_count ) + DAE_STR_INPUT_TEMPLATE_OFFSET_SET.format( "TEXCOORD", source, 3, 0 ) + '\n' )

        # p tag (array of indices)
        daefile.write( ( TAB * tab_count ) + '<p>' )

        for tri in geometry.faces:

            util.adjust_normals_for_dae( tri, geometry )
            
            for index in tri.indices:
                
                daefile.write( str(index) + ' ' )  # vertex position index
                daefile.write( str(index) + ' ' )  # vertex normal index
                daefile.write( str(index) + ' ' )  # vertex color index
                daefile.write( str(index) + ' ' )  # vertex uv coord index

        daefile.write( '</p>\n' )

        tab_count -= 1
        daefile.write( ( TAB * tab_count ) + '</triangles>\n' )
        


        # close mesh and geometry tags
        tab_count -= 1
        daefile.write( ( TAB * tab_count ) + '</mesh>\n' )

        tab_count -= 1
        daefile.write( ( TAB * tab_count ) + '</geometry>\n' )

    # close library_geometries tag
    tab_count -= 1
    daefile.write( ( TAB * tab_count ) + '</library_geometries>\n' )



    # LIBRARY_VISUAL_SCENES
    daefile.write( ( TAB * tab_count ) + '<library_visual_scenes>\n' )
    tab_count += 1

    # open visual scene tag
    daefile.write( ( TAB * tab_count ) + '<visual_scene id="Scene" name="Scene">\n' )
    tab_count += 1

    for i, geometry in enumerate( model.meshes ):

        # open node tag
        geometry_name = filename_root + "_" + str(i)
        daefile.write( ( TAB * tab_count ) + DAE_STR_NODE_TEMPLATE.format( geometry_name, geometry_name, "NODE" ) + '\n' )
        tab_count += 1

        # open and close matrix tag
        daefile.write( ( TAB * tab_count ) + '<matrix sid="transform">1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1</matrix>\n' )

        # geometry_instance tag
        url = '#' + geometry_name + '-mesh'
        daefile.write( ( TAB * tab_count ) + DAE_STR_INSTANCE_GEOMETRY_TEMPLATE.format( url, geometry_name ) + '\n' )

        # close node tag
        tab_count -= 1
        daefile.write( ( TAB * tab_count ) + '</node>\n' )

    # close visual scene tag
    tab_count -= 1
    daefile.write( ( TAB * tab_count ) + '</visual_scene>\n' )

    # close library_visual_scenes tag
    tab_count -= 1
    daefile.write( ( TAB * tab_count ) + '</library_visual_scenes>\n' )


    # SCENE
    daefile.write( ( TAB * tab_count ) + '<scene>\n' )
    tab_count += 1

    daefile.write( ( TAB * tab_count ) + '<instance_visual_scene url="#Scene"/>\n' )

    tab_count -= 1
    daefile.write( ( TAB * tab_count ) + '</scene>\n' )

    
    # close collada tag (end of file)
    tab_count -= 1
    daefile.write( ( TAB * tab_count ) + '</COLLADA>\n' )

    daefile.close()




# read dae and return a dict of its information
def read_dae( filepath ):

    model3d = m3d.Model3d()

    xmlroot = rlgtool_xml.read_xml( filepath )

    # loop through all geometry tags
    geometry_tags = xmlroot.findall( 'geometry' )
    print( "DEBUG: SBLORG " + str( geometry_tags ) )

    vertex_absolute_id = 0

    for i, geometry_tag in enumerate(geometry_tags):

        # VERTICES
        # find triangles tag
        triangles_tag = geometry_tag.find( 'triangles' )

        # get the ids for the tags we need
        input_vertex_tag = triangles_tag.find( 'input', { 'semantic' : 'VERTEX' } )
        vertices_id = input_vertex_tag.get( 'source' ).replace( '#', '' )
        input_normal_tag = triangles_tag.find( 'input', { 'semantic' : 'NORMAL' } )
        normals_id = input_normal_tag.get( 'source' ).replace( '#', '' )
        input_texcoord_tag = triangles_tag.find( 'input', { 'semantic' : 'TEXCOORD' } )
        texcoords_id = input_texcoord_tag.get( 'source' ).replace( '#', '' )

        # look for the vertices tag
        vertices_tag = geometry_tag.findid( vertices_id )
        
        # get the id of the position and find where it is
        input_tag = vertices_tag.find( 'input', { 'semantic' : 'POSITION' } )
        positions_id = input_tag.get( 'source' ).replace( '#', '' )
        
        # get the array of floats for positions
        source_tag = geometry_tag.findid( positions_id )
        array_of_floats_as_string = source_tag.find( 'float_array' ).content
        vertex_positions = str_to_num_list( array_of_floats_as_string, 3 )

        # get the array of floats for normals
        source_tag = geometry_tag.findid( normals_id )
        array_of_floats_as_string = source_tag.find( 'float_array' ).content
        vertex_normals = str_to_num_list( array_of_floats_as_string, 3 )

        # get the array of floats for uv coordinates
        source_tag = geometry_tag.findid( texcoords_id )
        array_of_floats_as_string = source_tag.find( 'float_array' ).content
        vertex_uvs = str_to_num_list( array_of_floats_as_string, 2 )

        vertices = []

        for j, vertex_position in enumerate(vertex_positions):
            vertex_absolute_id += 1
            new_vertex =  m3d.Vertex( vertex_absolute_id, j, 0, i, vertex_position, vertex_normals[j],
                                            vertex_uvs[j], 0, 0, 0, 0, 0, [0,0,0,0], [0,0,0,0] )
            
            vertices.append( new_vertex )

        print( "DEBUG: verts=" + str( vertices ) )


        # TRIANGLES
        array_of_ints_as_string = triangles_tag.find( 'p' ).content
        triangles = str_to_num_list( array_of_ints_as_string, 3, True )
        # TODO: finish this

        new_mesh = ( [], [], [], vertices, [] )

        model3d.meshes.append( new_mesh )

    print( "DEBUG: " + str( model3d ) )
    return model3d


def str_to_num_list( string, stride = 1, to_integer = False ):

    list_of_strings_raw = string.split(' ')
    list_of_strings = []

    # delete any empty string
    for string in list_of_strings_raw:
        if len(string) != 0:
            list_of_strings.append( string )
            

    list_of_numbers = []

    sublist = []

    for i, string in enumerate(list_of_strings):

        number = int( string, 10 ) if to_integer else float( string ) 

        if stride == 1:
            list_of_numbers.append( number )
        
        else:
            sublist.append( number )
            
            if i % stride == stride-1:
                list_of_numbers.append( sublist )
                sublist = []

    return list_of_numbers


