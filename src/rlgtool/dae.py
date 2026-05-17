import re
from .rlg_data_structures import *
from . import util
from .federxml import *
from . import nlgutil


REGEX_HASHID = r'(?<=_hashid0x)[0-9a-f]+'
REGEX_BONE = r'(?<=bone_)[0-9a-f]+'


def create_dae(rlgroot : RlgRoot, filepath : str, bone_tree_mode=False):
    """Create dae file
    Args:
        rlgroot: RlgRoot to create the file for
        filepath: path of the file to create
        bone_tree_mode: if true, the bones will be organized in a tree structure
    """
    filepath = filepath.replace('\\', '/')
    filename_root = filepath.split( "/" )[-1].split(".")[0]  # TODO: use some other method for this. Perhaps from some library like os.
    
    xmlroot = XmlNode(name='COLLADA', attributes={'xmlns' : "http://www.collada.org/2005/11/COLLADASchema", 'version' : "1.4.1",
                                                        'xmlns:xsi' : "http://www.w3.org/2001/XMLSchema-instance"})
    
    # Write the .dae file sections into the XmlNode object
    write_section_asset(xmlroot)
    write_section_library_effects(xmlroot, rlgroot, filename_root)
    write_section_library_images(xmlroot, rlgroot, filename_root)
    write_section_library_materials(xmlroot, rlgroot, filename_root)
    write_section_library_geometries(xmlroot, rlgroot, filename_root)
    write_section_library_controllers(xmlroot, rlgroot, filename_root)
    write_section_library_visual_scenes(xmlroot, rlgroot, filename_root, bone_tree_mode=bone_tree_mode)
    write_section_scene(xmlroot)

    # Create a file using the XmlNode object
    create_xml(filepath=filepath, xmlnode=xmlroot)




def get_image_base_name(texture_hash):
    """get the base name (no extension) that the texture file would have
    if extracted by rltool

    Args:
        texture_hash: hash referencing the texture in the game files
    """
    return hex(texture_hash).replace('0x', '') + '_enc_6'




def get_image_id(texture_hash):
    """base name of image + '_png'

    Args:
        texture_hash: hash referencing the texture in the game files
    """
    return get_image_base_name(texture_hash) + '_png'




def get_image_file_name(texture_hash):
    """get name that full name (including extension) that the texture file
    would have if extracted by rltool

    Args:
        texture_hash: hash referencing the texture in the game files
    """
    return get_image_base_name(texture_hash) + '.png'




def get_material_id(texture_hash):
    """get material id

    Args:
        texture_hash: hash referencing the texture in the game files
    """
    return get_image_base_name(texture_hash) + '-material'




def get_effect_id(texture_hash):
    """get effect id

    Args:
        texture_hash: hash referencing the texture in the game files
    """
    return get_image_base_name(texture_hash) + '-effect'




def get_surface_id(texture_hash):
    """get surface id

    Args:
        texture_hash: hash referencing the texture in the game files
    """
    return get_image_id(texture_hash) + '-surface'




def get_sampler_id(texture_hash):
    """get sampler id

    Args:
        texture_hash: hash referencing the texture in the game files
    """
    return get_image_id(texture_hash) + '-sampler'




def get_mesh_id(filename_root, mesh_hash):
    """get mesh id

    Args:
        texture_hash: hash referencing the texture in the game files
    """ 
    return filename_root + "_hashid" + hex(mesh_hash) + '-mesh'




def get_mesh_field_id(filename_root, mesh_hash, field : str):
    """get mesh id

    Args:
        texture_hash: hash referencing the texture in the game files
    """ 
    return get_mesh_id(filename_root, mesh_hash) + '-' + field




def get_mesh_field_array_id(filename_root, mesh_hash, field : str):
    """get mesh id

    Args:
        texture_hash: hash referencing the texture in the game files
    """ 
    return get_mesh_field_id(filename_root, mesh_hash, field) + '-array'




def get_armature_id(filename_root, mesh_hash):
    """get mesh id

    Args:
        texture_hash: hash referencing the texture in the game files
    """ 
    return "Armature_" + get_mesh_id(filename_root, mesh_hash) + '-skin'




