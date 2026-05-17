from . import util
from .rlg_data_structures import *
from . import nlgutil
from . import shier
import numpy as np


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

# SECTION SIZE CONSTANTS
MESH_RECORD_SIZE = 48
MATERIAL_RECORD_SIZE = 0x68
NUM_MATERIAL_TEXTURES = 6
MATERIAL_OTHER_DATA_BYTES = MATERIAL_RECORD_SIZE - (8*NUM_MATERIAL_TEXTURES)


def read_rlg(rlgpath : str, shierpath=None) -> RlgRoot:
    """Read rlg file and return a RlgRoot object

    Args:
        rlgpath: path of the rlg file to open
        shierpath: optional. If provided, this method will use it to
            extract extra information about the 3D model
    Returns:
        RlgRoot object equivalent of the file
    """
    rlgfile = open(rlgpath, "rb")
    # First, find the sections...
    root_section = nlgutil.get_section_tree(rlgfile)
    skeleton_container_sections = root_section.get_children_of_type(SECTION_SKELETON_CONTAINER)
    has_bones = False
    if len(skeleton_container_sections) > 0:
        skeleton_container_section = skeleton_container_sections[0]
        has_bones = True

    # Then, read their data
    root = RlgRoot()
    read_matrix(rlgfile, root_section.get_children_of_type(SECTION_MATRIX_DATA)[0], root)
    read_models(rlgfile, root_section.get_children_of_type(SECTION_MODEL_DATA)[0], root)
    read_meshes(rlgfile, root_section.get_children_of_type(SECTION_MESH_DATA)[0], root)

    if has_bones:
        if shierpath == None:
            read_bone_matrices(rlgfile, skeleton_container_section.get_children_of_type(SECTION_BONE_MATRICES)[0], root)
        else:
            shierfile = open(shierpath, "rb")
            read_bone_matrices(rlgfile, skeleton_container_section.get_children_of_type(SECTION_BONE_MATRICES)[0], root, shierfile)
            shier.organize_bone_hierarchy(shierfile=shierfile, model=root.models[0])
        read_bone_mesh_hashes(rlgfile, skeleton_container_section.get_children_of_type(SECTION_BONE_MESH_HASHES), root)

    read_faces(rlgfile, root_section.get_children_of_type(SECTION_INDEX_DATA)[0], root)
    read_materials(rlgfile, root_section.get_children_of_type(SECTION_MATERIAL_DATA)[0], root)
    read_vaps(rlgfile, root_section.get_children_of_type(SECTION_VERTEX_ATTRIBUTES)[0], root)
    read_vertices(rlgfile, root_section.get_children_of_type(SECTION_VERTEX_DATA)[0], root)
    
    rlgfile.close()
    return root




def read_materials(rlgfile, section : nlgutil.Section, root : RlgRoot):
    """Reads material data from an rlg file object

    Mutate each mesh of root by adding a material to it

    Args:
        rlgfile: rlg file object
        section: object that identifies the section within the file
        root: RlgRoot object to add the new data to
    """
    for model in root.models:
        for mesh in model.meshes:
            mesh.material = RlgMaterial()
            rlgfile.seek(section.body_location() + mesh.material_offset, 0)
            for i in range(NUM_MATERIAL_TEXTURES):
                mesh.material.texture_hashes.append(int.from_bytes(rlgfile.read(4), 'big'))
                mesh.material.texture_unk.append(int.from_bytes(rlgfile.read(4), 'big'))
            for i in range(MATERIAL_OTHER_DATA_BYTES):
                mesh.material.other_data += rlgfile.read(1)        




def read_faces(rlgfile, section : nlgutil.Section, root : RlgRoot):
    """Read index data from an rlg file object

    Mutate each mesh of root by adding indices and faces to it

    Important: the meshes must already have the index_offset and
    index_count set to the correct values

    Args:
        rlgfile: rlg file object
        section: object that identifies the section within the file
        root: RlgRoot object to add the new data to
    """
    for model in root.models:
        for mesh in model.meshes:
            rlgfile.seek(section.body_location() + mesh.index_offset, 0)
            indices = []
            for i in range(mesh.index_count):
                indices.append(int.from_bytes(rlgfile.read(2), 'big'))
            mesh.index_count = len(indices)
            mesh.decode_indices(indices)




