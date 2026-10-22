# Yuchao Li 个人主页

用 Hugo 和 Pascal Michaillat 的 [hugo-website](https://github.com/pmichaillat/hugo-website) 模板（基于 PaperMod 主题）搭建，部署在 GitHub Pages。页面不引用任何外部 CDN、字体或统计脚本。

## 改哪里

| 内容 | 文件 |
|---|---|
| 名字、简介、导航、邮箱、LinkedIn、GitHub | `config.yml` |
| 首页图标的样子 | `layouts/partials/svg.html`：邮件、LinkedIn、GitHub 用的是 Tabler Icons 的线条图标，按 `config.yml` 里 `socialIcons` 的 `name` 对应 |
| 首页求职信息（求职状态、JMP、研究领域、推荐人、毕业时间、邮箱） | `config.yml` 里的 `profileMode.jobMarket`：`status` 是加粗的第一行，`items` 每项一行，左边是标签，右边是内容；内容要分几行时写成列表（如 Research fields） |
| 首页的版式（600px 单栏、分隔线、标签和内容两栏对齐、白底按钮） | `assets/css/extended/site.css`。首页不显示页脚，见 `layouts/_default/baseof.html` |
| 论文 | `content/papers/<论文>/index.md`，PDF 放在同一个文件夹 |
| 教学 | `content/teaching.md` |
| Syllabus | `static/teaching/ECON100B_Syllabus_Summer2026.pdf`、`static/teaching/ECON294A_Syllabus_Spring2026.pdf`，Teaching 页上的 Syllabus 链接指向它们。只放 PDF，.tex 源文件不放进仓库 |
| ECON 294A 课程页和讲义 | `content/econ294a/`，见下文"ECON 294A 讲义" |
| 照片 | `static/picture.jpeg`：480×480 的正方形 JPEG，约 24 KB，首页显示成 130px 的圆形（手机上 110px）。换照片时同名覆盖，尺寸和大小保持在这个量级，不要直接放相机或影楼原图 |
| 分享链接时的预览图 | `static/og.jpg`（1200×630），由 `config.yml` 里的 `images` 指定。源文件是 `og-image/og.html`（这个文件夹不会发布），改完运行 `python3 og-image/render.py` 重新生成；换图后把 `images` 改成 `og.jpg?v=2` 这样，避免各平台显示缓存的旧图。图里有求职那一行，求职季结束后要删掉再生成 |
| CV | 在 Overleaf 里改，自动同步到 `static/Li_Yuchao_CV.pdf`（英文）和 `static/Li_Yuchao_CV_zh.pdf`（中文），见下文"更新 CV" |
| 网站地址 | `config.yml` 第一行的 `baseURL`（https://www.yuchaoli.com/） |
| GitHub Pages 部署 | `.github/workflows/hugo.yml` |
| CV 同步 | `.github/workflows/cv-sync.yml` |
| 检查论文页和 CV 是否一致 | `tools/check_papers.py`，在 `hugo.yml` 的 check-papers 里运行，见下文"更新 CV" |
| EdgeOne 构建设置（备用） | `edgeone.json` |

### 论文分组

Research 页按每篇论文 front matter 里的 `category` 分组，组内按 `weight` 从小到大排序：

| `category` | Research 页上的分组 |
|---|---|
| `"Job Market Paper"` | Job Market Paper |
| `"Working Paper"` | Working Papers |
| `"Work in Progress"` | Work in Progress |

新加一篇论文：复制一个论文文件夹，改标题、作者、`category`、`weight`、`summary`（Research 页卡片上的简介）、`description` 和摘要。

### 更新 CV

英文和中文 CV 各是一个 Overleaf 项目，在 Overleaf 里改完就行。`.github/workflows/cv-sync.yml` 每小时通过 Overleaf 的 Git 集成读取这两个项目；某一份出现新版本、并且到下一次检查时没再改动，就用完整的 TeX Live 编译，覆盖对应的 PDF，再重新发布网站。所以改完后一到两小时，网站上就是新版。要马上更新：仓库的 Actions → Sync CV from Overleaf → Run workflow。

同步只更新 PDF，不会改网站上的论文页。论文的标题和摘要在 `content/papers/<论文>/index.md`，摘要原样取自英文 CV；同一文件里的 `summary`（Research 页卡片上的简介）和 `description`（搜索结果和分享链接时显示的那句话）都是由摘要缩写的；首页 `config.yml` 里 `jobMarket` 也写着 JMP 的标题和简介（`note`）。在 CV 里改了论文的标题或摘要，这几处要另外改。

为了不漏改，网站每次重新发布（包括 CV 同步之后）都会检查各篇论文的标题和摘要是否还和英文 CV 一致。对不上就在仓库开一个 issue，标题是 "Paper text on the website differs from the English CV"（GitHub 会发邮件），里面列出是哪一篇、网站上哪几句在 CV 里找不到；改好推上去，一致了这个 issue 会自动关闭。检查结果不影响网站发布。

- 比较时不区分大小写，也不看标点、空格和换行，所以只改了标点（比如连字符）不会报。
- 只检查网站上已有的论文。CV 里新加的论文，要另外加到网站上。
- 某篇论文有意和 CV 不一样（比如网站上放的是论文里的完整摘要），在它的 front matter 里写 `cv_check: false`，就不再检查这一篇。`draft: true` 的论文也不检查。
- 在本机检查：`pip install pypdf`，然后在仓库目录运行 `python3 tools/check_papers.py`。

| | 英文 CV | 中文 CV |
|---|---|---|
| 网站上的文件 | `static/Li_Yuchao_CV.pdf` | `static/Li_Yuchao_CV_zh.pdf` |
| 项目 ID 的 secret | `OVERLEAF_PROJECT_ID` | `OVERLEAF_PROJECT_ID_ZH` |
| 编译器（和 Overleaf 项目的设置一致） | pdfLaTeX | XeLaTeX |
| 网站上的入口 | 导航栏 CV、首页 CV 按钮 | 导航栏"中文简历"、首页"中文简历"按钮 |

- 仓库 secret 在 Settings → Secrets and variables → Actions：
  - `OVERLEAF_TOKEN`：在 Overleaf → Account Settings → Git integration 生成，同一个账号下的项目共用。有效期一年，过期后重新生成，替换这个 secret。
  - 两个项目 ID：项目网址 `overleaf.com/project/` 后面那一串。哪份没设，就跳过哪份。
- Git 集成是 Overleaf 的付费功能。UCSC 的学校订阅包含它，前提是 Overleaf 账号关联了 UCSC SSO。
- "中文简历"按钮只在 `static/Li_Yuchao_CV_zh.pdf` 存在时显示（`layouts/partials/index_profile.html` 会检查按钮指向的站内 PDF 是否存在）。
- 中文字体：ctex 默认的 Fandol、Overleaf 自带的 Noto Serif/Sans CJK、上传到项目里的字体文件，同步编译时都有。
- 编译失败（或 token 过期）时，网站保留上一版，仓库里会开一个 issue（标题注明是哪一份 CV），GitHub 会发邮件通知。之后同步成功，issue 会自动关闭。
- 如果在 Overleaf 里换了编译器，cv-sync.yml 里对应那份的 `xelatex` 也要跟着改。
- 主文件自动识别：项目里唯一一个带 `\documentclass` 的 .tex 文件，有多个时用 `main.tex`。识别不了时，在 cv-sync.yml 里给那份 CV 写上 `main`。
- 仓库 60 天没有新提交，GitHub 会自动停用定时任务。到 Actions 页面点 Enable workflow 即可恢复。
- 也可以直接用同名文件覆盖 static/ 里的 PDF，但 Overleaf 上下一次有改动时会被覆盖回去。导航栏和首页按钮的链接都不用改。

## ECON 294A 讲义

网址是 https://www.yuchaoli.com/econ294a/ ，Teaching 页上 ECON 294A 那一行的 Lecture notes 链接到这里。

- 课程页：`content/econ294a/_index.md`。讲义列表直接写在正文里，新增或改名要手动改这里。
- 每一讲一个文件夹 `content/econ294a/lecture-N/`，里面有：
  - `index.html`：讲义网页的正文，由 notebook 转成，不要手改；
  - `fig-01.png`、`fig-02.png`……：notebook 里的图；
  - `ECON294A_LectureN.ipynb`：页面上"Download notebook"下载的就是这个文件。
- 模板在 `layouts/econ294a/`，样式在 `assets/css/extended/notebook.css`。
- 页面不加载任何站外资源，图片已压缩，国内可以正常打开。

更新某一讲（需要 Python，先 `pip install nbconvert nbformat beautifulsoup4 pillow`）：

1. 在 Colab 里改好、运行完，File → Download → Download .ipynb。
2. 清理成公开版：`python3 tools/econ294a/clean_notebook.py 下载的.ipynb ECON294A_LectureN.ipynb`。它会去掉 Colab 记在每个格子里的 Google 账号名和 ID、Colab 表格的脚本、pip 安装的进度输出和运行编号，并压缩图片。
3. 生成网页：`python3 tools/econ294a/nb2page.py ECON294A_LectureN.ipynb content/econ294a/lecture-N tools/econ294a/front-matter/N.json`。它会重建这一讲的文件夹（网页、图片和 .ipynb）。标题和简介在 `tools/econ294a/front-matter/N.json` 里改。
4. 本地预览没问题后提交。

`tools/` 文件夹不会发布到网站上。

## 上线前要做

- [x] 换照片 `static/picture.jpeg`
- [ ] 论文 PDF：放进各论文文件夹并命名为 `paper.pdf`，再删掉 Download 那段的注释标记。JMP 最要紧
- [ ] 核对各论文卡片上的简介（摘要原文取自 CV）
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

模板代码来自 Pascal Michaillat 的 hugo-website（MIT License，见 `LICENSE.md`）；KaTeX 为 MIT License（`static/katex/LICENSE`）；首页的邮件、LinkedIn、GitHub 图标来自 Tabler Icons（MIT License，Copyright (c) 2020-2026 Paweł Kuna）。网站内容 © Yuchao Li。
