from src.rlgtool.nlgutil import get_hash_name


bin = open('./other/hashid.bin', 'rb')
json = open('./other/hashnames.json', 'w')

STRING_SECTION_BEGIN = 0x1C8F4
SIZE_OF_RECORD = 8
NUMBER_OF_RECORDS = STRING_SECTION_BEGIN//SIZE_OF_RECORD - 1

json.write('{\n')

for i in range(NUMBER_OF_RECORDS):
    bin.seek(8 + (i*SIZE_OF_RECORD), 0)
    int.from_bytes(bin.read(4))
    hash = int.from_bytes(bin.read(4))
    name = get_hash_name(bin, hash)
    if i%100 == 0:
        print(i)
    json.write( '\"' + hex(hash).replace('0x', '') + '\" : \"' + name + '\",\n' )

json.write('}\n')
bin.close()
json.close()