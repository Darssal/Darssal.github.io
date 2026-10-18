# Darssal · Personal Portfolio

面向技术实习与求职的个人作品集，围绕多模态模型适配、Agent 记忆和 Python 实验工程展示项目、关键机制与代码入口。

**在线主页：[darssal.github.io](https://darssal.github.io/)** · [GitHub 账户](https://github.com/Darssal) · [验证范围与来源](https://darssal.github.io/verification.html)

## 网站结构

- [`site/index.html`](site/index.html)：个人介绍、精选项目和工程笔记入口。
- [`site/styles.css`](site/styles.css)：响应式布局、排版和交互状态。
- [`site/verification.html`](site/verification.html)：项目验证范围、来源与公开材料边界。
- [`site/404.html`](site/404.html)：缺失页面的返回入口。
- [`site/robots.txt`](site/robots.txt) 与 [`site/sitemap.xml`](site/sitemap.xml)：公开页面索引。
- [`tools/check_site.py`](tools/check_site.py)：标准库静态检查，无需安装依赖。
- [`.github/workflows/pages.yml`](.github/workflows/pages.yml)：PR 验证，合并到 `main` 后发布。

网站使用原生 HTML、CSS 和静态 SVG，无构建依赖。站点内容链接到已公开的代码与说明；单元测试数量用于说明代码检查范围，不代表模型效果或真实业务结果。

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

检查覆盖静态文件类型与大小预算、文件及锚点链接、允许的外链域、静态 SVG 和常见敏感内容特征。它是发布前检查，不替代人工内容核对、浏览器视觉检查或专门的密钥扫描。

## GitHub Pages 发布

Pages 的发布来源设置为 **GitHub Actions**。工作流仅上传 `site/`；根目录旧 JSP、文档和检查工具不进入网站产物。部署使用 `github-pages` 环境，仅 `main` 分支可发布。PR 只执行验证，不部署。

静态文件、检查脚本或 Pages workflow 合并到 `main` 后自动发布，也可在 Actions 中从 `main` 手动运行。更新后应检查 workflow 的部署结果，并访问真实网址核对页面与资源。

官方参考：[自定义 Pages workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) · [发布来源配置](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

## 早期 JSP 学习记录

仓库原有的 13 个 JSP 文件仍保留原样，相关实现范围、缺失资源、运行限制与 CodePen 来源见 [早期 JSP 项目说明](docs/LEGACY_JSP.md)。它们用于保留学习记录；当前作品集由 `site/` 中的静态页面提供。
