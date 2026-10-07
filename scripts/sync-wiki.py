#!/usr/bin/env python3
"""Sync API wiki HTML from the AuthMS monorepo into this portal, per language.

Source (generated in the monorepo):
    cd D:\\go\\auth_ms_new
    python scripts/generate/generate_api_wiki.py --html

The generator emits English template chrome + English content under
    document/generated/wiki/html/api/<service>/...
This script normalizes the generator's hardcoded URLs/branding per language and
copies the result to `wiki-src/<lang>/`:

    --lang zh : translates the English template chrome (breadcrumbs, section
                headings, table headers, Yes/No badges, footer, buttons) and
                rewrites URLs/branding to the `.cn` region.
    --lang en : keeps the English chrome as-is; rewrites URLs/branding to the
                `.com` region (URL/brand normalization only).

`wiki-src/<lang>/` is the build-time content source for the Astro pages and is
kept OUTSIDE `public/`, so the raw mirror never reaches `dist/`; legacy
`/wiki/api/**` URLs are 301-redirected to the clean Astro routes by
`vercel.json`. The Astro rendering layer (src/pages/[...slug].astro,
src/pages/[service].astro) additionally applies a REGION link-rewrite table as
a safety net (see src/lib/region-rewrite.ts).

The generator's raw root page (`api/index.html`, a stale overview) and its
`sitemap.xml` artifacts are NOT copied: the portal serves clean Astro routes
at `/` and an Astro sitemap-index instead.

Usage:
    python scripts/sync-wiki.py --lang zh
    # en: the raw html comes from the reference portal's en specs (see gen-wiki-en.py)
    python scripts/gen-wiki-en.py                 # prints the raw html dir
    python scripts/sync-wiki.py --lang en --src <that dir> [--out <dir>]
"""

import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