def read_vertices(rlgfile, section : nlgutil.Section, root : RlgRoot): 
    """Reads vertices from an rlg file

    Mutate each mesh of root by adding vertices to it

    Important: The mesh object must have its vertex attribute pointers
    set altready

    Args:
        rlgfile: rlg file object
        section: object that identifies the section within the file
        root: RlgRoot object to add the new data to
    """
    for model in root.models:
        for mesh in model.meshes:
            for k in range(mesh.vertex_count):
                # create the vertex
                vertex = RlgVertex()
                mesh.vertices.append(vertex)
                uv_occurrence = 0

                for vap in mesh.vaps:
                    location = section.body_location() + vap.offset + vap.stride*k
                    rlgfile.seek(location, 0)
                    
                    if vap.type == RlgVAPType.POSITION:
                        if vap.stride == 12:
                            vertex.position = [util.bytes_to_float(rlgfile.read(4)),  
                                                util.bytes_to_float(rlgfile.read(4)), 
                                                util.bytes_to_float(rlgfile.read(4))]
                        elif vap.stride == 6:
                            vertex.position = [int.from_bytes(rlgfile.read(2), 'big', signed=True) / 1024,
                                                int.from_bytes(rlgfile.read(2), 'big', signed=True) / 1024,
                                                int.from_bytes(rlgfile.read(2), 'big', signed=True) / 1024]
                        else:
                            print('there exist positions with stride {0}'.format(vap.stride))
                    elif vap.type == RlgVAPType.NORMAL:
                        if vap.stride == 12:
                            vertex.normal = [util.bytes_to_float(rlgfile.read(4)),  
                                                util.bytes_to_float(rlgfile.read(4)), 
                                                util.bytes_to_float(rlgfile.read(4))]
                        elif vap.stride == 3:
                            vertex.normal = [int.from_bytes(rlgfile.read(1), 'big', signed=True) / 255,
                                                int.from_bytes(rlgfile.read(1), 'big', signed=True) / 255,
                                                int.from_bytes(rlgfile.read(1), 'big', signed=True) / 255]
                        else:
                            print('there exist normals with stride {0}'.format(vap.stride))
                    elif vap.type == RlgVAPType.UV:
                        new_uv = [int.from_bytes(rlgfile.read(2), 'big', signed=True) / 1024,
                                    int.from_bytes(rlgfile.read(2), 'big', signed=True) / 1024]  # TODO: util should already have a function that does this
                        if len(vertex.uvs) > uv_occurrence:
                            vertex.uvs[uv_occurrence] = new_uv
                        else:
                            vertex.uvs.append(new_uv)
                        uv_occurrence += 1
                    elif vap.type == RlgVAPType.BONE_INDICES:
                        vertex.bone_ids = [int.from_bytes(rlgfile.read(1), 'big'),
                                            int.from_bytes(rlgfile.read(1), 'big'),
                                            int.from_bytes(rlgfile.read(1), 'big'),
                                            int.from_bytes(rlgfile.read(1), 'big')]
                    elif vap.type == RlgVAPType.BONE_WEIGHTS:
                        vertex.bone_weights = [util.bytes_to_float(rlgfile.read(4)),  
                                                util.bytes_to_float(rlgfile.read(4)),
                                                util.bytes_to_float(rlgfile.read(4)),  
                                                util.bytes_to_float(rlgfile.read(4))]




def read_vaps(rlgfile, section : nlgutil.Section, root : RlgRoot):  
    """Reads vertex attribute pointers from an rlg file

    Mutates each mesh of root by adding VAPs to it

    Args:
        rlgfile: rlg file object
        section: object that identifies the section within the file
        root: RlgRoot object to add the new data to
    """
    for model in root.models:
        for mesh in model.meshes:
            # go to the location of this meshes' VAPs 
            rlgfile.seek(section.body_location() + mesh.vap_offset, 0) 
            for k in range(mesh.vap_count):
                vap = RlgVertexAttributePointer(
                    offset  = int.from_bytes(rlgfile.read(4), 'big'),
                    flags    = int.from_bytes(rlgfile.read(1), 'big'),
                    stride  = int.from_bytes(rlgfile.read(1), 'big'),
                    type  = RlgVAPType(int.from_bytes(rlgfile.read(1), 'big')))
                padding = int.from_bytes(rlgfile.read(1), 'big')
                if padding != 0:
                    print('turns out the eight byte of VAP is not padding')
                mesh.vaps.append(vap)




