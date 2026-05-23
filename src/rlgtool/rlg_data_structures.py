from enum import Enum
import copy


class RlgRoot:
    """Class that representing an RLG file

    This data structure defines a collection of 3d models in a way which
    mimics the .rlg file format

    Attributes:
        matrix: a 4x4 transform matrix. We don't know what this is for
        models: a list of models. Usually it's just one
    """
    def __init__(self, matrices=None, models=[], bones=[]):
        self.matrices = matrices
        self.models = models
        if self.models == []:
            self.models = list()
        self.bones = bones
        if self.bones == []:
            self.bones = list()
        self.root_bone = None
    
    def get_bone_by_id(self, hash_id=None):
        for bone in self.bones:
            if bone.hash_id == hash_id:
                return bone
        return None


class RlgModel:
    """Class that represents a 3D model in the rlg format

    This data structure defines a 3d model in a way which mimics the .rlg
    file format

    Attributes:
        hash_id: hash that identifies the model
        mesh_count: number of meshes
        unk0x8: unknown
        meshes: list of RlgMesh object
    """
    def __init__(self, hash_id=None, mesh_count=None, unknown_data=None,
                 meshes=[], bones=[]):
        self.hash_id = hash_id
        self.mesh_count = mesh_count
        self.meshes = meshes
        self.unknown_data = unknown_data
        if self.meshes == []:
            self.meshes = list()        

    def get_mesh_by_id(self, hash_id=None):
        """Find mesh of the corresponding hash_id

        If no mesh matches hash_id, return None

        Args:
            hash_id: hash id of the mesh to search for
        Returns:
            RlgMesh object, or None if cannot find a matching hash_id
        """
        for mesh in self.meshes:
            if mesh.hash_id == hash_id:
                return mesh
        return None
    
    def get_main_texture_hashes(self):
        texture_hashes = []
        for mesh in self.meshes:
            if mesh.material is not None:
                hash = mesh.material.texture_hashes[0]
                if hash not in texture_hashes:
                    texture_hashes.append(hash)
        return texture_hashes
    
    def match_mesh_order(self, other):  # no_size_change_mode=True
        """Sort self.meshes to match the hash_id order of 
        other.meshes
        
        If self is missing a mesh with an hash_id X, copy it from other to
        self, but empty the vertices and faces of the copy

        Args:
            other: RlgModel object to mimic the mesh order of
        """
        new_mesh_list = []
        hash_id_list = other.get_list_of_mesh_hash_ids()
        for hash_id in hash_id_list:
            mesh = self.get_mesh_by_id(hash_id)
            if mesh != None:
                new_mesh_list.append(mesh)
            else:
                filler_mesh = copy.deepcopy(other.get_mesh_by_id(hash_id))
                filler_mesh.vertices.clear()
                filler_mesh.faces.clear()
                new_mesh_list.append(filler_mesh)
        self.meshes = new_mesh_list

    def get_list_of_mesh_hash_ids(self):
        hash_id_list = []
        for mesh in self.meshes:
            hash_id_list.append(mesh.hash_id)
        return hash_id_list
    
    def generate_vaps(self, other):
        """Generate VAPs for all meshes

        Args:
            other: the model to copy the VAPs from
        """
        offset = 0
        for self_mesh in self.meshes:
            other_mesh = other.get_mesh_by_id(self_mesh.hash_id)
            offset += self_mesh.generate_vaps(other=other_mesh, offset=offset)
    



