import csv,json,os
from pathlib import Path
from pypdf import PdfReader,PdfWriter
ROOT=Path(__file__).parent;DOWNLOAD=Path(os.environ.get('DOWNLOAD_DIR',ROOT/'downloaded'));OUT=ROOT/'final';OUT.mkdir(parents=True,exist_ok=True)
PDF=OUT/'Guia_GeoHints_V10_Atlas_Fotografico_250_Paises.pdf';AUDIT=OUT/'Guia_GeoHints_V10_Auditoria_Global.json';TABLE=OUT/'Guia_GeoHints_V10_Fuentes_Global.csv'
def files(pattern):return sorted(DOWNLOAD.rglob(pattern),key=lambda p:p.name)
def main():
 pdfs=files('GeoHints_Fotos_Batch_*.pdf');audits=files('GeoHints_Auditoria_Batch_*.json');tables=files('GeoHints_Fuentes_Batch_*.csv')
 if not(len(pdfs)==len(audits)==len(tables)==25):raise SystemExit(f'Expected 25 batches: {len(pdfs)}/{len(audits)}/{len(tables)}')
 writer=PdfWriter();pages=0
 for path in pdfs:
  reader=PdfReader(str(path));pages+=len(reader.pages)
  for page in reader.pages:writer.add_page(page)
 writer.add_metadata({'/Title':'Guía GeoHints V10 - Atlas fotográfico de 250 países y territorios','/Author':'Bastián Lisboa'})
 with PDF.open('wb') as handle:writer.write(handle)
 batches=[json.loads(path.read_text(encoding='utf-8')) for path in audits];batches.sort(key=lambda x:int(x['batch_id']));countries=[];items=[]
 for batch in batches:countries.extend(batch.get('countries',[]));items.extend(batch.get('items',[]))
 summary={'edition':'V10 - atlas fotográfico global','countries_and_territories':len(countries),'categories_per_country':52,'total_reference_cards':len(countries)*52,'exact_country_category_photos':sum(x.get('exact_photos',0) for x in batches),'contextual_real_photos_from_correct_country':sum(x.get('contextual_country_photos',0) for x in batches),'cards_without_verified_photo':sum(x.get('missing_photos',0) for x in batches),'unique_photos':sum(x.get('unique_photos',0) for x in batches),'reused_cards':sum(x.get('reused_cards',0) for x in batches),'generated_or_illustrated_images':0,'pdf_pages':pages,'pdf_file':PDF.name,'source':'Wikimedia Commons','batches':[{'batch_id':x['batch_id'],'countries':len(x.get('countries',[])),'exact':x.get('exact_photos',0),'contextual':x.get('contextual_country_photos',0),'missing':x.get('missing_photos',0),'unique':x.get('unique_photos',0),'reused':x.get('reused_cards',0)} for x in batches],'countries':countries,'items':items}
 AUDIT.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
 with TABLE.open('w',newline='',encoding='utf-8-sig') as out:
  w=csv.writer(out);first=True
  for path in tables:
   with path.open('r',newline='',encoding='utf-8-sig') as src:
    r=csv.reader(src);header=next(r,None)
    if first and header:w.writerow(header);first=False
    w.writerows(r)
 print(json.dumps({'pdf':str(PDF),'bytes':PDF.stat().st_size,'countries':len(countries),'cards':len(countries)*52,'exact':summary['exact_country_category_photos'],'contextual':summary['contextual_real_photos_from_correct_country'],'missing':summary['cards_without_verified_photo'],'unique':summary['unique_photos'],'reused':summary['reused_cards'],'pages':pages},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