def get_armature_field_id(filename_root, mesh_hash, field : str):
    """get armature id

    Args:
        texture_hash: hash referencing the texture in the game files
    """ 
    return get_armature_id(filename_root, mesh_hash) + '-' + field




def get_armature_field_array_id(filename_root, mesh_hash, field : str):
    """get armature id

    Args:
        texture_hash: hash referencing the texture in the game files
    """ 
    return get_armature_field_id(filename_root, mesh_hash, field) + '-array'




def get_bone_id(bone_hash):
    """get bone id

    Args:
        bone_hash: hash referencing the texture in the game files
    """
    #hashid_file = open('../other/hashid.bin', 'rb') 
    #return nlgutil.get_hash_name(binfile=hashid_file, hash=bone_hash).replace(' ', '_')
    return 'bone_' + hex(bone_hash).replace('0x', '')




def get_armature_bone_id(bone_hash):
    """get bone id

    Args:
        bone_hash: hash referencing the texture in the game files
    """ 
    return 'Armature_' + get_bone_id(bone_hash)



def write_section_asset(root : XmlNode):
    """Write the asset section to an XmlNode object

    This methods mutates root

    Args:
        root: XmlNode, root of the dae file
    """
    root.append_child(XmlNode('asset', has_body=False))




def write_section_library_effects(root : XmlNode, rlgroot : RlgRoot, filename_root : str):
    """Write the library_effects section to an XmlNode object

    This methods mutates root

    Args:
        root: XmlNode, root of the dae file
    """
    # First, get the list of textures that will appear in the file
    texture_hashes = rlgroot.models[0].get_main_texture_hashes()
    # Now write the XML structure
    library_effects = root.append_child(XmlNode('library_effects'))
    for texture_hash in texture_hashes:
        effect = library_effects.append_child(XmlNode('effect', attributes={'id' : get_effect_id(texture_hash)}))
        profile_common = effect.append_child(XmlNode('profile_COMMON'))
        # newparam (surface)
        newparam_1 = profile_common.append_child(XmlNode('newparam', attributes={'sid' : get_surface_id(texture_hash)}))
        surface = newparam_1.append_child(XmlNode('surface', attributes={'type' : '2D'}))
        surface.append_child(XmlNode('init_from', content=get_image_id(texture_hash)))
        # newparam (sampler2D)
        newparam_2 = profile_common.append_child(XmlNode('newparam', attributes={'sid' : get_sampler_id(texture_hash)}))
        sampler2D = newparam_2.append_child(XmlNode('sampler2D'))
        sampler2D.append_child(XmlNode('source', content=get_surface_id(texture_hash)))
        # technique
        technique = profile_common.append_child(XmlNode('technique', attributes={'sid' : 'common'}))
        lambert = technique.append_child(XmlNode('lambert'))
        emission = lambert.append_child(XmlNode('emission'))
        emission.append_child(XmlNode('color', attributes={'sid' : 'emission'}, content='0 0 0 1'))
        diffuse = lambert.append_child(XmlNode('diffuse'))
        diffuse.append_child(XmlNode('texture', attributes={'texture' : get_sampler_id(texture_hash), 'texcoord' : 'UV0'}, has_body=False))
        index_of_refraction = lambert.append_child(XmlNode('index_of_refraction'))
        index_of_refraction.append_child(XmlNode('float', attributes={'sid' : 'ior'}, content='1.5'))




def write_section_library_images(root : XmlNode, rlgroot : RlgRoot, filename_root : str):
    """Write the library_images section to an XmlNode object

    This methods mutates root

    Args:
        root: XmlNode, root of the dae file
    """
    # First, get the list of textures that will appear in the file
    texture_hashes = rlgroot.models[0].get_main_texture_hashes()
    # Now write the XML structure
    library_images = root.append_child(XmlNode('library_images'))
    for texture_hash in texture_hashes:
        image = library_images.append_child(XmlNode('image', attributes={'id' : get_image_id(texture_hash), 'name' : get_image_id(texture_hash)}))
        image.append_child(XmlNode('init_from', content=get_image_file_name(texture_hash)))




