def search(q,offset=0):
 p={'action':'query','generator':'search','gsrsearch':q,'gsrnamespace':6,'gsrlimit':50,'gsroffset':offset,'prop':'imageinfo|categories','iiprop':'url|extmetadata|mime|size','iiurlwidth':560,'cllimit':'max','format':'json','formatversion':2}
 data=api(p)
 return (data.get('query') or {}).get('pages') or []
