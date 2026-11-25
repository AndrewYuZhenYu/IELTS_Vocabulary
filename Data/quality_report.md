# 质量检查报告

- 总表：14212 词
- 六阶段：[1740, 1435, 3252, 2553, 3434, 1798]
- 阶段之和：14212 词
- 自动检查异常：0 项
- CSV 与 XLSX：已逐单元格比较
- 所有文件：已由 csv / openpyxl 重新读取

## 检查范围

检查三列结构、空值、词性标记、音标字符、拼写格式、乱码、重复、元数据来源、数量对账与 XLSX/CSV 一致性。词形变化由构建脚本依据 ECDICT exchange 处理；英美差异仅处理明确映射。语义正确性、纯英式音标、低频词实际价值均无法通过自动规则完全保证。

## 数据来源覆盖

- 中考（ECDICT 标签）：1562/1583，98.7%（分母为 ECDICT 中具有该标签的规范英文词形，不是独立官方词表）
- 高考（ECDICT 标签）：3528/3619，97.5%（分母为 ECDICT 中具有该标签的规范英文词形，不是独立官方词表）
- CET-4（ECDICT 标签）：3757/3818，98.4%（分母为 ECDICT 中具有该标签的规范英文词形，不是独立官方词表）
- CET-6（ECDICT 标签）：5239/5371，97.5%（分母为 ECDICT 中具有该标签的规范英文词形，不是独立官方词表）
- IELTS（ECDICT 标签）：4546/4995，91.0%（分母为 ECDICT 中具有该标签的规范英文词形，不是独立官方词表）
- TOEFL（ECDICT 标签）：6467/6957，93.0%（分母为 ECDICT 中具有该标签的规范英文词形，不是独立官方词表）
- ECDICT Oxford 3000 标记：3209/3328，96.4%（不是当前 Oxford 3000 官方表的独立核验）
- Oxford 官网 PDF：Oxford 3000 单词词头 2968/2968；Oxford 5000 追加单词词头 1944/1994。PDF 中多词短语与非规范标签另计 14 项，未纳入分母。英美拼写按显式映射折算。
- AWL、AVL：未成功取得可独立处理的官方清单；覆盖率未计算。

## Oxford 未覆盖词头原因

- ECDICT 无词条：1 词；示例：cryptocurrency
- 缺少可用音标：41 词；示例：additionally, affordable, all-time, benchmark, consistently, decision-making, deployment, evolutionary
- 缺少带词性的中文释义：8 词；示例：broadband, connectivity, extremist, listing, processing, screening, streaming, trading

Oxford PDF 仅供本地比较，不随分发压缩包附带。遗漏示例不是完整官方词表。

## 局限

ECDICT 音标采用旧式转写，本版规范化了可辨认的常见符号，仍不保证每词为标准英式 IPA。多读音不一定完整。中文释义尚未逐词人工核验。Oxford 的 CEFR 标注只用于词汇学习阶段的参考，不能等同雅思成绩。
