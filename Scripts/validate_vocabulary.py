from __future__ import annotations
import csv, re, json, collections
from pathlib import Path
from openpyxl import load_workbook
from build_vocabulary import BRIT_US, KEEP_INFLECTED, clean_phonetic, clean_translation
from oxford_reference import load_oxford

ROOT=Path(__file__).resolve().parents[1]
CSV_DIR=ROOT/'CSV'
FILES=['00_全部词汇总表.csv','01_基础英语词汇.csv','02_通用英语核心词汇.csv','03_大学英语词汇.csv','04_雅思核心词汇.csv','05_高阶学术英语词汇.csv','06_综合拓展词汇.csv']
SHEETS=['全部词汇总表','01 基础英语','02 通用英语','03 大学英语','04 雅思核心','05 高阶学术','06 综合拓展']
POS=re.compile(r'(?:^|；)(?:n|v|vt|vi|adj|adv|pron|prep|conj|num|art|int|aux|det|abbr|modal v)\.',re.I)
WORD=re.compile(r'^[a-z]+(?:-[a-z]+)?$')
PHON=re.compile(r'^/[a-zA-Zəɪʊæɑɔʌɛɜɒɚɝθðʃʒŋɹɾɐɨɯʔɡˈˌː.()\- ]+/(?:；/[a-zA-Zəɪʊæɑɔʌɛɜɒɚɝθðʃʒŋɹɾɐɨɯʔɡˈˌː.()\- ]+/)*$')
def read(path):
    with open(path,encoding='utf-8-sig',newline='') as f:
        rows=list(csv.reader(f))
    assert rows[0]==['单词','音标','中文释义（含词性）'],(path,rows[0])
    assert all(len(x)==3 for x in rows)
    return rows[1:]