def write_section_library_materials(root : XmlNode, rlgroot : RlgRoot, filename_root : str):
    """Write the library_images section to an XmlNode object

    This methods mutates root

    Args:
        root: XmlNode, root of the dae file
    """
    texture_hashes = rlgroot.models[0].get_main_texture_hashes()
    # Now write the XML structure
    library_materials = root.append_child(XmlNode('library_materials'))
    for texture_hash in texture_hashes:
        material = library_materials.append_child(XmlNode('material', attributes={'id' : get_material_id(texture_hash), 'name' : get_material_id(texture_hash)}))
        material.append_child(XmlNode('instance_effect', attributes={'url' : '#' + get_effect_id(texture_hash)}, has_body=False))




def write_section_library_geometries(root : XmlNode, rlgroot : RlgRoot, filename_root : str):
    """Write the library_geometries section to an XmlNode object

    This methods mutates root

    Args:
        root: XmlNode, root of the dae file
    """
    library_geometries = root.append_child(XmlNode('library_geometries'))

    for i, rlgmesh in enumerate(rlgroot.models[0].meshes):
        # open geometry tag
        # the geometry will have an id attribute that contains the "mesh_hash_id" value
        # this will be helpful to keep track of which mesh is which
        id = get_mesh_id(filename_root, rlgmesh.hash_id)
        geometry = library_geometries.append_child(XmlNode('geometry', attributes={'id' : id, 'name' : id}))
        
        # open mesh tag
        mesh = geometry.append_child(XmlNode('mesh'))

        # iteration 0 is for positions, 1 is for normals, 2 is for vertex colors, 3 is for uv coords
        for j, field in enumerate(['position', 'normal', 'color', 'texcoord' ]):
            # open source tag
            id = get_mesh_field_id(filename_root, rlgmesh.hash_id, field)
            source = mesh.append_child(XmlNode('source', attributes={'id' : id}))

            # open and close float array tag
            id = get_mesh_field_array_id(filename_root, rlgmesh.hash_id, field)

            if j in [0,1]:
                float_count = rlgmesh.vertex_count * 3  # TODO: strides won't always work like this. Fix in the future
            elif j == 2:
                float_count = rlgmesh.vertex_count * 4
            else:
                float_count = rlgmesh.vertex_count * 2

            float_array = source.append_child(XmlNode('float_array', attributes={'id' : id, 'count' : float_count}, content=''))

            for k, rlgvertex in enumerate(rlgmesh.vertices):
                if j == 0:
                    float_array.content += '{0} {1} {2} '.format(rlgvertex.position[0], rlgvertex.position[1], rlgvertex.position[2])
                elif j == 1:
                    float_array.content += '{0} {1} {2} '.format(rlgvertex.normal[0], rlgvertex.normal[1], rlgvertex.normal[2])
                elif j == 2:
                    float_array.content += '1 1 1 1 '
                else:
                    float_array.content += '{0} {1} '.format(rlgvertex.uvs[0][0], 1 - rlgvertex.uvs[0][1])  # the v coordinate is flipped

            # open technique_common tag
            technique_common = source.append_child(XmlNode('technique_common'))

            # open accessor tag
            source_attribute = "#" + get_mesh_field_array_id(filename_root, rlgmesh.hash_id, field)
            count = rlgmesh.vertex_count
            stride = [3, 3, 4, 2][j]
            accessor = technique_common.append_child(XmlNode('accessor', attributes={'source' : source_attribute, 'count' : count, 'stride' : stride}))

            # param tag
            if j in [0,1]:
                accessor.append_child(XmlNode('param', attributes={'name' : 'X', 'type' : 'float'}, has_body=False))
                accessor.append_child(XmlNode('param', attributes={'name' : 'Y', 'type' : 'float'}, has_body=False))
                accessor.append_child(XmlNode('param', attributes={'name' : 'Z', 'type' : 'float'}, has_body=False))
            elif j == 2:
                accessor.append_child(XmlNode('param', attributes={'name' : 'R', 'type' : 'float'}, has_body=False))
                accessor.append_child(XmlNode('param', attributes={'name' : 'G', 'type' : 'float'}, has_body=False))
                accessor.append_child(XmlNode('param', attributes={'name' : 'B', 'type' : 'float'}, has_body=False))
                accessor.append_child(XmlNode('param', attributes={'name' : 'A', 'type' : 'float'}, has_body=False))
            else:
                accessor.append_child(XmlNode('param', attributes={'name' : 'S', 'type' : 'float'}, has_body=False))
                accessor.append_child(XmlNode('param', attributes={'name' : 'T', 'type' : 'float'}, has_body=False))

        # vertices
        id = get_mesh_field_id(filename_root, rlgmesh.hash_id, 'vertex')
        vertices = mesh.append_child(XmlNode('vertices', attributes={'id' : id}))
        # vertices -> input
        source = '#' + get_mesh_field_id(filename_root, rlgmesh.hash_id, 'position')
        vertices.append_child(XmlNode('input', attributes={'semantic' : 'POSITION', 'source' : source}, has_body=False))

        # triangles
        triangles_count = len(rlgmesh.faces)
        triangles = mesh.append_child(XmlNode('triangles', attributes={'count' : triangles_count}))
        # triangles -> input
        source = '#' + get_mesh_field_id(filename_root, rlgmesh.hash_id, 'vertex')
        triangles.append_child(XmlNode('input', attributes={'semantic' : 'VERTEX', 'source' : source, 'offset' : '0'}, has_body=False))
        source = '#' + get_mesh_field_id(filename_root, rlgmesh.hash_id, 'normal')
        triangles.append_child(XmlNode('input', attributes={'semantic' : 'NORMAL', 'source' : source, 'offset' : '1'}, has_body=False))
        source = '#' + get_mesh_field_id(filename_root, rlgmesh.hash_id, 'color')
        triangles.append_child(XmlNode('input', attributes={'semantic' : 'COLOR', 'source' : source, 'offset' : '2', 'set' : '0'}, has_body=False))
        source = '#' + get_mesh_field_id(filename_root, rlgmesh.hash_id, 'texcoord')
        triangles.append_child(XmlNode('input', attributes={'semantic' : 'TEXCOORD', 'source' : source, 'offset' : '3', 'set' : '0'}, has_body=False))
        # triangles -> p (array of indices)
        p = triangles.append_child(XmlNode('p', content=''))
        for tri in rlgmesh.faces:
            util.adjust_normals_for_dae(tri, rlgmesh)
            for index in tri.indices:
                p.content += str(index) + ' '  # vertex position index
                p.content += str(index) + ' '  # vertex normal index
                p.content += str(index) + ' '  # vertex color index
                p.content += str(index) + ' '  # vertex uv coord index




