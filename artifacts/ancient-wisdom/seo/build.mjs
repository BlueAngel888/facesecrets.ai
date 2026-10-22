// Static SEO build. Runs after `vite build` and writes, into dist/public:
//   - a localized, crawlable home page per language (/, /ro/, /de/, ...)
//   - guides, blog articles and info pages rendered from seo/content/*.md
//   - sitemap.xml, robots.txt, llms.txt, llms-full.txt and 404.html
// Usage: node seo/build.mjs            (build)
//        node seo/build.mjs --rewrites (print the rewrite rules for artifact.toml)
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { BRAND, DEFAULT_LANGUAGE, HOME, LANGUAGES, PRICE_EUR, SITE_URL, homePath } from "./site.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const out = path.join(root, "dist", "public");
const contentDir = path.join(here, "content");
const today = new Date().toISOString().slice(0, 10);

const esc = value => String(value ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const abs = urlPath => `${SITE_URL}${urlPath}`;
const jsonld = data => `<script type="application/ld+json">${JSON.stringify(data).replace(/</g, "\\u003c")}</script>`;

// ---------------------------------------------------------------- markdown --
// A small Markdown subset is enough for the articles: headings, paragraphs,
// lists, tables, blockquotes, bold, italic and links.
function inline(text) {
  return esc(text)
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, label, href) => `<a href="${href}">${label}</a>`)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[\s(])\*([^*\s][^*]*)\*/g, "$1<em>$2</em>");
}

const slugify = text => text.toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