def read_meshes(rlgfile, section : nlgutil.Section, root : RlgRoot):
    """Read data of meshes from an rlg file object

    Mutates root by adding meshes to each of its models

    Args:
        rlgfile: rlg file object
        section: object that identifies the section within the file
        root: RlgRoot object to add the RlgMeshes to
    """
    for model in root.models:
        # go to where data starts
        rlgfile.seek(section.body_location(), 0)
        mesh_count = section.size//MESH_RECORD_SIZE
        for i in range(mesh_count):
            mesh = RlgMesh(
                index_offset  = int.from_bytes(rlgfile.read(4), "big"),
                index_format        = int.from_bytes(rlgfile.read(2), "big"),
                index_count         = int.from_bytes(rlgfile.read(2), "big"),
                vertex_count        = int.from_bytes(rlgfile.read(2), "big"),
                unk0xA              = int.from_bytes(rlgfile.read(1), "big"),
                vap_count           = int.from_bytes(rlgfile.read(1), "big"),
                vap_offset          = int.from_bytes(rlgfile.read(4), "big"),
                material_hash_id    = int.from_bytes(rlgfile.read(4), "big"),
                hash_id             = int.from_bytes(rlgfile.read(4), "big"),
                unk0x18             = int.from_bytes(rlgfile.read(4), "big"),
                unk0x1C             = int.from_bytes(rlgfile.read(4), "big"),
                material_offset     = int.from_bytes(rlgfile.read(4), "big"),
                unk0x24             = int.from_bytes(rlgfile.read(4), "big"),
                unk0x28             = int.from_bytes(rlgfile.read(4), "big"),
                unk0x2C             = int.from_bytes(rlgfile.read(4), "big"))
            model.meshes.append(mesh)




def read_models(rlgfile, section : nlgutil.Section, root : RlgRoot):
    """Reads models from an rlg file

    Mutates root by adding models to it

    Args:
        rlgfile: rlg file object
        section: object that identifies the section within the file
        root: RlgRoot object to add the RlgModels to
    """
    MODEL_RECORD_SIZE = 12
    # go to where model data starts
    rlgfile.seek(section.body_location(), 0)
    model_count = section.size//MODEL_RECORD_SIZE
    for i in range(model_count):
        model = RlgModel(
            hash_id     = int.from_bytes(rlgfile.read(4), "big"),
            mesh_count  = int.from_bytes(rlgfile.read(4), "big"),
            unk0x8      = int.from_bytes(rlgfile.read(4), "big"))
        root.models.append(model)




def read_matrix(rlgfile, section : nlgutil.Section, root : RlgRoot):
    """Reads the matrix section from an rlg file

    Mutates root by adding the matrix to it

    Args:
        rlgfile: rlg file object
        section: object that identifies the section within the file
        root: RlgRoot object to add the matrix to
    """
    rlgfile.seek(section.body_location(), 0)
    matrix = []
    for i in range(4):
        matrix_row = []
        for j in range(4):
            matrix_row.append(util.bytes_to_float(rlgfile.read(4)))
        matrix.append(matrix_row)
    root.matrix = matrix




def read_bone_mesh_hashes(rlgfile, sections : list[nlgutil.Section], root : RlgRoot):
    """Reads bone hashes from an rlg file object

    Mutate root by adding bones to its meshes

    Args:
        rlgfile: rlg file object
        sections: list of the bone mesh hashes sections
        root: RlgRoot object to add the data to
    """
    section_occurrence = 0

    for model in root.models:
        for mesh in model.meshes:
            section = sections[section_occurrence]
            section_occurrence += 1
            rlgfile.seek(section.body_location())

            for i in range(0, section.size, 4):
                mesh.bones.append(model.get_bone_by_id(int.from_bytes(rlgfile.read(4))))




