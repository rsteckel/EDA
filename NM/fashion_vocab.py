import os


def add_terms(filename, delimiter):
    with open( os.environ['NM_HOME']+'/Data/'+filename, 'r') as f:
        lines = f.readlines()

    tokens = []
    for line in lines:
        if line.startswith('#'):
            continue;

        l = line.strip().lower()
        for token in l.split(delimiter):
            tokens.append(token)
        
    return tokens
    
    
def build_vocabulary(terms):
    vocab = set(terms)

    valid_vocab = {}
    for t in vocab:
        try:
            t.decode('utf-8')
            valid_vocab[t] = True
        except:
            pass;

    return valid_vocab


class FashionVocabulary:
    def __init__(self):
        terms = add_terms('designers-db.txt', ' ')
        terms += add_terms('colors-db.txt', ' ')
        terms += add_terms('fabrics-db.txt', ' ')
        terms += add_terms('misc_classifications.csv', '_')
        terms += add_terms('vocab-common.txt', ' ')
        
        self.vocab_ = build_vocabulary(terms)
    
    def contains(self, term):
        return self.vocab_.has_key(term.lower())

