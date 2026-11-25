from __future__ import annotations
import csv, re, json, collections
from pathlib import Path
from openpyxl import load_workbook
from build_vocabulary import BRIT_US, KEEP_INFLECTED

ROOT=Path(__file__).resolve().parents[1]
CSV_DIR=ROOT/'CSV'
FILES=['00_全部词汇总表.csv','01_基础英语词汇.csv','02_通用英语核心词汇.csv','03_大学英语词汇.csv','04_雅思核心词汇.csv','05_高阶学术英语词汇.csv','06_综合拓展词汇.csv']
SHEETS=['全部词汇总表','01 基础英语','02 通用英语','03 大学英语','04 雅思核心','05 高阶学术','06 综合拓展']
POS=re.compile(r'(?:^|；)(?:n|v|vt|vi|adj|adv|pron|prep|conj|num|art|int|aux|det|abbr|modal v)\.',re.I)
WORD=re.compile(r'^[a-z]+(?:-[a-z]+)?$')
PHON=re.compile(r'^/[a-zA-Zəɪʊæɑɔʌɛɜɒɚɝθðʃʒŋɹɾɐɨɯʔˈˌː.()\- ]+/(?:；/[a-zA-Zəɪʊæɑɔʌɛɜɒɚɝθðʃʒŋɹɾɐɨɯʔˈˌː.()\- ]+/)*$')
def read(path):
    with open(path,encoding='utf-8-sig',newline='') as f:
        rows=list(csv.reader(f))
    assert rows[0]==['单词','音标','中文释义（含词性）'],(path,rows[0])
    assert all(len(x)==3 for x in rows)
    return rows[1:]
def main():
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
            if '0:' in ex and w not in KEEP_INFLECTED:
                issue('unnecessary_inflection',w,ex)
            if not meta[w].get('source'):
                issue('missing_provenance',w,'来源字段为空')
            try:
                b=int(meta[w].get('bnc') or 0);f=int(meta[w].get('frq') or 0)
                if (b==0 or b>45000) and (f==0 or f>45000) and not meta[w].get('tag') and not meta[w].get('oxford'):
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
    with open(ROOT/'Data'/'exceptions.csv','w',encoding='utf-8-sig',newline='') as f:
        out=csv.writer(f);out.writerow(['问题类型','单词','详情']);out.writerows(issues)
    lines=['# 质量检查报告','',f'- 总表：{len(master)} 词',f'- 六阶段：{stage_counts}',f'- 阶段之和：{sum(stage_counts)} 词',f'- 自动检查异常：{len(issues)} 项','- CSV 与 XLSX：已逐单元格比较','- 所有文件：已由 csv / openpyxl 重新读取','', '## 检查范围','', '检查三列结构、空值、词性标记、音标字符、拼写格式、乱码、重复、元数据来源、数量对账与 XLSX/CSV 一致性。词形变化由构建脚本依据 ECDICT exchange 处理；英美差异仅处理明确映射。语义正确性、纯英式音标、低频词实际价值均无法通过自动规则完全保证。','', '## 数据来源覆盖','']
    tags=stats['source_tags'];selected=stats['selected_tags']
    for key,label in [('zk','中考（ECDICT 标签）'),('gk','高考（ECDICT 标签）'),('cet4','CET-4（ECDICT 标签）'),('cet6','CET-6（ECDICT 标签）'),('ielts','IELTS（ECDICT 标签）'),('toefl','TOEFL（ECDICT 标签）')]:
        n=tags.get(key,0);s=selected.get(key,0)
        lines.append(f'- {label}：{s}/{n}，{(s/n*100 if n else 0):.1f}%（分母为 ECDICT 中具有该标签的规范英文词形，不是独立官方词表）')
    o=stats['source_oxford_flag'];sel=stats['selected_oxford_flag']
    lines.append(f'- ECDICT Oxford 3000 标记：{sel}/{o}，{(sel/o*100 if o else 0):.1f}%（不是当前 Oxford 3000 官方表的独立核验）')
    lines+=['- Oxford 5000、AWL、AVL、CEFR：未取得可重新分发且可独立核对的清单；覆盖率未计算。','','## 局限','', 'ECDICT 的音标为混合历史转写，仅做字形替换，不保证标准英式 IPA。多读音没有可靠结构化字段，含缩略记法的词条可能被排除。释义来自原库按词性行选取，未对每一词条人工复核。选词以来源标签和词频排序，六阶段是启发式学习路径。','']
    if issues:lines+=['## 前 30 项异常','']+[f'- {a}: {b} — {c}' for a,b,c in issues[:30]]
    (ROOT/'Data'/'quality_report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'total':len(master),'stage_counts':stage_counts,'issues':len(issues)},ensure_ascii=False))
    if issues:raise SystemExit(1)

def read_meta():
    with open(ROOT/'Data'/'vocabulary_metadata.csv',encoding='utf-8-sig',newline='') as f:
        return {r['word']:r for r in csv.DictReader(f)}
if __name__=='__main__':main()
