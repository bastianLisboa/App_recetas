def page_item(page,country):
 info=(page.get('imageinfo') or [{}])[0]
 meta=info.get('extmetadata') or {}
 mime=str(info.get('mime','')).lower()
 if mime not in {'image/jpeg','image/webp'} or not allowed(meta):
  return None
 cats=' '.join(x.get('title','') for x in page.get('categories') or [])
 text=' '.join([page.get('title',''),cats,mv(meta,'ImageDescription'),mv(meta,'ObjectName'),mv(meta,'Categories'),mv(meta,'Credit')])
 z=norm(text)
 if any(x in z for x in BAD):
  return None
 aliases=[norm(x) for x in country['aliases'] if len(norm(x))>=4]
 if not any(alias in z for alias in aliases):
  return None
 w=int(info.get('width') or 0);h=int(info.get('height') or 0)
 if min(w,h) and min(w,h)<180:
  return None
 return {'base_score':min(w*h/1500000,10),'text':z,'title':page.get('title','').replace('File:',''),'image_url':info.get('thumburl') or info.get('url'),'source_url':info.get('descriptionurl') or info.get('url'),'author':mv(meta,'Artist') or mv(meta,'Credit') or 'Autor indicado en Wikimedia Commons','license':mv(meta,'LicenseShortName') or mv(meta,'UsageTerms')}