def read_bone_matrices(rlgfile, section : nlgutil.Section, root : RlgModel, shierfile=None):    
    """Reads bones from an rlg file object

    Mutate root by adding bone matrices to its bones

    Args:
        rlgfile: rlg file object
        section: object that identifies the section within the file
        root: RlgRoot object to add the data to
    """
    # TODO: rewrite like everything in this method. Lmao
    BONE_RECORD_SIZE = 0x44
    for model in root.models:
        rlgfile.seek(section.body_location(), 0)  # with this, every model reads the all the bones TODO: maybe move bones to the root in the future
        bone_count = section.size // BONE_RECORD_SIZE    
        for i in range(bone_count):
            hash_id=int.from_bytes(rlgfile.read(4))
            rlgfile.read(16)  # skip 16 bytes
            scale_x = util.bytes_to_float(rlgfile.read(4))
            scale_y = util.bytes_to_float(rlgfile.read(4))
            scale_z = util.bytes_to_float(rlgfile.read(4))
            rlgfile.read(4)
            rotate_x = util.bytes_to_float(rlgfile.read(4))
            rotate_y = util.bytes_to_float(rlgfile.read(4))
            rotate_z = util.bytes_to_float(rlgfile.read(4))
            rlgfile.read(4)
            translate_x = util.bytes_to_float(rlgfile.read(4))
            translate_y = util.bytes_to_float(rlgfile.read(4))
            translate_z = util.bytes_to_float(rlgfile.read(4))
            rlgfile.read(4)

            translation_matrix = np.array([[1,0,0,0], [0,1,0,0], [0,0,1,0], [translate_x,translate_y,-translate_z,1]])
            # rotation_matrix_x = np.array([[1,0,0,0], [0,np.cos(rotate_x),np.sin(rotate_x),0], [0,np.sin(-rotate_x),np.cos(rotate_x),0], [0,0,0,1]])
            # rotation_matrix_y = np.array([[np.cos(rotate_y),0,np.sin(-rotate_y),0], [0,1,0,0], [np.sin(rotate_y),0,np.cos(rotate_y),0], [0,0,0,1]])
            # rotation_matrix_z = np.array([[np.cos(rotate_z),np.sin(rotate_z),0,0], [np.sin(-rotate_z),np.cos(rotate_z),0,0], [0,0,1,0], [0,0,0,1]])
            # scale_matrix = np.array([[scale_x,0,0,0], [0,scale_y,0,0], [0,0,scale_z,0], [0,0,0,1]])

            matrix = translation_matrix
            # matrix = np.matmul(rotation_matrix_x, matrix)
            # matrix = np.matmul(rotation_matrix_y, matrix)
            # matrix = np.matmul(rotation_matrix_z, matrix)
            # matrix = np.matmul(scale_matrix, matrix)
            matrix = matrix.tolist()
            bone = RlgBone(hash_id=hash_id, matrix=matrix)
            model.bones.append(bone)
            
            # if a shier file is provided 
            if shierfile != None:
                bone.tip_offset[0], bone.tip_offset[1], bone.tip_offset[2] = shier.get_bone_float_vector(shierfile=shierfile, bone_hash=hash_id)
             



