---
title: "如何跟踪计算机视觉三维重建方向的最新论文"
date: 2025-03-01T12:00:00+08:00
tags:
  [
    "Computer Vision",
    "3D Reconstruction",
    "SfM",
    "SLAM",
    "MVS",
    "NeRF",
    "3DGS",
    "论文跟踪",
  ]
excerpt: "总结跟踪 SfM、SLAM、MVS、3DGS、LiDAR 等三维重建与几何方向最新研究的多种方式，并以邮件为核心设计每日/每周工作流。"
draft: false
---

# 如何跟踪计算机视觉三维重建方向的最新论文

想持续跟进 **SfM、SLAM、MVS、SGM、几何、3DGS、LiDAR 点云、NeRF、VGGT** 等三维重建与几何方向的最新工作，可以依赖多种信息源。下面按类别整理「有哪些方式」，以及「每种方式具体怎么做」，并尽量统一到 **邮件**，方便每天看一次就管住。

---

## 一、有哪些方式可以跟踪

大致可以分成几类：

1. **论文源**：顶会/顶刊 + arXiv
2. **邮件订阅与提醒**
3. **聚合站与代码站**
4. **社区与社交**
5. **实验室/作者跟踪**

---

## 二、每种方式具体怎么做（尽量统一到「每天看邮件」）

### 1. arXiv 邮件订阅（最核心，建议必做）

