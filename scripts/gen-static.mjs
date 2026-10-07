#!/usr/bin/env node
/**
 * gen-static.mjs —— B2 构建前生成物（执行卡 §2 行 2）：public/robots.txt ← SITE_URL.
 *
 * 纪律：生成物已 gitignore + `git rm --cached`（勿手改、勿入库）；幂等，同一 env 重复执行输出一致。
 */
import { writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readBuildEnv } from './env.mjs';

const root = fileURLToPath(new URL('..', import.meta.url));
const { region, siteUrl, defaultLang } = readBuildEnv();

writeFileSync(join(root, 'public', 'robots.txt'), `User-agent: *\nAllow: /\nSitemap: ${siteUrl}/sitemap-index.xml\n`);

console.log(`[gen-static] region=${region} defaultLang=${defaultLang} site=${siteUrl} → public/robots.txt`);