AUTH_WIKI = r"D:\go\auth_ms_new\document\generated\wiki\html"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Files at the docs root that must not be copied (stale generator output;
# the portal has clean equivalents — see module docstring).
SKIP_AT_ROOT = {"index.html", "sitemap.xml"}

# Display names emitted by the generator (h1, breadcrumbs, titles) mapped to the
# portal's Chinese service titles (kept in line with src/data/services.ts).
SERVICE_NAME_ZH = {
    "Identity Service": "身份服务",
    "Profile Service": "用户资料服务",
    "Tenant Service": "租户服务",
    "Session Service": "会话服务",
    "MFA Service": "多因素认证服务",
    "OAuth Service": "OAuth 服务",
    "Wallet Service": "钱包服务",
    "Point Service": "积分服务",
    "Audit Service": "审计服务",
    "Notification Service": "通知服务",
    "Communication Service": "通信服务",
    "Storage Service": "存储服务",
    "Billing Service": "计费服务",
    "Compliance Service": "合规服务",
    "Status Service": "状态服务",
    "Secret Service": "密钥服务",
    "SAML Service": "SAML 服务",
    "Pay Service": "支付服务",
    "Thirdparty Service": "第三方服务",
    "Verification Service": "身份验证服务",
    "RBAC Service": "RBAC 服务",
    "Gateway Service": "网关服务",
    "Hash Service (Standard)": "密码哈希服务",
    "Hash Service (SM3)": "国密哈希服务",
    "Captcha3D Service": "3D 验证码服务",
    "Config Service": "配置中心服务",
    "Stream Service": "实时事件流服务",
}


def _strip_gitee(m: re.Match) -> str:
    """gitee_com_autional_service-X_internal_handler_dto.Type -> service-X/internal/handler/dto.Type

    Applied identically to display text, element ids and href fragments so the
    `#schema-...` anchors stay mutually consistent."""
    mod, pkg, typ = m.group(1), m.group(2), m.group(3) or ""
    return f"{mod}/{pkg.replace('_', '/')}{typ}"


# URL / branding normalization shared by both languages. The region host is the
# only difference (cn: *.autional.cn / com: *.autional.com).
def _shared_replacements(region: str) -> list:
    ref = f"https://reference.autional.{region}"
    wiki = f"https://wiki.autional.{region}"
    www = f"https://www.autional.{region}"
    return [
        # Spec download links (generator emits a path without file extension)
        (re.compile(r"https://iam\.tianv\.com/docs/specs/([a-z0-9-]+)"), rf"{ref}/specs/\1.json"),
        # Scalar explorer deep links
        (re.compile(r"https://iam\.tianv\.com/docs/([a-z0-9-]+)"), rf"{ref}/\1/"),
        (re.compile(r"https://iam\.tianv\.com/docs/"), f"{ref}/"),
        # Portal hosts
        ("https://wiki.iam.tianv.com", wiki),
        ("https://iam.tianv.com", www),
        ("iam.tianv.com →", f"www.autional.{region} →"),
        ("iam.tianv.com", f"www.autional.{region}"),
        # Generator bug: `docs.autional.com/referenceX` / `.../referencespecs/` are
        # malformed; they belong to the reference portal.
        (re.compile(r"https://docs\.autional\.com/reference([a-z])"), rf"{ref}/\1"),
        ("https://docs.autional.com/referencespecs/", f"{ref}/specs/"),
        ('"https://docs.autional.com/reference"', f'"{ref}"'),
        # Any remaining `.com`/`.cn` hosts -> this region's tld
        (re.compile(r"https://(?:(docs|reference|wiki|developer|demos)\.)?autional\.com"), rf"https://\1.autional.{region}"),
        (f"https://autional.{region}", f"{www}"),
        # Branding
        ("AuthMS", "Autional"),
        # The generator emits legacy `/api/...` paths; the portal serves the same
        # pages at clean root paths (see src/pages/[service].astro, [...slug].astro).
        ('href="/api/', 'href="/'),
        (f"{wiki}/api/", f"{wiki}/"),
        # Internal gitee repo paths -> module/package path (text/id/href consistent).
        (re.compile(r"gitee_com_autional_(service-[a-z0-9-]+)_([a-z0-9_]+)(\.[A-Za-z0-9_]+)?"), _strip_gitee),
        # Legacy example domains / internal hostnames.
        ("authms.example.com", "app.example.com"),
        ("https://minio:9000/", "https://minio.example.com:9000/"),
        # Service summary line: internal docker path -> public spec JSON link
        # (the surrounding text is translated separately, see ZH_CHROME_TRANSLATIONS).
        (re.compile(r"<code>docker/specs/([a-z0-9-]+)/</code>"),
         rf'<a href="{ref}/specs/\1.json"><code>\1.json</code></a>'),
        # Mobile: wrap tables in a horizontal scroll container (styling in global.css).
        ("<table", '<div class="table-wrap"><table'),
        ("</table>", "</table></div>"),
    ]


# zh-only template-chrome translation (content-flow audit W-03/W-04/W-07/W-12/W-13).
ZH_CHROME_TRANSLATIONS = [
    # Breadcrumbs: 文档 / API 参考 (third segment = service name via mapping below).
    ('breadcrumb"><a href="/">Docs</a>', 'breadcrumb"><a href="/">文档</a>'),
    ('<span>›</span><a href="/">API Reference</a>', '<span>›</span><a href="https://reference.autional.cn">API 参考</a>'),
    # Same phrase in the raw page's own header nav (outside <main>; dead chrome,
    # kept translated so no English survives in the committed source).
    ('<a href="/">API Reference</a>', '<a href="https://reference.autional.cn">API 参考</a>'),
    # Service display names in h1/breadcrumbs/titles.
    *SERVICE_NAME_ZH.items(),
    # Titles + service meta descriptions.
    (" API | Autional</title>", " API 文档 — Autional</title>"),
    (re.compile(r" API reference — (\d+) endpoints\. Port (\d+)\."), r" API 参考 — \1 个端点。端口 \2。"),
    # Section headings.
    ("<h2>Request Parameters</h2>", "<h2>请求参数</h2>"),
    ("<h2>Request Body</h2>", "<h2>请求体</h2>"),
    ("<h2>Responses</h2>", "<h2>响应</h2>"),
    ("<h2>Referenced Schemas</h2>", "<h2>引用的 Schema</h2>"),
    # Table headers (four variants).
    ("<th>Field</th><th>Type</th><th>Required</th><th>Example</th><th>Constraints</th><th>Description</th>",
     "<th>字段</th><th>类型</th><th>必填</th><th>示例</th><th>约束</th><th>描述</th>"),
    ("<th>Status</th><th>Description</th><th>Schema</th>",
     "<th>状态</th><th>描述</th><th>Schema</th>"),
    ("<th>Name</th><th>In</th><th>Type</th><th>Required</th><th>Default</th><th>Example</th><th>Constraints</th><th>Description</th>",
     "<th>名称</th><th>位置</th><th>类型</th><th>必填</th><th>默认值</th><th>示例</th><th>约束</th><th>描述</th>"),
    ("<th>Method</th><th>Path</th><th>Summary</th><th></th>",
     "<th>方法</th><th>路径</th><th>摘要</th><th></th>"),
    # Required / optional badges.
    ('<span class="optional">No</span>', '<span class="optional">否</span>'),
    ('<span class="required">Yes</span>', '<span class="required">是</span>'),
    # Misc phrases.
    ("<strong>Schema:</strong>", "<strong>Schema：</strong>"),
    ("Accepts an empty JSON object", "接受空 JSON 对象"),
    ('See <a href="#schema-', '参见 <a href="#schema-'),
    (">detail →</a>", ">详情 →</a>"),
    # Action buttons + footer.
    ("Try this API in Scalar →", "在 Scalar 中试用此 API →"),
    ("Download OpenAPI spec (JSON) ↓", "下载 OpenAPI 规范（JSON）↓"),
    ("Generated from OpenAPI specs.", "基于 OpenAPI 规范自动生成。"),
    ("Interactive API explorer (Scalar)", "交互式 API 浏览器（Scalar）"),
    # Service summary line text (the docker path -> spec link rewrite is shared).
    (re.compile(r"Port (\d+) &middot; (\d+) endpoints &middot;"),
     r"端口 \1 &middot; \2 个端点 &middot;"),
]


# en-only normalization: the generator's own pages carry zh-flavored lang
# attributes (`<html lang="zh-CN">` + language metas); the en corpus must be
# en-US throughout (zh keeps them as-is).
EN_CHROME_ADDITIONS = [
    ('<html lang="zh-CN">', '<html lang="en-US">'),
    ('content="zh-CN"', 'content="en-US"'),
    ('hreflang="zh"', 'hreflang="en"'),
]


def replacements_for(lang: str) -> list:
    shared = _shared_replacements("cn" if lang == "zh" else "com")
    if lang == "zh":
        # Shared URL/branding normalization first (order identical to the
        # pre-merge sync-wiki-zh.py), then the template-chrome translation
        # (its ` API | Autional</title>` pattern depends on the AuthMS→Autional
        # rename having happened already).
        return shared + ZH_CHROME_TRANSLATIONS
    return shared + EN_CHROME_ADDITIONS


# A quote right after `href="/` means a replacement ate the closing quote and
# left the rest of the URL as stray text (see the `href="/api/` rule above).
MALFORMED_HREF = re.compile(r'href="/"[A-Za-z]')

# Strings that must not survive normalization; a hit means the generator changed
# its templates and the replacement table above needs updating.
COMMON_RESIDUALS = [
    "gitee_com_autional_",
    "docker/specs/",
]

ZH_RESIDUALS = COMMON_RESIDUALS + [
    # English chrome that must be gone in the zh corpus ("endpoints &middot;"
    # legitimately remains in the en corpus).
    "endpoints &middot;",
    ">detail →</a>",
    "Request Parameters</h2>",
    "Referenced Schemas</h2>",
    "Generated from OpenAPI specs.",
    "Interactive API explorer (Scalar)",
    "Try this API in Scalar",
    "Download OpenAPI spec (JSON)",
    " API | Autional</title>",
    'class="optional">No<',
    'class="required">Yes<',
    '<a href="/">API Reference</a>',
]

EN_RESIDUALS = COMMON_RESIDUALS + [
    "tianv",
    "AuthMS",
    "autional.cn",
    # zh-flavored head attributes that EN_CHROME_ADDITIONS must have rewritten
    # ("zh-CN" bare is legitimate page CONTENT, e.g. the communication templates
    # locale parameter — only the attribute forms are gate-worthy).
    'lang="zh-CN"',
    'content="zh-CN"',
    'hreflang="zh"',
]


def normalize(content: str, lang: str) -> str:
    for old, new in replacements_for(lang):
        if isinstance(old, re.Pattern):
            content = old.sub(new, content)
        else:
            content = content.replace(old, new)
    return content


def check(content: str, src: str, lang: str) -> str | None:
    if MALFORMED_HREF.search(content):
        return "malformed href remains after normalization"
    residuals = ZH_RESIDUALS if lang == "zh" else EN_RESIDUALS
    for residual in residuals:
        if residual in content:
            return f"residual ({lang}): {residual!r}"
    if content.count("<table") != content.count("</table>"):
        return "table tag count unbalanced after wrapping"
    if content.count('<div class="table-wrap">') != content.count("</table>"):
        return "table-wrap div count mismatch"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync API wiki HTML per language")
    parser.add_argument("--lang", choices=["zh", "en"], required=True, help="target language corpus")
    parser.add_argument("--out", default=None, help="output dir (default: wiki-src/<lang>)")
    parser.add_argument("--src", default=AUTH_WIKI, help=f"source html dir (default: {AUTH_WIKI})")
    args = parser.parse_args()

    lang = args.lang
    wiki_src = args.out or os.path.join(REPO_ROOT, "wiki-src", lang)
    auth_wiki = args.src

    if not os.path.isdir(auth_wiki):
        print(f"ERROR: source not found: {auth_wiki}")
        print("Run first: python scripts/generate/generate_api_wiki.py --html (zh)")
        print("      or: python scripts/gen-wiki-en.py (en, from reference specs)")
        return 1

    os.makedirs(wiki_src, exist_ok=True)

    copied = 0
    skipped = 0
    written = set()

    for root, _dirs, files in os.walk(auth_wiki):
        # The generator nests everything under `api/`; `wiki-src/<lang>/` is already
        # the docs root, so that segment must be dropped (not doubled).
        rel = os.path.relpath(root, auth_wiki)
        parts = [] if rel == "." else rel.split(os.sep)
        if parts[:1] == ["api"]:
            parts = parts[1:]
        rel = os.path.join(*parts) if parts else "."
        dst_dir = wiki_src if rel == "." else os.path.join(wiki_src, rel)
        os.makedirs(dst_dir, exist_ok=True)

        for name in files:
            if not (name.endswith(".html") or name.endswith(".xml")):
                continue
            if dst_dir == wiki_src and name in SKIP_AT_ROOT:
                skipped += 1
                continue
            src = os.path.join(root, name)
            dst = os.path.join(dst_dir, name)
            with open(src, encoding="utf-8") as fh:
                content = normalize(fh.read(), lang)
            problem = check(content, src, lang)
            if problem:
                print(f"ERROR: {problem}: {src}")
                return 1
            with open(dst, "w", encoding="utf-8", newline="") as fh:
                fh.write(content)
            written.add(os.path.normcase(os.path.normpath(dst)))
            copied += 1

    removed = 0
    for root, _dirs, files in os.walk(wiki_src, topdown=False):
        for name in files:
            if not (name.endswith(".html") or name.endswith(".xml")):
                continue
            path = os.path.normcase(os.path.normpath(os.path.join(root, name)))
            if path not in written:
                os.remove(path)
                removed += 1
        if root != wiki_src and not os.listdir(root):
            os.rmdir(root)

    print(f"synced [{lang}] {copied} files (skipped {skipped} root artifacts), removed {removed} stale -> {wiki_src}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
