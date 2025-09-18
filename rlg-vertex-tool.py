import os, struct, math, shutil, glob, re



section_matrix_data = b'\x00\x01\xb0\x02'
section_model_data = b'\x00\x01\xb0\x03'
section_mesh_data = b'\x00\x01\xb0\x04'
section_vertex_attributes = b'\x00\x01\xb0\x05'
section_vertex_data = b'\x00\x01\xb0\x06'
section_index_data = b'\x00\x01\xb0\x07'
section_skeleton_data = b'\x00\x01\xb0\x08'
section_bone_mesh_hashes = b'\x00\x01\xb0\x0b'
section_bone_data = b'\x00\x01\xb0\x0a'
section_unkown_data = b'\x00\x01\xb0\x0c'
section_material_data = b'\x00\x01\xb0\x16'


def rlg_get_size(rlg):
    rlg.seek(0,2)
    return rlg.tell()

def rlg_get_data(rlg):
    size = rlg_get_size( rlg )
    rlg.seek(0,0)
    return rlg.read( size )

def rlg_get_section_info( rlg, section_identifier ):
    a = []
    data = rlg_get_data( rlg )
    location = data.find( section_identifier )
    a.append( location )              # location of section
    a.append( data[ location ] )      # flags
    a.append( data[ location + 4 ] )  # section size
    return a



# Function to read floats of the vertex data section
# I made this when I didn't know anything else about how the vertex section works
def read_vertex_floats(rlg):

    file_size = rlg_get_size(rlg)
    data = rlg_get_data(rlg)

    #find the section
    location = data.find( section_vertex_data )
    print( hex(location) )

    floats = []
    rlg.seek( location+8 ,0 )
    while rlg.tell() < file_size:
        bytes = rlg.read(4)
        f = struct.unpack( '!f', bytes )[0]
        if( math.isnan(f) or math.isinf(f) ):
            break
        floats.append(f)
    print(floats[:10])




def read_model_data(rlg):
    
    section_info = rlg_get_section_info( rlg, section_model_data )
    location = section_info[0]
    section_size = section_info[2]

    # go to where model data starts
    rlg.seek( location + 4, 0 )

    # loop on it and read stuff idk
    model_count = section_size//12
    for i in range(0, model_count):
        rlg.read(4)
        mesh_count = int.from_bytes( rlg.read(4), "big" )
        print("mesh count: " +str(mesh_count))
        rlg.read(4)



