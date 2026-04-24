#!/usr/bin/env python3
"""
分析LLM论文的创新点
"""

import json

# 论文数据
papers = [
    {
        "title": "Grounded Token Initialization for New Vocabulary in LMs for Generative Recommendation",
        "summary": "Language models (LMs) are increasingly extended with new learnable vocabulary tokens for domain-specific tasks, such as Semantic-ID tokens in generative recommendation. The standard practice initializes these new tokens as the mean of existing vocabulary embeddings, then relies on supervised fine-tuning to learn their representations. We present a systematic analysis of this strategy: through spectral and geometric diagnostics, we show that mean initialization collapses all new tokens into a degenerate subspace, erasing inter-token distinctions that subsequent fine-tuning struggles to fully recover. These findings suggest that token initialization is a key bottleneck when extending LMs with new vocabularies. Motivated by this diagnosis, we propose the Grounded Token Initialization Hypothesis: linguistically grounding novel tokens in the pretrained embedding space before fine-tuning better enables the model to leverage its general-purpose knowledge for novel-token domains. We operationalize this hypothesis as GTI (Grounded Token Initialization), a lightweight grounding stage that, prior to fine-tuning, maps new tokens to distinct, semantically meaningful locations in the pretrained embedding space using only paired linguistic supervision.",
        "innovation": {
            "core_problem": "为领域特定任务扩展语言模型词汇时，标准初始化方法（均值初始化）会将所有新token坍缩到退化子空间，导致后续微调无法充分恢复token间的区别",
            "main_innovation": "提出Grounded Token Initialization (GTI)假设，在微调前将新token语言学地锚定在预训练嵌入空间中有语义意义的位置",
            "tech_highlights": [
                "使用谱分析和几何诊断揭示初始化问题",
                "设计轻量级grounding阶段，仅使用配对语言监督",
                "生成推荐任务上优于均值初始化和现有辅助任务适应方法"
            ]
        }
    },
    {
        "title": "No Single Best Model for Diversity: Learning a Router for Sample Diversity",
        "summary": "When posed with prompts that permit a large number of valid answers, comprehensively generating them is the first step towards satisfying a wide range of users. In this paper, we study methods to elicit a comprehensive set of valid responses. To evaluate this, we introduce diversity coverage, a metric that measures the total quality scores assigned to each unique answer in the predicted answer set relative to the best possible answer set with the same number of answers. Using this metric, we evaluate 18 LLMs, finding no single model dominates at generating diverse responses to a wide range of open-ended prompts. Yet, per each prompt, there exists a model that outperforms all other models significantly at generating a diverse answer set. Motivated by this finding, we introduce a router that predicts the best model for each query.",
        "innovation": {
            "core_problem": "没有单一模型能在所有开放式提示下生成多样化回答，但每个提示都有某个模型表现最优",
            "main_innovation": "设计一个路由器，为每个查询预测最佳模型，实现模型ensemble的智能选择",
            "tech_highlights": [
                "提出diversity coverage评估指标",
                "评估18个LLM的多样性生成能力",
                "路由器在NB-Wildchat上超越单模型基线（26.3% vs 23.8%）"
            ]
        }
    },
    {
        "title": "CV-18 NER: Augmented Common Voice for Named Entity Recognition from Arabic Speech",
        "summary": "End-to-end speech Named Entity Recognition (NER) aims to directly提取实体 from speech. Prior work has shown that end-to-end (E2E) approaches can outperform cascaded pipelines for English, French, and Chinese, but Arabic remains under-explored due to its morphological complexity, the absence of short vowels, and limited annotated resources. We introduce CV-18 NER, the first publicly available dataset for NER from Arabic speech, created by augmenting the Arabic Common Voice 18 corpus with manual NER annotations following the fine-grained Wojood schema (21 entity types). We benchmark both pipeline systems (ASR + text NER) and E2E models based on Whisper and AraBEST-RQ.",
        "innovation": {
            "core_problem": "阿拉伯语语音NER研究不足，因形态复杂、缺少短元音、标注资源有限",
            "main_innovation": "创建首个公开的阿拉伯语语音NER数据集CV-18 NER，采用精细Wojood schema（21种实体类型）",
            "tech_highlights": [
                "扩充阿拉伯语Common Voice 18语料库",
                "对比级联系统和E2E模型（Whisper和AraBEST-RQ）",
                "E2E系统在测试集上显著优于最佳级联配置（37.0% CoER, 38.0% CVER）"
            ]
        }
    },
    {
        "title": "Towards Position-Robust Talent Recommendation via Large Language Models",
        "summary": "Talent recruitment is a critical, yet costly process for many industries, with high recruitment costs and long hiring cycles. Existing talent recommendation systems increasingly adopt large language models (LLMs) due to their remarkable language understanding capabilities. However, most prior approaches follow a pointwise paradigm, which requires LLMs to repeatedly process some text and fails to capture the relationships among candidates in the list, resulting in higher token consumption and suboptimal recommendations. Besides, LLMs exhibit position bias and the lost-in-the-middle issue when answering multiple-choice questions and processing multiple long documents. To address these issues, we introduce an implicit strategy to utilize LLM's potential output for the recommendation task and propose L3TR, a novel framework for listwise talent recommendation with LLMs. In this framework, we propose a block attention mechanism and a local positional encoding method to enhance inter-document processing and mitigate the position bias and concurrent token bias issue.",
        "innovation": {
            "core_problem": "现有人才推荐系统采用点式范式，无法捕捉候选人之间的关系，且存在位置偏见和lost-in-the-middle问题",
            "main_innovation": "提出L3TR框架，首次将listwise范式应用于LLM人才推荐，设计block attention和局部位置编码",
            "tech_highlights": [
                "block attention机制增强文档间处理",
                "局部位置编码缓解位置偏见和token偏见",
                "ID采样方法解决训练和推理阶段候选集大小不一致问题",
                "设计位置偏见检测和去偏方法"
            ]
        }
    },
    {
        "title": "Neuro-RIT: Neuron-Guided Instruction Tuning for Robust Retrieval-Augmented Language Model",
        "summary": "Retrieval-Augmented Language Models (RALMs) have demonstrated significant potential in knowledge-intensive tasks; however, they remain vulnerable to performance degradation when presented with irrelevant or noisy retrieved contexts. Existing approaches to enhance robust性 typically operate via coarse-grained parameter updates at the layer or module level, often overlooking the inherent neuron-level sparsity of Large Language Models (LLMs). To address this limitation, we propose Neuro-RIT (Neuron-guided Robust Instruction Tuning), a novel framework that shifts the paradigm from dense adaptation to precision-driven neuron alignment. Our method explicitly disentangles neurons that are responsible for processing relevant versus irrelevant contexts using attribution-based neuron mining. Subsequently, we introduce a two-stage instruction tuning strategy that enforces a dual capability for noise robustness: achieving direct noise suppression by functionally deactivating neurons exclusive to irrelevant contexts, while simultaneously optimizing targeted layers for evidence distillation.",
        "innovation": {
            "core_problem": "RALM在遇到不相关或噪声检索上下文时性能下降，现有方法在粗粒度层/模块层面更新参数，忽视LLM的神经元级稀疏性",
            "main_innovation": "提出Neuro-RIT框架，从密集适应转向精准驱动的神经元对齐，显式解耦处理相关和不相关上下文的神经元",
            "tech_highlights": [
                "使用基于归因的神经元挖掘显式区分神经元",
                "两阶段指令调优策略：直接噪声抑制 + 证据蒸馏",
                "通过功能性停用专属不相关上下文的神经元实现噪声抑制",
                "在多个QA基准上持续超越强基线"
            ]
        }
    }
]

