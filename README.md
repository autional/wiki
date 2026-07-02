# Autional API Wiki Portal

**Domain**: wiki.autional.com
**Stack**: Astro 5 + Tailwind 3.4
**Repository**: [github.com/autional/wiki](https://github.com/autional/wiki)

## Development

```bash
pnpm install
pnpm dev      # http://localhost:4435
pnpm build    # Static output to dist/
```

## Content Source

English Wiki HTML synced from the AuthMS backend monorepo:
`D:\go\auth_ms_new\document\generated\wiki\html-en\` → `public/wiki/api/`

## Update Content

```bash
cd D:\go\auth_ms_new
python scripts/generate/generate_api_wiki.py --english --html
python autional/scripts/sync_wiki.py           # sync to portal
cd D:\autional\wiki && pnpm build             # rebuild
```