# Function to read the vertices of a rlg file
def get_vertices_from_rlg(rlg, vertex_attributes):

    section_info = rlg_get_section_info( rlg, section_vertex_data )
    location = section_info[0]
    section_size = section_info[2]

    # go to where vertex data starts
    rlg.seek( location + 4, 0 )

    section_size = int.from_bytes( rlg.read(4), "big" )
    start_of_data = rlg.tell()
    group = 0
    last_0x4 = 0
    unknown_0x4 = None
    a = []
    while rlg.tell() < start_of_data+section_size:
        current_byte = rlg.tell() - start_of_data
        stride = 4
        # check vertex attribute offset
        for i in vertex_attributes:
            if( i['offset'] <= current_byte ):
                stride = i['stride']
                unknown_0x4 = i['0x4']                
        if(last_0x4 == 0xb0 and unknown_0x4 == 0x67):
            group += 1
        last_0x4 = unknown_0x4

        new_vector = []
        for i in range(0, stride//4):
            bytes = rlg.read(4)
            f = struct.unpack( '!f', bytes )[0]
            new_vector.append(f)
        a.append( {
            "offset" : current_byte,
            "type" : unknown_0x4, 
            "group" : group,
            "values" : new_vector
        } )
    
    # fliter only the vertices we need
    vertices = []

    for i in a:
        if( i['type'] == 0x67 ):
            vertices.append( i )
    return vertices


#TODO remove this garbage
def get_indices_from_rlg(rlg):

    section_info = rlg_get_section_info( rlg, section_index_data )
    location = section_info[0]

    rlg.seek( location+8 , 0 )

    a = []
    for i in range(8): #TODO range(4) is temporary. replace it with length of section
        a.append( [rlg.read(2), rlg.read(2), rlg.read(2), rlg.read(2), rlg.read(2), rlg.read(2), rlg.read(2), rlg.read(2), rlg.read(2)] )
    return a


def read_vertex_attribute(rlg):
    
    section_info = rlg_get_section_info( rlg, section_vertex_attributes )
    location = section_info[0]
    section_size = section_info[2]

    # go to where data starts
    rlg.seek( location + 4 ,0)

    # read data
    section_size_b = rlg.read(4)
    section_size = int.from_bytes( section_size_b, "big" )
    a = []
    while rlg.tell() < location+8+section_size:  # TODO: this is ugly as hell. Fix
        offset = int.from_bytes( rlg.read(4), "big" )
        unknown_0x4 = int.from_bytes( rlg.read(1), "big" )
        stride = int.from_bytes( rlg.read(1), "big" )
        unknown_0x6 = int.from_bytes( rlg.read(2), "big" )

        a.append( {
            "offset" : offset,
            "0x4" : unknown_0x4, # 67 fe cc ed 52 c0 d6 d7 d4 b0
            "stride" : stride,
            "0x6" : unknown_0x6
        } )
    return a




def read_mesh_data(rlg, verbose = False):

    # get the filename and strip the extention
    filename = os.path.basename(rlg.name)
    print("Reading mesh data of: " +filename)
    
    section_info = rlg_get_section_info( rlg, section_mesh_data )
    location = section_info[0]
    section_size = section_info[2]

    # go to where data starts
    rlg.seek( location+4 , 0 )
    start_of_data = rlg.tell()

    # read data
    a = []
    while rlg.tell() < start_of_data+section_size:  # TODO: edit the condition to make it more readable
        index_start_offset = int.from_bytes( rlg.read(4), "big" )
        index_flags = int.from_bytes( rlg.read(4), "big" )
        face_type = int.from_bytes( rlg.read(1), "big" )
        attribute_count = int.from_bytes( rlg.read(1), "big" )
        unknown_0x0a = int.from_bytes( rlg.read(4), "big" )
        material_hash_id = int.from_bytes( rlg.read(4), "big" )
        mesh_hash_id = int.from_bytes( rlg.read(4), "big" )
        unknown_0x16 = int.from_bytes( rlg.read(4), "big" )
        unknown_0x1a = int.from_bytes( rlg.read(4), "big" )
        material_offset = int.from_bytes( rlg.read(4), "big" )
        unknown_0x22 = int.from_bytes( rlg.read(4), "big" )
        unknown_0x26 = int.from_bytes( rlg.read(4), "big" )
        unknown_0x2a = int.from_bytes( rlg.read(6), "big" )

        if(verbose):
            a.append( { 
                "index_start_offset" : index_start_offset,
                "index_count" : index_flags & 0xffffff,
                "index_format" : index_flags >> 24,
                "face_type" : face_type,
                "attribute_count" : attribute_count,
                "0x0a" : unknown_0x0a,
                "material_hash_id" : material_hash_id,
                "0x16" : unknown_0x16,
                "0x1a" : unknown_0x1a,
                "mesh_hash_id" : mesh_hash_id,
                "material_offset" : material_offset,
                "0x22" : unknown_0x22,
                "0x26" : unknown_0x26,
                "0x2a" : unknown_0x2a,
            }   
            )
        else:
            a.append( {  # TODO: redundant code?
                "index_start_offset" : index_start_offset,
                "index_count" : index_flags & 0xffffff,
                "index_format" : index_flags >> 24,
                "face_type" : face_type,
                "attribute_count" : attribute_count,
                "material_hash_id" : material_hash_id,
                "mesh_hash_id" : mesh_hash_id,
                "material_offset" : material_offset,
            }   
            )
    return a
    



def read_index_data(rlg):

    filename = os.path.basename(rlg.name)  # TODO: this message doesn't have to be here
    print("Reading index data of: " +filename)
    
    section_info = rlg_get_section_info( rlg, section_index_data )
    location = section_info[0]
    section_size = section_info[2]

    # go to where data starts
    rlg.seek( location + 4 ,0)
    start_of_data = rlg.tell() 

    bytestr = b''

    bytestr = rlg.read(section_size)
    return bytestr




def read_index_data_and_group_by_mesh(rlg):
    data = []
    read_model_data(rlg)
    filename = os.path.basename(rlg.name)
    # Read data
    mesh_data = read_mesh_data(rlg, True)
    index_data = read_index_data(rlg)
    vertex_attribute = read_vertex_attribute(rlg)
    # Create text file
    txt = open("output/" +filename+ "_miscdata.txt", "w")

    # Loop 
    for m in range(0, len(mesh_data)):

        # Mesh data
        txt.write("================================ MESH " +str(m)+ ": ================================\n")
        for i in mesh_data[m]:
            txt.write( str(i) + " : " +str(mesh_data[m].get(i))+ "\n")

        # Vertex attributes of mesh
        txt.write("----------------------------------------------------------------\n")
        txt.write("VERTEX ATTRIBUTES: \n")
        mesh_vertex_attributes = vertex_attribute[10*m:10*(m+1)]
        for i in mesh_vertex_attributes:
            txt.write( str(i) + "\n")

        # Vertices of mesh
        txt.write("----------------------------------------------------------------\n")
        txt.write("VERTICES: \n")
        vertices = get_vertices_from_rlg(rlg, mesh_vertex_attributes)
        for i in vertices:
            # Number of the vertex inside the mesh
            vertex_number = hex( ( i["offset"] - mesh_vertex_attributes[0]["offset"] ) // 12 )
            txt.write( "Offset: " +hex(i["offset"])+ " (Num: " +vertex_number+ ") Coordinates: " +str(i["values"])+ "\n")
        
        # Index data
        txt.write("----------------------------------------------------------------\n")
        txt.write("INDEX DATA: \n")
        index_data_end = mesh_data[m]['index_start_offset'] + ( (mesh_data[m]['index_count']) * 2 )
        mesh_index_data = []
        for i in range(mesh_data[m]['index_start_offset'], index_data_end): 
            mesh_index_data.append( index_data[i] )
            txt.write( byte_hex( index_data[i]) )
            if(i%2 == 1):
                txt.write(" ")
            if(i%24 == 23):
                txt.write("\n")
        txt.write("\n\n\n\n\n\n")

        # Add data to array
        data.append({
            "mesh_data" : mesh_data,
            "index_data" : mesh_index_data,
            "vertex_attribute" : mesh_vertex_attributes,
            "vertices" : vertices
        })
    print(filename+"_miscdata.txt file successfully created in output folder")
    txt.close()
    return data




def create_obj(filename, vertices, indices=[]):
    # Remove .rlg from the filename
    filename = re.split(".rlg", filename)[0]
    # Create file
    obj = open("output/" +filename+ ".obj", "w")
    curr_group = -1

    # Now write the vertices
    for v in vertices:
        # Write the group of the vertices
        if(v["group"] != curr_group):

            #TODO temporary (print the first faces if this is group 1) One day I really need to burn this whole script in a fire and rewrite it from scratch
            if(v["group"] == 1):
                for i in indices:
                    obj.write("f " +str(int.from_bytes(i[0], 'big'))+ "/" +str(int.from_bytes(i[1], 'big'))+ "/" +str(int.from_bytes(i[2], 'big')) )
                    obj.write(" " +str(int.from_bytes(i[3], 'big'))+ "/" +str(int.from_bytes(i[4], 'big'))+ "/" +str(int.from_bytes(i[5], 'big')) )
                    obj.write(" " +str(int.from_bytes(i[6], 'big'))+ "/" +str(int.from_bytes(i[7], 'big'))+ "/" +str(int.from_bytes(i[8], 'big')) + "\n" )

            curr_group = v["group"]
            line = "g group" + str( v["group"] ) + "\n"
            obj.write(line)
        # Write the vertex
        line = "v " + str( v["values"][0] ) + " " + str( v["values"][1] ) + " " + str( v["values"][2] ) + "\n"
        obj.write(line)

    print(filename + ".obj was successfully created in output folder")
    obj.close()




def create_obj_for_each_group(filename, vertices):
    # Remove .rlg from the filename
    filename = re.split(".rlg", filename)[0]
    curr_group = 0
    group_filename = filename + "_0"
    obj = open("output/" +group_filename+ ".obj", "w")

    for v in vertices:
        # Switch file
        if(v["group"] != curr_group):
            curr_group = v["group"]
            # Create file
            group_filename = filename + "_" + str(v["group"])
            obj.close()
            obj = open("output/" +group_filename+ ".obj", "w")
            line = "g group" + str( v["group"] ) + "\n"
            obj.write(line)
        # Write the vertex
        line = "v " + str( v["values"][0] ) + " " + str( v["values"][1] ) + " " + str( v["values"][2] ) + "\n"
        obj.write(line)
    print("files created in output folder")
    obj.close()




def read_obj(filename):
    print("filename: " +filename)
    obj = open("obj/" + filename + ".obj", "r")
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
    # Get the rlg filename without extension
    filename = os.path.basename(original_rlg.name)
    filename = re.split(".rlg", filename)[0]
    # Get the data from both the rlg and the obj
    try:
        new_vertices = read_obj(filename)
    except:
        print("Error: .obj file not found")
        return
    old_vertices = get_vertices_from_rlg(original_rlg, read_vertex_attribute(original_rlg))
    print("Found " + str(len(new_vertices)) + " Vertices in given obj file")
    print("Found " + str(len(old_vertices)) + " Vertices in given rlg file")
    if( len(new_vertices) != len(old_vertices)):
        print("Warning: The vertex count of the two files doesn't match. This may lead to errors, or the output rlg file might be incorrect")

    rlg = open("rlg/"+filename+".rlg", "rb")
    
    section_info = rlg_get_section_info( rlg, section_mesh_data )
    location = section_info[0]
    
    # find the start of the section we need
    start_of_data = location+8
    rlg.close()

    # Now it's time to copy the rlg file and replace its vertices 
    shutil.copyfile('./rlg/'+filename+'.rlg', './output/'+filename+'.rlg')
    rlg = open("output/"+filename+'.rlg', "r+b")
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
    



# Function to convert a bytearray into a clean string (so that it doesn't show ascii characters when printing, just hex)
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





while True:
    r = input('''\n\n-- Select a command --
              
    COMMANDS FOR EXPORTING/IMPORTING FILES:
    e - Extract vertices from rlg file
    g - Generate new rlg (by starting from an original rlg and replacing its vertices with the ones of an obj)
              
    DEV STUFF:
    es - Extract vertices from rlg file and put them in separate OBJs (by group) (for dev purposes only. Those objs won't be useful to recreate an .rlg file)
    data - print misc data about each mesh of the .rlg file. Data will go into a txt file in the output folder
    va - print vertex attributes to txt file
    mesh - print mesh data to txt file
    index - print index data to txt file
    
    exit - Exit\n\n''')

    # Check if response is exit
    if(r == "exit"):
        exit()

    filenames = get_all_rlg_filenames()
    

    for i in filenames:
        rlg = open("rlg/" + i, "rb")
        print("\n================================================================")

        if(r == "e"):
            # Convert all the .rlg files to .obj 
            vertex_attributes = read_vertex_attribute(rlg)
            vertices = get_vertices_from_rlg(rlg, vertex_attributes)
            create_obj(i, vertices)

        #TODO test
        if(r == "palle"):
            # Convert all the .rlg files to .obj 
            vertex_attributes = read_vertex_attribute(rlg)
            vertices = get_vertices_from_rlg(rlg, vertex_attributes)
            indices = get_indices_from_rlg(rlg)
            create_obj(i, vertices, indices)

        elif(r == "g"):
            generate_new_rlg(rlg)

        elif(r == "es"):
            # Convert all the .rlg files to .obj
                vertex_attributes = read_vertex_attribute(rlg)
                vertices = get_vertices_from_rlg(rlg, vertex_attributes)
                create_obj_for_each_group(i, vertices)
                rlg.close()

        elif(r == "va"):
            # Read vertex attributes
            vertex_attribute = read_vertex_attribute(rlg)
            for a in vertex_attribute:
                print(a)
            # Print vertex attribute on text file
            txt = open("output/" +i+ "_vertexattribute.txt", "w")
            txt.write( str(len(vertex_attribute)) +" attributes found\n\n")
            for a in vertex_attribute:
                for j in a:
                    txt.write( j +" : "+ hex(a.get(j)) )
                    txt.write("\n")
                txt.write("------------------------------------------------\n")
            txt.close

        elif(r == "mesh"):
            # Read mesh data
            mesh_data = read_mesh_data(rlg, True)
            for m in mesh_data:
                print(m)
            rlg.close()
            # Print mesh data on text file
            txt = open("output/" +i+ "_meshdata.txt", "w")
            txt.write( str(len(mesh_data)) +" mesh data found\n\n")
            for m in mesh_data:
                for j in m:
                    txt.write( j +" : "+ hex(m.get(j)) )
                    txt.write("\n")
                txt.write("------------------------------------------------\n")
            txt.close

        elif(r == "index"):
            # Read index data
            bytestr = read_index_data(rlg)
            rlg.close()
            # Print index data on text file
            txt = open("output/" +i+ "_indexdata.txt", "w")
            string = byte_hex_str(bytestr)
            for j in range(0, len(string)):
                txt.write(string[j])
                if(j%12 == 11):
                    txt.write("\n")
            txt.close()
            print("Created txt file containing index data of " +i+ " in output folder")

        elif(r == "data" or r == "d"):
            # Read data
            read_index_data_and_group_by_mesh(rlg)

        else:
            print("invalid input")
            break
        print("================================================================")
        rlg.close()
    rlg.close()
    input("Press Enter to continue...")