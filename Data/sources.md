# 数据来源与使用边界

## 实际使用

- **ECDICT**：https://github.com/skywind3000/ECDICT 及 https://raw.githubusercontent.com/skywind3000/ECDICT/master/ecdict.csv 。本包保留下载的原始 CSV、SHA-256（见 `build_stats.json`）及 `ECDICT_LICENSE.txt`。仓库许可证为 MIT，重新分发时保留版权与许可通知。字段含 `word`、`phonetic`、`translation`、`pos`、`tag`、`oxford`、`collins`、`bnc`、`frq`、`exchange`。仓库说明称 `phonetic` 以英式音标为主；这不是逐词纯英式 IPA 保证。`tag` 以空格分隔。`oxford` 是源库的牛津三千标记，不等同于当前官方 Oxford 3000/5000 清单。
- **用户提供的任务文字**：`conduct` 两读音示例；仅用于该词读音修正。
- **Cambridge Dictionary**：https://dictionary.cambridge.org/us/pronunciation/english/a 用于 `a` 的弱读和强读核验；https://dictionary.cambridge.org/dictionary/english/moustache 用于核验 `moustache/mustache` 英美拼写映射。没有批量抓取其词典内容。

## 已查阅但未导入

- Oxford 3000/5000：https://www.oxfordlearnersdictionaries.com/wordlists/oxford3000-5000 。未获得可确认许可及可逐词自动核对的完整官方清单，未导入。
- AWL：https://www.wgtn.ac.nz/lals/resources/academicwordlist 。未获得可确认再分发许可的完整词表，未导入。
- AVL：https://www.academicvocabulary.info/ 。未取得可确认再分发许可的完整词表，未导入。
- BNC/COCA：https://www.wgtn.ac.nz/lals/resources/paul-nations-resources 、https://www.english-corpora.org/coca/ 。仅使用 ECDICT 内含的 `bnc`、`frq` 排名字段，没有独立导入原始词频表。
- English Vocabulary Profile：https://www.englishprofile.org/wordlists 。未导入；本库不含经核验的 CEFR 等级。
- Cambridge、Oxford、Longman 在线词典未逐词查询或抓取。

源库标签的覆盖率只衡量本项目对 **ECDICT 内相应标签词条** 的收录比例，不能解释为官方考试大纲或独立词表覆盖率。源库筛选时会排除无法形成有效三列词条、词形合并、英美拼写合并及低价值条目。所有未纳入的原始行可由保留的 ECDICT CSV 和构建脚本复核。