def main():
    ox3000,ox5000,oxford,_=load_oxford()
    data=[read(CSV_DIR/x) for x in FILES]
    issues=[]
    def issue(kind,word,detail):issues.append((kind,word,detail))
    master=data[0];stages=data[1:]
    if master!=sum(stages,[]):issue('master_mismatch','','总表与分阶段拼接不一致')
    allwords=[r[0] for r in master]
    for w,n in collections.Counter(allwords).items():
        if n>1:issue('duplicate',w,str(n))
    for row in master:
        w,p,t=row
        if not w or not p or not t:issue('empty_field',w,str(row))
        if not WORD.fullmatch(w):issue('invalid_word',w,'拼写格式异常')
        if not PHON.fullmatch(p):issue('invalid_phonetic',w,p)
        if not POS.search(t):issue('missing_pos',w,t[:80])
        if '�' in ''.join(row):issue('replacement_character',w,'包含乱码替换字符')
    meta=read_meta()
    if len(meta)!=len(master):issue('metadata_count','','元数据条数不一致')
    for w in allwords:
        if w not in meta:issue('missing_provenance',w,'元数据中缺失')
        else:
            ex=meta[w].get('exchange','')
            lemma=next((x.split(':',1)[1] for x in ex.split('/') if x.startswith('0:')),None)
            if lemma and lemma!=meta[w].get('source_word',w).lower() and w not in KEEP_INFLECTED and w not in oxford and meta[w].get('source_word','').lower() not in oxford:
                issue('unnecessary_inflection',w,ex)
            if not meta[w].get('source'):
                issue('missing_provenance',w,'来源字段为空')
            try:
                b=int(meta[w].get('bnc') or 0);f=int(meta[w].get('frq') or 0)
                if (b==0 or b>45000) and (f==0 or f>45000) and not meta[w].get('tag') and not meta[w].get('oxford') and w not in oxford:
                    issue('low_frequency_no_evidence',w,f'bnc={b}; frq={f}')
            except ValueError:issue('invalid_rank',w,'词频字段非整数')
    for us,uk in BRIT_US.items():
        if us!=uk and us in allwords and uk in allwords:issue('us_uk_duplicate',us,uk)
    wb=load_workbook(ROOT/'IELTS_Vocabulary_Master.xlsx',read_only=True,data_only=True)
    for i,sheet in enumerate(SHEETS):
        actual=[[str(x or '') for x in r] for r in wb[sheet].iter_rows(values_only=True)]
        if actual[0]!=['单词','音标','中文释义（含词性）'] or actual[1:]!=data[i]:
            issue('xlsx_csv_mismatch',sheet,'XLSX 与 CSV 不一致')
    wb.close()
    stage_counts=[len(x) for x in stages]
    if sum(stage_counts)!=len(master):issue('count_mismatch','','阶段数量不等于总表')
    stats=json.loads((ROOT/'Data'/'build_stats.json').read_text(encoding='utf-8'))
    official=stats['oxford_official']
    canonical=lambda w:BRIT_US.get(w,w)
    if official['oxford3000_covered']!=sum(canonical(w) in allwords for w in ox3000):issue('oxford_coverage_mismatch','Oxford 3000','统计值与复算不一致')
    if official['oxford5000_extension_covered']!=sum(canonical(w) in allwords for w in ox5000):issue('oxford_coverage_mismatch','Oxford 5000','统计值与复算不一致')
    missing={w for w in oxford if canonical(w) not in allwords}
    source={}
    with open(ROOT/'Data'/'ecdict.csv',encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f):
            w=r['word'].lower()
            if w in missing:source[w]=r
    omission=collections.defaultdict(list)
    for w in sorted(missing):
        r=source.get(w)
        reason='ECDICT 无词条' if not r else ('缺少可用音标' if not clean_phonetic(r['phonetic']) else ('缺少带词性的中文释义' if not clean_translation(r['translation']) else '其他筛选规则'))
        omission[reason].append(w)
    with open(ROOT/'Data'/'exceptions.csv','w',encoding='utf-8-sig',newline='') as f:
        out=csv.writer(f);out.writerow(['问题类型','单词','详情']);out.writerows(issues)
    lines=['# 质量检查报告','',f'- 总表：{len(master)} 词',f'- 六阶段：{stage_counts}',f'- 阶段之和：{sum(stage_counts)} 词',f'- 自动检查异常：{len(issues)} 项','- CSV 与 XLSX：已逐单元格比较','- 所有文件：已由 csv / openpyxl 重新读取','', '## 检查范围','', '检查三列结构、空值、词性标记、音标字符、拼写格式、乱码、重复、元数据来源、数量对账与 XLSX/CSV 一致性。词形变化由构建脚本依据 ECDICT exchange 处理；英美差异仅处理明确映射。语义正确性、纯英式音标、低频词实际价值均无法通过自动规则完全保证。','', '## 数据来源覆盖','']
    tags=stats['source_tags'];selected=stats['selected_tags']
    for key,label in [('zk','中考（ECDICT 标签）'),('gk','高考（ECDICT 标签）'),('cet4','CET-4（ECDICT 标签）'),('cet6','CET-6（ECDICT 标签）'),('ielts','IELTS（ECDICT 标签）'),('toefl','TOEFL（ECDICT 标签）')]:
        n=tags.get(key,0);s=selected.get(key,0)
        lines.append(f'- {label}：{s}/{n}，{(s/n*100 if n else 0):.1f}%（分母为 ECDICT 中具有该标签的规范英文词形，不是独立官方词表）')
    o=stats['source_oxford_flag'];sel=stats['selected_oxford_flag']
    lines.append(f'- ECDICT Oxford 3000 标记：{sel}/{o}，{(sel/o*100 if o else 0):.1f}%（不是当前 Oxford 3000 官方表的独立核验）')
    lines.append(f'- Oxford 官网 PDF：Oxford 3000 单词词头 {official["oxford3000_covered"]}/{official["oxford3000_single_headwords"]}；Oxford 5000 追加单词词头 {official["oxford5000_extension_covered"]}/{official["oxford5000_extension_single_headwords"]}。PDF 中多词短语与非规范标签另计 {official["excluded_phrases_or_noncanonical_labels"]} 项，未纳入分母。英美拼写按显式映射折算。')
    lines+=['- AWL、AVL：未成功取得可独立处理的官方清单；覆盖率未计算。','','## Oxford 未覆盖词头原因','']
    for reason,words in sorted(omission.items()):lines.append(f'- {reason}：{len(words)} 词；示例：{", ".join(words[:8])}')
    lines+=['','Oxford PDF 仅供本地比较，不随分发压缩包附带。遗漏示例不是完整官方词表。','','## 局限','', 'ECDICT 音标采用旧式转写，本版规范化了可辨认的常见符号，仍不保证每词为标准英式 IPA。多读音不一定完整。中文释义尚未逐词人工核验。Oxford 的 CEFR 标注只用于词汇学习阶段的参考，不能等同雅思成绩。','']
    if issues:lines+=['## 前 30 项异常','']+[f'- {a}: {b} — {c}' for a,b,c in issues[:30]]
    (ROOT/'Data'/'quality_report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'total':len(master),'stage_counts':stage_counts,'issues':len(issues)},ensure_ascii=False))
    if issues:raise SystemExit(1)

def read_meta():
    with open(ROOT/'Data'/'vocabulary_metadata.csv',encoding='utf-8-sig',newline='') as f:
        return {r['word']:r for r in csv.DictReader(f)}
if __name__=='__main__':main()