class RlgMesh:
    """Class that represents a mesh of 3D model in the rlg format

    Attributes:
        nah, I'm not gonna do this.
    """
    def __init__(
            self, index_offset=None, index_count=None, index_format=None,
            vertex_count=None, vap_count=None, vap_offset=None,
            material_hash_id=None, hash_id=None,
            material_offset=None, unknown_data=None,
            vaps=[], vertices=[], faces=[], material=None, bones=[]):
        # MeshData
        self.index_offset = index_offset
        self.index_count = index_count
        self.index_format = index_format
        self.vertex_count = vertex_count
        self.vap_count = vap_count
        self.vap_offset = vap_offset
        self.material_hash_id = material_hash_id
        self.hash_id = hash_id
        self.material_offset = material_offset
        self.unknown_data = unknown_data
        # Child objects
        self.vaps = vaps
        if self.vaps == []:
            self.vaps = list()
        self.vertices = vertices
        if self.vertices == []:
            self.vertices = list()
        self.faces = faces
        if self.faces == []:
            self.faces = list()
        self.material = material
        self.bones = bones
        if self.bones == []:
            self.bones = list()

    def get_vap_by_type(self, type):
        """Returns a the first occurrence matching VAPs found in the mesh

        Args:
            type: RlgVAPType
        """
        for vap in self.vaps:
            if vap.type == type:
                return vap
        return None
    
    def get_vap_by_flags(self, flags):
        """Returns the VAP with matching flags found in the mesh

        Args:
            flags: int
        """
        for vap in self.vaps:
            if vap.flags == flags:
                return vap
        return None
    
    def generate_vaps(self, other, offset : int) -> int:
        """Generate Vertex Attribute Pointers for this mesh

        add RlgVertexAttributePointer objects to mesh.vaps.
        Copy the VAPs from other, then change the offset
        This meshe's vertices must already be set for this method to work properly.

        Args: 
            other: the mesh to copy the VAPs from
            offset: offset
        Returns:
            int, new offset
        """
        self.vaps.clear()

        for vap in other.vaps:
            self.vaps.append(copy.copy(vap))
            vap.offset = offset
            offset += len(self.vertices) * vap.stride
        return offset
        #vap_types = ((RlgVAPType.POSITION, 12),
        #            (RlgVAPType.NORMAL, 12),
        #            (RlgVAPType.UV0, 4),
        #            (RlgVAPType.UNK0, 4),
        #            (RlgVAPType.UNK1, 4),
        #            (RlgVAPType.UNK2, 4),
        #            (RlgVAPType.UNK3, 4),
        #            (RlgVAPType.UNK4, 4),
        #            (RlgVAPType.BONE_INDICES, 4),
        #            (RlgVAPType.BONE_WEIGHTS, 16))

    def decode_indices(self, indices : list[int]):
        """Generate faces from a list of indices formatted as the RLG format

        convert the RLG index list into a list of RlgFace objects and
        assign that list to self.faces

        All the faces previously contained in self.faces will be deleted
        
        Args:
            indices: list of ints
        """
        self.faces.clear()
        if len(indices) < 3:
            return
        for i in range(0, len(indices)-2):
            if indices[i+1] != indices[i+2] \
                and indices[i] != indices[i+1] \
                and indices[i] != indices[i+2]:
                if i%2 == 0:
                    self.faces.append(RlgFace([
                        indices[i],
                        indices[i+1],
                        indices[i+2]
                    ]))
                else:  # in RLG files, the normal is flipped for faces that start at odd indices
                    self.faces.append(RlgFace([
                        indices[i+1],
                        indices[i],
                        indices[i+2]
                    ]))

    def encode_indices(self) -> list[int]:
        """Convert this meshe's faces into a list of indices formatted as
        in an RLG file

        The method will return a list of indices. The meshe's faces will
        not be mutated
                
        Return:
            list of ints
        """
        indices = []
        for face in self.faces:
            # initial padding (add next face's first index an extra time)
            if len(indices) > 0:
                indices.append(face.indices[0])
            # add the actual faces indices
            indices = indices + face.indices
            # final padding (repeat last index twice)
            indices.append(indices[-1])
            indices.append(indices[-1])
        return indices



class RlgVAPType(Enum):
    """Enum for vertex attribute pointer's type
    """
    POSITION = 1
    NORMAL = 2  # can have stride 12 or 3
    COLOR = 3
    UV = 4
    BONE_WEIGHTS = 5
    BONE_INDICES = 7




class RlgVertexAttributePointer:
    """A record that is used in the rlg file format to determine which
    data does what in the "vertex_data" section

    Attributes:
        group: int, leftover from older versions of the tool. Probably be the mesh number
        offset: int, where to find the attribute in the vertex data
        type: enum, type of attribute. What will you find at the specified offset?
            i.e. positions, normals, uv coords, bone weights...     
        stride: int, how many bytes of data for each vertex
        unk0x6: unknown
    """
    def __init__(self, offset=None, flags=None, stride=None, type=None):  
        self.offset = offset
        self.flags = flags
        self.stride = stride
        self.type = type
        



class RlgVertex:
    """Represent a vertex of a RlgMesh object 

    Attributes:
        position: list of 3 floats, position of the vertex
        normal: list of 3 floats, normal of the vertex, used by the
            associated faces to determine on which side the face normal is
        color: RGBA color. 32-bit integer of the form 0xRRGGBBAA
        uvs: list where each element is a list of 2 floats. Element i is
            a list of length 2 containing the UV coordinates of texture i
        bone_ids: list of 4 ints. IDs of bones
        bone_weights: list of 4 ints. The weight of each of the 4 bones.
    """
    def __init__(self, position=None, normal=None, color=0xFFFFFFFF,
                 uvs=None, bone_ids=None, bone_weights=None):
        self.position = position
        self.normal = normal
        if self.normal == None:
            self.normal = list()
            self.normal += [1.0, 0.0, 0.0]
        self.color = color
        self.uvs = uvs
        if self.uvs == None:
            self.uvs = list()
            self.uvs.append([0.0, 0.0])
        self.bone_ids = bone_ids
        if self.bone_ids == None:
            self.bone_ids = list()
            self.bone_ids += [0, 0, 0, 0]
        self.bone_weights = bone_weights
        if self.bone_weights == None:
            self.bone_weights = list()
            self.bone_weights += [1.0, 0.0, 0.0, 0.0]




class RlgFace:
    """A face of a RlgMesh object 

    indices: list of ints. The face indices
    """
    def __init__(self, indices=list()):
        self.indices = indices




class RlgMaterial:
    """The material of a RlgMesh object 

    texture_hashes: list of ints. The hash IDs of the textures
    """
    def __init__(self, texture_hashes=[], texture_unk=[]):
        self.texture_hashes = texture_hashes
        if self.texture_hashes == []:
            self.texture_hashes = list()
        self.texture_unk = texture_unk
        if self.texture_unk == []:
            self.texture_unk = list()
        self.other_data = b''




class RlgBone:
    def __init__(self, hash_id=None, matrix=None):
        self.hash_id = hash_id
        self.matrix = matrix
        self.children = list()
        self.tip_offset = [0.0,0.5,0.0]  # don't mind this