def patch_rlg(srcpath : str, dstpath : str, new_root : RlgRoot, keep_old_indices=True):
    """Open rlg file, write to it and save as new rlg file

    Args:
        srcpath: path of the rlg file to open and read from
        dstpath: path of the rlg file to create/overwrite
        new_rlgroot: RlgRoot object with the changes you want to apply to the
            rlg file
        keep_old_indices: True takes indices from old file.
            False generates indices from the new RlgRoot
    """
    # get the data of the original rlg file as a rlgroot object
    old_root = read_rlg(srcpath)
    srcrlg = open(srcpath, "r+b")
    # create the destination file and open it
    dstrlg = open(dstpath, "wb")

    dstrlg.seek(0, 0)
    root_section = nlgutil.get_section_tree(srcrlg)
    nlgutil.write_section_header(rlgfile=dstrlg, section=root_section)

    # We sort the new file's meshes to match the original file order. 
    # Then we generate the Vertex Attribute Pointers for the new meshes
    # TODO: should we also sort models?
    new_root.models[0].match_mesh_order(other=old_root.models[0])
    new_root.models[0].generate_vaps(other=old_root.models[0])  # TODO: make this generic


    for section in root_section.children:
        if section.type in [SECTION_MODEL_DATA, SECTION_MATRIX_DATA]:
            nlgutil.copy_section(src=srcrlg, dst=dstrlg, section=section) 
        else:
            new_header_location = dstrlg.tell()
            nlgutil.write_section_header(rlgfile=dstrlg, section=section)
            section.header_location = new_header_location
            if section.type == SECTION_INDEX_DATA:
                if keep_old_indices:
                    nlgutil.copy_section(src=srcrlg, dst=dstrlg, section=section)
                else:
                    write_indices(rlgfile=dstrlg, root=new_root)                    
            
            elif section.type == SECTION_MATERIAL_DATA:
                write_material(rlgfile=dstrlg, new_root=new_root, old_root=old_root)

            elif section.type == SECTION_VERTEX_DATA:
                write_vertices(rlgfile=dstrlg, section=section, new_root=new_root, old_root=old_root)

            elif section.type == SECTION_VERTEX_ATTRIBUTES:
                write_vaps(rlgfile=dstrlg, new_root=new_root, old_root=old_root)

            elif section.type == SECTION_MESH_DATA:  # TODO: make this generic, iterate on all models
                write_meshes(rlgfile=dstrlg, new_model=new_root.models[0], old_model=old_root.models[0], keep_old_indices=keep_old_indices)
            
            elif section.type == SECTION_SKELETON_CONTAINER:
                patch_skeleton_section(srcrlg=srcrlg, dstrlg=dstrlg, new_root=new_root, old_root=old_root, section=section)
            
            # once you're done editing a section, update its size
            nlgutil.update_section_size_and_go_to_end(file=dstrlg, section=section)

    # once you're done, update the root section size
    nlgutil.update_section_size_and_go_to_end(file=dstrlg, section=root_section)

    srcrlg.close()
    dstrlg.close()




def patch_skeleton_section(srcrlg, dstrlg, new_root : RlgRoot, old_root : RlgRoot, section : nlgutil.Section):
    """subprocedure of patch_rlg that handles the skeleton part

    Args:
        srcrlg: source rlg file
        dstrlg: destination rlg file
        new_root: RlgRoot object containing the new data
        old_root: RlgRoot object containing the old data
        section: skeleton section
    """
    mesh_number = 0
    for subsection in section.children:
        if subsection.type in [SECTION_BONE_MATRICES, SECTION_BONE_UNKNOWN]:
            nlgutil.copy_section(src=srcrlg, dst=dstrlg, section=subsection)
            # write_bone_matrices(rlgfile=dstrlg, new_root=new_root, old_root=old_root)
        else:
            new_header_location = dstrlg.tell()
            nlgutil.write_section_header(rlgfile=dstrlg, section=subsection)
            subsection.header_location = new_header_location
            if subsection.type == SECTION_BONE_MESH_HASHES:
                write_bone_mesh_hashes(rlgfile=dstrlg, new_root=new_root,
                                    old_root=old_root, mesh_number=mesh_number)
                mesh_number += 1
    
            # once you're done editing a subsection, update its size
            nlgutil.update_section_size_and_go_to_end(file=dstrlg, section=subsection)




def write_material(rlgfile, new_root : RlgRoot, old_root : RlgRoot):
    """Write the material data of new_root

    RLGFILE MUST HAVE ITS POINTER AT THE BEGINNING OF MATERIAL SECTION

    Args:
        rlgfile: the file to be edited
        new_root: RlgRoot object containing the new data
        old_root: RlgRoot object containing the old data
    """
    for new_model in new_root.models:
        for new_mesh in new_model.meshes:
            old_mesh = old_root.models[0].get_mesh_by_id(new_mesh.hash_id)  # TODO: change this to make multi-model mods possible
            for i in range(NUM_MATERIAL_TEXTURES):
                rlgfile.write(old_mesh.material.texture_hashes[i].to_bytes(4, 'big'))
                rlgfile.write(old_mesh.material.texture_unk[i].to_bytes(4, 'big'))
            rlgfile.write(old_mesh.material.other_data)




