# 数据来源与使用边界

## 实际使用

- **ECDICT**：https://github.com/skywind3000/ECDICT 及 https://raw.githubusercontent.com/skywind3000/ECDICT/master/ecdict.csv 。本包保留下载的原始 CSV、SHA-256（见 `build_stats.json`）及 `ECDICT_LICENSE.txt`。仓库许可证为 MIT，重新分发时保留版权与许可通知。字段含 `word`、`phonetic`、`translation`、`pos`、`tag`、`oxford`、`collins`、`bnc`、`frq`、`exchange`。仓库说明称 `phonetic` 以英式音标为主；这不是逐词纯英式 IPA 保证。`tag` 以空格分隔。`oxford` 是源库的牛津三千标记，不等同于当前官方 Oxford 3000/5000 清单。
- **Oxford 官方 PDF（仅本地对照）**：[Oxford 3000 by CEFR level](https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_3000_by_CEFR_level.pdf)、[Oxford 5000 by CEFR level](https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_5000_by_CEFR_level.pdf)。2026-11-25 下载于 `Data/References/`，以单词词头与 CEFR 标注比对、补词和调整阶段。Oxford 网站允许下载 PDF 供离线查阅或学习；未找到允许将完整 PDF 或完整清单重新分发的明确许可，因此本项目的 ZIP **不包含这些 PDF、提取后的完整 Oxford 清单或逐词 Oxford 成员标记**。可在本地运行下载脚本重新获取。解析规则与未纳入的短语/标签数量见 `Scripts/oxford_reference.py` 和质量报告。Oxford 的词义与音标没有批量复制。
- **用户提供的任务文字**：`conduct` 两读音示例；仅用于该词读音修正。
- **Cambridge Dictionary**：https://dictionary.cambridge.org/us/pronunciation/english/a 用于 `a` 的弱读和强读核验；https://dictionary.cambridge.org/dictionary/english/moustache 用于核验 `moustache/mustache` 英美拼写映射。另对 `blog`、`bored`、`app` 等少量缺音标的词核验英式 IPA，具体词见 `Scripts/build_vocabulary.py` 的 `CAMBRIDGE_SUPPLEMENTS`。没有批量抓取其词典内容。
- **Oxford Learner's Dictionaries 在线词条**：https://www.oxfordlearnersdictionaries.com/definition/english/located 、https://www.oxfordlearnersdictionaries.com/definition/english/photographer 、https://www.oxfordlearnersdictionaries.com/definition/english/impressed ，仅用于核验这 3 个词的英式 IPA。

## 已查阅但未导入

- AWL：https://www.wgtn.ac.nz/lals/resources/academicwordlist 。尝试获取大学官方 PDF/DOCX 时服务器返回 403；未导入或计算覆盖率。
- AVL：https://www.academicvocabulary.info/ 。未取得可确认再分发许可的完整词表，未导入。
- BNC/COCA：https://www.wgtn.ac.nz/lals/resources/paul-nations-resources 、https://www.english-corpora.org/coca/ 。仅使用 ECDICT 内含的 `bnc`、`frq` 排名字段，没有独立导入原始词频表。
- English Vocabulary Profile：https://www.englishprofile.org/wordlists 。未导入；Oxford PDF 中的 CEFR 标注仅用于阶段参考，不等同于 EVP 数据。
- Longman 在线词典未逐词查询或抓取。

源库标签的覆盖率只衡量本项目对 **ECDICT 内相应标签的规范词头** 的收录比例，不能解释为官方考试大纲覆盖率。Oxford 官方 PDF 的覆盖率另行计算，分母只包括解析出的规范单词词头，不包含多词短语、词义或词性覆盖。源库筛选时会排除无法形成有效三列词条、词形合并、英美拼写合并及低价值条目。所有未纳入的 ECDICT 原始行可由保留的 CSV 和构建脚本复核。