arXiv 的每日摘要目前通过**发邮件订阅**，官方说明见：[Email subscriptions for new papers](https://info.arxiv.org/help/subscribe.html)。

- **做法**：
  - 用**纯文本邮件**（不要用 HTML/富文本，Subject 里不要用 UTF-8 字符）发到 **cs@arxiv.org**。
  - **Subject**：`subscribe 你的名字`（如 `subscribe Zhang San`）。
  - **正文**：按学科分类添加，一行一个。计算机视觉三维重建相关可订阅（均为 cs 下子类）：
    - `add AI` — 人工智能（cs.AI）
    - `add CG` — 计算几何（cs.CG）
    - `add CV` — 计算机视觉与模式识别（cs.CV）
    - `add GR` — 图形学（cs.GR）
    - `add LG` — 机器学习（cs.LG，含 3DGS/NeRF 等）
    - `add RO` — 机器人（cs.RO，含 SLAM 等）
  - 示例：
    ```
    To: cs@arxiv.org
    Subject: subscribe Zhang San

    add AI
    add CG
    add CV
    add GR
    add LG
    add RO
    ```
  - 之后每天会收到当日新提交的摘要邮件。取消订阅：向 **cs@arxiv.org** 发一封 **Subject 为 `cancel`** 的邮件即可。
- **关键词**：在每日邮件里用 Ctrl+F 搜：SfM, SLAM, MVS, SGM, NeRF, 3D Gaussian, point cloud, LiDAR, reconstruction, structure from motion, multi-view stereo, VGGT 等，几分钟就能扫完。
- **优点**：覆盖顶会预印本、顶刊预印本，和邮件习惯完美契合，适合做「每日一次」的主入口。

### 2. 会议/期刊的官方邮件与页面

- **做法**：
  - 到 **CVPR、ICCV、ECCV、3DV、WACV、SIGGRAPH** 等官网，用同一邮箱做 **Registration** 或 **Mailing list** 订阅（若有）。
  - 会议公布 **accepted papers** 后，官网会列出标题/链接，有的会发邮件通知；把「看 accepted list」固定成会议截稿后的一个习惯。
- **和邮件配合**：会议邮件提醒你「名单出了」→ 你点进官网看列表，把相关论文加入阅读列表或再在 arXiv 搜一下是否有更新版。
- **建议**：不必每个会都深跟，优先 **CVPR/ICCV/ECCV + 3DV**，几何/SfM/MVS 在 3DV 特别多。

### 3. Google Scholar 邮件提醒（按关键词/作者）

- **做法**：
  - [Google Scholar](https://scholar.google.com) → 左上角「三」→ **Alerts** → **Create alert**。
  - 用 **关键词** 建多个 alert，例如：
    - "structure from motion"
    - "multi-view stereo"
    - "3D Gaussian splatting"
    - "NeRF 3D reconstruction"
    - "LiDAR point cloud"
    - "visual SLAM"
  - 每个 alert 选「每天」或「每周」邮件。
- **优点**：不仅 arXiv，也包含期刊、会议正式版、有时还有 workshop，全部进邮箱，适合「只看邮件」的习惯。

### 4. Papers With Code / Semantic Scholar（用邮件或固定书签）

- **Papers With Code**：
  - [paperswithcode.com](https://paperswithcode.com) 上按任务选：**3D Reconstruction**、**SfM**、**SLAM**、**Point Cloud** 等，可按「最新」排序。
  - 若站点有 **Newsletter/邮件订阅**，优先用邮件；没有则把对应任务页加入浏览器书签，每周固定一天打开扫一眼。
- **Semantic Scholar**：
  - 注册后可为「3D reconstruction」等主题建 **email digest**（若功能可用），同样收到摘要邮件。
- **建议**：能邮件就邮件；不能的话就「每周一次书签」和「每日 arXiv 邮件」搭配，避免信息分散。

### 5. 邮件列表（Mailing lists）

- **Vision list 等**：
  - 如 **visionlist**（部分学校/实验室维护）、**ROS users**（若做 SLAM/机器人）等，可搜 "computer vision mailing list" 按需订阅。
  - 用单独邮箱或 Gmail 标签/过滤器把「论文/CFP」类邮件归到一个标签，每天只看该标签。
- **特点**：讨论 + CFP + 偶尔新工作推荐，邮件量可能偏多，适合「扫标题 + 关键词」快速过滤。

### 6. GitHub / 代码（用邮件或每周一次）

- **做法**：
  - 在 GitHub 用 **Topics** 搜索：`3d-reconstruction`、`slam`、`structure-from-motion`、`multi-view-stereo`、`nerf`、`3d-gaussian-splatting`、`point-cloud` 等，star 几个高质量 repo，点 **Watch**。
  - GitHub 的 **Watch** 会发邮件通知（可在 Settings → Notifications 里调成仅邮件、按日汇总）。
- **建议**：只 watch 真正在跟的 repo，避免邮件爆炸；其余用「每周一次 Trending + topic」补漏。

### 7. 社区与社交（可选，不一定要邮件）

- **Twitter/X**：关注做 SfM/SLAM/MVS/3DGS 的学者和 lab，会议期间 #CVPR 等 hashtag 会有论文解读；若不想装 app，可用 **RSS 转邮件**（如 Zapier/IFTTT 把某列表推成每日摘要邮件）。
- **Reddit**：r/computervision、r/MachineLearning 的「Top this week」每周看一次即可，不必每天。
- **知乎/公众号**：若有固定几个做「顶会解读」的，可看是否提供邮件订阅或周刊；没有就固定每周某天扫一眼。

### 8. 实验室/作者页（配合 Scholar 或 RSS）

- **做法**：把常发 3D 重建/几何的 lab（如 TUM、ETH、MIT、FAIR 等）的 **Publications** 页用 **RSS 转邮件** 工具（如 Feedburner、Blogtrottr）转成邮件；或只依赖 **Google Scholar 按作者 alert**，同样全部进邮箱。

---

## 三、如何「全部用邮件、每天看一次就管住」

可以这样设计一个「邮件为主」的流程：

| 方式 | 是否邮件 | 频率 | 建议用法 |
|------|----------|------|----------|
| arXiv digest | ✅ 是 | 每日 | 主入口，扫标题 + 关键词 |
| Google Scholar alerts | ✅ 是 | 每日/每周 | 按 5–8 个关键词建 alert |
| 会议 mailing | ✅ 是 | 有则收 | 提醒看 accepted list |
| Papers With Code / Semantic Scholar | 若支持则用邮件 | 每周 | 否则书签每周一次 |
| Mailing lists | ✅ 是 | 每日 | 用标签/过滤器归类，扫标题 |
| GitHub Watch | ✅ 是 | 按需 | 仅 watch 少量 repo，邮件汇总 |
| 实验室/作者 | RSS→邮件 或 Scholar 作者 alert | 每周 | 补漏 |

**实际操作建议**：

- **每天早上或晚上固定 10–15 分钟**：只开邮箱，按顺序看：arXiv 摘要 → Scholar 提醒 → 会议/列表邮件标题；用关键词快速过滤，把要读的丢进「待读」列表或稍后读。
- **每周一次**：打开 Papers With Code 对应任务页 + 若有的周刊/Reddit，做一次补漏和深度几篇。

这样 SfM、SLAM、MVS、SGM、几何、3DGS、LiDAR、VGGT 等方向的新工作就不会漏掉，又不会占用太多时间。
