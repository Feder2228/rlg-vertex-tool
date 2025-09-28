import math
import struct, re, glob

DEBUG = True


# 3D MATHS UTILITY FUNCTIONS
def vector_sum( v1, v2 ):
    return [ v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2] ]

def vector_sum3( v1, v2, v3 ):
    return [ v1[0] + v2[0] + v3[0], v1[1] + v2[1] + v3[1], v1[2] + v2[2] + v3[2]]

def vector_sub( v1, v2 ):
    return [ v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2] ]

def dot_product( v1, v2 ):
    result = 0
    for i in range( len(v1) ):
        result += v1[i] * v2[i]
    return result

# find the plane the vectors v1 and v2 belong to
# return: [ a, b, c ], which represents the normal of the plane
# the equation of the plane is ax + by + cz = 0
def find_plane( v1, v2 ):

    a = det2( [ [ v1[1], v1[2] ],
                [ v2[1], v2[2] ] ] )
    
    b = det2( [ [ v1[0], v1[2] ],
                [ v2[0], v2[2] ] ] ) * -1
    
    c = det2( [ [ v1[0], v1[1] ],
                [ v2[0], v2[1] ] ] )
    
    return [ a, b, c ]


def det2( m ):
    return (m[0][0] * m[1][1]) - (m[0][1] * m[1][0])


# This function checks the vertex normals of a tri to determine on which side that tri should face.
# If the triangle vertices are clockwise, it makes them counterclockwise. Otherwise does nothing.
def adjust_normals_for_dae( tri, geometry ):  # TODO: move this into the Model3d class

    # look at the vertex normals to determine which side the tri is facing (this is how it works in .rlg files)
    vertices = geometry.vertices
    index0 = tri.indices[0]
    index1 = tri.indices[1]
    index2 = tri.indices[2]

    # sum the normals of the vertices. In the rlg format, the triagle faces towards this point
    # (this is not actually the normal, just a random point on the same side as the normal)
    tri_normal_thing = vector_sum3( vertices[ index0 ].normal, vertices[ index1 ].normal, vertices[ index2 ].normal )

    # make a matrix of the positions of the triangle's vertices
    tri_positions = [ [ vertices[ index0 ].position[0], vertices[ index0 ].position[1], vertices[ index0 ].position[2] ],
                      [ vertices[ index1 ].position[0], vertices[ index1 ].position[1], vertices[ index1 ].position[2] ],
                      [ vertices[ index2 ].position[0], vertices[ index2 ].position[1], vertices[ index2 ].position[2] ] ]
    
    # shift the tri in a way so that the first vertex is on the origin
    tri_positions_on_origin = [ vector_sub( tri_positions[0], tri_positions[0] ),
                                vector_sub( tri_positions[1], tri_positions[0] ),
                                vector_sub( tri_positions[2], tri_positions[0] ) ]

    # find the counterclockwise normal
    dae_normal = find_plane( tri_positions_on_origin[1], tri_positions_on_origin[2] )

    # determine whether the vertex normal sum is on the counterclockwise side or not.
    # use dot product for this. If the result is negative they're on opposite sides
    # in that case, it would be on the clockwise side, so swap two of the indices to make it counterclockwise
    if dot_product( dae_normal, tri_normal_thing ) < 0:
        # swap two indices
        tmp = tri.indices[0]
        tri.indices[0] = tri.indices[1]
        tri.indices[1] = tmp





# FILE UTILITY FUNCTIONS
# Function that scans a folder for files and returns a list containing all the file names
def get_all_filenames_of_specified_extension( dir_path, extension ):

    filenames_r = glob.glob( "./{0}*{1}".format( dir_path, extension )  )
    filenames = []

    print("found", str(len(filenames_r)), "files:")  # TODO: this print shouldn't be here

    for i in filenames_r:

        file = re.split("\\\\", i)[1]
        print(file)
        filenames.append(file)

    return filenames






# DATA TYPE UTILITY FUNCTIONS
# Function to convert a bytearray into a string where each byte corresponds to two hexadecimal digits (in ascii)
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


def bytes_to_float( bytes ):
    return struct.unpack( '!f', bytes )[0]

def float_to_bytes4( number ):
    hexstr = hex(struct.unpack('<I', struct.pack( '<f', number ))[0])
    if hexstr != "0x0":
        return bytes.fromhex( hexstr[2:] )
    return b'\x00\x00\x00\x00'
    
# This function takes a float value as input.
# It then multiplies this float by 1024. Then it casts it to a bytes object with the length of 2.
# That's how uv coordinates are represented in .rlg files.
def float_to_bytes2( float ):
    integer = int( float * 1024 )
    return integer.to_bytes( 2, 'big', signed=True )

def float_to_bytes1( float ):
    integer = int( float * 255 )
    return integer.to_bytes( 2, 'big', signed=True )