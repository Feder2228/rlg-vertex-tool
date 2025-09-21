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

# DIRECTORT PATHS
DIR_PATH_OUTPUT = "output/"
DIR_PATH_INPUT_NLG_FORMATS = "rlg/"
DIR_PATH_INPUT_COMMON_FORMATS = "obj/"

# PROMPT STRINGS
PROMPT_STR_BASE_COMMANDS = '''-- Select a command --
    e - extract data from .rlg (save as .obj)
    g - generate new .rlg (use original .rlg plus a modified .obj)
    x - exit
    help - more info      
'''
PROMPT_STR_HELP = '''
    REGULAR COMMANDS:

    e
    Takes all the .rlg files it finds in the "rlg" folder, reads their data, then for each of them it creates a .obj file containing the vertices and faces (separated by group).
    For 3D model mods, import this .obj file in a program like blender, move the vertices around (but do NOT add/remove any!), then export it and save it to the obj folder, than use the g command
    
    g
    Takes all the .rlg files it finds in the "rlg" folder and for each of them it searches the "obj" folder for an .obj file that has the same name.
    For each file it finds the .obj of, it reads the vertices of the .obj and overwrites the .rlg's vertices with those.
    (Saves the modified .rlg as a copy in the "output" folder. The original .rlg won't be modified)
              
    
    DEV COMMANDS:

    es 
    Same as "e" command, but each group (mesh) is saved in a different .obj file (for dev purposes only. Those objs can't be used to recreate an .rlg file)

    d
    Create a .txt file containing various data about each group (mesh) of the .rlg file. The .txt will be saved in the "output" folder.
'''

# DAE STRINGS
DAE_STR_HEADER = '''<?xml version="1.0" encoding="utf-8"?>
<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <asset/>'''
DAE_STR_GEOMETRY_TEMPLATE = '<geometry id="{0}" name="{1}">'
DAE_STR_SOURCE_TEMPLATE = '<source id="{0}">'
DAE_STR_FLOAT_ARRAY_TEMPLATE = '<float_array id="{0}" count="{1}">'
DAE_STR_ACCESSOR_TEMPLATE = '<accessor source="{0}" count="{1}" stride="{2}">'
DAE_STR_PARAM_TEMPLATE = '<param name="{0}" type="{1}" />'
DAE_STR_NODE_TEMPLATE = '<node id="{0}" name="{1}" type="{2}">'
DAE_STR_INSTANCE_GEOMETRY_TEMPLATE = '<instance_geometry url="{0}" name="{1}"/>'