def write_section_library_controllers(root : XmlNode, rlgroot : RlgRoot, filename_root : str):
    """Write the library_controller section to an XmlNode object

    This methods mutates root

    Args:
        root: XmlNode, root of the dae file
    """
    library_controller = root.append_child(XmlNode('library_controllers'))
    for rlgmesh in rlgroot.models[0].meshes:
        controller = library_controller.append_child(XmlNode('controller', attributes={'id' : get_armature_id(filename_root, rlgmesh.hash_id), 'name' : 'Armature'}))
        skin = controller.append_child(XmlNode('skin', attributes={'source' : '#' + get_mesh_id(filename_root, rlgmesh.hash_id)}))
        skin.append_child(XmlNode('bind-shape-matrix', content='1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'))
        # source tag (joints)
        source_1 = skin.append_child(XmlNode('source', attributes={'id' : get_armature_field_id(filename_root, rlgmesh.hash_id, 'joints')}))
        name_array = source_1.append_child(XmlNode('Name_array', attributes={'id' : get_armature_field_array_id(filename_root, rlgmesh.hash_id, 'joints'), 'count' : len(rlgmesh.bones)}))
        for rlgbone in rlgmesh.bones:
            name_array.content += get_bone_id(rlgbone.hash_id) + ' '
        technique_common_1 = source_1.append_child(XmlNode('technique_common'))
        accessor = technique_common_1.append_child(XmlNode('accessor', attributes={'source' : '#' + get_armature_field_array_id(filename_root, rlgmesh.hash_id, 'joint'),
                                                                                   'count'  : len(rlgmesh.bones),
                                                                                   'stride' : '1'})) 
        accessor.append_child(XmlNode('param', attributes={'name' : 'JOINT', 'type' : 'name'}, has_body=False))
        # source tag (inv bind matrix)
        source_2 = skin.append_child(XmlNode('source', attributes={'id' : get_armature_field_id(filename_root, rlgmesh.hash_id, 'inv_bind_matrix')}))
        float_array_1 = source_2.append_child(XmlNode('float_array', attributes={'id' : get_armature_field_array_id(filename_root, rlgmesh.hash_id, 'inv_bind_matrix'),
                                                                                  'count' : len(rlgmesh.bones) * 16}))
        for rlgbone in rlgmesh.bones:
            for i in range(4):
                for j in range(4):
                    float_array_1.content += str(rlgbone.matrix[j][i]) + ' '
        technique_common_2 = source_2.append_child(XmlNode('technique_common'))
        accessor = technique_common_2.append_child(XmlNode('accessor', attributes={'source' : '#' + get_armature_field_array_id(filename_root, rlgmesh.hash_id, 'inv_bind_matrix'),
                                                                                   'count' : len(rlgmesh.bones),
                                                                                   'stride' : '16'}))
        accessor.append_child(XmlNode('param', attributes={'name' : 'TRANSFORM', 'type' : 'float4x4'}, has_body=False))
        # source tag (weights)
        source_3 = skin.append_child(XmlNode('source', attributes={'id' : get_armature_field_id(filename_root, rlgmesh.hash_id, 'weights')}))
        weight_count = len(rlgmesh.vertices)*4  # 4 is the maximum number of weights per vertex (in an rlg file)
        float_array_2 = source_3.append_child(XmlNode('float_array', attributes={'id' : get_armature_field_array_id(filename_root, rlgmesh.hash_id, 'weights'),
                                                                                 'count' : weight_count},  
                                                                                 content='')) 
        for rlgvertex in rlgmesh.vertices:
            for weight in rlgvertex.bone_weights:
                float_array_2.content += str(weight) + ' '
        technique_common_3 = source_3.append_child(XmlNode('technique_common'))
        accessor = technique_common_3.append_child(XmlNode('accessor', attributes={'source' : '#' + get_armature_field_array_id(filename_root, rlgmesh.hash_id, 'weights'),
                                                                                   'count' : weight_count,  
                                                                                   'stride' : '1'}))
        accessor.append_child(XmlNode('param', attributes={'name' : 'WEIGHT', 'type' : 'float'}, has_body=False))  
        # joints tag
        joints = skin.append_child(XmlNode('joints'))
        joints.append_child(XmlNode('input', attributes={'semantic': 'JOINT', 'source' : '#' + get_armature_field_id(filename_root, rlgmesh.hash_id, 'joints')}))
        joints.append_child(XmlNode('input', attributes={'semantic': 'INV_BIND_MATRIX', 'source' : '#' + get_armature_field_id(filename_root, rlgmesh.hash_id, 'inv_bind_matrix')}))
        # vertex_weights tag
        vertex_weights = skin.append_child(XmlNode('vertex_weights', attributes={'count': len(rlgmesh.vertices)}))  
        vertex_weights.append_child(XmlNode('input', 
                                            attributes={'semantic': 'JOINT', 'source' : '#' + get_armature_field_id(filename_root, rlgmesh.hash_id, 'joints'), 'offset' : '0'},
                                            has_body=False))
        vertex_weights.append_child(XmlNode('input', 
                                            attributes={'semantic': 'WEIGHT', 'source' : '#' + get_armature_field_id(filename_root, rlgmesh.hash_id, 'weights'), 'offset' : '1'},
                                            has_body=False))
        vcount = vertex_weights.append_child(XmlNode('vcount'))  
        for i in range(len(rlgmesh.vertices)):
            vcount.content += '4 '
        v = vertex_weights.append_child(XmlNode('v'))  
        for i, rlgvertex in enumerate(rlgmesh.vertices):
            for j, bone_id in enumerate(rlgvertex.bone_ids):
                index_of_current_weight = (4 * i) + j
                v.content += '{0} {1} '.format(bone_id, index_of_current_weight)





