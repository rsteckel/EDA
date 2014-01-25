
infile = open('nmd_trans.txt', 'r')
outfile = open('nmd_trans_encoded.txt', 'w')

linenumber = 1
while True:
    line = infile.readline()
    if len(line) == 0:
        break
    
    line = line.replace('\x00', '')
    utfline = line.decode('utf', errors='ignore')
    #utfline = utfline.encode('UTF-8', errors='ignore')

    tokens = line.split('|')
    if len(tokens) != 32:
        print 'error line', linenumber, line
        continue
    
    outfile.write(utfline)
    linenumber += 1
    
infile.close()

outfile.flush()
outfile.close()