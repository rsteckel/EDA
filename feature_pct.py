import simplejson as json
import re

with open('/Users/rsteckel/Downloads/concept_export.json', 'r') as oldf:
    oldj = json.load(oldf)
    
with open('/Users/rsteckel/Downloads/concept_export (1).json', 'r') as newf:
    newj = json.load(newf)
    


for i in range(len(oldj)):
    print 'old', oldj[i]['id'], 'new', newj[i]['id']
    
    newj[i]['digital_total_pct'] = oldj[i]['digital_signal']



with open('/tmp/concept_export_new.json', 'w') as outf:
    outf.write(json.dumps(newj, sort_keys=True, indent=4))
    outf.flush()
    




terms,weights = load_term_vector('couture')

term_map = {}
for term in terms:
    term_map[term] = True

#0418084847761
#
#fitted
#feminine
#chic
#spring
#weddings
#sleeves
#
desc1 = """A soft cowlneck and enchanting rose print make this fitted dress a statement 
        in feminine chic, the perfect choice for garden parties and spring weddings. 
        Cowlneck Short sleeves Lined Pullover style About 27" from natural waist 
        Polyamide Dry clean Made in Italy"""

fitted, feminine, chic, spring, weddings, sleeves

couture: 0.9884954
feature_pct: 16%

#0478903722853


desc2 = """This body-skimming stretch jersey dress is shaped with beautiful draped 
        ruching for an effortlessly elegant effect. Three-quarter sleeves Ruched 
        along side Draped ruched panel from waist Side overlay panel from waist Pullover 
        style About 22" from natural waist Rayon/spandex Dry clean Made in USA"""

elegant
sleeves

couture: .14

tokens = re.findall('[a-z]+', desc2.lower())

for t in tokens:
    if term_map.has_key(t):
        print t
