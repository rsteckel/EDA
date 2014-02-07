import csv

infile = open('/Users/rsteckel/Workspace/NM/nm_bullets_corpus.tdf', 'r')
outfile = open('/Users/rsteckel/Workspace/NM/nm_bullets_features.txt', 'w')

reader = csv.reader(infile, delimiter='\t')
writer = csv.writer(outfile, delimiter='\t')

for row in reader:
    item = row[0]
    desc = row[1]
    bullets = row[2]
    
    if len(bullets) > 1:
        clean_bullets = bullets.replace('.', ' ')
        #writer.writerow([ [item], [clean_bullets] ])
        writer.writerow([ desc + ' ' + clean_bullets ])


infile.close()
outfile.flush()
outfile.close()
