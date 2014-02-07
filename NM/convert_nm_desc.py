import csv, string, os


infile = open(os.environ['NM_HOME']+'/Data/product_catalog_features.tdf', 'r')
outfile = open(os.environ['NM_HOME']+'/Data/product_desc_text.txt', 'w')

reader = csv.reader(infile, delimiter='\t')
writer = csv.writer(outfile, delimiter='\t')

replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))

for row in reader:
    item = row[0]
    desc_text = row[9]
    
    clean_text = desc_text.translate(replace_punctuation)
    
    writer.writerow([ item, clean_text ])

infile.close()
outfile.flush()
outfile.close()