def write_indices(rlgfile, root : RlgRoot):
    """Write the index data of an RlgRoot to an rlg file

    Args:
        rlgfile: the file to be edited
        root: RlgRoot object containing the new data
    """
    for model in root.models:
        for mesh in model.meshes:
            indices = mesh.encode_indices()
            for index in indices:
                rlgfile.write(index.to_bytes(2, 'big'))




def write_vertices(rlgfile, section : nlgutil.Section, new_root : RlgRoot, old_root : RlgRoot):
    """Write new_mesh's vertices to fileì

    No preconditions for the rlgfile's pointer

    Args:
        rlgfile: rlg file object to write the vertices to 
        section: object that identifies the section within the file
        new_mesh: RlgMesh object containing the vertices to be written
        old_mesh: used to find the correct place in the file where to write vertices
    """
    for new_model in new_root.models:
        for new_mesh in new_model.meshes:
            old_mesh = old_root.models[0].get_mesh_by_id(new_mesh.hash_id)  # TODO: change this to make multi-model mods possible
            if len(new_mesh.vertices) != len(old_mesh.vertices):
                print('newL={0} newVC={1} oldL={2} oldVC={3} '.format(len(new_mesh.vertices), new_mesh.vertex_count, len(old_mesh.vertices), old_mesh.vertex_count))
            for k in range(len(new_mesh.vertices)):
                uv_occurrence = 0
                for vap in new_mesh.vaps:
                    location = section.body_location() + vap.offset + vap.stride*k
                    rlgfile.seek(location, 0)
                    if vap.type == RlgVAPType.POSITION: 
                        if vap.stride == 12:
                            rlgfile.write(util.float_to_bytes4(new_mesh.vertices[k].position[0]))
                            rlgfile.write(util.float_to_bytes4(new_mesh.vertices[k].position[1]))
                            rlgfile.write(util.float_to_bytes4(new_mesh.vertices[k].position[2]))
                        elif vap.stride == 6:
                            rlgfile.write(util.float_to_bytes2(new_mesh.vertices[k].position[0]))
                            rlgfile.write(util.float_to_bytes2(new_mesh.vertices[k].position[1]))
                            rlgfile.write(util.float_to_bytes2(new_mesh.vertices[k].position[2]))
                        else:
                            raise Exception('error, unexpected stride for position: {0}'.format(vap.stride))
                    elif vap.type == RlgVAPType.NORMAL:
                        if vap.stride == 12:
                            rlgfile.write(util.float_to_bytes4(new_mesh.vertices[k].normal[0]))
                            rlgfile.write(util.float_to_bytes4(new_mesh.vertices[k].normal[1]))
                            rlgfile.write(util.float_to_bytes4(new_mesh.vertices[k].normal[2]))
                        elif vap.stride == 3:
                            rlgfile.write(util.float_to_bytes1(new_mesh.vertices[k].normal[0]))
                            rlgfile.write(util.float_to_bytes1(new_mesh.vertices[k].normal[1]))
                            rlgfile.write(util.float_to_bytes1(new_mesh.vertices[k].normal[2]))
                        else:
                            raise Exception('error, unexpected stride for normal: {0}'.format(vap.stride))
                    elif vap.type == RlgVAPType.UV:
                        if uv_occurrence == 0:
                            rlgfile.write(util.float_to_bytes2(new_mesh.vertices[k].uvs[uv_occurrence][0]))
                            rlgfile.write(util.float_to_bytes2(new_mesh.vertices[k].uvs[uv_occurrence][1]))
                        else:
                            rlgfile.write(util.float_to_bytes2(old_mesh.vertices[k].uvs[uv_occurrence][0]))
                            rlgfile.write(util.float_to_bytes2(old_mesh.vertices[k].uvs[uv_occurrence][1]))
                        uv_occurrence += 1
                    elif vap.type == RlgVAPType.BONE_INDICES:
                        for bone_id in new_mesh.vertices[k].bone_ids:
                            rlgfile.write(bone_id.to_bytes(1, 'big'))
                    elif vap.type == RlgVAPType.BONE_WEIGHTS:
                        for bone_weight in new_mesh.vertices[k].bone_weights:
                            rlgfile.write(util.float_to_bytes4(bone_weight))
        