def write_section_library_visual_scenes(root : XmlNode, rlgroot : RlgRoot, filename_root : str, bone_tree_mode=False):
    """Write the library_visual_scenes section to an XmlNode object

    This methods mutates root

    Args:
        root: XmlNode, root of the dae file
    """
    library_visual_scenes = root.append_child(XmlNode('library_visual_scenes'))
    # open visual scene tag
    visual_scene = library_visual_scenes.append_child(XmlNode('visual_scene', attributes={'id' : 'Scene', 'name' : 'Scene'}))

    # armature
    node_armature = visual_scene.append_child(XmlNode('node', attributes={'id' : 'Armature', 'name' : 'Armature', 'type' : 'NODE'}))
    node_armature.append_child(XmlNode('matrix', attributes={'sid' : 'transform'}, content='1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'))
    if bone_tree_mode == True:
        for rlg_level_one_bone in rlgroot.models[0].root_bone.children:
            write_tree_of_bone_nodes(xmlnode=node_armature, rlgbone=rlg_level_one_bone)
    else:
        for rlgbone in rlgroot.models[0].bones:
            node_bone = node_armature.append_child(XmlNode('node', attributes={'id' : get_armature_bone_id(rlgbone.hash_id),
                                                                            'name' : get_armature_bone_id(rlgbone.hash_id),
                                                                            'sid' : get_bone_id(rlgbone.hash_id),
                                                                            'type' : 'JOINT'}))
            
            matrix = node_bone.append_child(XmlNode('matrix', attributes={'sid' : 'transform'}))
            for i in range(4):
                for j in range(4):
                    matrix.content += str(rlgbone.matrix[j][i]) + ' '

    for i, rlgmesh in enumerate(rlgroot.models[0].meshes):
        # node tag
        geometry_name = filename_root + "_hashid" + hex(rlgmesh.hash_id)
        node = visual_scene.append_child(XmlNode('node', attributes={'id' : geometry_name, 'name' : geometry_name, 'type' : 'NODE'}))
        # matrix tag
        # node.append_child(XmlNode('matrix', attributes={'sid' : 'transform'}, content='1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'))
        # instance_geometry tag
        url = '#' + geometry_name + '-mesh'
        texture_hash = rlgmesh.material.texture_hashes[0]
        image_base_name = hex(texture_hash).replace('0x', '') + '_enc_6'
        # instance controller tag
        instance_controller = node.append_child(XmlNode('instance_controller', attributes={'url' : '#' + get_armature_id(filename_root, rlgmesh.hash_id)}))
        instance_controller.append_child(XmlNode('skeleton', content='#Armature'))

        bind_material = instance_controller.append_child(XmlNode('bind_material'))
        technique_common = bind_material.append_child(XmlNode('technique_common'))
        instance_material = technique_common.append_child(XmlNode('instance_material', attributes={'symbol' : image_base_name + '-material', 'target' : '#' + image_base_name + '-material'}))
        instance_material.append_child(XmlNode('bind_vertex_input', attributes={'semantic' : 'UV0', 'input_semantic' : 'TEXCOORD', 'input_set' : '0'}, has_body=False))




