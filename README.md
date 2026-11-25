# IELTS 7.0—8.0 综合英语词汇库

本库面向雅思学术类 7.0—8.0 学习者，覆盖基础英语、通用英语、大学英语、雅思相关词和高阶扩展词。**这不是雅思官方指定词汇表，词数本身不能保证考试分数。**

## 快速开始

1. 打开 `IELTS_Vocabulary_Master.xlsx`，先查看「词汇统计」，再选择适合自己的阶段。
2. 在阶段工作表中筛选、查词；跨阶段检索使用「全部词汇总表」。
3. 要导入背词软件，使用 `CSV/` 中对应阶段的文件。三个学习字段依次是单词、音标、中文释义（含词性）。
4. 遇到可疑读音或释义时再查权威词典；本版未完成逐词人工审校。

## 规模与阶段

共 **14,212** 个不同拼写的词条，比上一版净增 412 词：补入 413 词，并将美式拼写 `flavor` 并入英式 `flavour`。每词仅出现于一个阶段；总表顺次拼接六阶段。阶段内依 ECDICT 的 BNC/当代语料排名取较高频的一项排序，缺排名者按词形排序。

| 阶段 | 词数 | 分类依据 |
|---|---:|---|
| 基础英语 | 1,740 | Oxford A1—A2 词头、原有基础词 |
| 通用英语核心 | 1,435 | Oxford B1 词头、原有通用词 |
| 大学英语 | 3,252 | Oxford B2 词头、原有四六级词 |
| 雅思核心 | 2,553 | 原有 IELTS/TOEFL/考研标签词 |
| 高阶学术 | 3,434 | Oxford C1 词头、原有高阶词 |
| 综合拓展 | 1,798 | 原有扩展词 |

新版优先按 Oxford PDF 中的 CEFR 标注调整相应词头的学习阶段，其余原有词条保留之前的阶段。各阶段词数不是固定配额；因此与初版规划数量不同。CEFR 是词汇学习参考，不是雅思分数换算。实际的专业领域和学术词覆盖未经独立清单核对。

## 来源、许可证与覆盖率