# RLG UTILITY FUNCTIONS
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
            position = [ bytes_to_float( rlg.read(4) ),  
                         bytes_to_float( rlg.read(4) ), 
                         bytes_to_float( rlg.read(4) ) ]
           
            offset = vertex_attributes[ i*10 + 1 ]['offset']
            rlg.seek( start_of_data + offset + (j*12), 0 )
            normal = [ bytes_to_float( rlg.read(4) ),  
                       bytes_to_float( rlg.read(4) ), 
                       bytes_to_float( rlg.read(4) ) ]
            
            offset = vertex_attributes[ i*10 + 2 ]['offset']
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xcc = [ bytes_to_float( rlg.read(4) ) ]

            offset = vertex_attributes[ i*10 + 3 ]['offset']
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xed = [ bytes_to_float( rlg.read(4) ) ]

            offset = vertex_attributes[ i*10 + 4 ]['offset']
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0x52 = [ bytes_to_float( rlg.read(4) ) ]

            offset = vertex_attributes[ i*10 + 5 ]['offset']
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xc0 = [ bytes_to_float( rlg.read(4) ) ]

            offset = vertex_attributes[ i*10 + 6 ]['offset']
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xd6 = [ bytes_to_float( rlg.read(4) ) ]

            offset = vertex_attributes[ i*10 + 7 ]['offset']
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xd7 = [ bytes_to_float( rlg.read(4) ) ]

            offset = vertex_attributes[ i*10 + 8 ]['offset']
            rlg.seek( start_of_data + offset + (j*4), 0 )
            attribute_0xd4 = [ bytes_to_float( rlg.read(4) ) ]

            offset = vertex_attributes[ i*10 + 9 ]['offset']
            rlg.seek( start_of_data + offset + (j*16), 0 )
            attribute_0xb0 = [ bytes_to_float( rlg.read(4) ),  
                               bytes_to_float( rlg.read(4) ), 
                               bytes_to_float( rlg.read(4) ),
                               bytes_to_float( rlg.read(4) ) ]

            a.append( {
                "absolute_id" : absolute_id,       # id
                "relavtive_id" : relative_id,      # id (relative to the start of the group)
                "offset" : current_byte,           # TODO: should I remove this?
                "group" : i,
                "position" : position,
                "normal" : normal,
                "attribute_0xcc" : attribute_0xcc,
                "attribute_0xed" : attribute_0xed,
                "attribute_0x52" : attribute_0x52,
                "attribute_0xc0" : attribute_0xc0,
                "attribute_0xd6" : attribute_0xd6,
                "attribute_0xd7" : attribute_0xd7,
                "attribute_0xd4" : attribute_0xd4,
                "attribute_0xb0" : attribute_0xb0,
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

            matrix_row.append( bytes_to_float( rlg.read(4) ) )
        
        matrix.append( matrix_row )


    return matrix





# Get a dict with various data from an rlg file
# Still WIP. Currently structured like this:
# Dict that has the following keys: "model_data", "meshes"
# "meshes" is a list of dicts, each of which contain data of a group/mesh: "mesh_data", "index_data", "vertex_attributes", "vertices", "faces"
# For more info look at the comments next to the last "append" in this function
def get_rlg_dict(rlg):

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




# Create obj file, given an rlg file
def create_obj( rlg, split_files_by_group = False ):

    # take the filename, but remove the ".rlg" part
    filename_root = os.path.basename( rlg.name ).split(".")[0]

    # create the file (single file mode)
    if( not split_files_by_group ):
        filename = filename_root
        obj = open( DIR_PATH_OUTPUT + filename + ".obj", "w" )

    groups = get_rlg_dict( rlg )['meshes']


    # iterate on all the rlg's groups (meshes) and save their data in obj format
    for group, group_data in enumerate( groups ):

        # create the file (multi-file mode)
        if( split_files_by_group ):
            filename = filename_root + "_" + str(group)
            obj = open( DIR_PATH_OUTPUT + filename + ".obj", "w" )


        # Write the number of group
        obj.write( "g group " + str( group ) + "\n" )


        # Write the vertices of this group. In the .obj format, each vertex is a "v" follwed by the XYZ coordinates
        for vertex in group_data['vertices']: 
            obj.write( "v " + str( vertex["position"][0] ) + " " + str( vertex["position"][1] ) + " " + str( vertex["position"][2] ) + "\n" )
        

        # Write the faces of this group 
        first_vertex_identifier_of_group = group_data['vertices'][0]['absolute_id']  # get the absolute ID of the first vertex of the group

        for face in group_data['faces']:

            obj.write( "f " )  # write "f", which identifies a face in a .obj file    

            for relative_index in face:  # write the IDs of the vertices that make up the face

                # unlike for .rlg, in a .obj file, the IDs of the vertices aren't relative to their group (they don't reset on each group), so we must convert to absolute index
                # that is unless we're splitting files by group. In that case we just use the relative_index
                # also in a .obj file the first vertex has an ID of 1 (instead of 0 like .rlg), so we must add 1
                if( split_files_by_group ):
                    obj.write( str( relative_index + 1 ) + " " )  # write relative index + 1
                else: 
                    obj.write( str( first_vertex_identifier_of_group + relative_index + 1 ) + " " )  # write absolute index + 1

            obj.write( "\n" )


        # save the file (multi-file mode)
        if( split_files_by_group ):
            print(filename + ".obj was successfully created in output folder")
            obj.close()


    # save the file (single file mode)
    if( not split_files_by_group ):
        print(filename + ".obj was successfully created in output folder")
        obj.close()




def create_dae( model, filename_root ):

    filename = filename_root
    dae = open( DIR_PATH_OUTPUT + filename + ".dae", "w" )

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

        # open source tag - vertex positions of geometry
        id = geometry_name + '-mesh-position'
        dae.write( ( TAB * tab_count ) + DAE_STR_SOURCE_TEMPLATE.format( id ) + '\n' )
        tab_count += 1

        # float array for vertex positions
        id = geometry_name + '-mesh-position-array'
        float_count = int( geometry['mesh_data']['vertex_count'], 16 ) * geometry['vertex_attributes'][0]['stride']//4
        dae.write( ( TAB * tab_count ) + DAE_STR_FLOAT_ARRAY_TEMPLATE.format( id, float_count ) )

        for j, vertex in enumerate( geometry['vertices'] ):
            position = vertex['position']
            dae.write( '{0} {1} {2} '.format( position[0], position[1], position[2] ) )

        dae.write( '</float_array>\n' )

        # open technique_common tag
        dae.write( ( TAB * tab_count ) + '</technique_common>\n' )
        tab_count += 1

        # open accessor tag
        source = "#" + geometry_name + "-mesh-position-array"
        count = int( geometry['mesh_data']['vertex_count'], 16 )
        stride = geometry['vertex_attributes'][0]['stride']//4
        dae.write( ( TAB * tab_count ) + DAE_STR_ACCESSOR_TEMPLATE.format( source, count, stride ) + '\n' )
        tab_count += 1

        # param tags
        dae.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "X", "float" ) + '\n')
        dae.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "Y", "float" ) + '\n')
        dae.write( ( TAB * tab_count ) + DAE_STR_PARAM_TEMPLATE.format( "Z", "float" ) + '\n')

        # close accessor tag
        tab_count -= 1
        dae.write( ( TAB * tab_count ) + '</accessor>\n' )

        # close technique_common tag
        tab_count -= 1
        dae.write( ( TAB * tab_count ) + '</technique_common>\n' )

        # close source tag (positions)
        tab_count -= 1
        dae.write( ( TAB * tab_count ) + '</source>\n' )

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