def write_tree_of_bone_nodes(xmlnode : XmlNode, rlgbone):
    xml_child_node = xmlnode.append_child(XmlNode('node', attributes={'id' : get_armature_bone_id(rlgbone.hash_id),
                                                                            'name' : get_armature_bone_id(rlgbone.hash_id),
                                                                            'sid' : get_bone_id(rlgbone.hash_id),
                                                                            'type' : 'JOINT'}))
    matrix = xml_child_node.append_child(XmlNode('matrix', attributes={'sid' : 'transform'}))
    for i in range(4):
        for j in range(4):
            matrix.content += str(rlgbone.matrix[j][i]) + ' '
    for rlg_child_bone in rlgbone.children:
        write_tree_of_bone_nodes(xmlnode=xml_child_node, rlgbone=rlg_child_bone)
    extra = xml_child_node.append_child(XmlNode('extra'))
    technique = extra.append_child(XmlNode('technique', attributes={'profile' : 'blender'}))
    technique.append_child(XmlNode('tip_x', attributes={'sid' : 'tip_x', 'type' : 'float'}, content=str(rlgbone.tip_offset[0])))
    technique.append_child(XmlNode('tip_y', attributes={'sid' : 'tip_y', 'type' : 'float'}, content=str(rlgbone.tip_offset[1])))
    technique.append_child(XmlNode('tip_z', attributes={'sid' : 'tip_z', 'type' : 'float'}, content=str(rlgbone.tip_offset[2])))




