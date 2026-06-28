import csv,html,json,os,re,shutil,time,unicodedata
from pathlib import Path
import pycountry,requests
from babel import Locale
from PIL import Image,ImageOps
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT=Path(__file__).parent
BATCH=int(os.environ.get('BATCH_ID','0'));SIZE=int(os.environ.get('BATCH_SIZE','10'))
OUT=ROOT/'out'/f'batch-{BATCH:02d}';IMG=OUT/'images';OUT.mkdir(parents=True,exist_ok=True);IMG.mkdir(parents=True,exist_ok=True)
API='https://commons.wikimedia.org/w/api.php';S=requests.Session();S.headers['User-Agent']='GeoHintsPhotoAtlas/1.0 educational project'
ES=Locale('es')
CATS=['Arquitectura','Bolardos','Generaciones de cámara','Países y cobertura','Monedas','Dominios','Lado de conducción','Banderas','Vehículos seguidores','Animales','ATV','Barcos','Teleféricos','Automóviles','Motocicletas','Otros vehículos','Motos de nieve','Trenes','Números de casa','Matrículas','Líneas viales','Números telefónicos','Buzones','Aceras','Semáforos','Postes eléctricos','Naturaleza','Paisajes','Advertencia de animales','Reverso de señales','Paradas de autobús','Cheurones','Señales de ciudad','Direcciones','Peatones','Cruces ferroviarios','Ríos','Numeración vial','Postes de señal','Velocidad','Stop','Nombres de calles','Velocidad de tranvía','Paradas de tranvía','Ceda el paso','Rifts y anomalías','Nieve','Años de captura','Sufijos de calles','Cervezas y marcas','Gasolineras','Empresas postales']
KEYS=['architecture building house','bollard delineator roadside post','street view camera panorama','street road city village','banknote coin currency','website domain shop sign','traffic driving road cars','flag flying building','escort convoy vehicle','animal cattle livestock wildlife','all terrain quad ATV','boat ferry harbour ship','cable car gondola ropeway','car automobile traffic','motorcycle scooter motorbike','bus truck taxi transport','snowmobile snow vehicle','train railway station','house number address','license registration plate','road marking lane highway','telephone phone number sign','post box mailbox','sidewalk pavement curb','traffic light signal intersection','utility pole power line','nature forest vegetation flora','landscape scenery countryside','animal warning sign','back rear traffic sign','bus stop shelter','chevron curve road sign','town city village entrance sign','direction arrow road sign','pedestrian zebra crossing','railway level crossing','river bridge waterway','route number highway shield','traffic sign post pole','speed limit sign','stop sign traffic','street road name sign','tram speed tramway','tram stop station','yield give way sign','street view glitch panorama artifact','snow winter road','historic old dated photograph','street road name abbreviation','beer brewery advertisement','petrol gas fuel station','post office postal service']
BROAD=['street road city architecture','transport traffic signs vehicles','nature landscape coast river','town village buildings shops','public space station harbour','historic photograph countryside']
BAD=['locator map','location map','administrative map','route map','diagram','drawing','illustration','icon','template','logo','coat of arms','blank map','silhouette','svg']

def norm(v):
 v=html.unescape(re.sub('<[^>]+>',' ',v or ''));v=unicodedata.normalize('NFKD',v).encode('ascii','ignore').decode().lower();return re.sub('[^a-z0-9]+',' ',v).strip()
def clean(v):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',v or ''))).strip()
def mv(m,k):return clean((m.get(k) or {}).get('value',''))
def allowed(m):
 z=norm(mv(m,'LicenseShortName') or mv(m,'UsageTerms'));return bool(z) and any(x in z for x in ['cc0','public domain','cc by','cc-by','attribution','pdm']) and 'noncommercial' not in z and 'no derivatives' not in z
def api(p):
 delay=1
 for _ in range(7):
  try:
   r=S.get(API,params=p,timeout=60)
   if r.status_code==200:time.sleep(.25);return r.json()
   if r.status_code==429:delay=max(delay,int(r.headers.get('Retry-After','8')))
  except Exception:pass
  time.sleep(delay);delay=min(delay*2,40)
 return {}
def countries():
 out=[]
 for c in pycountry.countries:
  code=c.alpha_2;name=ES.territories.get(code,c.name);aliases=list({c.name,name,getattr(c,'official_name',''),getattr(c,'common_name','')}-set(['']))
  out.append({'code':code,'name':name,'english':c.name,'aliases':aliases})
 out.append({'code':'XK','name':'Kosovo','english':'Kosovo','aliases':['Kosovo','Republic of Kosovo']})
 return sorted(out,key=lambda x:norm(x['name']))
