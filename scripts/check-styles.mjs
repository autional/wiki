#!/usr/bin/env node
/**
 * check-styles.mjs —— 内文样式层门（postbuild 校验 dist；非零退出 = 阻断发布）。
 *
 * 背景（2026-10-27，修复 87e91528）：模板容器类名由 .wiki-detail-content 漂移成
 * .wiki-content 后，`astro build`、`astro check`、`check-i18n` 全绿，但整站内文退化成
 * 无样式纯文本，漂移潜伏三个月才被肉眼发现。更隐蔽的第二种形态是把语料自带的
 * <style> 注回页面：它是无层样式，在 Tailwind 4 下永远压过 @layer 里的 utility。
 *
 * 断言（全部对着构建产物，不看源码意图）：
 *   S1 内文层全覆盖：除白名单（首页 / 404）外，每个 HTML 都带 .wiki-detail-content；
 *   S2 无旧内联样式：任何 HTML 都不得含语料独立页面样式标记 --c-method-post；
 *   S3 设计层规则在产物里：dist 的 CSS bundle 内 .wiki-detail-content 规则数 ≥ 30；
 *   S4 面包屑规则在产物里：语料每页都用 .breadcrumb，缺规则会渲染成裸链接。
 */
import { readdirSync, readFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const distPath = fileURLToPath(new URL('../dist', import.meta.url));

// 不走内文层的页面：首页（自绘卡片）与 404。新增此类页面要在这里显式登记。
const ALLOWLIST = new Set(['index.html', '404.html']);

const issues = [];
const walk = (dir, out) => {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) walk(full, out);
    else out.push(full);
  }
  return out;
};

let files;
try {
  files = walk(distPath, []);
} catch (e) {
  console.error(`[check-styles] 读不到构建产物：${distPath}（先跑 build）`);
  process.exit(1);
}

const htmlFiles = files.filter((f) => f.endsWith('.html'));
const cssFiles = files.filter((f) => f.endsWith('.css'));

if (htmlFiles.length === 0) issues.push('[S1] dist 里没有任何 HTML —— 产物异常');

let covered = 0;
for (const file of htmlFiles) {
  const rel = relative(distPath, file).replace(/\\/g, '/');
  const html = readFileSync(file, 'utf8');
  if (html.includes('wiki-detail-content')) covered++;
  else if (!ALLOWLIST.has(rel)) issues.push(`[S1] 内文层类名缺失：${rel}`);
  if (html.includes('--c-method-post')) issues.push(`[S2] 旧语料内联样式未清除：${rel}`);
}

if (cssFiles.length === 0) issues.push('[S3] dist 里没有 CSS bundle');

let layerHits = 0;
let breadcrumbHits = 0;
for (const file of cssFiles) {
  const css = readFileSync(file, 'utf8');
  layerHits += (css.match(/\.wiki-detail-content/g) || []).length;
  if (css.includes('.wiki-detail-content .breadcrumb')) breadcrumbHits++;
}
if (layerHits < 30) issues.push(`[S3] 内文层规则过少：CSS 内 .wiki-detail-content 命中 ${layerHits} 次（期望 ≥30）`);
if (breadcrumbHits === 0) issues.push('[S4] 缺 .wiki-detail-content .breadcrumb 规则');

console.log(
  `[check-styles] html=${htmlFiles.length} · 内文层覆盖=${covered} · css 命中=${layerHits} · ` +
    `面包屑=${breadcrumbHits > 0 ? '✔' : '✘'}`,
);
if (issues.length) {
  for (const line of issues.slice(0, 40)) console.error('  ' + line);
  if (issues.length > 40) console.error(`  … 其余 ${issues.length - 40} 条省略`);
  console.error(`[check-styles] FAIL —— ${issues.length} 项问题`);
  process.exit(1);
}
console.log('[check-styles] PASS');
