# Autional API Wiki Portal

**Sites**: [wiki.autional.com](https://wiki.autional.com) (com) / [wiki.autional.cn](https://wiki.autional.cn) (cn)
**Stack**: Astro 7 + Tailwind 4（2026-10-22 由 Astro 5 / Tailwind 3.4 抬版，CVE-2026-114127/114128）
**Repository**: [github.com/autional/wiki](https://github.com/autional/wiki)

API reference wiki: generated HTML for every endpoint of every service, rendered by Astro.

Single source, dual-region build: one repo serves both regions. Regional differences (site URL, default/fallback language, CDN host, brother-site links) are injected at build time via env — `REGION` / `SITE_URL` / `DEFAULT_LANG` / `FALLBACK_LANG` / `CDN_HOST`（读取单点 `scripts/env.mjs`；落点见 `astro.config.mjs` 的 `vite.define` 与 `src/lib/site-env.ts`）。默认语言 zh 兜底为本区（cn）。文案双语化（`src/i18n/{en-US,zh-CN}.json` 单键空间，`scripts/check-i18n.mjs` 门禁）；语言切换为客户端行为（localStorage 键 `autional-lang`），静态页始终是区域默认语言。

## Development

```bash
pnpm install
pnpm dev      # http://localhost:4435（无 env 时兜底 cn 值）
pnpm build    # 产物 dist/；prebuild 生成 public/robots.txt + 跑 check-i18n
```

双区本地构建：

```bash
REGION=cn SITE_URL=https://wiki.autional.cn DEFAULT_LANG=zh FALLBACK_LANG=zh CDN_HOST=https://cdn.autional.cn pnpm build
REGION=com SITE_URL=https://wiki.autional.com DEFAULT_LANG=en FALLBACK_LANG=en CDN_HOST=https://cdn.autional.com pnpm build
```

## Content Source

`wiki-src/<lang>/` is the build-time content source for the Astro pages and is committed (Vercel builds from this repo). It lives outside `public/`, so the raw mirror never reaches `dist/`; legacy `/wiki/api/**` URLs are 301-redirected to the clean routes by `vercel.json`.

- **zh** — generated in the Autional monorepo: `python scripts/generate/generate_api_wiki.py --html`, then normalized and copied into `wiki-src/zh/` by `python scripts/sync-wiki.py --lang zh`.
- **en** — regenerated from the reference portal's English specs by `python scripts/gen-wiki-en.py` (runs the same generator against `reference/public/specs/*-en.json`), then normalized and copied into `wiki-src/en/` by `python scripts/sync-wiki.py --lang en --src <gen-wiki-en html dir>`.

Services without a spec render the portal's "not yet indexed" fallback.

## 语料刷新记录

- **2026-10-13 已重跑 zh 语料**（`generate_api_wiki.py --html` → `sync-wiki.py --lang zh`）：补齐 48 个缺失 admin 端点页（billing alerts、notification 模板/统计、storage、communication dashboard、pay/point admin 等）、侧栏补 `stream-service`、按最新 swagger 更新服务页端点计数与内容、移除 1 个已下线端点（identity role-activation approve → revoke）。语料无品牌残留。
- `wiki-src/en/` 的覆盖受 reference 侧 en 规范落后影响（en 为人工英文快照，见 reference 仓 README「en 端点覆盖落后」）；英文语料随 en 规范重生成。

## 内文样式层（改样式前必读）

语料 HTML 由 `src/pages/[service].astro` / `src/pages/[...slug].astro` 在构建期读出 `<main>` 内容、用 `set:html` 注入页面。内文样式**只有一个来源**：`src/styles/global.css` 里挂在 `.wiki-detail-content` 下的规则（约 48 条，覆盖 h1–h4 / p / a / code / table / meta pill / 面包屑 / 按钮组）。

三条硬约束：

1. **容器类名必须是 `wiki-detail-content`**。改成别的名字不会报错，构建、`astro check`、`check-i18n` 全绿，但内文会退化成无样式纯文本。2026-07-02 的 SSG 改造曾把它写成 `wiki-content`，漂移到 2026-10-27 才被肉眼发现。
2. **不要注入语料自带的 `<style>`**。那是按「独立页面」写死的样式（`:root` 变量、`*{margin:0;padding:0}` 全局重置、裸 `h1/h2/table` 选择器），注入后会泄漏到站点 chrome（顶栏、侧栏、正文字体）。2026-10-22 Tailwind 3→4 后更致命：v4 的 utility 在原生 `@layer` 里，**无层样式永远压过带层样式（与特异度无关）**，一个 `*{padding:0}` 就能让全站内容区 padding 归零。
3. **语料新增 class 要同步补规则**。语料生成器（`generate_api_wiki.py` / `gen-wiki-en.py`）产出的 class 若在 `.wiki-detail-content` 下没有对应规则，就会渲染成裸元素；`.breadcrumb` 就是这样补上的。

排查法：打开页面执行 `getComputedStyle(document.querySelector('.wiki-detail-content')).padding`——正常是 `40px 32px`（桌面）；若为 `0px`，先找有没有无层 `<style>` 注入（`document.styleSheets` 里 `href === null` 的表），或临时把它 `disabled = true` 看是否恢复。

## Deploy

Push to `main` — Vercel auto-deploys. Projects: `wiki` (com) / `cn-wiki` (cn)；env 按项目分别注入。
