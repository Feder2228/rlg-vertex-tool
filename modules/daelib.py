import xmllib, util

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


def create_dae( model, filename_root ):

    filename = filename_root
    dae = open( DIR_PATH_OUTPUT + filename + ".dae", "w" )  # TODO: this function shouldn't have access to this constant. The full path should be passed as argument, or the file should

    dae.write( DAE_STR_HEADER + '\n' )

    TAB = "  "
    tab_count = 1
    


    # LIBRARY_GEOMETRIES
    dae.write( ( TAB * tab_count ) + '<library_geometries>\n' )
    tab_count += 1

    for i, geometry in enumerate( model['meshes'] ):

        # open geometry tag
        geometry_name = filename_root + "_" + str(i)
        id = geometry_name + '-mesh'
        dae.write( ( TAB * tab_count ) + DAE_STR_GEOMETRY_TEMPLATE.format( id, geometry_name ) + '\n' )
        tab_count += 1
        
        # open mesh tag
        dae.write( ( TAB * tab_count ) + '<mesh>\n' )
        tab_count += 1

        # iteration 0 is for positions, 1 is for normals, 2 is for vertex colors, 3 is for uv coords
        for j in range(4):
            
            # open source tag
            id = geometry_name + ['-mesh-position', '-mesh-normal', '-mesh-color', '-mesh-texcoord' ][j]
            dae.write( ( TAB * tab_count ) + DAE_STR_SOURCE_TEMPLATE.format( id ) + '\n' )
            tab_count += 1

            # open and close float array tag
            id = geometry_name + ['-mesh-position', '-mesh-normal', '-mesh-color', '-mesh-texcoord' ][j] + '-array'

            if j in [0,1]:
                float_count = int( geometry['mesh_data']['vertex_count'], 16 ) * 3  # TODO: strides won't always work like this. Fix in the future
            elif j == 2:
                float_count = int( geometry['mesh_data']['vertex_count'], 16 ) * 4
            else:
                float_count = int( geometry['mesh_data']['vertex_count'], 16 ) * 2

            dae.write( ( TAB * tab_count ) + DAE_STR_FLOAT_ARRAY_TEMPLATE.format( id, float_count ) )

            for k, vertex in enumerate( geometry['vertices'] ):

                if j == 0:
                    dae.write( '{0} {1} {2} '.format( vertex['position'][0], vertex['position'][1], vertex['position'][2] ) )
                elif j == 1:
                    dae.write( '{0} {1} {2} '.format( vertex['normal'][0], vertex['normal'][1], vertex['normal'][2] ) )
                elif j == 2:
                    dae.write( '1 1 1 1 ' )
                else:
                    dae.write( '{0} {1} '.format( vertex['uv0'][0], 1 - vertex['uv0'][1] ) )  # the v coordinate is flipped

            dae.write( '</float_array>\n' )

            # open technique_common tag
            dae.write( ( TAB * tab_count ) + '<technique_common>\n' )
            tab_count += 1

            # open accessor tag
            source = "#" + geometry_name + [ "-mesh-position-array", "-mesh-normal-array", "-mesh-color-array", "-texcoord-array" ][j]
            count = int( geometry['mesh_data']['vertex_count'], 16 )

            if j in [0,1]:
                stride = 3
            elif j == 2:
                stride = 4
            else:
                stride = 2

            dae.write( ( TAB * tab_count ) + DAE_STR_ACCESSOR_TEMPLATE.format( source, count, stride ) + '\n' )
            tab_count += 1

            # param tag
            if j in [0,1]:
                dae.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "X", "float" ) + '\n')
                dae.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "Y", "float" ) + '\n')
                dae.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "Z", "float" ) + '\n')
            elif j == 2:
                dae.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "R", "float" ) + '\n')
                dae.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "G", "float" ) + '\n')
                dae.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "B", "float" ) + '\n')
                dae.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "A", "float" ) + '\n')
            else:
                dae.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "S", "float" ) + '\n')
                dae.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "T", "float" ) + '\n')

            # close accessor tag
            tab_count -= 1
            dae.write( ( TAB * tab_count ) + '</accessor>\n' )

            # close technique_common tag
            tab_count -= 1
            dae.write( ( TAB * tab_count ) + '</technique_common>\n' )

            # close source tag (positions)
            tab_count -= 1
            dae.write( ( TAB * tab_count ) + '</source>\n' )

        
        # vertices
        id = geometry_name + '-mesh-vertex'
        dae.write( ( TAB * tab_count ) + DAE_STR_VERTICES_TEMPLATE.format( id ) + '\n' )
        tab_count += 1

        source = '#' + geometry_name + '-mesh-position'
        dae.write( ( TAB * tab_count ) + DAE_STR_INPUT_TEMPLATE.format( "POSITION", source ) + '\n' )

        tab_count -= 1
        dae.write( ( TAB * tab_count ) + '</vertices>\n' )


        # triangles
        dae.write( ( TAB * tab_count ) + DAE_STR_TRIANGLES_TEMPLATE.format( len( geometry['faces'] ) ) + '\n' )
        tab_count += 1

        source = '#' + geometry_name + '-mesh-vertex'
        dae.write( ( TAB * tab_count ) + DAE_STR_INPUT_TEMPLATE_OFFSET.format( "VERTEX", source, 0 ) + '\n' )
        source = '#' + geometry_name + '-mesh-normal'
        dae.write( ( TAB * tab_count ) + DAE_STR_INPUT_TEMPLATE_OFFSET.format( "NORMAL", source, 1 ) + '\n' )
        source = '#' + geometry_name + '-mesh-color'
        dae.write( ( TAB * tab_count ) + DAE_STR_INPUT_TEMPLATE_OFFSET_SET.format( "COLOR", source, 2, 0 ) + '\n' )
        source = '#' + geometry_name + '-mesh-texcoord'
        dae.write( ( TAB * tab_count ) + DAE_STR_INPUT_TEMPLATE_OFFSET_SET.format( "TEXCOORD", source, 3, 0 ) + '\n' )

        # p tag (array of indices)
        dae.write( ( TAB * tab_count ) + '<p>' )

        for tri in geometry['faces']:

            util.adjust_normals_for_dae( tri, geometry )
            
            for index in tri:
                
                dae.write( str(index) + ' ' )  # vertex position index
                dae.write( str(index) + ' ' )  # vertex normal index
                dae.write( str(index) + ' ' )  # vertex color index
                dae.write( str(index) + ' ' )  # vertex uv coord index

        dae.write( '</p>\n' )

        tab_count -= 1
        dae.write( ( TAB * tab_count ) + '</triangles>\n' )
        


        # close mesh and geometry tags
        tab_count -= 1
        dae.write( ( TAB * tab_count ) + '</mesh>\n' )

        tab_count -= 1
        dae.write( ( TAB * tab_count ) + '</geometry>\n' )

    # close library_geometries tag
    tab_count -= 1
    dae.write( ( TAB * tab_count ) + '</library_geometries>\n' )



    # LIBRARY_VISUAL_SCENES
    dae.write( ( TAB * tab_count ) + '<library_visual_scenes>\n' )
    tab_count += 1

    # open visual scene tag
    dae.write( ( TAB * tab_count ) + '<visual_scene id="Scene" name="Scene">\n' )
    tab_count += 1

    for i, geometry in enumerate( model['meshes'] ):

        # open node tag
        geometry_name = filename_root + "_" + str(i)
        dae.write( ( TAB * tab_count ) + DAE_STR_NODE_TEMPLATE.format( geometry_name, geometry_name, "NODE" ) + '\n' )
        tab_count += 1

        # open and close matrix tag
        dae.write( ( TAB * tab_count ) + '<matrix sid="transform">1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1</matrix>\n' )

        # geometry_instance tag
        url = '#' + geometry_name + '-mesh'
        dae.write( ( TAB * tab_count ) + DAE_STR_INSTANCE_GEOMETRY_TEMPLATE.format( url, geometry_name ) + '\n' )

        # close node tag
        tab_count -= 1
        dae.write( ( TAB * tab_count ) + '</node>\n' )

    # close visual scene tag
    tab_count -= 1
    dae.write( ( TAB * tab_count ) + '</visual_scene>\n' )

    # close library_visual_scenes tag
    tab_count -= 1
    dae.write( ( TAB * tab_count ) + '</library_visual_scenes>\n' )


    # SCENE
    dae.write( ( TAB * tab_count ) + '<scene>\n' )
    tab_count += 1

    dae.write( ( TAB * tab_count ) + '<instance_visual_scene url="#Scene"/>\n' )

    tab_count -= 1
    dae.write( ( TAB * tab_count ) + '</scene>\n' )

    
    # close collada tag (end of file)
    tab_count -= 1
    dae.write( ( TAB * tab_count ) + '</COLLADA>\n' )

    dae.close()




