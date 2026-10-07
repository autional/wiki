# Autional API Wiki Portal

**Domain**: wiki.autional.cn
**Stack**: Astro 5 + Tailwind 3.4
**Repository**: [github.com/autional-cn/wiki](https://github.com/autional-cn/wiki)

## Development

```bash
pnpm install
pnpm dev      # http://localhost:4435
pnpm build    # Static output to dist/
```

## Content Source

Chinese Wiki HTML synced from the AuthMS backend monorepo:
`D:\go\auth_ms_new\document\generated\wiki\html\` → `wiki-src/`

`wiki-src/` is the build-time content source for the Astro pages and is
committed (Vercel builds from this repo). It lives outside `public/` so the
raw mirror is not shipped in `dist/`; legacy `/wiki/api/**` URLs are
301-redirected to the clean routes by `vercel.json`.

## Update Content

```bash
cd D:\go\auth_ms_new
python scripts/generate/generate_api_wiki.py --html   # generate Chinese HTML
python D:\ws\autional-cn\sites\wiki\scripts\sync-wiki-zh.py   # sync + normalize for .cn
pnpm build                                            # rebuild
```
