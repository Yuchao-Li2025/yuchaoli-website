# Yuchao Li 个人主页

用 Hugo 和 Pascal Michaillat 的 [hugo-website](https://github.com/pmichaillat/hugo-website) 模板（基于 PaperMod 主题）搭建，部署在腾讯 EdgeOne Pages。页面不引用任何境外 CDN、字体或统计脚本，国内外都能正常加载。

## 改哪里

| 内容 | 文件 |
|---|---|
| 名字、简介、导航、邮箱、LinkedIn | `config.yml` |
| 首页求职信息（JMP、领域、毕业时间、推荐人） | `config.yml` 里的 `profileMode.jobMarket` |
| 论文 | `content/papers/<论文>/index.md`，PDF 放在同一个文件夹 |
| 教学 | `content/teaching.md` |
| 照片、CV | `static/picture.jpeg`、`static/Li_Yuchao_CV.pdf` |
| 网站地址 | `config.yml` 第一行的 `baseURL`（https://www.yuchaoli.com/） |
| EdgeOne 构建设置 | `edgeone.json` |

### 论文分组

Research 页按每篇论文 front matter 里的 `category` 分组，组内按 `weight` 从小到大排序：

| `category` | Research 页上的分组 |
|---|---|
| `"Job Market Paper"` | Job Market Paper |
| `"Working Paper"` | Working Papers |
| `"Work in Progress"` | Work in Progress |

新加一篇论文：复制一个论文文件夹，改标题、作者、`category`、`weight`、`summary`（Research 页卡片上的简介）和摘要。

### 更新 CV

用同名文件覆盖 `static/Li_Yuchao_CV.pdf`，导航栏、首页按钮和图标的链接都不用改。

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

## 部署（EdgeOne Pages）

1. 把本仓库推到 GitHub。
2. 在 EdgeOne Pages 控制台导入这个仓库。它会识别出 Hugo，并读取 `edgeone.json`。
3. 加速区域选「全球可用区（不含中国大陆）」，不需要备案。
4. 绑定自定义域名 `www.yuchaoli.com`：先在 Porkbun 的 DNS 里删掉指向 `pixie.porkbun.com` 的默认记录，再按 EdgeOne 弹窗的提示加验证记录和 CNAME，然后在 EdgeOne 里申请免费 HTTPS 证书。
5. 不带 www 的 `yuchaoli.com`：在 Porkbun 的 URL Forwarding 里转发到 `https://www.yuchaoli.com`（301，勾选保留路径）。
6. 之后每次 `git push`，EdgeOne 会自动重新构建发布。

## 保持国内可访问

- 公式渲染（KaTeX）放在 `static/katex/`，默认关闭。需要公式的页面在 front matter 里加 `math: true`。
- 不要在页面里嵌入 Google Fonts、Google Analytics、YouTube 等境外服务。
- PDF 一律放在站内，不要链接到 Google Drive 或 Dropbox。

## 许可

模板代码来自 Pascal Michaillat 的 hugo-website（MIT License，见 `LICENSE.md`）；KaTeX 为 MIT License（`static/katex/LICENSE`）。网站内容 © Yuchao Li。
