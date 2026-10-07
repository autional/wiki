import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';
import { readBuildEnv } from './scripts/env.mjs';

// ── 构建期区域环境（B2 单源双区；契约见 23 执行卡 §2）────────────────────────
// 两区同源构建，区域差异全部经 env 注入（Vercel 项目侧值；读取单点 = scripts/env.mjs）。
// 此处经 vite.define 内联成 import.meta.env.PUBLIC_*，供 src/lib/site-env.ts、src/i18n 与客户端脚本使用。
const {
  siteUrl: ENV_SITE_URL,
  region: ENV_REGION,
  defaultLang: ENV_DEFAULT_LANG,
  fallbackLang: ENV_FALLBACK_LANG,
  cdnHost: ENV_CDN_HOST,
} = readBuildEnv();

export default defineConfig({
  integrations: [tailwind(), sitemap()],
  output: 'static',
  site: ENV_SITE_URL,
  base: '/',
  vite: {
    define: {
      'import.meta.env.PUBLIC_REGION': JSON.stringify(ENV_REGION),
      'import.meta.env.PUBLIC_SITE_URL': JSON.stringify(ENV_SITE_URL),
      'import.meta.env.PUBLIC_DEFAULT_LANG': JSON.stringify(ENV_DEFAULT_LANG),
      'import.meta.env.PUBLIC_FALLBACK_LANG': JSON.stringify(ENV_FALLBACK_LANG),
      'import.meta.env.PUBLIC_CDN_HOST': JSON.stringify(ENV_CDN_HOST),
    },
  },
});
