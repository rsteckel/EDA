import csv

filenames = ['sporty-romantic-train.txt',
'romantic-sporty-train.txt',
'punk-baroque-train.txt',
'baroque-punk-train.txt',
'metallic-floral-train.txt',
'floral-metallic-train.txt',
'ruffles-festival-train.txt',
'festival-ruffles-train.txt',
'pantone-earthy-train.txt',
'earthy-pantone-train.txt',
'formal-casual-train.txt',
'casual-formal-train.txt',
'romantic-practical-train.txt',
'practical-romantic-train.txt',
'contemporary-classical-train.txt',
'classical-contemporary-train.txt',
'gown-cocktail-train.txt',
'cocktail-gown-train.txt',
'unhealthy-healthy-train.txt',
'healthy-unhealthy-train.txt',
'sensual-comfortable-train.txt',
'comfortable-sensual-train.txt',
'stunning-comfortable-train.txt',
'comfortable-stunning-train.txt',
'punk-princess-train.txt',
'princess-punk-train.txt',
'sophisticated-edgy-train.txt',
'edgy-sophisticated-train.txt',
'sporty-bohemian-train.txt',
'bohemian-sporty-train.txt',
'hydrate-cleanse-train.txt',
'cleanse-hydrate-train.txt']




def split_file(filename):
    tokens = filename.split('-')
    name1_file = open('Data/'+tokens[0]+'-fashion-google.txt', 'w')
    name2_file = open('Data/'+tokens[1]+'-fashion-google.txt', 'w')        
    train_file = open('Data/'+filename, 'r')
    reader = csv.reader(train_file, delimiter='\t')

    for row in reader:
        if row[0] == '1':
            name1_file.write(row[1]+'\n')
        elif row[0] == '0':
            name2_file.write(row[1]+'\n')
        else:
            print 'No classification'
    name1_file.close()
    name2_file.close()
    train_file.close()            
    

for f in filenames:
    split_file(f)