# 总体评价
overall_evaluation = {
    "most_noteworthy": "Neuro-RIT的神经元级精准对齐范式",
    "reasoning": "从粗粒度参数更新转向神经元级精准控制，是对LLM适应方法的范式级创新，有望在更多任务中应用",
    "trends": [
        "从粗粒度适配向细粒度（神经元级）控制演进",
        "从单一模型向智能ensemble路由发展",
        "从通用数据集向低资源语言（阿拉伯语）拓展",
        "从点式处理向listwise全局关系建模转变"
    ]
}

# 输出
print("="*80)
print("📚 LLM论文创新点分析")
print("="*80)

for i, paper in enumerate(papers, 1):
    print(f"\n论文{i}: {paper['title']}")
    print("-"*80)
    print(f"核心问题: {paper['innovation']['core_problem']}")
    print(f"主要创新: {paper['innovation']['main_innovation']}")
    print("技术亮点:")
    for j, highlight in enumerate(paper['innovation']['tech_highlights'], 1):
        print(f"  {j}. {highlight}")

print("\n" + "="*80)
print("总体评价")
print("="*80)
print(f"最值得关注的创新方向: {overall_evaluation['most_noteworthy']}")
print(f"理由: {overall_evaluation['reasoning']}")
print("\n发展趋势:")
for i, trend in enumerate(overall_evaluation['trends'], 1):
    print(f"{i}. {trend}")

# 保存结果
output = {
    "papers": papers,
    "evaluation": overall_evaluation
}

with open("/home/admin/.openclaw/workspace/data/llm_paper_innovations.json", 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n✓ 创新点分析已保存到 /home/admin/.openclaw/workspace/data/llm_paper_innovations.json")