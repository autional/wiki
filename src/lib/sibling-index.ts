/**
 * 对侧区同端点解析（构建期，SSG 专用）—— 修复 hreflang 死链。
 *
 * 背景：两区语料由各自的规范生成，路径参数名不同（zh `{user_id}` / en `{id}`），
 * 因此同一端点在两区的 slug 不同；直接按 pathname 拼接对侧 URL 会指向 404。
 * 本模块按「METHOD + 归一化 path」建立对侧索引，返回对侧真实路由。
 *
 * 返回值：
 *   string  —— 对侧存在的同端点路径（以 / 结尾）
 *   null    —— 对侧未收录（调用方应省略该 hreflang）
 */
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { DEFAULT_LANG } from './site-env';

const CURRENT_DIR = join(process.cwd(), 'wiki-src', DEFAULT_LANG === 'en' ? 'en' : 'zh');
const SIBLING_DIR = join(process.cwd(), 'wiki-src', DEFAULT_LANG === 'en' ? 'zh' : 'en');

const KEY_RE = /<span class="meta-item method ([A-Z]+)">[A-Z]*<\/span>\s*<code class="path">([^<]+)<\/code>/;
const keyOf = (method: string, endpointPath: string) =>
  `${method} ${endpointPath.trim().replace(/\{[^}]*\}/g, '{}')}`;

let siblingIndex: Map<string, string> | null = null;

function buildIndex(): Map<string, string> {
  if (siblingIndex) return siblingIndex;
  const map = new Map<string, string>();
  siblingIndex = map;
  if (!existsSync(SIBLING_DIR)) return map;

  const walk = (dir: string, base: string) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const full = join(dir, entry.name);
      const rel = base ? `${base}/${entry.name}` : entry.name;
      if (entry.isDirectory()) {
        walk(full, rel);
        continue;
      }
      if (entry.name !== 'index.html' || !base) continue;
      const hit = KEY_RE.exec(readFileSync(full, 'utf8'));
      if (!hit) continue;
      map.set(keyOf(hit[1], hit[2]), `/${base}/`);
    }
  };
  walk(SIBLING_DIR, '');
  return map;
}

export function siblingPathFor(pathname: string): string | null {
  const segs = pathname.split('/').filter(Boolean);
  // 首页与服务索引页在两区由同一份 services.ts 生成，恒存在。
  if (segs.length <= 1) return `/${segs.join('/')}${segs.length ? '/' : ''}`;

  const siblingFile = join(SIBLING_DIR, ...segs, 'index.html');
  const currentFile = join(CURRENT_DIR, ...segs, 'index.html');
  if (!existsSync(currentFile)) {
    // 当前页本身不在语料里（理论上只有服务级页面），退回同路径判断。
    return existsSync(siblingFile) ? pathname : null;
  }

  const hit = KEY_RE.exec(readFileSync(currentFile, 'utf8'));
  // 解析失败（格式漂移）时退回同路径判断，至少不放弃可用的对侧页。
  if (!hit) return existsSync(siblingFile) ? pathname : null;

  return buildIndex().get(keyOf(hit[1], hit[2])) ?? (existsSync(siblingFile) ? pathname : null);
}
