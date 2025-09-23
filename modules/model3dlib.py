ID_MATRIX = [ [1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1] ]

# a data structure that defines a 3d model and aims to mimic the rlg/glg format
class Model3d:
    def __init__( self, matrix_data = ID_MATRIX, model_data = None, meshes = [] ):
        self.matrix_data = matrix_data
        self.model_data = model_data
        self.meshes = meshes

class ModelData:
    def __init__( self, hash_id, mesh_count, unknown0x8 ):
        self.hash_id = hash_id
        self.mesh_count = mesh_count
        self.unknown0x8 = unknown0x8
        # TODO: GLG - unknown0xC 

class Mesh:
    def __init__( self, mesh_data, index_data, vertex_attributes, vertices, faces ):
        self.mesh_data = mesh_data
        self.index_data = index_data
        self.vertex_attributes = vertex_attributes
        self.vertices = vertices
        self.faces = faces

    def get_face_verts( self, face_number ):
        indices = self.faces[ face_number ].indices
        face_vertices = []
        for index in indices:
            face_vertices.append( self.vertices[ index ] )
        return face_vertices

class MeshData:
    def __init__( self, index_start_offset, index_count, vertex_count, unknown0xA,
                  material_hash_id, unknown0x16, unknown0x1A, mesh_hash_id,
                  material_offset, unknown_0x22, unknown_0x26, unknown_0x2A ):
        self.index_start_offset = index_start_offset
        self.index_count = index_count
        self.vertex_count = vertex_count
        self.unknown0xA = unknown0xA
        self.material_hash_id = material_hash_id
        self.unknown0x16 = unknown0x16
        self.unknown0x1A = unknown0x1A
        self.mesh_hash_id = mesh_hash_id
        self.material_offset = material_offset
        self.unknown_0x22 = unknown_0x22
        self.unknown_0x26 = unknown_0x26
        self.unknown_0x2A = unknown_0x2A


class VertexAttribute:
    def __init__( self, group, offset, type, stride, unknown0x6 ):  
        self.group = group  # TODO: should "group" be removed?
        self.offset = offset
        self.type = type
        self.stride = stride
        self.unknown0x6 = unknown0x6

class Vertex:
    def __init__( self, absolute_id, relative_id, offset, group, position, normal, uv0,
                  unknown0xED, unknown0x52, unknown0xC0, unknown0xD6, unknown0xD7,
                  bone_ids, bone_weights ):
        self.absolute_id = absolute_id  # TODO: maybe I can remove this and replace it with a method "get_absolute_id()"
        self.relative_id = relative_id 
        self.offset = offset  # TODO: should probably remove this
        self.group = group  # TODO: should also probably remove this
        self.position = position
        self.normal = normal
        self.uv0 = uv0
        self.unknown0xED = unknown0xED
        self.unknown0x52 = unknown0x52
        self.unknown0xC0 = unknown0xC0
        self.unknown0xD6 = unknown0xD6
        self.unknown0xD7 = unknown0xD7
        self.bone_ids = bone_ids
        self.bone_weights = bone_weights

class Face:
    def __init__( self, indices ):
        self.indices = indices
