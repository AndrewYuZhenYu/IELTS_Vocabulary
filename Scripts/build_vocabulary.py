from __future__ import annotations
import csv, re, collections, hashlib, json
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from oxford_reference import load_oxford

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'Data' / 'ecdict.csv'
CSV_DIR = ROOT / 'CSV'
HEADER = ['单词', '音标', '中文释义（含词性）']
STAGES = ['基础英语词汇','通用英语核心词汇','大学英语词汇','雅思核心词汇','高阶学术英语词汇','综合拓展词汇']
QUOTAS = [2300,2300,2600,2600,2200,1800]
STAGE_FILES = [f'{i:02d}_{n}.csv' for i,n in enumerate(STAGES,1)]
POS = re.compile(r'^(n|v|vt|vi|a|adj|adv|pron|prep|conj|num|art|int|interj|aux|det|abbr|pl|modal v)\.(?:\s*|$)', re.I)
WORD = re.compile(r'^[a-z]+(?:-[a-z]+)?$')
BAD = re.compile(r'[�□◆◇]|\\x00')
BRIT_US = {'color':'colour','center':'centre','theater':'theatre','behavior':'behaviour','favor':'favour','favorite':'favourite','honor':'honour','labor':'labour','neighbor':'neighbour','organize':'organise','organization':'organisation','organise':'organise','analyze':'analyse','analysis':'analysis','recognize':'recognise','realize':'realise','apologize':'apologise','civilization':'civilisation','defense':'defence','offense':'offence','license':'licence','practice':'practise','traveling':'travelling','counseling':'counselling','program':'programme','catalog':'catalogue','dialog':'dialogue','gray':'grey','meter':'metre','liter':'litre','fiber':'fibre','pediatric':'paediatric','estrogen':'oestrogen','mustache':'moustache'}
# These pairs can differ by meaning or grammatical role in British English.
for ambiguous in ('license','practice','program','meter','analysis'):
    BRIT_US.pop(ambiguous,None)
BRIT_US['organized']='organised'
BRIT_US['flavor']='flavour'
KEEP_INFLECTED = {'building','understanding','concerning','given','outstanding','training','learning','reading','writing','thinking','meeting','beginning','ending','living','housing','working','following','leading','interesting','exciting','developed','developing','advanced','limited','related','used','based','affected','data','children','people','women','men','media','criteria','phenomena'}
CAPITALIZED_COMMON={'i','monday','tuesday','wednesday','thursday','friday','saturday','sunday','january','february','march','april','may','june','july','august','september','october','november','december','english','british','american','european','chinese','french','german','spanish','asian','african','australian','christian','christmas','internet'}
CAMBRIDGE_SUPPLEMENTS={
    'blog':('/blɒɡ/',None),'bored':('/bɔːd/','adj. 感到无聊的；厌倦的'),
    'girlfriend':('/ˈɡɜːl.frend/',None),'online':('/ˈɒn.laɪn/；/ˌɒnˈlaɪn/','adj. 在线的；adv. 在线地'),
    't-shirt':('/ˈtiː.ʃɜːt/',None),'thanks':('/θæŋks/',None),
    'tv':('/ˌtiːˈviː/','abbr. 电视；电视机'),'website':('/ˈweb.saɪt/',None),
    'app':('/æp/','n. 应用程序；手机应用'),'divorced':('/dɪˈvɔːst/',None),
    'download':('/ˈdaʊn.ləʊd/；/ˌdaʊnˈləʊd/','n. 下载文件；v. 下载'),
    'exactly':('/ɪɡˈzækt.li/',None),'god':('/ɡɒd/','n. 神；上帝'),
    'including':('/ɪnˈkluː.dɪŋ/',None),'laptop':('/ˈlæp.tɒp/','n. 笔记本电脑'),
    'smartphone':('/ˈsmɑːt.fəʊn/',None),
    'ai':('/ˌeɪˈaɪ/','abbr. 人工智能'),
    'annoyed':('/əˈnɔɪd/',None),'associated':('/əˈsəʊ.si.eɪ.tɪd/',None),
    'confusing':('/kənˈfjuː.zɪŋ/',None),'curved':('/kɜːvd/',None),
    'directly':('/daɪˈrekt.li/',None),'expected':('/ɪkˈspek.tɪd/',None),
    'funding':('/ˈfʌn.dɪŋ/','n. 资金；资助'),
    'long-term':('/ˌlɒŋˈtɜːm/',None),
    'organised':('/ˈɔː.ɡən.aɪzd/',None),
    'planning':('/ˈplæn.ɪŋ/',None),'podcast':('/ˈpɒd.kɑːst/',None),
    'relaxing':('/rɪˈlæk.sɪŋ/',None),'rugby':('/ˈrʌɡ.bi/',None),
    'significantly':('/sɪɡˈnɪf.ɪ.kənt.li/',None),
}
OXFORD_SUPPLEMENTS={
    'located':('/ləʊˈkeɪtɪd/',None),
    'photographer':('/fəˈtɒɡrəfə(r)/',None),
    'impressed':('/ɪmˈprest/','adj. 印象深刻的；钦佩的'),
}