def write_vaps(rlgfile, new_root : RlgRoot, old_root : RlgRoot):
    """Write the vap data of a mesh to an rlg file

    RLGFILE MUST HAVE ITS POINTER AT THE BEGINNING OF VAP SECTION

    new_root contains the new data. old_root will be used for the things
    that we want to leave unaltered because we don't know how it works

    Args:
        rlgfile: the file to be edited
        new_root: RlgRoot object containing the new data
        old_root: RlgRoot object containing the original data
    """
    for new_model in new_root.models:
        for new_mesh in new_model.meshes:
            # old_mesh = old_root.models[0].get_mesh_by_id(new_mesh.hash_id)  # TODO: change this to make multi-model mods possible
            for k in range(len(new_mesh.vaps)):
                rlgfile.write(new_mesh.vaps[k].offset.to_bytes(4, 'big'))
                rlgfile.write(new_mesh.vaps[k].flags.to_bytes(1, 'big'))
                rlgfile.write(new_mesh.vaps[k].stride.to_bytes(1, 'big'))
                rlgfile.write(new_mesh.vaps[k].type.value.to_bytes(1, 'big'))
                rlgfile.write(b'\x00')




def write_meshes(rlgfile, new_model : RlgModel, old_model : RlgModel, keep_old_indices=True):
    """Write the mesh data to an rlg file

    RLGFILE MUST HAVE ITS POINTER AT THE BEGINNING OF MESH SECTION'S BODY

    Args:
        rlgfile: the file to be edited
        new_model: RlgModel object containing the new data
        old_model: RlgModel object containing the original data
    """
    INDEX_RECORD_SIZE = 2
    VAP_RECORD_SIZE = 8
    index_offset = 0
    vap_offset = 0
    for i, new_mesh in enumerate(new_model.meshes):
        old_mesh = old_model.get_mesh_by_id(new_mesh.hash_id)
        if keep_old_indices:
            index_count = old_mesh.index_count
        else:
            index_count = len(new_mesh.encode_indices())
        rlgfile.write(index_offset.to_bytes(4, 'big'))
        rlgfile.write(old_mesh.index_format.to_bytes(2, 'big'))
        rlgfile.write(index_count.to_bytes(2, 'big'))
        rlgfile.write(len(new_mesh.vertices).to_bytes(2, 'big'))
        rlgfile.write(old_mesh.unk0xA.to_bytes(1, 'big'))
        rlgfile.write(len(new_mesh.vaps).to_bytes(1, 'big'))
        rlgfile.write(vap_offset.to_bytes(4, 'big'))
        rlgfile.write(old_mesh.material_hash_id.to_bytes(4, 'big'))
        rlgfile.write(new_mesh.hash_id.to_bytes(4, 'big'))
        rlgfile.write(old_mesh.unk0x18.to_bytes(4, 'big'))
        rlgfile.write(old_mesh.unk0x1C.to_bytes(4, 'big'))
        rlgfile.write(old_mesh.material_offset.to_bytes(4, 'big'))
        rlgfile.write(old_mesh.unk0x24.to_bytes(4, 'big'))
        rlgfile.write(old_mesh.unk0x28.to_bytes(4, 'big'))
        rlgfile.write(old_mesh.unk0x2C.to_bytes(4, 'big'))
        # increment the offsets for next iteration
        index_offset += index_count*INDEX_RECORD_SIZE
        vap_offset += len(new_mesh.vaps)*VAP_RECORD_SIZE


    

def write_bone_mesh_hashes(rlgfile, new_root : RlgRoot, old_root : RlgRoot, mesh_number : int):
    """Write the bone hashes of a mesh to an rlg file
    """
    old_mesh = old_root.models[0].meshes[mesh_number]
    for bone in old_mesh.bones:
        rlgfile.write(bone.hash_id.to_bytes(4, 'big'))




def write_bone_matrices(rlgfile, new_root : RlgRoot, old_root : RlgRoot):
    """Write the bone hashes of a mesh to an rlg file
    """
    for old_model in old_root.models:
        for bone in old_model.bones:
            rlgfile.write(bone.hash_id.to_bytes(4, 'big'))
            for i in range(4):
                for j in range(4):
                    rlgfile.write(bone.matrix[i][j].to_bytes(4, 'big'))
