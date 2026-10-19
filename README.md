# 沈瑚双 / Darssal · Academic Homepage

沈瑚双的个人学术主页，面向科研、算法实习与技术求职，集中展示教育背景、论文、科技竞赛与开源项目。研究与项目围绕多模态模型适配、Agent 记忆和 Python 实验工程展开。

主页收录 2 篇第一作者 SCI-E 期刊已发表论文，以及 1 篇共同第一作者 IEEE SMC 已录用论文。论文条目保留完整作者顺序、发表或录用状态和一手链接；获奖条目注明年份、等级和级别。公开职业与学术信息来自本人本轮明确授权的简历、论文及获奖材料。

目前本科在读，预计 2027 年毕业；2027 级保研去向为中国科学院大学／计算技术研究所，计算机科学与技术，尚未入学。研究经历分别列示新立项时序 Transformer 项目和本人作为成员参与的已结题国家级大创项目。

**在线主页：[darssal.github.io](https://darssal.github.io/)** · [公开简历](https://darssal.github.io/cv.html) · [GitHub 账户](https://github.com/Darssal) · [验证范围与来源](https://darssal.github.io/verification.html)

## 网站结构

- [`site/index.html`](site/index.html)：个人介绍、教育背景、论文、获奖与开源项目。
- [`site/cv.html`](site/cv.html)：可打印的公开简历。
- [`site/styles.css`](site/styles.css)：响应式布局、排版和交互状态。
- [`site/assets/`](site/assets/)：本人照片及研究方法示意图。
- [`site/verification.html`](site/verification.html)：论文状态、材料来源与项目验证范围。
- [`site/404.html`](site/404.html)：缺失页面的返回入口。
- [`site/robots.txt`](site/robots.txt) 与 [`site/sitemap.xml`](site/sitemap.xml)：公开页面索引。
- [`tools/check_site.py`](tools/check_site.py)：标准库静态检查，无需安装依赖。
- [`docs/MAINTENANCE.md`](docs/MAINTENANCE.md)：内容核对与网站维护规范。
- [`.github/workflows/pages.yml`](.github/workflows/pages.yml)：PR 验证，合并到 `main` 后发布。

网站使用原生 HTML、CSS 和静态图像，无构建依赖。论文中的模型性能按原文报告的实验条件表述；代码仓库的单元测试数量用于说明代码检查范围。二者采用各自的证据和口径。首页借鉴研究者网站的介绍、论文列表与简历入口组织方式，参考作者的工作单位和职业经历不属于本人的履历。

## 本地预览与验证

在仓库根目录执行：

```sh
python tools/check_site.py
python -m http.server 8132 --bind 127.0.0.1 --directory site
```

浏览器打开 `http://127.0.0.1:8132/`。预览服务器只供本机查看，发布产物来自 `site/`。

检查脚本默认自动定位仓库根目录，也可指定其他工作副本：

```sh
python tools/check_site.py --root /path/to/Darssal.github.io
```

检查覆盖静态文件类型与大小预算、文件及锚点链接、允许的外链域、静态 SVG 和常见敏感内容特征。文本中的国内手机号码、邮箱地址、符合日期结构的 18 位居民身份证号码，以及私有文件名也会被拒绝。检查输出仅含路径、规则名和行号。

论文外链使用精确主机白名单：`www.mdpi.com`、`www.jove.com`、`doi.org`、`pubmed.ncbi.nlm.nih.gov`、`conf.papercept.net` 与 `www.ieeesmc2026.org`，不允许其任意子域。官方论文 URL 中的纯数字文章标识不会按手机号码误报。自动检查应配合人工事实核对、图像内容检查和浏览器验证。

## GitHub Pages 发布

Pages 的发布来源设置为 **GitHub Actions**。工作流仅上传 `site/`；文档和检查工具不进入网站产物。部署使用 `github-pages` 环境，仅 `main` 分支可发布。PR 只执行验证，不部署。

静态文件、检查脚本或 Pages workflow 合并到 `main` 后自动发布，也可在 Actions 中从 `main` 手动运行。更新后应检查 workflow 的部署结果，并访问真实网址核对页面与资源。

官方参考：[自定义 Pages workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) · [发布来源配置](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

## 早期 JSP 学习记录

早期学习代码现独立维护于 [JSP-UI-Prototype](https://github.com/Darssal/JSP-UI-Prototype)。迁移保留 13 个 JSP 文件与原项目说明的 Git blob、CodePen 来源、缺失资源和无后端验证的范围说明；本仓库当前版本仅保留外链，原文件仍可从 Git 历史恢复。

## 独立代码项目

- [FracLogGPT-Lite](https://github.com/Darssal/FracLogGPT-Lite)：多模态模型适配与推理。
- [MemLab](https://github.com/Darssal/MemLab)：Agent 多层记忆与实验控制。
- [Recruitment-Text-Classification](https://github.com/Darssal/Recruitment-Text-Classification)：招聘文本分类与批处理基线。

[Research-Code-Collection](https://github.com/Darssal/Research-Code-Collection) 作为研究代码索引与工程笔记入口；每个项目的当前规范源码仅在对应独立仓库维护。
