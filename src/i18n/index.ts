/**
 * i18n 单键空间（轻实现，无 npm 依赖；契约见 B2 执行卡 §1.1 与 B1 web / B2 docs 同源约定）：
 * - 双资源 en-US / zh-CN，嵌套键空间；键名本身禁含点号（check-i18n G1）；
 * - 初始语言由构建期 env 注入（REGION / DEFAULT_LANG / FALLBACK_LANG，见 astro.config.mjs vite.define）；
 *   不做 navigator 探测——区域即语言；
 * - 手动切换为客户端行为：WikiLayout 内联脚本监听 LANG_EVENT，按 [data-i18n*] 重写文本/属性，无 URL 变化；
 *   偏好存 localStorage（键 autional-lang），刷新后由 restoreLang() 采纳（首帧仍为区域默认语言，属已接受代价）。
 */
import enUS from './en-US.json';
import zhCN from './zh-CN.json';

export const langs = ['zh', 'en'] as const;
export type Lang = (typeof langs)[number];

/** 语言偏好存储键（与主题键 autional-theme 并列）。 */
export const LANG_STORAGE_KEY = 'autional-lang';

/** 语言切换事件名：WikiLayout 的 DOM 交换脚本监听此事件。 */
export const LANG_EVENT = 'autional:lang';

/** lang 短码 ↔ BCP-47 locale（资源键用 locale 全码）。 */
export const langToLocale = (lang: Lang): string => (lang === 'en' ? 'en-US' : 'zh-CN');
export const localeToLang = (locale: string): Lang => (locale.startsWith('en') ? 'en' : 'zh');

/** 区域 → 默认语言（com=en / cn=zh）。region 缺省取构建期 REGION。 */
export const defaultLang = (region?: string): Lang =>
  (region ?? (import.meta.env.PUBLIC_REGION as string | undefined) ?? 'cn') === 'com' ? 'en' : 'zh';

const resources: Record<string, unknown> = { 'en-US': enUS, 'zh-CN': zhCN };

/** 本区渲染语言：DEFAULT_LANG 优先（构建期显式声明），缺省按区域推导。 */
const envDefaultLang: Lang =
  (import.meta.env.PUBLIC_DEFAULT_LANG as Lang | undefined) ?? defaultLang();
const envFallbackLocale = langToLocale(
  ((import.meta.env.PUBLIC_FALLBACK_LANG as Lang | undefined) ?? envDefaultLang) as Lang,
);

type Params = Record<string, string | number>;

/** 点路径查找（数值段回落数组下标）。 */
const lookup = (resource: unknown, key: string): unknown => {
  let node: unknown = resource;
  for (const seg of key.split('.')) {
    if (node === null || typeof node !== 'object') return undefined;
    node = Array.isArray(node) ? node[Number(seg)] : (node as Record<string, unknown>)[seg];
  }
  return node;
};

const interpolate = (template: string, params?: Params): string =>
  params ? template.replace(/\{(\w+)\}/g, (m, p: string) => (p in params ? String(params[p]) : m)) : template;

/** 取值：默认语言 → 回落语言 → 构建期 throw（缺键即失败）/ 浏览器 console.warn + 返回键名。 */
const resolve = (lang: Lang, key: string): unknown => {
  const value = lookup(resources[langToLocale(lang)], key) ?? lookup(resources[envFallbackLocale], key);
  if (value !== undefined) return value;
  if (typeof window === 'undefined') throw new Error(`[i18n] missing key: ${key}`);
  console.warn(`[i18n] missing key: ${key}`);
  return key;
};

/** 取词单点（构建期，.astro frontmatter 用）：字符串缺省，`{ returnObjects: true }` 取数组/对象。 */
export function t(key: string, options: { returnObjects: true } & Params): unknown;
export function t(key: string, options?: Params): string;
export function t(key: string, options?: Params & { returnObjects?: boolean }): unknown {
  const value = resolve(envDefaultLang, key);
  if (options?.returnObjects) return value;
  return interpolate(String(value), options);
}

/** 客户端取词（WikiLayout 内联脚本用）：按当前语言取字符串。 */
export const translate = (lang: Lang, key: string, params?: Params): string =>
  interpolate(String(resolve(lang, key)), params);

const isLang = (v: unknown): v is Lang => typeof v === 'string' && (langs as readonly string[]).includes(v);

/** 当前生效语言（客户端读 <html lang>，构建期即本区渲染语言）。 */
export const currentLang = (): Lang =>
  typeof document !== 'undefined'
    ? localeToLang(document.documentElement.lang || langToLocale(envDefaultLang))
    : envDefaultLang;

/** 当前语言之外的另一种语言（切换目标）。 */
export const otherLang = (lang: Lang): Lang => (lang === 'zh' ? 'en' : 'zh');

/** 客户端切换：localStorage 持久化 + <html lang> 同步 + LANG_EVENT 广播（WikiLayout 脚本据此重写 DOM）。 */
export const setLang = (lang: Lang): void => {
  try {
    localStorage.setItem(LANG_STORAGE_KEY, lang);
  } catch {
    /* 隐私模式等场景忽略 */
  }
  if (typeof document !== 'undefined') document.documentElement.lang = langToLocale(lang);
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent(LANG_EVENT, { detail: { lang, locale: langToLocale(lang) } }));
  }
};

/** 客户端采纳已存偏好（非本区默认语言才切换；构建期与无偏好路径为 no-op）。 */
export const restoreLang = (): void => {
  if (typeof window === 'undefined') return;
  try {
    const saved = localStorage.getItem(LANG_STORAGE_KEY);
    if (isLang(saved) && saved !== envDefaultLang) setLang(saved);
  } catch {
    /* 忽略 */
  }
};
