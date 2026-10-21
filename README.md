# Yuchao Li 个人主页

用 Hugo 和 Pascal Michaillat 的 [hugo-website](https://github.com/pmichaillat/hugo-website) 模板（基于 PaperMod 主题）搭建，部署在 GitHub Pages。页面不引用任何外部 CDN、字体或统计脚本。

## 改哪里

| 内容 | 文件 |
|---|---|
| 名字、简介、导航、邮箱、LinkedIn | `config.yml` |
| 首页求职信息（JMP、领域、毕业时间、推荐人） | `config.yml` 里的 `profileMode.jobMarket` |
| 论文 | `content/papers/<论文>/index.md`，PDF 放在同一个文件夹 |
| 教学 | `content/teaching.md` |
| 照片 | `static/picture.jpeg` |
| CV | 在 Overleaf 里改，自动同步到 `static/Li_Yuchao_CV.pdf`（见下文"更新 CV"） |
| 网站地址 | `config.yml` 第一行的 `baseURL`（https://www.yuchaoli.com/） |
| GitHub Pages 部署 | `.github/workflows/hugo.yml` |
| CV 同步 | `.github/workflows/cv-sync.yml` |
| EdgeOne 构建设置（备用） | `edgeone.json` |

### 论文分组

Research 页按每篇论文 front matter 里的 `category` 分组，组内按 `weight` 从小到大排序：

| `category` | Research 页上的分组 |
|---|---|
| `"Job Market Paper"` | Job Market Paper |
| `"Working Paper"` | Working Papers |
| `"Work in Progress"` | Work in Progress |

新加一篇论文：复制一个论文文件夹，改标题、作者、`category`、`weight`、`summary`（Research 页卡片上的简介）和摘要。

### 更新 CV

在 Overleaf 里改完就行。`.github/workflows/cv-sync.yml` 每小时通过 Overleaf 的 Git 集成读取 CV 项目；发现新版本、并且到下一次检查时没再改动，就用完整的 TeX Live 编译，覆盖 `static/Li_Yuchao_CV.pdf`，再重新发布网站。所以改完后一到两小时，网站上就是新版。要马上更新：仓库的 Actions → Sync CV from Overleaf → Run workflow。

- 需要两个仓库 secret（Settings → Secrets and variables → Actions）：
  - `OVERLEAF_TOKEN`：在 Overleaf → Account Settings → Git integration 生成。有效期一年，过期后重新生成，替换这个 secret。
  - `OVERLEAF_PROJECT_ID`：CV 项目网址 `overleaf.com/project/` 后面那一串。
- Git 集成是 Overleaf 的付费功能。UCSC 的学校订阅包含它，前提是 Overleaf 账号关联了 UCSC SSO。
- 编译失败（或 token 过期）时，网站保留上一版 CV，仓库里会开一个 issue，GitHub 会发邮件通知。之后同步成功，issue 会自动关闭。
- 编译用 pdfLaTeX，和现在 Overleaf 的设置一致。如果在 Overleaf 里改用 XeLaTeX，工作流里的编译设置也要跟着改。
- 主文件自动识别：项目里唯一一个带 `\documentclass` 的 .tex 文件，有多个时用 `main.tex`。识别不了时，在仓库的 Actions variables 里加 `CV_MAIN_TEX`，值为文件名。
- 仓库 60 天没有新提交，GitHub 会自动停用定时任务。到 Actions 页面点 Enable workflow 即可恢复。
- 也可以直接用同名文件覆盖 `static/Li_Yuchao_CV.pdf`，但 Overleaf 上下一次有改动时会被覆盖回去。导航栏、首页按钮和图标的链接都不用改。

## 上线前要做

- [ ] 换照片 `static/picture.jpeg`（正方形，现在是占位图）
- [ ] 论文 PDF：放进各论文文件夹并命名为 `paper.pdf`，再删掉 Download 那段的注释标记。JMP 最要紧
- [ ] 核对首页的 JMP 简介和各论文卡片上的简介（摘要原文取自 CV）
- [x] 域名：yuchaoli.com（Porkbun）

## 本地预览

部署用的是 Hugo Extended 0.147.2。本地可以 `brew install hugo` 装最新版；如果构建报错，换成 [0.147.2](https://github.com/gohugoio/hugo/releases/tag/v0.147.2)。在仓库目录运行：

```bash
hugo server
```

浏览器打开 http://localhost:1313/ ，改完文件页面会自动刷新。

## 部署（GitHub Pages）

每次推送到 `main`，`.github/workflows/hugo.yml` 会自动构建并发布到 GitHub Pages。

- 仓库设置：Settings → Pages → Source 选 **GitHub Actions**；Custom domain 填 `www.yuchaoli.com`，勾选 Enforce HTTPS。
- DNS（Porkbun）：`www` 的 CNAME 指向 `yuchao-li2025.github.io`。不带 www 的 `yuchaoli.com` 用 URL Forwarding 301 跳转到 `https://www.yuchaoli.com`（保留路径）。
- 备用：EdgeOne Pages 项目仍然连着这个仓库，`edgeone.json` 是它的构建设置。要切回 EdgeOne，先在 EdgeOne 项目里重新绑定 `www.yuchaoli.com` 并完成 TXT 验证，再把 `www` 的 CNAME 改回 EdgeOne 给的地址。之前 UCSC 校园网的 DNS 安全过滤会把 EdgeOne 的地址（`dnsoe7.com`）当成钓鱼网站拦截，所以换到了 GitHub Pages。

## 保持国内可访问

- 公式渲染（KaTeX）放在 `static/katex/`，默认关闭。需要公式的页面在 front matter 里加 `math: true`。
- 不要在页面里嵌入 Google Fonts、Google Analytics、YouTube 等境外服务。
- PDF 一律放在站内，不要链接到 Google Drive 或 Dropbox。

## 许可

模板代码来自 Pascal Michaillat 的 hugo-website（MIT License，见 `LICENSE.md`）；KaTeX 为 MIT License（`static/katex/LICENSE`）。网站内容 © Yuchao Li。