def rank(v):
    try: return int(v) if int(v)>0 else 999999
    except (ValueError,TypeError): return 999999

def clean_phonetic(s):
    s=s.strip().strip('/')
    # ECDICT's legacy transcription uses Cyrillic lookalikes and ASCII vowel
    # digraphs. Convert only documented, recognizable patterns; reject others.
    s=s.replace('ә:','ɜː').replace('әː','ɜː')
    s=s.replace('є','e').replace('ε','e').replace('ә','ə').replace('Ә','ə')
    s=s.replace('ɑ:','ɑː').replace('ɔ:','ɔː').replace('ɒ:','ɔː').replace('i:','iː').replace('u:','uː')
    s=s.replace('ei','eɪ').replace('ai','aɪ').replace('ɔi','ɔɪ').replace('au','aʊ').replace('ou','əʊ')
    s=s.replace('əu','əʊ').replace('iə','ɪə').replace('uə','ʊə')
    s=re.sub(r'i(?!ː|$)','ɪ',s)
    s=re.sub(r'u(?!ː|$)','ʊ',s)
    s=s.replace("'",'ˈ').replace('`','ˌ').replace(':','ː')
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
        line=re.sub(r'^interj\.', 'int.', line)
        line=re.sub(r'^pl\.', 'n.', line)
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
    level=r.get('_oxford_level')
    if level in {'A1','A2'}:return 0
    if level=='B1':return 1
    if level=='B2':return 2
    if level=='C1':return 4
    if r.get('_baseline_stage') is not None:return r['_baseline_stage']
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
    ox3000,ox5000,oxford,ox_phrases=load_oxford()
    with open(ROOT/'Data'/'baseline_stage.csv',encoding='utf-8',newline='') as f:
        baseline={r['word']:int(r['stage']) for r in csv.DictReader(f)}
    CSV_DIR.mkdir(exist_ok=True)
    rows={}; rejected=collections.Counter(); source_tag_words=collections.defaultdict(set); source_ox_words=set()
    sha=hashlib.sha256()
    with open(RAW,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):sha.update(chunk)
    with open(RAW,encoding='utf-8',newline='') as f:
        reader=csv.DictReader(f)
        required={'word','phonetic','translation','pos','tag','oxford','collins','bnc','frq','exchange'}
        if not required.issubset(reader.fieldnames): raise ValueError(reader.fieldnames)
        for r in reader:
            raw_word=r['word'].strip().lower()
            w=BRIT_US.get(raw_word,raw_word)
            if not WORD.fullmatch(raw_word) or len(raw_word)>25 or len(raw_word)<2 and raw_word not in {'a','i'}:
                rejected['invalid_word']+=1;continue
            if r['word'][:1].isupper() and w not in CAPITALIZED_COMMON and raw_word not in oxford and w not in oxford:
                rejected['proper_name_or_capitalized']+=1;continue
            if not r['tag'].strip() and re.search(r'（姓氏）|\(姓氏\)|（人名）|（地名）',r['translation'][:80]):
                rejected['proper_name_meaning']+=1;continue
            for t in r['tag'].split():source_tag_words[t].add(w)
            if rank(r['oxford'])<999999:source_ox_words.add(w)
            if raw_word!=w:rejected['normalized_us_variant']+=1
            ex=dict(part.split(':',1) for part in r['exchange'].split('/') if ':' in part)
            oxlevel=(oxford.get(raw_word) or oxford.get(w) or (None,None))[0]
            if ex.get('0') and ex['0']!=raw_word and w not in KEEP_INFLECTED and not oxlevel:
                rejected['inflection']+=1;continue
            ph=clean_phonetic(r['phonetic'])
            tr=clean_translation(r['translation'])
            if w=='a':
                tr='art. 一个；一（用于单数可数名词前）'
                ph='/ə/；/eɪ/'
            if w=='conduct':ph='/ˈkɒndʌkt/；/kənˈdʌkt/'
            if w=='internet' and not tr:tr='n. 互联网；因特网'
            if w in CAMBRIDGE_SUPPLEMENTS:
                ph,override=CAMBRIDGE_SUPPLEMENTS[w]
                if override:tr=override
            if w in OXFORD_SUPPLEMENTS:
                ph,override=OXFORD_SUPPLEMENTS[w]
                if override:tr=override
            if not ph or not tr:
                rejected['missing_or_invalid_pronunciation_or_meaning']+=1;continue
            if min(rank(r['bnc']),rank(r['frq']))>45000 and not r['tag'].strip() and not rank(r['oxford'])<999999 and not oxlevel:
                rejected['low_value']+=1;continue
            r['_phonetic']=ph;r['_translation']=tr;r['_word']=w;r['_oxford_level']=oxlevel
            r['_baseline_stage']=baseline.get(w)
            if w not in rows or quality_score(r)<quality_score(rows[w]): rows[w]=r
    for w,r in rows.items():
        r['tag']=' '.join(sorted(t for t,words in source_tag_words.items() if w in words))
        if w in source_ox_words:r['oxford']='1'
    candidates=sorted(rows.values(),key=quality_score)
    # Preserve previously published learning entries, then add Oxford headwords
    # that have usable ECDICT pronunciations and meanings.
    buckets=[[] for _ in range(6)]; selected=set()
    for r in candidates:
        if r['_oxford_level'] or r['_baseline_stage'] is not None:
            stage=stage_hint(r);buckets[stage].append(r);selected.add(r['_word'])
    # Stage targets are advisory. Do not add unrelated low-value entries merely
    # to refill stages after authoritative CEFR evidence moves a baseline word.
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
            w=r['_word']
            correction='user-provided pronunciation example' if w=='conduct' else ('Cambridge UK pronunciation and manual article gloss' if w=='a' else ('Oxford Learner Dictionary UK pronunciation verification' if w in OXFORD_SUPPLEMENTS else ('Cambridge UK pronunciation verification' if w in CAMBRIDGE_SUPPLEMENTS else ('manual internet gloss' if w=='internet' else ''))))
            phon_source='user prompt example' if w=='conduct' else ('Oxford Learner Dictionary' if w in OXFORD_SUPPLEMENTS else ('Cambridge Dictionary' if w=='a' or w in CAMBRIDGE_SUPPLEMENTS else 'ECDICT phonetic (normalized)'))
            trans_source='manual correction' if w in {'a','internet'} or (w in CAMBRIDGE_SUPPLEMENTS and CAMBRIDGE_SUPPLEMENTS[w][1]) or (w in OXFORD_SUPPLEMENTS and OXFORD_SUPPLEMENTS[w][1]) else 'ECDICT translation (selected POS lines)'
            phon_url=('https://dictionary.cambridge.org/pronunciation/english/'+('organized' if w=='organised' else w)) if phon_source=='Cambridge Dictionary' else (('https://www.oxfordlearnersdictionaries.com/definition/english/'+w) if phon_source=='Oxford Learner Dictionary' else ('https://github.com/skywind3000/ECDICT' if phon_source.startswith('ECDICT') else '用户提供的任务文字'))
            meta.append([w,STAGES[i],'ECDICT',r['tag'],r['oxford'],r['collins'],r['bnc'],r['frq'],r['exchange'],phon_source,phon_url,trans_source,str(stage_hint(r)+1),correction,r['word']])
    write_csv(CSV_DIR/'00_全部词汇总表.csv',allrows)
    with open(ROOT/'Data'/'vocabulary_metadata.csv','w',encoding='utf-8-sig',newline='') as f:
        wr=csv.writer(f);wr.writerow(['word','stage','source','tag','oxford','collins','bnc','frq','exchange','phonetic_source','phonetic_source_url','translation_source','evidence_stage','correction','source_word']);wr.writerows(meta)
    wb=Workbook();intro=wb.active;intro.title='使用说明'
    for row in [['雅思 7.0—8.0 综合英语词汇库'],['词条底库为 ECDICT；Oxford 官方词表 PDF 用于本地比对和阶段调整。非雅思官方词表。'],['大部分音标来自 ECDICT 旧式转写；未能保证全部为纯英式 IPA。'],['按基础到高阶学习；释义来自源词典，重要多义词仍建议查权威词典核对。'],['完整来源、限制和生成方法见 README.md。']]:intro.append(row)
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
    chosen={r['_word'] for r in sum(buckets,[])}
    canonical=lambda w:BRIT_US.get(w,w)
    def covered(ref):return sum(canonical(w) in chosen for w in ref)
    manifest={'total':len(allrows),'stages':stats,'source_sha256':sha.hexdigest(),'source_bytes':RAW.stat().st_size,'rejected':dict(rejected),'source_tags':{t:len(words) for t,words in source_tag_words.items()},'source_oxford_flag':len(source_ox_words),'selected_tags':{t:len(words&chosen) for t,words in source_tag_words.items()},'selected_oxford_flag':len(source_ox_words&chosen),'oxford_official':{'oxford3000_single_headwords':len(ox3000),'oxford3000_covered':covered(ox3000),'oxford5000_extension_single_headwords':len(ox5000),'oxford5000_extension_covered':covered(ox5000),'excluded_phrases_or_noncanonical_labels':len(ox_phrases)}}
    (ROOT/'Data'/'build_stats.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
