from __future__ import annotations
import csv, re, collections, hashlib, json
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'Data' / 'ecdict.csv'
CSV_DIR = ROOT / 'CSV'
HEADER = ['单词', '音标', '中文释义（含词性）']
STAGES = ['基础英语词汇','通用英语核心词汇','大学英语词汇','雅思核心词汇','高阶学术英语词汇','综合拓展词汇']
QUOTAS = [2300,2300,2600,2600,2200,1800]
STAGE_FILES = [f'{i:02d}_{n}.csv' for i,n in enumerate(STAGES,1)]
POS = re.compile(r'^(n|v|vt|vi|a|adj|adv|pron|prep|conj|num|art|int|aux|det|abbr|modal v)\.(?:\s*|$)', re.I)
WORD = re.compile(r'^[a-z]+(?:-[a-z]+)?$')
BAD = re.compile(r'[�□◆◇]|\\x00')
BRIT_US = {'color':'colour','center':'centre','theater':'theatre','behavior':'behaviour','favor':'favour','favorite':'favourite','honor':'honour','labor':'labour','neighbor':'neighbour','organize':'organise','organization':'organisation','organise':'organise','analyze':'analyse','analysis':'analysis','recognize':'recognise','realize':'realise','apologize':'apologise','civilization':'civilisation','defense':'defence','offense':'offence','license':'licence','practice':'practise','traveling':'travelling','counseling':'counselling','program':'programme','catalog':'catalogue','dialog':'dialogue','gray':'grey','meter':'metre','liter':'litre','fiber':'fibre','pediatric':'paediatric','estrogen':'oestrogen','mustache':'moustache'}
KEEP_INFLECTED = {'building','understanding','concerning','given','outstanding','training','learning','reading','writing','thinking','meeting','beginning','ending','living','housing','working','following','leading','interesting','exciting','developed','developing','advanced','limited','related','used','based','affected','data','children','people','women','men','media','criteria','phenomena'}
CAPITALIZED_COMMON={'i','monday','tuesday','wednesday','thursday','friday','saturday','sunday','january','february','march','april','may','june','july','august','september','october','november','december','english','british','american','european','chinese','french','german','spanish','asian','african','australian','christian','christmas','internet'}

def rank(v):
    try: return int(v) if int(v)>0 else 999999
    except (ValueError,TypeError): return 999999

def clean_phonetic(s):
    s=s.strip().strip('/')
    # ECDICT uses an older transcription: ASCII apostrophe for primary stress,
    # Cyrillic ә for schwa, and colon for length. These are glyph conversions only.
    s=s.replace('ә','ə').replace('Ә','ə').replace("'",'ˈ').replace('`','ˌ').replace(':','ː')
    s=s.replace('ɡ','g')
    if not s or BAD.search(s) or re.search(r'[А-Яа-я0-9<>={}\\[\\]\\n]',s): return ''
    if ',' in s or ' -' in s or ';' in s: return ''
    if not re.fullmatch(r"[a-zA-Zəɪʊæɑɔʌɛɜɒɚɝθðʃʒŋɹɾɐɨɯʔˈˌː.()\- ]+",s): return ''
    return '/'+s+'/'

def clean_translation(s):
    parts=[]
    for line in s.replace('\\r\\n','\n').replace('\\n','\n').replace('\r','\n').split('\n'):
        line=line.strip()
        if not POS.match(line): continue
        line=re.sub(r'^a\.', 'adj.', line)
        line=re.sub(r'\s*[,，]\s*','；',line)
        line=line.replace('...', '……')
        line=re.sub(r'\s+',' ',line)
        line=re.sub(r'\s*；\s*','；',line).strip('； ')
        if BAD.search(line): continue
        # Keep at most six source senses per POS, preserving common secondary senses.
        senses=line.split('；')
        line='；'.join(senses[:7])
        if len(line)>220: line=line[:220].rsplit('；',1)[0]
        if re.search('[\u4e00-\u9fff]',line): parts.append(line)
    return '；'.join(parts[:5])

