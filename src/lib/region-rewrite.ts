import { REGION } from './site-env';

/**
 * 语料兜底区域重写（B2 单源双区）——com 线旧「重写层」的泛化：
 * sync-wiki.py 已在语料层把 URL 定向到本区，这里只收口漏网形式：
 * 跨区 → 本区；裸域 → www.本区；本区带子域 → 原样（同一替换式自然收敛）。
 */
const REGION_URL = /https:\/\/(?:(docs|reference|wiki|developer|demos|www)\.)?autional\.(?:cn|com)/g;

export function rewriteRegionLinks(html: string): string {
  return html.replace(REGION_URL, (_m, sub: string | undefined) => `https://${sub ?? 'www'}.autional.${REGION}`);
}
