# Autional API Wiki Portal

**Sites**: [wiki.autional.com](https://wiki.autional.com) (com) / [wiki.autional.cn](https://wiki.autional.cn) (cn)
**Stack**: Astro 5 + Tailwind 3.4
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

- **zh** — generated in the AuthMS monorepo: `python scripts/generate/generate_api_wiki.py --html`, then normalized and copied into `wiki-src/zh/` by `python scripts/sync-wiki.py --lang zh`.
- **en** — regenerated from the reference portal's English specs by `python scripts/gen-wiki-en.py` (runs the same generator against `reference/public/specs/*-en.json`), then normalized and copied into `wiki-src/en/` by `python scripts/sync-wiki.py --lang en --src <gen-wiki-en html dir>`.

Services without a spec render the portal's "not yet indexed" fallback.

## Deploy

Push to `main` — Vercel auto-deploys. Projects: `wiki` (com) / `cn-wiki` (cn)；env 按项目分别注入。