def write_section_scene(root : XmlNode):
    """Write the scene section to an XmlNode object

    This methods mutates root

    Args:
        root: XmlNode, root of the dae file
    """
    scene = root.append_child(XmlNode('scene'))
    scene.append_child(XmlNode('instance_visual_scene', attributes={'url' : '#Scene'}, has_body=False))




def read_dae(filepath : str) -> RlgRoot:
    """Read dae file
    Args:
        filepath: path of the file to read
    Returns:
        RlgRoot object that represents the 3D model
    """
    rlgroot = RlgRoot()
    rlgmodel = RlgModel()
    rlgroot.models.append(rlgmodel)
    xmlroot = read_xml(filepath)

    library_geometries = xmlroot.find('library_geometries')
    geometry_tags = library_geometries.findall('geometry')
    for i, xmlgeometry in enumerate(geometry_tags):
        rlgmesh = RlgMesh()
        rlgmodel.meshes.append(rlgmesh)
        hash_id_match = re.search(REGEX_HASHID, xmlgeometry.get('id')) 
        rlgmesh.hash_id = int(hash_id_match.group(), 16) if hash_id_match != None else None
        read_triangles_and_vertices_of_mesh(rlgmesh=rlgmesh, xmlgeometry=xmlgeometry)
        #if i not in [4,5,7,8,9,10,11]:  # TODO: temp thing. pls remove
        #    rlgmesh.faces.clear()
    
    library_controllers = xmlroot.find('library_controllers')
    controller_tags = library_controllers.findall('controller')
    for i, xmlcontroller in enumerate(controller_tags):
        rlgmesh = rlgmodel.meshes[i]
        read_vertex_weights_of_mesh(rlgmesh=rlgmesh, xmlcontroller=xmlcontroller)
    
    return rlgroot




def read_triangles_and_vertices_of_mesh(rlgmesh, xmlgeometry):
    """
    """
    # find triangles tag 
    # in order to be able to parse triangles and vertices we need this tag's data first
    triangles_tag = xmlgeometry.find('triangles')

    # TRIANGLES
    array_of_ints_as_string = triangles_tag.find('p').content
    input_tag_count = len(triangles_tag.findall('input'))
    triangles = str_to_num_list(array_of_ints_as_string, group=3, to_integer=True, step=input_tag_count, offset=0)
    for tri in triangles:
        rlgmesh.faces.append(RlgFace(indices=tri))
    
    # VERTICES
    # get the ids for the tags we need
    input_vertex_tag = triangles_tag.find('input', { 'semantic' : 'VERTEX' })
    vertices_id = input_vertex_tag.get('source').replace('#', '')
    input_normal_tag = triangles_tag.find('input', { 'semantic' : 'NORMAL' })
    normals_id = input_normal_tag.get('source').replace('#', '')
    input_texcoord_tag = triangles_tag.find('input', { 'semantic' : 'TEXCOORD' })
    texcoords_id = input_texcoord_tag.get('source').replace('#', '')

    # get the p tag's data
    # we want to know what data is associated to each vertex position (normals, uv)
    p_data = str_to_num_list(array_of_ints_as_string, group=input_tag_count, to_integer=True)
    vertex_indices = {}  # dict of indices
    for sublist in p_data:
        if sublist[0] not in vertex_indices:
            vertex_indices.update({ sublist[0] : sublist[1:] })  # detect which normal and uv indices are associated to the position index
    normal_offset = int(input_normal_tag.get('offset'))
    texcoord_offset = int(input_texcoord_tag.get('offset'))

    # look for the vertices tag
    vertices_tag = xmlgeometry.findid(vertices_id)
    
    # get the id of the position and find where it is
    input_tag = vertices_tag.find('input', {'semantic' : 'POSITION'})
    positions_id = input_tag.get('source').replace('#', '')
    
    # get the array of floats for positions
    source_tag = xmlgeometry.findid(positions_id)
    array_of_floats_as_string = source_tag.find('float_array').content
    vertex_positions = str_to_num_list(string=array_of_floats_as_string, group=3)

    # get the array of floats for normals
    source_tag = xmlgeometry.findid(normals_id)
    array_of_floats_as_string = source_tag.find('float_array').content
    vertex_normals = str_to_num_list(string=array_of_floats_as_string, group=3)

    # get the array of floats for uv coordinates
    source_tag = xmlgeometry.findid(texcoords_id)
    array_of_floats_as_string = source_tag.find('float_array').content
    vertex_uvs = str_to_num_list(string=array_of_floats_as_string, group=2)
    # flip them
    for uv in vertex_uvs:
        uv[1] = 1 - uv[1]

    for j, vertex_position in enumerate(vertex_positions):

        new_vertex =  RlgVertex( 
            position=vertex_position, 
            normal=vertex_normals[vertex_indices[j][normal_offset-1]],
            uvs=[vertex_uvs[vertex_indices[j][texcoord_offset-1]]])
        rlgmesh.vertices.append(new_vertex) 
    rlgmesh.vertex_count = len(rlgmesh.vertices)