def get_vertices_from_obj(filename):
    print("filename: " +filename)
    obj = open( DIR_PATH_INPUT_COMMON_FORMATS + filename + ".obj", "r" )
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
    




# FUNCTIONS THAT PRINT DATA TO TXT FILE
def print_misc_data_to_file(rlg):

    filename = os.path.basename(rlg.name)
    data = get_rlg_dict(rlg)

    txt = open( DIR_PATH_OUTPUT + filename + "_miscdata.txt", "w" )

    txt.write( "4x4 MATRIX:\n" )
    for row in data['matrix']:
        txt.write( str( row ) + "\n" )
    txt.write( "\n" )

    txt.write( "MODEL DATA:\n" )
    txt.write( str( data['model_data'] ) + "\n\n" )

    txt.write( "ALL MESH DATA:\n" )
    for d in data['meshes']:
        txt.write( str(d['mesh_data'] ) + "\n" )
    txt.write( "\n\n\n\n" )

    for i, d in enumerate( data['meshes'] ):

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
            txt.write( str( e['position'] ) + "\n" )
            txt.write( str( e['normal'] ) + "\n" )
            txt.write( str( e['attribute_0xcc'] ) + "\n" )
            txt.write( str( e['attribute_0xed'] ) + "\n" )
            txt.write( str( e['attribute_0x52'] ) + "\n" )
            txt.write( str( e['attribute_0xc0'] ) + "\n" )
            txt.write( str( e['attribute_0xd6'] ) + "\n" )
            txt.write( str( e['attribute_0xd7'] ) + "\n" )
            txt.write( str( e['attribute_0xd4'] ) + "\n" )
            txt.write( str( e['attribute_0xb0'] ) + "\n" )
            txt.write( "\n" )

        txt.write( "\n\nFACES:\n" )
        for e in d['faces']:
            txt.write( str(e) + "\n" )
        txt.write("\n\n\n\n\n\n\n\n")

    txt.close()
    print(filename+"_miscdata.txt file successfully created in output folder")



# START OF CODE
while True:
    r = input("\n\n" +PROMPT_STR_BASE_COMMANDS+ "\n\n")

    # Check if response is exit
    if(r == "x"):
        exit()

    filenames = get_all_rlg_filenames()


    # check response and execute if it's a valid command
    if(r == "e"):
        for i in filenames:
            rlg = open( DIR_PATH_INPUT_NLG_FORMATS + i, "rb" )
            create_obj( rlg )
            rlg.close()

    elif(r == "g"):
        for i in filenames:
            rlg = open( DIR_PATH_INPUT_NLG_FORMATS + i, "rb" )
            generate_new_rlg( rlg )
            rlg.close()

    elif(r == "es"):
        for i in filenames:
            rlg = open( DIR_PATH_INPUT_NLG_FORMATS + i, "rb" )
            create_obj( rlg, split_files_by_group=True )
            rlg.close()
        
    elif(r == "d"):
        for i in filenames:
            rlg = open( DIR_PATH_INPUT_NLG_FORMATS + i, "rb" )
            print_misc_data_to_file( rlg )
            rlg.close()

    elif(r == "dae"):
        for i in filenames:
            rlg = open( DIR_PATH_INPUT_NLG_FORMATS + i, "rb" )
            create_dae( get_rlg_dict(rlg), i.split(".")[0] )
    
    elif(r == "help"):
        print( PROMPT_STR_HELP + "\n")

    else:
        print("invalid input")
        
    input("Press Enter to continue...")