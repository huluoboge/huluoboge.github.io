# Blog Writing Style

Use this guide only when writing or revising blog article prose. Do not load it for ordinary site maintenance, link fixes, build checks, or static asset edits.

# 前提

如果是写某篇文章的理解，需要先下载原论文，充分阅读论文，然后再开始写作。

论文类文章默认按[论文解读写作 Skill](../skills/write-paper-tech-blog/SKILL.md)执行：基于完整阅读准确转述论文，融入自己的理解、推导和机制分析，保留必要的论证关系与限定。篇幅以讲清楚为准，不追求缩短。解释自然接入相关段落，需要区分时使用 Markdown 引文块 `>`，不反复划分翻译与解释。

## Voice

- Write in calm, direct Chinese. Prefer declarative sentences and steady explanation.
- Begin with the core idea, then unfold mechanism, formulas, examples, and system consequences.
- Keep the tone narrative and technical. Avoid marketing language, slogans, and exaggerated claims.
- 以独立解读者口吻写作，不用“我们”“我们的模型”代替论文作者。按语义使用“作者”“论文”“该方法”或直接陈述，避免机械重复主语。
- 解释直接写出，或使用 Markdown 引文块 `>`，不加固定的“补充解释”“推导补充”“译注”标签。

## Purpose and Audience

- Treat the blog as the author's technical notebook for self-summary and self-study.
- Write for readers with a similar technical background who may discover the article while trying to reconstruct the same problem and its history.
- Explain the causes, mechanisms, relationships, and limits of a method. Do not turn the article into an implementation assignment or a set of instructions to the reader.
- Prefer sections such as “小结”“方法关系” and “核心认识” over “实践启示” or advice addressed to the reader.
- Keep titles of papers, books, and other named works in their original language. Explain their meaning in the surrounding Chinese prose instead of translating the title.

## Phrasing

- 标题不要使用套路化的“从 XXX 到 XXX”范式，也避免用冒号连接标题层次。标题直接说明文章的主题和范围。
- Avoid habitual contrast patterns such as “不是……而是……” and rhetorical chains such as “为什么？因为……”.
- Use declarative section titles and prose. Do not organize the body as repeated questions followed by answers.
- Replace rhetorical framing with direct cause, structure, and consequence.
- Use “先看宏观，再看微观” as an organizing principle, not as a repeated phrase.
- 优先正面说明对象、用途与成立条件，例如“下面用一组假设分数说明分配过程”。来源和用途已清楚时，省去“不是论文实验”之类的重复声明；否定句用于澄清具体误解。

## Technical Writing

- Tie each formula to a system action: what a residual compares, what a Jacobian differentiates, what an update changes, and where the result is reused.
- For paper comparisons, explain each paper through state propagation, observation construction, iteration/update location, and feedback to the map or next frame.
- Reading guidance may appear, but the article body should teach the mechanism rather than only list what to read next.
- 面向有相关技术背景、尚未读过当前论文的同行，补充理解所需的背景、推导和机制联系。对公式说明要算什么、为什么成立、结果如何继续使用；准确转述原文并在相关位置直接展开解释；通过措辞和来源区分论文结论、实现细节与自己的推断。
- 例子按理解难点选用，可不用、局部使用或贯穿使用。只有同一输入确实能帮助解释连续变化时才贯穿全文；训练与实验按各自问题展开。例子应减少解释成本，不能只为模块名添一个场景。

# Review
写作完成后，需要阅读并检查以下内容：
- 如果是写某篇文章的理解，需要下载原论文，并逐项对比，是否有错误和偏差
- 只读中文检查语序、指代、术语和段落衔接，修改不通顺之处后回查原意。
- 按目标读者检查关键推理是否能跟上，定位缺失的背景、中间步骤和机制联系，在相关位置补足；新增解释再检查准确性与表达。完整执行 Skill 中的三轮 review，发现问题后实际修订。
- 为了方便人类本地review，我们写好的index.md,draft直接设置成false即可，也就是默认发表

# 提交

如果提交代码， 下载的pdf请不要提交。
