import urllib2


def clean_pages(pages):
    documents = []    
    for i in range(len(pages)):
        doc = pages[i].lower()

        try:                            
            decoded_page = doc.decode(encoding, errors='ignore')
            
            text = nltk.clean_html(decoded_page)            
            
            utf8_text = text.encode('utf-8')
            
            text_page = utf8_text.translate(replace_punctuation)

            words = re.findall('[a-z]+', text_page)            

            #check words???

            documents.append( ' '.join(words) )        
        except UnicodeError:
            print "string is not UTF-8"
            
    return documents          



http://www.srussellgroves.com/01%20STUDIO/S%20RUSSELL%20GROVES%20PROFILE.pdf

t http://www.furniture-ma.com/Gamma-Arredamenti-Furniture-l1-c-122/?page=4
http://www.brettdesigninc.com/fullsite.html
http://www.stepevi.com/i/content/171_1_January2011-IMMCologne.doc
http://www.couturefashionweek.com/news.htm
http://www.modernopticalny.com/FramesandSunglasses.php
http://www.jeffreycourt.com/faqs.asp
http://nymag.com/weddings/listings/flowers/index3.html
http://www.finelineslingerie.com.au/
http://www.i-escape.com/argentina/boutique-hotels
http://bellevuecollection.com/FashionWeek/TicketsSchedule.php
http://www.safilo.com/en/2-max-mara.php
http://www.pastichenashville.com/pages/vendors.php?id=1
http://www.brettdesigninc.com/fullsite.html
http://www.furniture-ma.com/Gamma-Arredamenti-Furniture-l1-c-122/?page=4
http://www.blindalley.com/portfolios/hunterdouglas/luminette.html
http://www.theblindalley.com/portfolios/hunterdouglas/vignette.html
http://www.modernopticalny.com/FramesandSunglasses.php
http://www.couturefashionweek.com/news.htm



url = 'http://www.dolmetsch.com/defsd2.htm'
response = urllib2.urlopen(url)
html = response.read()

charset = response.headers.getparam('charset')   
charset == None

char_detection = chardet.detect(html)
encoding = char_detection['encoding']

html.decode('ISO-8859-2')

clean_pages( [html,] )