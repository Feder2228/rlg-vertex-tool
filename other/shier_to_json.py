from src.rlgtool import nlgutil
from src.rlgtool import util


# python -m other.shier_to_json

shierfile = open('./other/mario.shier', 'rb')
binfile = open('./other/hashid.bin', 'rb')
jsonfile = open('./other/shierdata.json', 'w')
section_map = nlgutil.get_map_of_sections(shierfile)


jsonfile.write('{\n')

hashes = []
section_b003 = section_map[b'\x80\x03'][0]
shierfile.seek(section_b003.body_location())

for i in range(section_b003.size//4):
    hashes.append(int.from_bytes(shierfile.read(4)))

data = []

 # I think this section holds the parent data. 2 means that the parent is the root node, I think
data.append(list())
shierfile.seek(section_map[b'\x80\x09'][0].body_location()) 
for i in range(section_map[b'\x80\x09'][0].size//4):
    data[0].append(int.from_bytes(shierfile.read(4)))

# this section contains numbers from 0 to 3
data.append(list())
shierfile.seek(section_map[b'\x80\x04'][0].body_location())
for i in range(section_map[b'\x80\x04'][0].size//4):
    data[1].append(int.from_bytes(shierfile.read(4)))

# this section is sorted. 0 to 0x2B
data.append(list())
shierfile.seek(section_map[b'\x80\x05'][0].body_location())
for i in range(section_map[b'\x80\x05'][0].size//4):
    data[2].append(int.from_bytes(shierfile.read(4)))

# this is identical to the previous section
data.append(list())
shierfile.seek(section_map[b'\x80\x06'][0].body_location())
for i in range(section_map[b'\x80\x06'][0].size//4):
    data[3].append(int.from_bytes(shierfile.read(4)))

data.append(list())
data[4].append(0x6969)
shierfile.seek(section_map[b'\x80\x07'][0].body_location())
for i in range(section_map[b'\x80\x07'][0].size//4):
    data[4].append(int.from_bytes(shierfile.read(4)))

# this section tells you who's the symmetrical bone (for instance r foot -> l foot)
data.append(list())
shierfile.seek(section_map[b'\x80\x08'][0].body_location())  
for i in range(section_map[b'\x80\x08'][0].size//4):
    data[5].append(int.from_bytes(shierfile.read(4)))

float_vectors = []
shierfile.seek(section_map[b'\x80\x10'][0].body_location())
for i in range(section_map[b'\x80\x10'][0].size//12):
    float_vectors.append([
    (util.bytes_to_float(shierfile.read(4))),
    (util.bytes_to_float(shierfile.read(4))),
    (util.bytes_to_float(shierfile.read(4)))
    ]
    )

for i, hash in enumerate(hashes):
    hashname = nlgutil.get_hash_name(binfile=binfile, hash=hash)
    jsonfile.write('"{0:X}"'.format(hash))
    tab = 11 - len(hex(hash))
    jsonfile.write(' '*tab) 
    jsonfile.write(': ["{0}",'.format(hashname))
    if hashname != None:
        tab = 30 - len(hashname)
        jsonfile.write(' '*tab) 

    for j, d in enumerate(data):
        if i >= len(d):
            jsonfile.write(' '*15) 
            continue
        jsonfile.write('"0x{0:X}"'.format(d[i]))
        tab = 11 - len(hex(d[i]))
        jsonfile.write(' '*tab) 
        jsonfile.write(', ')

    jsonfile.write('[{0}, {1}, {2}]'.format(float_vectors[i][0], float_vectors[i][1], float_vectors[i][2]))

    jsonfile.write('],\n')



jsonfile.write('}\n')

jsonfile.close()
shierfile.close()