# read dae and return a dict of its information
def read_dae( dae ):

    dict_thing = {  # TODO: use a custom class instead of dict
        'matrix' : [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],
        'model_data' : None, 
        'meshes' : []
    }

    # generic element of meshes:
    #    {
    #        "mesh_data" :                      # raw mesh data
    #        "index_data" :                     # raw index data (0 based, vertex ids are relative to beginning of mesh/group)
    #        "vertex_attributes" :              # raw vertex attribute data
    #        "vertices" :                       # processed vertices
    #        "faces" :                          # processed faces (0 based, vertex ids are relative to beginning of mesh/group)
    #    }

    xml_root_node = xmllib.get_xml_tree( dae )

    # loop through all geometry tags
    geometry_tags = xml_root_node.find_all_nodes( 'geometry' )

    vertex_absolute_id = 0

    for i, geometry_tag in enumerate(geometry_tags):

        # VERTICES
        # find triangles tag
        triangles_tag = geometry_tag.find_node( 'triangles' )

        # get the ids for the tags we need
        input_vertex_tag = triangles_tag.find_node( 'input', { 'semantic' : 'VERTEX' } )
        vertices_id = input_vertex_tag.attributes[ 'source' ].replace( '#', '' )
        input_normal_tag = triangles_tag.find_node( 'input', { 'semantic' : 'NORMAL' } )
        normals_id = input_normal_tag.attributes[ 'source' ].replace( '#', '' )
        input_texcoord_tag = triangles_tag.find_node( 'input', { 'semantic' : 'TEXCOORD' } )
        texcoords_id = input_texcoord_tag.attributes[ 'source' ].replace( '#', '' )

        # look for the vertices tag
        vertices_tag = geometry_tag.find_node( None, { 'id' : vertices_id } )
        
        # get the id of the position and find where it is
        input_tag = vertices_tag.find_node( 'input', { 'semantic' : 'POSITION' } )
        positions_id = input_tag.attributes[ 'source' ].replace( '#', '' )
        
        # get the array of floats for positions
        source_tag = geometry_tag.find_node( None, { 'id' : positions_id } )
        array_of_floats_as_string = source_tag.find_node( 'float_array' ).content
        vertex_positions = convert_string_to_list_of_numbers( array_of_floats_as_string, 3 )

        # get the array of floats for normals
        source_tag = geometry_tag.find_node( None, { 'id' : normals_id } )
        array_of_floats_as_string = source_tag.find_node( 'float_array' ).content
        vertex_normals = convert_string_to_list_of_numbers( array_of_floats_as_string, 3 )

        # get the array of floats for uv coordinates
        source_tag = geometry_tag.find_node( None, { 'id' : texcoords_id } )
        array_of_floats_as_string = source_tag.find_node( 'float_array' ).content
        vertex_uvs = convert_string_to_list_of_numbers( array_of_floats_as_string, 2 )

        vertices = []

        for j, vertex_position in enumerate(vertex_positions):
            vertex_absolute_id += 1
            vertex =  {
                    "absolute_id" : vertex_absolute_id,       # id TODO
                    "relavtive_id" : j,      # id (relative to the start of the group)
                    "offset" : 0,           # TODO
                    "group" : i,
                    "position" : vertex_position,
                    "normal" : vertex_normals[j],
                    "uv0" : vertex_uvs[j],
                    "attribute_0xed" : 0,
                    "attribute_0x52" : 0,
                    "attribute_0xc0" : 0,
                    "attribute_0xd6" : 0,
                    "attribute_0xd7" : 0,
                    "bone_ids" : [0,0,0,0],
                    "bone_weights" : [0,0,0,0],
                }
            
            vertices.append( vertex )


        # TRIANGLES
        array_of_ints_as_string = triangles_tag.find_node( 'p' ).content
        triangles = convert_string_to_list_of_numbers( array_of_ints_as_string, 3, True )
        # TODO: finish this

        print(  )
            

        mesh_dict_thing = {
            "mesh_data" : [],                     # raw mesh data
            "index_data" : [],                    # raw index data (0 based, vertex ids are relative to beginning of mesh/group)
            "vertex_attributes" : [],             # raw vertex attribute data
            "vertices" : vertices,                     # processed vertices
            "faces" : []  
        }

        dict_thing['meshes'].append( mesh_dict_thing )

    print( "DEBUG: DICT: " + str(dict_thing) )
    return dict_thing


def convert_string_to_list_of_numbers( string, stride = 1, to_integer = False ):

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