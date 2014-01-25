# -*- coding: utf-8 -*-
import urllib
import urllib2
import simplejson as json
 
BASE_SEARCH_URL = 'https://api.datamarket.azure.com/Bing/SearchWeb/v1/'
 
#remove duplicates preserving order
def remove_duplicates(result_list):
    seen = set()
    seen_add = seen.add
    return [ x for x in result_list if x not in seen and not seen_add(x)]    
 
 
def bing_search(query, search_type, num_results=50):
    #search_type: Web, Image, News, Video
    key = 'EGtQ4MxfZzaiNN0fJOv/Mf3ev5MZi3GKr08kPizIe/4='
    
    query = urllib.quote(query)

    user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
    credentials = (':%s' % key).encode('base64')[:-1]
    auth = 'Basic %s' % credentials
    
    result_count = 0
    offset = 0
    urls = []
    while result_count < num_results:
        #Can only get 50 at a time
        url = BASE_SEARCH_URL+search_type+'?Query=%27'+query+'%27&$top=50&$format=json&$skip='+str(offset)
        offset += 50
        result_count += 50

        request = urllib2.Request(url)
        request.add_header('Authorization', auth)
        request.add_header('User-Agent', user_agent)
        request_opener = urllib2.build_opener()
        response = request_opener.open(request) 
        response_data = response.read()    
    
        json_result = json.loads(response_data)    
        result_list = json_result['d']['results']
    
        for result in result_list:
            urls.append(result['Url'])
    
    
    return remove_duplicates(urls)
 
    