function markdown(source) {
  const lines = source.replace(/\r/g, "").split("\n");
  const html = [];
  const toc = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim()) { i++; continue; }
    const heading = line.match(/^(#{2,4})\s+(.*)$/);
    if (heading) {
      const level = heading[1].length, text = heading[2].trim(), id = slugify(text);
      if (level === 2) toc.push({ id, text });
      html.push(`<h${level} id="${id}">${inline(text)}</h${level}>`);
      i++; continue;
    }
    if (/^\|/.test(line)) {
      const rows = [];
      while (i < lines.length && /^\|/.test(lines[i])) rows.push(lines[i++]);
      const cells = row => row.replace(/^\||\|$/g, "").split("|").map(cell => cell.trim());
      const [head, , ...body] = rows;
      html.push(`<div class="table-wrap"><table><thead><tr>${cells(head).map(c => `<th>${inline(c)}</th>`).join("")}</tr></thead><tbody>${body.map(r => `<tr>${cells(r).map(c => `<td>${inline(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
      continue;
    }
    if (/^>\s?/.test(line)) {
      const quote = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) quote.push(lines[i++].replace(/^>\s?/, ""));
      html.push(`<blockquote><p>${inline(quote.join(" "))}</p></blockquote>`);
      continue;
    }
    const list = line.match(/^(-|\d+\.)\s+/);
    if (list) {
      const ordered = list[1] !== "-";
      const items = [];
      while (i < lines.length && /^(-|\d+\.)\s+/.test(lines[i])) items.push(lines[i++].replace(/^(-|\d+\.)\s+/, ""));
      html.push(`<${ordered ? "ol" : "ul"}>${items.map(item => `<li>${inline(item)}</li>`).join("")}</${ordered ? "ol" : "ul"}>`);
      continue;
    }
    const paragraph = [];
    while (i < lines.length && lines[i].trim() && !/^(#{2,4}\s|\||>|-\s|\d+\.\s)/.test(lines[i])) paragraph.push(lines[i++].trim());
    html.push(`<p>${inline(paragraph.join(" "))}</p>`);
  }
  return { html: html.join("\n"), toc };
}

function readPage(file) {
  const raw = fs.readFileSync(file, "utf8");
  const match = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) throw new Error(`${file}: missing front matter`);
  const meta = {};
  for (const line of match[1].split("\n")) {
    const pair = line.match(/^(\w+):\s*(.*)$/);
    if (pair) meta[pair[1]] = pair[2].trim();
  }
  for (const key of ["title", "description", "path", "kind"]) if (!meta[key]) throw new Error(`${file}: front matter needs ${key}`);
  if (meta.description.length > 165) console.warn(`[seo] ${meta.path}: description is ${meta.description.length} characters (aim for 120-160)`);
  return { ...meta, body: match[2].trim(), related: (meta.related || "").split(",").map(s => s.trim()).filter(Boolean) };
}

// ------------------------------------------------------------------ chrome --
const FONTS = `<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Instrument+Serif:ital@0;1&family=Space+Mono&display=swap">`;

function headTags({ title, description, urlPath, language = DEFAULT_LANGUAGE, alternates = null, type = "website", image = "/og-image.png", noindex = false, extra = "" }) {
  const tags = [
    `<title>${esc(title)}</title>`,
    `<meta name="description" content="${esc(description)}">`,
    `<meta name="robots" content="${noindex ? "noindex, follow" : "index, follow, max-image-preview:large, max-snippet:-1"}">`,
    noindex ? "" : `<link rel="canonical" href="${abs(urlPath)}">`,
    `<meta name="theme-color" content="#080b12">`,
    `<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">`,
    `<meta property="og:site_name" content="${BRAND}"><meta property="og:type" content="${type}"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(description)}"><meta property="og:url" content="${abs(urlPath)}"><meta property="og:image" content="${abs(image)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:locale" content="${LANGUAGES[language].locale}">`,
    `<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="${esc(title)}"><meta name="twitter:description" content="${esc(description)}"><meta name="twitter:image" content="${abs(image)}">`,
    `<link rel="alternate" type="text/plain" title="LLM summary" href="/llms.txt">`,
  ];
  if (alternates) {
    for (const code of Object.keys(LANGUAGES)) tags.push(`<link rel="alternate" hreflang="${code}" href="${abs(homePath(code))}">`);
    tags.push(`<link rel="alternate" hreflang="x-default" href="${abs("/")}">`);
  }
  return tags.filter(Boolean).join("\n    ") + (extra ? `\n    ${extra}` : "");
}

const organization = { "@type": "Organization", "@id": `${SITE_URL}/#organization`, name: BRAND, url: `${SITE_URL}/`, logo: { "@type": "ImageObject", url: abs("/logo.png"), width: 512, height: 512 } };
const website = { "@type": "WebSite", "@id": `${SITE_URL}/#website`, name: BRAND, url: `${SITE_URL}/`, publisher: { "@id": `${SITE_URL}/#organization` }, inLanguage: Object.keys(LANGUAGES) };

function siteHeader(copy = HOME.en, language = DEFAULT_LANGUAGE) {
  const home = homePath(language);
  return `<header class="site-header"><div class="wrap nav-row">
      <a class="logo" href="${home}"><span class="logo-mark">F</span> ${BRAND}</a>
      <nav aria-label="Main"><a href="/guides">${esc(copy.nav.guides)}</a><a href="/blog">${esc(copy.nav.blog)}</a><a href="/tools/face-symmetry-test">${esc(copy.nav.tool)}</a><a href="/faq">${esc(copy.nav.faq)}</a></nav>
      <a class="nav-cta" href="${home}#begin">${esc(copy.cta)}</a>
    </div></header>`;
}

function siteFooter(copy = HOME.en, language = DEFAULT_LANGUAGE) {
  const languages = Object.entries(LANGUAGES).map(([code, { name }]) => `<a href="${homePath(code)}" hreflang="${code}" lang="${code}">${esc(name)}</a>`).join("");
  return `<footer class="site-footer"><div class="wrap footer-grid">
      <div><a class="logo" href="${homePath(language)}"><span class="logo-mark">F</span> ${BRAND}</a><p>${esc(copy.footer)}</p></div>
      <nav aria-label="Guides"><strong>${esc(copy.nav.guides)}</strong><a href="/guides/face-reading">Face reading</a><a href="/guides/facial-symmetry">Facial symmetry</a><a href="/guides/microexpressions">Microexpressions</a><a href="/blog">${esc(copy.nav.blog)}</a></nav>
      <nav aria-label="FaceSecrets"><strong>${BRAND}</strong><a href="/how-it-works">${esc(copy.nav.how)}</a><a href="/tools/face-symmetry-test">${esc(copy.nav.tool)}</a><a href="/faq">${esc(copy.nav.faq)}</a><a href="/privacy">${esc(copy.nav.privacy)}</a></nav>
      <nav aria-label="Languages" class="footer-languages"><strong>Languages</strong>${languages}</nav>
    </div></footer>`;
}

function document({ language = DEFAULT_LANGUAGE, head, body, scripts = "" }) {
  return `<!doctype html>
<html lang="${language}" dir="${LANGUAGES[language].dir}">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    ${head}
    ${FONTS}
    <link rel="stylesheet" href="/site.css">
  </head>
  <body class="static-page">
    ${body}
    ${scripts}
  </body>
</html>
`;
}

// ------------------------------------------------------------- home pages --
function homeStatic(language) {
  const copy = HOME[language];
  const home = homePath(language);
  const faqSchema = { "@context": "https://schema.org", "@graph": [organization, website,
    { "@type": "WebApplication", "@id": `${SITE_URL}/#app`, name: BRAND, url: abs(home), applicationCategory: "LifestyleApplication", operatingSystem: "Web browser", inLanguage: language, description: copy.description, publisher: { "@id": `${SITE_URL}/#organization` },
      offers: { "@type": "Offer", price: PRICE_EUR, priceCurrency: "EUR", availability: "https://schema.org/InStock", url: abs(`${home}#begin`) } },
    { "@type": "FAQPage", "@id": `${abs(home)}#faq`, inLanguage: language, mainEntity: copy.faq.map(([q, a]) => ({ "@type": "Question", name: q, acceptedAnswer: { "@type": "Answer", text: a } })) },
  ] };
  const inRoot = `<div class="prerender"><div class="wrap"><p class="kicker">${BRAND}</p><h1>${esc(copy.h1)}</h1><p class="lead">${esc(copy.intro)}</p><p><a class="button" href="${home}#begin">${esc(copy.cta)} · €${PRICE_EUR}</a></p></div></div>`;
  const after = `<div id="seo-home" class="seo-home">
      <section class="wrap seo-block"><h2>${esc(copy.stepsTitle)}</h2><ol class="steps">${copy.steps.map(([t, d]) => `<li><h3>${esc(t)}</h3><p>${esc(d)}</p></li>`).join("")}</ol></section>
      <section class="wrap seo-block"><h2>${esc(copy.coversTitle)}</h2><ul class="checks">${copy.covers.map(c => `<li>${esc(c)}</li>`).join("")}</ul><p class="honest">${esc(copy.honest)}</p></section>
      <section class="wrap seo-block" id="faq"><h2>${esc(copy.faqTitle)}</h2>${copy.faq.map(([q, a]) => `<details><summary>${esc(q)}</summary><p>${esc(a)}</p></details>`).join("")}</section>
      <section class="wrap seo-block"><h2>${esc(copy.learnTitle)}</h2><div class="cards">
        <a class="card-link" href="/guides/face-reading"><span>Guide</span><strong>Face reading: the complete guide to physiognomy</strong></a>
        <a class="card-link" href="/guides/facial-symmetry"><span>Guide</span><strong>Facial symmetry: how it is measured and what it means</strong></a>
        <a class="card-link" href="/guides/microexpressions"><span>Guide</span><strong>Microexpressions: the 7 universal emotions</strong></a>
        <a class="card-link" href="/tools/face-symmetry-test"><span>Free tool</span><strong>Face symmetry test, right in your browser</strong></a>
      </div></section>
      ${siteFooter(copy, language)}
    </div>`;
  return { copy, schema: jsonld(faqSchema), inRoot, after };
}

function buildHomes(template, pages) {
  for (const language of Object.keys(LANGUAGES)) {
    const { copy, schema, inRoot, after } = homeStatic(language);
    const urlPath = homePath(language);
    let html = template
      .replace(/<html[^>]*>/, `<html lang="${language}" dir="${LANGUAGES[language].dir}">`)
      .replace(/<title>[\s\S]*?<\/title>/, "")
      .replace("<!--seo:head-->", `${headTags({ title: copy.title, description: copy.description, urlPath, language, alternates: true })}\n    ${schema}\n    <link rel="stylesheet" href="/site.css">`)
      .replace("<!--seo:root-->", inRoot)
      .replace("<!--seo:after-->", after);
    if (html.includes("<!--seo:")) throw new Error("index.html is missing the seo markers");
    const file = language === DEFAULT_LANGUAGE ? path.join(out, "index.html") : path.join(out, language, "index.html");
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, html);
    pages.push({ path: urlPath, file, priority: language === DEFAULT_LANGUAGE ? "1.0" : "0.9", alternates: true, title: copy.title, description: copy.description, kind: "home", language });
  }
}

// ---------------------------------------------------------- content pages --
const KIND_LABEL = { guide: "Guides", blog: "Blog", page: null, tool: "Tools" };
const KIND_INDEX = { guide: "/guides", blog: "/blog", tool: null };

function articlePage(page, all) {
  const { html, toc } = markdown(page.body);
  const crumbs = [{ name: BRAND, path: "/" }];
  if (KIND_INDEX[page.kind]) crumbs.push({ name: KIND_LABEL[page.kind], path: KIND_INDEX[page.kind] });
  crumbs.push({ name: page.h1 || page.title, path: page.path });
  const graph = [organization, website,
    { "@type": "BreadcrumbList", itemListElement: crumbs.map((c, i) => ({ "@type": "ListItem", position: i + 1, name: c.name, item: abs(c.path) })) }];
  if (page.kind === "guide" || page.kind === "blog") {
    graph.push({ "@type": page.kind === "blog" ? "BlogPosting" : "Article", headline: page.h1 || page.title, description: page.description, url: abs(page.path), mainEntityOfPage: abs(page.path), image: abs("/og-image.png"), inLanguage: "en", datePublished: page.date || today, dateModified: page.updated || page.date || today, author: { "@id": `${SITE_URL}/#organization` }, publisher: { "@id": `${SITE_URL}/#organization` }, about: (page.about || "").split(",").map(s => s.trim()).filter(Boolean).map(name => ({ "@type": "Thing", name })) });
  }
  if (page.schema === "faq") {
    const questions = [...page.body.matchAll(/^###\s+(.+)\n+([\s\S]*?)(?=\n###\s|\n##\s|$)/gm)].map(([, q, a]) => ({ "@type": "Question", name: q.trim(), acceptedAnswer: { "@type": "Answer", text: a.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").replace(/\*\*/g, "").replace(/\s+/g, " ").trim() } }));
    graph.push({ "@type": "FAQPage", mainEntity: questions });
  }
  if (page.kind === "tool") graph.push({ "@type": "WebApplication", name: page.h1 || page.title, url: abs(page.path), applicationCategory: "LifestyleApplication", operatingSystem: "Web browser", offers: { "@type": "Offer", price: "0", priceCurrency: "EUR" }, publisher: { "@id": `${SITE_URL}/#organization` } });

  const related = page.related.map(p => all.find(other => other.path === p)).filter(Boolean);
  const meta = page.kind === "guide" || page.kind === "blog" ? `<p class="meta">${KIND_LABEL[page.kind]} · Updated <time datetime="${page.updated || page.date || today}">${page.updated || page.date || today}</time></p>` : "";
  const tocHtml = toc.length >= 4 ? `<nav class="toc" aria-label="Contents"><strong>Contents</strong><ol>${toc.map(t => `<li><a href="#${t.id}">${esc(t.text)}</a></li>`).join("")}</ol></nav>` : "";
  const tool = page.kind === "tool" ? fs.readFileSync(path.join(here, "symmetry-tool.html"), "utf8") : "";
  const body = `${siteHeader()}
    <main class="wrap article">
      <nav class="crumbs" aria-label="Breadcrumb">${crumbs.map((c, i) => i === crumbs.length - 1 ? `<span>${esc(c.name)}</span>` : `<a href="${c.path}">${esc(c.name)}</a>`).join(" / ")}</nav>
      <h1>${esc(page.h1 || page.title)}</h1>
      ${meta}
      ${page.lead ? `<p class="lead">${inline(page.lead)}</p>` : ""}
      ${tool}
      ${tocHtml}
      <div class="prose">${html}</div>
      <aside class="cta-box"><h2>See what your own face shows</h2><p>FaceSecrets reads one portrait across 12 facial zones, symmetry and expression, then reflects on them through five face-reading traditions. Private PDF report in 9 languages; the photo is deleted after analysis.</p><a class="button" href="/#begin">Start your face reading · €${PRICE_EUR}</a></aside>
      ${related.length ? `<section class="related"><h2>Keep reading</h2><div class="cards">${related.map(r => `<a class="card-link" href="${r.path}"><span>${KIND_LABEL[r.kind] || BRAND}</span><strong>${esc(r.h1 || r.title)}</strong></a>`).join("")}</div></section>` : ""}
    </main>
    ${siteFooter()}`;
  return document({ head: headTags({ title: page.title, description: page.description, urlPath: page.path, type: page.kind === "guide" || page.kind === "blog" ? "article" : "website" }) + `\n    ${jsonld({ "@context": "https://schema.org", "@graph": graph })}`, body, scripts: page.kind === "tool" ? `<script src="/symmetry-tool.js" defer></script>` : "" });
}

function indexPage(kind, entries) {
  const title = kind === "guide" ? "Face Reading Guides: Physiognomy, Symmetry, Microexpressions | FaceSecrets" : "FaceSecrets Blog: Face Reading, Facial Features and Expressions";
  const h1 = kind === "guide" ? "Face reading guides" : "The FaceSecrets blog";
  const description = kind === "guide" ? "In-depth guides to face reading, facial symmetry and microexpressions: what each tradition claims, what science says, and how to read a face responsibly." : "Articles on face reading, facial features, face shapes, smiles and microexpressions, written with a clear line between tradition and science.";
  const urlPath = KIND_INDEX[kind];
  const sorted = [...entries].sort((a, b) => (b.updated || b.date || "").localeCompare(a.updated || a.date || ""));
  const graph = [organization, website, { "@type": "CollectionPage", name: h1, url: abs(urlPath), description, hasPart: sorted.map(e => ({ "@type": kind === "blog" ? "BlogPosting" : "Article", headline: e.h1 || e.title, url: abs(e.path) })) },
    { "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: BRAND, item: abs("/") }, { "@type": "ListItem", position: 2, name: KIND_LABEL[kind], item: abs(urlPath) }] }];
  const body = `${siteHeader()}
    <main class="wrap article">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="/">${BRAND}</a> / <span>${KIND_LABEL[kind]}</span></nav>
      <h1>${h1}</h1><p class="lead">${esc(description)}</p>
      <div class="list">${sorted.map(e => `<article class="list-item"><h2><a href="${e.path}">${esc(e.h1 || e.title)}</a></h2><p>${esc(e.description)}</p></article>`).join("")}</div>
    </main>
    ${siteFooter()}`;
  return { urlPath, title, description, html: document({ head: headTags({ title, description, urlPath }) + `\n    ${jsonld({ "@context": "https://schema.org", "@graph": graph })}`, body }) };
}

function writePage(urlPath, html) {
  const file = path.join(out, urlPath.replace(/^\//, ""), "index.html");
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, html);
  return file;
}

function notFound() {
  const body = `${siteHeader()}<main class="wrap article"><h1>Page not found</h1><p class="lead">This page does not exist or has moved.</p><p><a class="button" href="/">Go to the home page</a></p><p>Or browse the <a href="/guides">face reading guides</a> and the <a href="/blog">blog</a>.</p></main>${siteFooter()}`;
  return document({ head: headTags({ title: "Page not found | FaceSecrets", description: "This page does not exist.", urlPath: "/404", noindex: true }), body });
}

// --------------------------------------------------- sitemap, robots, llms --
function sitemap(pages) {
  const urls = pages.filter(p => !p.noindex).map(p => {
    const alternates = p.alternates ? Object.keys(LANGUAGES).map(code => `\n    <xhtml:link rel="alternate" hreflang="${code}" href="${abs(homePath(code))}"/>`).join("") + `\n    <xhtml:link rel="alternate" hreflang="x-default" href="${abs("/")}"/>` : "";
    return `  <url>\n    <loc>${abs(p.path)}</loc>\n    <lastmod>${p.updated || p.date || today}</lastmod>\n    <priority>${p.priority}</priority>${alternates}\n  </url>`;
  });
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n${urls.join("\n")}\n</urlset>\n`;
}

function robots() {
  // Search engines and AI assistants are explicitly welcome: being quoted by
  // ChatGPT, Claude, Perplexity or Gemini is part of how people find the site.
  const aiAgents = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "Meta-ExternalAgent", "Amazonbot", "DuckAssistBot", "MistralAI-User", "CCBot"];
  // /api/page must stay crawlable: Google renders the app with it.
  return `# ${BRAND} robots.txt\nUser-agent: *\nAllow: /\nAllow: /api/page\nDisallow: /api/\nDisallow: /success\nDisallow: /cancel\n\n${aiAgents.map(agent => `User-agent: ${agent}`).join("\n")}\nAllow: /\nAllow: /api/page\nDisallow: /api/\n\nSitemap: ${abs("/sitemap.xml")}\n`;
}

function llms(pages, full) {
  const en = HOME.en;
  const section = kind => pages.filter(p => p.kind === kind).map(p => `- [${p.h1 || p.title}](${abs(p.path)}): ${p.description}`).join("\n");
  const head = `# ${BRAND}

> ${BRAND} (${SITE_URL}) is an online AI face reading and facial analysis service. A user uploads one portrait photo and receives a private PDF report that describes visible features in 12 facial zones, facial symmetry and expression, and reflects on them through five face-reading traditions (Chinese Mian Xiang, Greek physiognomy, Vedic Samudrika Shastra, Islamic Firasa, modern FACS/Ekman expression science). A full report costs €${PRICE_EUR}. Reports are available in English, Romanian, German, Italian, French, Spanish, Chinese, Arabic and Japanese. The photo is deleted as soon as the analysis finishes.

Key facts:
- What it is: AI face reading / face analysis report from a single photo, for entertainment and self-reflection.
- What it is not: not identity recognition, not a medical, psychological or predictive assessment. Face-reading traditions are presented as cultural frameworks, not science.
- Privacy: no account needed; photo processed only for the report and deleted after analysis; report deleted from the server once downloaded; payments by Stripe.
- Free tool: a face symmetry test that runs entirely in the browser (${abs("/tools/face-symmetry-test")}).
- Start a reading: ${abs("/#begin")}

## Product
- [Home](${abs("/")}): ${en.description}
${section("page")}
${section("tool")}

## Guides
${section("guide")}

## Blog
${section("blog")}

## Languages
${Object.entries(LANGUAGES).map(([code, { name }]) => `- [${name}](${abs(homePath(code))})`).join("\n")}
`;
  if (!full) return head;
  const bodies = pages.filter(p => p.body).map(p => `\n\n---\n\n# ${p.h1 || p.title}\n\nURL: ${abs(p.path)}\n\n${p.lead ? `${p.lead}\n\n` : ""}${p.body}`).join("");
  const faq = `\n\n---\n\n# FAQ (home page)\n\n${en.faq.map(([q, a]) => `## ${q}\n\n${a}`).join("\n\n")}`;
  return head + faq + bodies + "\n";
}

// -------------------------------------------------------------- rewrites --
function rewriteRules(paths) {
  const rules = [];
  for (const p of paths) {
    const target = p === "/" ? "/index.html" : `${p.replace(/\/$/, "")}/index.html`;
    if (p === "/") continue;
    const bare = p.replace(/\/$/, "");
    rules.push([bare, target], [`${bare}/`, target]);
  }
  return rules;
}

// ------------------------------------------------------------------ main --
function contentPages() {
  return fs.readdirSync(contentDir).filter(f => f.endsWith(".md")).sort().map(f => readPage(path.join(contentDir, f)));
}

function allPaths(content) {
  return [...Object.keys(LANGUAGES).map(homePath), ...content.map(p => p.path), KIND_INDEX.guide, KIND_INDEX.blog];
}

if (process.argv.includes("--rewrites")) {
  for (const [from, to] of rewriteRules(allPaths(contentPages()))) console.log(`[[services.production.rewrites]]\nfrom = "${from}"\nto = "${to}"\n`);
  process.exit(0);
}

const templateFile = path.join(out, "index.html");
if (!fs.existsSync(templateFile)) throw new Error("Run vite build first: dist/public/index.html is missing");
const template = fs.readFileSync(templateFile, "utf8");
const pages = [];
buildHomes(template, pages);

const content = contentPages();
for (const page of content) {
  const file = writePage(page.path, articlePage(page, content));
  pages.push({ ...page, file, priority: page.kind === "guide" ? "0.8" : page.kind === "tool" ? "0.8" : page.kind === "blog" ? "0.7" : "0.5" });
}
for (const kind of ["guide", "blog"]) {
  const index = indexPage(kind, content.filter(p => p.kind === kind));
  pages.push({ path: index.urlPath, file: writePage(index.urlPath, index.html), priority: "0.7", title: index.title, description: index.description, kind: "index" });
}

fs.writeFileSync(path.join(out, "404.html"), notFound());
fs.copyFileSync(path.join(here, "site.css"), path.join(out, "site.css"));
fs.copyFileSync(path.join(here, "symmetry-tool.js"), path.join(out, "symmetry-tool.js"));
fs.writeFileSync(path.join(out, "sitemap.xml"), sitemap(pages));
fs.writeFileSync(path.join(out, "robots.txt"), robots());
fs.writeFileSync(path.join(out, "llms.txt"), llms(pages.filter(p => p.kind !== "home"), false));
fs.writeFileSync(path.join(out, "llms-full.txt"), llms(pages.filter(p => p.kind !== "home"), true));
fs.writeFileSync(path.join(out, "seo-pages.json"), JSON.stringify(pages.map(p => abs(p.path)), null, 2));

// Every clean URL needs an exact rewrite in the deployment config, or the
// static host falls back to the app shell. Warn loudly when one is missing.
const toml = fs.readFileSync(path.join(root, ".replit-artifact", "artifact.toml"), "utf8");
const missing = rewriteRules(pages.map(p => p.path)).filter(([from]) => !toml.includes(`from = "${from}"`));
if (missing.length) console.warn(`[seo] artifact.toml is missing ${missing.length} rewrites; run: node seo/build.mjs --rewrites`);
console.log(`[seo] wrote ${pages.length} pages, sitemap.xml, robots.txt, llms.txt, llms-full.txt, 404.html`);