def stage_hint(r):
    tags=set(r['tag'].split())
    b,f=rank(r['bnc']),rank(r['frq'])
    m=min(b,f)
    ox=rank(r['oxford'])<999999
    if 'zk' in tags or (ox and m<=2400) or m<=1700: return 0
    if 'gk' in tags or (ox and m<=5500) or m<=4000: return 1
    if tags & {'cet4','cet6'} or m<=8000: return 2
    if 'ielts' in tags or tags & {'toefl','ky'} or m<=12500: return 3
    if tags & {'gre'} or m<=19000: return 4
    return 5

def quality_score(r):
    m=min(rank(r['bnc']),rank(r['frq']))
    tags=set(r['tag'].split())
    return (stage_hint(r), m, -len(tags), r['word'])

def main():
    if not RAW.exists(): raise SystemExit(f'Missing {RAW}. Run download_sources.py first.')
    CSV_DIR.mkdir(exist_ok=True)
    rows={}; rejected=collections.Counter(); raw_tags=collections.Counter(); raw_ox=0
    sha=hashlib.sha256()
    with open(RAW,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):sha.update(chunk)
    with open(RAW,encoding='utf-8',newline='') as f:
        reader=csv.DictReader(f)
        required={'word','phonetic','translation','pos','tag','oxford','collins','bnc','frq','exchange'}
        if not required.issubset(reader.fieldnames): raise ValueError(reader.fieldnames)
        for r in reader:
            w=r['word'].strip().lower()
            if not WORD.fullmatch(w) or len(w)>25 or len(w)<2 and w not in {'a','i'}:
                rejected['invalid_word']+=1;continue
            if r['word'][:1].isupper() and w not in CAPITALIZED_COMMON:
                rejected['proper_name_or_capitalized']+=1;continue
            if not r['tag'].strip() and re.search(r'（姓氏）|\(姓氏\)|（人名）|（地名）',r['translation'][:80]):
                rejected['proper_name_meaning']+=1;continue
            for t in r['tag'].split(): raw_tags[t]+=1
            if rank(r['oxford'])<999999:raw_ox+=1
            if w in BRIT_US and BRIT_US[w]!=w:
                rejected['us_variant']+=1;continue
            ex=dict(part.split(':',1) for part in r['exchange'].split('/') if ':' in part)
            if ex.get('0') and w not in KEEP_INFLECTED:
                rejected['inflection']+=1;continue
            ph=clean_phonetic(r['phonetic'])
            tr=clean_translation(r['translation'])
            if w=='a':
                tr='art. 一个；一（用于单数可数名词前）'
                ph='/ə/；/eɪ/'
            if w=='conduct':ph='/ˈkɒndʌkt/；/kənˈdʌkt/'
            if not ph or not tr:
                rejected['missing_or_invalid_pronunciation_or_meaning']+=1;continue
            if min(rank(r['bnc']),rank(r['frq']))>45000 and not r['tag'].strip() and not rank(r['oxford'])<999999:
                rejected['low_value']+=1;continue
            r['_phonetic']=ph;r['_translation']=tr;r['_word']=w
            if w not in rows or quality_score(r)<quality_score(rows[w]): rows[w]=r
    candidates=sorted(rows.values(),key=quality_score)
    # Stage quotas are planning targets. Fill each stage with highest ranked entries
    # whose evidence suggests that stage, then distribute remaining high-value words.
    buckets=[[] for _ in range(6)]; selected=set()
    for stage in range(6):
        for r in candidates:
            w=r['_word']
            if w in selected or stage_hint(r)>stage or len(buckets[stage])>=QUOTAS[stage]:continue
            buckets[stage].append(r);selected.add(w)
    for stage in range(6):
        for r in candidates:
            w=r['_word']
            if w in selected or len(buckets[stage])>=QUOTAS[stage]:continue
            if stage_hint(r)<=stage+1:
                buckets[stage].append(r);selected.add(w)
    for bucket in buckets:bucket.sort(key=lambda r:(min(rank(r['bnc']),rank(r['frq'])),r['_word']))
    def outrow(r):
        w=r['_word'];tr=r['_translation']
        aliases=[us for us,uk in BRIT_US.items() if uk==w and us!=w]
        if aliases:tr+=f'（美式拼写：{aliases[0]}）'
        return [w,r['_phonetic'],tr]
    def write_csv(path, records):
        with open(path,'w',encoding='utf-8-sig',newline='') as f:
            writer=csv.writer(f);writer.writerow(HEADER);writer.writerows(records)
    allrows=[]; meta=[];stats=[]
    for i,b in enumerate(buckets):
        output=[outrow(r) for r in b];write_csv(CSV_DIR/STAGE_FILES[i],output)
        allrows+=output;stats.append((STAGES[i],len(output)))
        for r in b:
            correction='user-provided pronunciation example' if r['_word']=='conduct' else ('Cambridge UK pronunciation and manual article gloss' if r['_word']=='a' else '')
            meta.append([r['_word'],STAGES[i],'ECDICT',r['tag'],r['oxford'],r['collins'],r['bnc'],r['frq'],r['exchange'],'user prompt example' if r['_word']=='conduct' else ('Cambridge Dictionary' if r['_word']=='a' else 'ECDICT phonetic (glyph-normalized)'), 'manual correction' if r['_word']=='a' else 'ECDICT translation (selected POS lines)',str(stage_hint(r)+1),correction])
    write_csv(CSV_DIR/'00_全部词汇总表.csv',allrows)
    with open(ROOT/'Data'/'vocabulary_metadata.csv','w',encoding='utf-8-sig',newline='') as f:
        wr=csv.writer(f);wr.writerow(['word','stage','source','tag','oxford','collins','bnc','frq','exchange','phonetic_source','translation_source','evidence_stage','correction']);wr.writerows(meta)
    wb=Workbook();intro=wb.active;intro.title='使用说明'
    for row in [['雅思 7.0—8.0 综合英语词汇库'],['基于 ECDICT 开源词典构建；非雅思官方词表。'],['音标来自 ECDICT，原始格式作字形标准化；未能保证全部为纯英式 IPA。'],['按基础到高阶学习；释义来自源词典，重要多义词仍建议查权威词典核对。'],['完整来源、限制和生成方法见 README.md。']]:intro.append(row)
    stat=wb.create_sheet('词汇统计');stat.append(['阶段','词条数'])
    for row in stats:stat.append(row)
    stat.append(['总计',len(allrows)])
    sheet_data=[('全部词汇总表',allrows)]+[(f'{i:02d} {name.replace("词汇","")}',[outrow(r) for r in buckets[i-1]]) for i,name in enumerate(STAGES,1)]
    sheet_data=[('全部词汇总表',allrows),('01 基础英语',[outrow(r) for r in buckets[0]]),('02 通用英语',[outrow(r) for r in buckets[1]]),('03 大学英语',[outrow(r) for r in buckets[2]]),('04 雅思核心',[outrow(r) for r in buckets[3]]),('05 高阶学术',[outrow(r) for r in buckets[4]]),('06 综合拓展',[outrow(r) for r in buckets[5]])]
    for name,data in sheet_data:
        ws=wb.create_sheet(name);ws.append(HEADER)
        for row in data:ws.append(row)
        ws.freeze_panes='A2';ws.auto_filter.ref=f'A1:C{ws.max_row}'
        for col,width in [('A',24),('B',32),('C',90)]:ws.column_dimensions[col].width=width
        ws.row_dimensions[1].height=28
        for c in ws[1]:c.fill=PatternFill('solid',fgColor='183B56');c.font=Font(color='FFFFFF',bold=True);c.alignment=Alignment(vertical='center')
        for row in ws.iter_rows(min_row=2):
            row[2].alignment=Alignment(wrap_text=True,vertical='top')
            if len(row[2].value)>90:ws.row_dimensions[row[0].row].height=34
    for ws in [intro,stat]:
        ws.column_dimensions['A'].width=85;ws.column_dimensions['B'].width=18
        ws['A1'].font=Font(bold=True,color='183B56',size=14)
    wb.save(ROOT/'IELTS_Vocabulary_Master.xlsx')
    manifest={'total':len(allrows),'stages':stats,'source_sha256':sha.hexdigest(),'source_bytes':RAW.stat().st_size,'rejected':dict(rejected),'source_tags':dict(raw_tags),'source_oxford_flag':raw_ox,'selected_tags':dict(collections.Counter(t for r in sum(buckets,[]) for t in r['tag'].split())),'selected_oxford_flag':sum(rank(r['oxford'])<999999 for r in sum(buckets,[]))}
    (ROOT/'Data'/'build_stats.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
