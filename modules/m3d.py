ID_MATRIX = [ [1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1] ]

STR_MATRIX = '''4x4 MATRIX:
{0}
'''
STR_MODEL_DATA = '''MODEL DATA:
hash_id = {0}
mesh_count = {1}
unknown0x8 = {2}
'''
STR_MESH = '''MESH_DATA:
{0}

INDEX_DATA:
{1}

VERTEX_ATTRIBUTES:
{2}

VERTICES:
{3}

FACES:
{4}
'''
STR_MESH_DATA = '''0x00 index_offset: {0}
0x06 index_format: {1}
0x04 index_count: {2}
0x08 vertex_count: {3}
0x0A unknown: {4}
0x0B attrib_count: {5}
0x0C unknown: {6}
0x10 material_hash_id: {7} 
0x14 mesh_hash_id: {8} 
0x18 unknown: {9}
0x1C unknown: {10}
0x20 material_offset: {11} 
0x24 unknown: {12}
0x28 unknown: {13}
0x2C unknown: {14}
'''


# a data structure that defines a 3d model and aims to mimic the rlg/glg format
class Model3d:
    def __init__( self, matrix_data = ID_MATRIX, model_data = None, meshes = [] ):
        self.matrix_data = matrix_data
        self.model_data = model_data
        self.meshes = meshes

    def __str__( self ):
        output = STR_MATRIX.format( self.matrix_data, str( self.model_data ) )
        if self.model_data != None:
            for i, model in enumerate( self.model_data ):
                output += "MODEL {0}:\n\n".format( str(i) )
                output += str( model ) + '\n\n\n\n'
        for i, mesh in enumerate( self.meshes ):
            output += "MESH {0}:\n\n".format( str(i) )
            output += str( mesh ) + '\n\n\n\n'
        return output
    
    def get_mesh_by_id( self, hash_id ):
        for mesh in self.meshes:
            if mesh.mesh_data.mesh_hash_id == hash_id:
                return mesh
        return None

class ModelData:
    def __init__( self, hash_id, mesh_count, unknown0x8 ):
        self.hash_id = hash_id
        self.mesh_count = mesh_count
        self.unknown0x8 = unknown0x8
        # TODO: GLG - unknown0xC 
    def __str__( self ):
        return STR_MODEL_DATA.format( self.hash_id, self.mesh_count, self.unknown0x8 )

class Mesh:
    def __init__( self, mesh_data=None, index_data=None, vertex_attributes=None, vertices=None, faces=None, material=None ):
        self.mesh_data = mesh_data
        self.index_data = index_data
        self.vertex_attributes = vertex_attributes
        self.vertices = vertices
        self.faces = faces
        self.material = material
    def __str__( self ):
        return STR_MESH.format( self.mesh_data, self.index_data, self.vertex_attributes, self.vertices, self.faces )

    def get_face_verts( self, face_number ):
        indices = self.faces[ face_number ].indices
        face_vertices = []
        for index in indices:
            face_vertices.append( self.vertices[ index ] )
        return face_vertices

class MeshData:
    def __init__( self, index_offset=0, index_count=0, index_format=0, vertex_count=0, unknown0xA=0,
                  attribute_count=0, unknown0xC=0, material_hash_id=0, unknown0x18=0, unknown0x1C=0, mesh_hash_id=0,
                  material_offset=0, unknown_0x24=0, unknown_0x28=0, unknown_0x2C=0 ):
        self.index_offset = index_offset
        self.index_count = index_count
        self.index_format = index_format
        self.vertex_count = vertex_count
        self.unknown0xA = unknown0xA
        self.attribute_count = attribute_count
        self.unknown0xC = unknown0xC
        self.material_hash_id = material_hash_id
        self.unknown0x18 = unknown0x18
        self.unknown0x1C = unknown0x1C
        self.mesh_hash_id = mesh_hash_id
        self.material_offset = material_offset
        self.unknown_0x24 = unknown_0x24
        self.unknown_0x28 = unknown_0x28
        self.unknown_0x2C = unknown_0x2C
    
    def __str__( self ):
        return STR_MESH_DATA.format( self.index_offset, self.index_format, self.index_count,
                  self.vertex_count, self.unknown0xA, self.attribute_count, self.unknown0xC,
                  self.material_hash_id, self.mesh_hash_id, self.unknown0x18, self.unknown0x1C,
                  self.material_offset, self.unknown_0x24, self.unknown_0x28, self.unknown_0x2C )


class VertexAttribute:
    def __init__( self, group=0, offset=-1, type=-1, stride=0, unknown0x6=0 ):  
        self.group = group  # TODO: should "group" be removed?
        self.offset = offset
        self.type = type
        self.stride = stride
        self.unknown0x6 = unknown0x6
    def __str__( self ):
        return ""

class Vertex:
    def __init__( self, absolute_id=None, relative_id=None, offset=None,
                  group=None, position=None, normal=None, uv0=None,
                  unknown0xED=None, unknown0x52=None, unknown0xC0=None, 
                  unknown0xD6=None, unknown0xD7=None, bone_ids=None, 
                  bone_weights=None ):
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

class Material:
    def __init__( self, tex_hashes=None ):
        self.tex_hashes = tex_hashes

class Bone:
    def __init__( self, hash_id, matrix ):
        self.hash_id = hash_id
        self.matrix = matrix