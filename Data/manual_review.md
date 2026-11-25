# 抽样语义复核记录

2026-11-25 从每个阶段以固定随机种子抽取 4 词，共 24 词（约占总表 0.17%），阅读词性、中文释义和阶段位置。样本如下：

| 阶段 | 抽查词 |
|---|---|
| 基础英语 | connected, say, fire, scientist |
| 通用英语核心 | management, cholesterol, primitive, interpreter |
| 大学英语 | democratic, valuation, monarchy, marsh |
| 雅思核心 | desperation, proxy, renounce, overestimate |
| 高阶学术 | abortion, thrift, campfire, candlelight |
| 综合拓展 | distent, horticultural, unsolved, stingy |

复核时确认 Oxford A1 的 `scientist` 和 A2 的 `connected` 已归入基础阶段。`cholesterol`、`campfire` 和 `candlelight` 等未列于此次解析的 Oxford 词头清单，沿用了原有阶段；它们的学习阶段未经过独立 CEFR 证实，仍可能需要调整。`renounce`、`overestimate` 等多义词保留了源库的次要或偏旧义项，仍需逐词删选。另检查了高频词 `a`、`air`、`where`、`work`、`go` 及本次补入的 `blog`、`bored`、`website`、`download`；此前由旧式音标字形或缺音标造成的漏收已修复。

本抽样仅用于发现明显问题，不代表全库语义、音标或分级已完成全面人工校对。