词条的中文释义和大部分音标来自 [ECDICT](https://github.com/skywind3000/ECDICT)，以仓库的 [MIT 许可证](https://github.com/skywind3000/ECDICT/blob/master/LICENSE) 再分发，版权许可文本见 `Data/ECDICT_LICENSE.txt`。原始 CSV 随包保存。新版使用 Oxford 官网可下载的 [Oxford 3000](https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_3000_by_CEFR_level.pdf) 和 [Oxford 5000 追加词](https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_5000_by_CEFR_level.pdf) PDF 作本地比较、补词及分级参考。**Oxford PDF 不包含在分发压缩包中，也不复制其完整词表。**重新生成时，下载脚本会将 PDF 保存到本地 `Data/References/` 供比对。来源详情见 `Data/sources.md`。

下表前七行分母为 ECDICT 原库内带相应标签、经过规范拼写和英美拼写合并后的不同词头，不是独立官方考试大纲。

| ECDICT 标记 | 本库收录 / 源库 | 覆盖率 |
|---|---:|---:|
| 中考 `zk` | 1,562 / 1,583 | 98.7% |
| 高考 `gk` | 3,528 / 3,619 | 97.5% |
| CET-4 `cet4` | 3,757 / 3,818 | 98.4% |
| CET-6 `cet6` | 5,239 / 5,371 | 97.5% |
| IELTS `ielts` | 4,546 / 4,995 | 91.0% |
| TOEFL `toefl` | 6,467 / 6,957 | 93.0% |
| ECDICT Oxford 3000 标记 | 3,209 / 3,328 | 96.4% |

官方 Oxford PDF 的独立比对结果：Oxford 3000 中可解析为规范单词的 **2,968/2,968** 个词头已收录；Oxford 5000 的追加词中可解析的 **1,944/1,994** 个词头已收录（97.5%）。PDF 中多词短语、同形词标签等 14 项未纳入上述分母；英美拼写按明确映射折算。因此前一个比例不能简写为“完整覆盖 Oxford 3000 全部词义、词组或发音”。其余 50 个 Oxford 5000 追加词头的遗漏原因见 `Data/quality_report.md`。

AWL、AVL 未成功获取可独立处理的官方完整清单，**不作覆盖声明**。BNC/当代语料词频仍使用 ECDICT 内含字段，没有单独导入原始词频表。

## 处理标准

- 普通词统一小写；排除非规范拼写、明显专名及无法组成完整三列的条目。
- 依据 ECDICT `exchange` 中的 lemma 信息排除常规屈折形式，保留 `building`、`understanding` 等有独立用法者；Oxford 将 `bored` 等列为独立词头时也保留。派生词若有独立学习价值则分别收录。
- 英美拼写仅按脚本中的明确映射合并，优先英式拼写，在释义中标注对应美式拼写；映射范围有限。
- 音标主要来自 ECDICT `phonetic`，对 `ә`、`є`、常见旧式元音与重音符号作规则化转写后加 `/ /`。少量基础词和遗漏词从 [Cambridge Dictionary](https://dictionary.cambridge.org/) 与 [Oxford Learner's Dictionaries](https://www.oxfordlearnersdictionaries.com/) 核验英式 IPA，逐词来源记在元数据中。**其余源库音标仍不保证全部符合标准英式 IPA，也不能保证多读音完整。**
- 中文释义取源库带词性标记的常见释义行，统一分隔符，保留多词性；`a` 的明显异常源释义作人工修正。释义仍有源库旧义、领域义和错漏风险。

## 文件和使用方法

- `IELTS_Vocabulary_Master.xlsx`：使用说明、统计、总表和六个阶段工作表；学习表严格三列，冻结首行并可筛选。
- `CSV/`：UTF-8 BOM 编码的总表与六阶段 CSV，第一行为列名。Excel 可直接打开；Anki 以逗号分隔导入，将第一行设为表头并映射单词、音标、中文释义三个字段。
- `Data/vocabulary_metadata.csv`：逐词来源、标签、词频、词形及修正记录。
- `Data/quality_report.md`、`Data/exceptions.csv`：自动检查结果及异常；`Data/manual_review.md`：抽样语义复核。

目录结构：

```text
IELTS_Vocabulary/
├── README.md
├── IELTS_Vocabulary_Master.xlsx
├── CSV/                 # 总表和六阶段 CSV
├── Data/                # 原始 ECDICT、基线阶段、许可证、元数据及检查报告
├── Scripts/             # 下载、构建、验证脚本
└── requirements.txt
```

Excel 文件包含「使用说明」「词汇统计」「全部词汇总表」和六个阶段工作表。学习工作表冻结首行、开启自动筛选；可在 macOS 或 Windows 的 Excel 中打开。CSV 使用 UTF-8 BOM、标准逗号分隔和引号转义。导入 Anki 时，选择相应阶段 CSV，指定逗号分隔和 UTF-8，将三列映射到卡片字段，并跳过第一行表头。

## 复现

安装 `requirements.txt` 后依次执行：

```bash
python3 -m pip install -r requirements.txt
python3 Scripts/download_sources.py
python3 Scripts/build_vocabulary.py
python3 Scripts/validate_vocabulary.py
```

脚本在 `IELTS_Vocabulary` 目录运行或使用脚本绝对路径均可。构建时读取 `Data/ecdict.csv` 与本地 `Data/References/` 下的两份 Oxford PDF；后者仅供本地比对，不随 ZIP 分发。下载脚本在源文件已存在且大小合理时使用本地副本。`Data/baseline_stage.csv` 保存上一版选词及阶段，以确保重新生成时不丢失原有词条。

本次生成后的自动检查结果为 **0 项结构异常**：总表与六阶段数量一致，词条无重复，XLSX 与 CSV 已逐单元格比较，Oxford PDF 覆盖率已独立复算，文件可正常读取。另有 24 词的人工式抽查记录。自动检查通过不表示释义和音标已获全面人工核验。

## 已知局限

本版以 ECDICT 作为可分发的英汉内容底库，Oxford PDF 用于选词与阶段比对；未复制 Oxford 的词典释义。50 个 Oxford 5000 追加词头仍缺失，主要因 ECDICT 无可用音标或带词性的中文释义。AWL、AVL 和各学科术语覆盖尚未独立核对。词性与中文释义依赖源库，可能保留过时义项；源库音标也不一定是严格 IPA。学习发音和写作选词时请再查权威词典。