def read_vertex_weights_of_mesh(rlgmesh : RlgMesh, xmlcontroller : XmlNode):
    """Get the vertex weights and indices from a dae controller, then add
    them to the vertices of rlgmesh

    Args:
        rlgmesh: the RlgMesh object to be updated
        xmlcontroller: xml element where to look for the information
    """
    # Look for array IDs
    xml_accessors = xmlcontroller.findall('accessor')
    joint_array_id = None
    weight_array_id = None
    for xml_accessor in xml_accessors:
        xml_joint_param = xml_accessor.find(name='param', attributes={'name' : 'JOINT'})
        if xml_joint_param != None:
            joint_array_id = xml_accessor.get('source').replace('#', '')
        xml_weight_param = xml_accessor.find(name='param', attributes={'name' : 'WEIGHT'})
        if xml_weight_param != None:
            weight_array_id = xml_accessor.get('source').replace('#', '')

    # With the IDs that were found, go to the arrays
    # joints = xmlcontroller.findid(joint_array_id).content
    # TODO: need regex for this
    # then we could use this to manually fill the "0xB00B" section
    weights = str_to_num_list(xmlcontroller.findid(weight_array_id).content)

    xml_vertex_weights = xmlcontroller.find('vertex_weights')
    vcount = str_to_num_list(string=xml_vertex_weights.find('vcount').content,
                             to_integer=True)
    v = str_to_num_list(string=xml_vertex_weights.find('v').content,
                        group=2,
                        to_integer=True)

    k = 0
    for i in range(len(vcount)):
        for j in range(vcount[i]):
            rlgmesh.vertices[i].bone_ids[j] = v[k][0]  # this should be fine, as long as the joints are in the same order as the meshe's bone hashes in the rlg file section B00B
            rlgmesh.vertices[i].bone_weights[j] = weights[v[k][1]]
            k += 1




def str_to_num_list(string : str, group = 1, to_integer = False, step = 1, offset = 0) -> list:
    """Converts a string to a list of floats, or a list of ints, or a list of list of floats, or a list of list of ints
    Args:
        string: the string to be converted
        group: the length of the lists that will be contained in the big list. 
            If 1, return one-dimensional list
            If it's N>1, group the numbers in lists of N each 
        to_integer: if true casts the floats to ints. Throws an error if
            it finds a number that has decimal digits
        step: how many indices to step by at each iteration. default is 1
        offset: where to start. Use in combination with step
    Returns:
        one-dimentional list if group is 1. bidimensional list otherwise
    """
    if offset >= step:
        raise Exception('Offset should be smaller than step. offset:{0}, step:{1}'.format(offset, step))

    list_of_strings_raw = string.split(' ')
    list_of_strings = []

    # delete any empty string
    for string in list_of_strings_raw:
        if len(string) != 0:
            list_of_strings.append(string)
            
    list_of_numbers = []
    sublist = []
    for i in range(offset, len(list_of_strings), step):
        string = list_of_strings[i]
        number = int(string, 10) if to_integer else float(string) 
        if group == 1:
            list_of_numbers.append(number)
        else:
            sublist.append(number)
            if i % group == group-1:
                list_of_numbers.append(sublist)
                sublist = []
    return list_of_numbers


