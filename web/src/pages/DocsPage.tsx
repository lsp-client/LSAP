import { ChevronRight, FileText } from "lucide-react";
import { isValidElement, useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Link, useParams } from "react-router-dom";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  oneDark,
  oneLight,
} from "react-syntax-highlighter/dist/esm/styles/prism";
import remarkGfm from "remark-gfm";
import Header from "../components/Header";
import { Card } from "../components/ui/card";
import { useTheme } from "../lib/ThemeProvider";

type DocEntry = {
  route: string;
  relativePath: string;
  title: string;
  draft?: boolean;
};

type Frontmatter = Record<string, string>;

function parseFrontmatter(markdown: string): {
  frontmatter: Frontmatter;
  body: string;
} {
  if (!markdown.startsWith("---\n")) return { frontmatter: {}, body: markdown };
  const endIndex = markdown.indexOf("\n---\n", 4);
  if (endIndex === -1) return { frontmatter: {}, body: markdown };

  const raw = markdown.slice(4, endIndex);
  const body = markdown.slice(endIndex + "\n---\n".length);
  const frontmatter: Frontmatter = {};

  for (const line of raw.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    const match = /^([A-Za-z0-9_-]+)\s*:\s*(.*)$/.exec(trimmed);
    if (!match) continue;
    const key = match[1] ?? "";
    if (!key) continue;
    const value = (match[2] ?? "").replace(/^["']|["']$/g, "").trim();
    frontmatter[key] = value;
  }

  return { frontmatter, body };
}

function extractTitleFromMarkdown(markdown: string): string | null {
  const lines = markdown.split("\n");
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    if (trimmed.startsWith("# ")) return trimmed.replace(/^#\s+/, "").trim();
    if (trimmed.startsWith("## ")) return trimmed.replace(/^##\s+/, "").trim();
  }
  return null;
}

function posixJoin(baseDir: string, hrefPath: string) {
  const parts = [...baseDir.split("/"), ...hrefPath.split("/")].filter(Boolean);
  const out: string[] = [];
  for (const part of parts) {
    if (part === ".") continue;
    if (part === "..") out.pop();
    else out.push(part);
  }
  return out.join("/");
}

const RAW_DOCS = import.meta.glob("../../../docs/**/*.md", {
  query: "?raw",
  import: "default",
  eager: true,
}) as Record<string, string>;

function makeDocIndex(): DocEntry[] {
  const entries: DocEntry[] = [];

  for (const [sourcePath, raw] of Object.entries(RAW_DOCS)) {
    const marker = "/docs/";
    const idx = sourcePath.lastIndexOf(marker);
    if (idx === -1) continue;
    const relativePath = sourcePath.slice(idx + marker.length);
    const { frontmatter, body } = parseFrontmatter(raw);
    const draft = relativePath.startsWith("schemas/draft/");

    const frontmatterTitle = frontmatter.title?.trim();
    const headingTitle = extractTitleFromMarkdown(body)?.trim();
    const fallbackTitle = relativePath
      .replace(/\.md$/, "")
      .split("/")
      .pop()
      ?.replace(/_/g, " ");
    const title =
      frontmatterTitle || headingTitle || fallbackTitle || "Documentation";

    const route = `/docs/${relativePath.replace(/\.md$/, "")}`;
    entries.push({ route, relativePath, title, draft });
  }

  entries.sort((a, b) => {
    const aIsReadme = a.relativePath.toLowerCase() === "schemas/readme.md";
    const bIsReadme = b.relativePath.toLowerCase() === "schemas/readme.md";
    if (aIsReadme !== bIsReadme) return aIsReadme ? -1 : 1;
    
    // Group by category: root docs vs schema docs
    const aIsSchema = a.relativePath.startsWith("schemas/");
    const bIsSchema = b.relativePath.startsWith("schemas/");
    if (aIsSchema !== bIsSchema) return aIsSchema ? 1 : -1;
    
    if (a.draft !== b.draft) return a.draft ? 1 : -1;
    return a.relativePath.localeCompare(b.relativePath);
  });

  return entries;
}

const DOC_INDEX = makeDocIndex();
const DOC_BY_ROUTE = new Map(DOC_INDEX.map((d) => [d.route, d]));
const DEFAULT_ROUTE = "/docs/schemas/README";

function canonicalRouteFromSplat(splat?: string) {
  const cleaned = (splat || "").replace(/^\/+/, "").replace(/\/+$/, "");
  if (!cleaned) return DEFAULT_ROUTE;
  if (cleaned === "schemas") return DEFAULT_ROUTE;
  if (cleaned === "schemas/README") return DEFAULT_ROUTE;

  const normalized = cleaned.replace(/\.md$/, "");
  return `/docs/${normalized}`;
}

function hrefToDocsRoute(href: string, currentDocRelativePath: string) {
  const [pathPart, hashPart] = href.split("#", 2);
  const hash = hashPart ? `#${hashPart}` : "";
  const normalized = (pathPart || "").replace(/^\.\//, "");

  const filenameMatch = /([^/]+)\.md$/.exec(normalized);
  if (!filenameMatch) return href;

  if (normalized.startsWith("/docs/")) {
    const stripped = normalized.replace(/^\/docs\//, "").replace(/\.md$/, "");
    return `/docs/${stripped}${hash}`;
  }

  const underSchemas = normalized.startsWith("schemas/");
  const schemaRelative = underSchemas
    ? normalized.replace(/^schemas\//, "")
    : normalized;
  const baseDir = currentDocRelativePath.split("/").slice(0, -1).join("/");
  const resolvedRelative = schemaRelative.startsWith("/")
    ? schemaRelative.replace(/^\//, "")
    : posixJoin(baseDir, schemaRelative);

  const withoutExt = resolvedRelative.replace(/\.md$/, "");
  return `/docs/${withoutExt}${hash}`;
}

export default function DocsPage() {
  const params = useParams();
  const splat = params["*"];
  const [content, setContent] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const { resolvedTheme } = useTheme();

  const docs = useMemo(() => DOC_INDEX, []);
  const canonicalRoute = useMemo(() => canonicalRouteFromSplat(splat), [splat]);
  const currentDoc =
    DOC_BY_ROUTE.get(canonicalRoute) ?? DOC_BY_ROUTE.get(DEFAULT_ROUTE);

  const generalDocs = useMemo(
    () => docs.filter(doc => !doc.relativePath.startsWith("schemas/")),
    [docs]
  );
  const schemaDocs = useMemo(
    () => docs.filter(doc => doc.relativePath.startsWith("schemas/")),
    [docs]
  );

  useEffect(() => {
    const titleSuffix = currentDoc?.draft ? " (draft)" : "";
    document.title = `${
      currentDoc?.title ?? "Documentation"
    }${titleSuffix} | LSAP`;
  }, [currentDoc?.route, currentDoc?.title, currentDoc?.draft]);

  useEffect(() => {
    if (!currentDoc) return;
    setLoading(true);
    const sourcePath = Object.keys(RAW_DOCS).find((p) =>
      p.endsWith(`/docs/${currentDoc.relativePath}`)
    );
    const raw = sourcePath ? RAW_DOCS[sourcePath] ?? "" : "";
    const { body } = parseFrontmatter(raw);
    if (!body) {
      setContent(
        "# Documentation Not Found\n\nThe requested documentation could not be loaded."
      );
      setLoading(false);
      return;
    }
    setContent(body);
    setLoading(false);
  }, [currentDoc?.route, currentDoc?.relativePath]);

  if (!currentDoc) return null;

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <div className="container max-w-7xl mx-auto px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <aside className="lg:col-span-1">
            <Card className="p-4 sticky top-24">
              <h2 className="font-mono text-sm font-medium mb-4 text-foreground">
                Documentation
              </h2>
              <nav className="space-y-1">
                {/* Root level docs */}
                {generalDocs.length > 0 && (
                  <>
                    <div className="px-3 py-2 font-mono text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      General
                    </div>
                    {generalDocs.map((doc) => (
                      <Link
                        key={doc.route}
                        to={doc.route}
                        className={`
                          flex items-center gap-2 px-3 py-2 rounded-sm text-sm transition-colors
                          ${
                            currentDoc.route === doc.route
                              ? "bg-primary/10 text-primary font-medium"
                              : "text-muted-foreground hover:text-foreground hover:bg-muted"
                          }
                        `}
                      >
                        <FileText className="h-3.5 w-3.5" />
                        <span className="font-mono text-xs">{doc.title}</span>
                        {currentDoc.route === doc.route && (
                          <ChevronRight className="h-3.5 w-3.5 ml-auto" />
                        )}
                      </Link>
                    ))}
                  </>
                )}
                
                {/* Schema docs */}
                {schemaDocs.length > 0 && (
                  <>
                    <div className="px-3 py-2 font-mono text-xs font-medium text-muted-foreground uppercase tracking-wider mt-4">
                      Schemas
                    </div>
                    {schemaDocs.map((doc) => (
                      <Link
                        key={doc.route}
                        to={doc.route}
                        className={`
                          flex items-center gap-2 px-3 py-2 rounded-sm text-sm transition-colors
                          ${
                            currentDoc.route === doc.route
                              ? "bg-primary/10 text-primary font-medium"
                              : "text-muted-foreground hover:text-foreground hover:bg-muted"
                          }
                        `}
                      >
                        <FileText className="h-3.5 w-3.5" />
                        <span className="font-mono text-xs">{doc.title}</span>
                        {doc.draft && (
                          <span
                            title="Draft: content may change"
                            aria-label="Draft: content may change"
                            className="ml-1 cursor-help rounded-sm border border-border bg-muted px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground"
                          >
                            draft
                          </span>
                        )}
                        {currentDoc.route === doc.route && (
                          <ChevronRight className="h-3.5 w-3.5 ml-auto" />
                        )}
                      </Link>
                    ))}
                  </>
                )}
              </nav>
            </Card>
          </aside>

          <main className="lg:col-span-3">
            <Card className="p-8 lg:p-12">
              {loading ? (
                <div className="flex items-center justify-center py-24">
                  <div className="animate-pulse text-muted-foreground font-mono text-sm">
                    Loading documentation...
                  </div>
                </div>
              ) : (
                <article className="prose prose-slate max-w-none">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      h1: ({ node, ...props }) => (
                        <h1
                          className="font-serif text-4xl font-light text-foreground mb-6 pb-4 border-b border-border"
                          {...props}
                        >
                          <span className="inline-flex items-baseline gap-3">
                            <span>{props.children}</span>
                            {currentDoc.draft && (
                              <span
                                title="Draft: content may change"
                                aria-label="Draft: content may change"
                                className="cursor-help rounded-sm border border-border bg-muted px-2 py-1 font-mono text-xs uppercase tracking-wider text-muted-foreground"
                              >
                                draft
                              </span>
                            )}
                          </span>
                        </h1>
                      ),
                      h2: ({ node, ...props }) => (
                        <h2
                          className="font-serif text-2xl font-light text-foreground mt-12 mb-4"
                          {...props}
                        />
                      ),
                      h3: ({ node, ...props }) => (
                        <h3
                          className="font-mono text-lg font-medium text-foreground mt-8 mb-3"
                          {...props}
                        />
                      ),
                      p: ({ node, ...props }) => (
                        <p
                          className="font-serif text-base text-muted-foreground leading-relaxed mb-4"
                          {...props}
                        />
                      ),
                      code: ({ className, ...props }: any) => (
                        <code
                          className={`font-mono text-sm bg-muted px-1.5 py-0.5 rounded text-foreground ${
                            className || ""
                          }`}
                          {...props}
                        />
                      ),
                      pre: ({ children, ...props }: any) => {
                        const child = Array.isArray(children)
                          ? children[0]
                          : children;

                        if (isValidElement(child)) {
                          const rawClassName =
                            (child.props as any)?.className || "";
                          const match = /language-(\w+)/.exec(rawClassName);
                          const codeText = String(
                            (child.props as any)?.children ?? ""
                          ).replace(/\n$/, "");

                          if (match) {
                            // Special handling for markdown code blocks - render them as actual markdown
                            if (match[1] === 'markdown') {
                              return (
                                <div className="my-6 rounded-md border border-border bg-muted p-6">
                                  <ReactMarkdown
                                    remarkPlugins={[remarkGfm]}
                                    components={{
                                      h1: ({ node, ...props }) => (
                                        <h1 className="font-serif text-3xl font-light text-foreground mb-4" {...props} />
                                      ),
                                      h2: ({ node, ...props }) => (
                                        <h2 className="font-serif text-xl font-light text-foreground mt-6 mb-3" {...props} />
                                      ),
                                      h3: ({ node, ...props }) => (
                                        <h3 className="font-mono text-base font-medium text-foreground mt-4 mb-2" {...props} />
                                      ),
                                      p: ({ node, ...props }) => (
                                        <p className="font-serif text-sm text-muted-foreground leading-relaxed mb-3" {...props} />
                                      ),
                                      code: ({ className, ...props }: any) => (
                                        <code className={`font-mono text-xs bg-background px-1 py-0.5 rounded text-foreground ${className || ""}`} {...props} />
                                      ),
                                      table: ({ node, ...props }) => (
                                        <div className="overflow-x-auto my-4">
                                          <table className="w-full border-collapse" {...props} />
                                        </div>
                                      ),
                                      thead: ({ node, ...props }) => (
                                        <thead className="bg-background/50" {...props} />
                                      ),
                                      th: ({ node, ...props }) => (
                                        <th className="font-mono text-xs font-medium text-left p-2 border border-border" {...props} />
                                      ),
                                      td: ({ node, ...props }) => (
                                        <td className="font-mono text-xs text-muted-foreground p-2 border border-border" {...props} />
                                      ),
                                      blockquote: ({ node, ...props }) => (
                                        <blockquote className="border-l-4 border-primary/20 pl-3 italic text-muted-foreground my-4 text-sm" {...props} />
                                      ),
                                      hr: ({ node, ...props }) => (
                                        <hr className="border-border my-4" {...props} />
                                      ),
                                    }}
                                  >
                                    {codeText}
                                  </ReactMarkdown>
                                </div>
                              );
                            }
                            
                            return (
                              <div className="my-6">
                                <SyntaxHighlighter
                                  style={
                                    resolvedTheme === "dark"
                                      ? oneDark
                                      : oneLight
                                  }
                                  language={match[1]}
                                  PreTag="div"
                                  className="rounded-md border border-border"
                                  customStyle={{
                                    margin: 0,
                                    padding: "1.5rem",
                                    fontSize: "0.875rem",
                                    lineHeight: "1.5",
                                    backgroundColor: "hsl(var(--muted))",
                                  }}
                                  codeTagProps={{
                                    style: {
                                      background: "transparent",
                                      lineHeight: "inherit",
                                      fontSize: "inherit",
                                      fontFamily: "inherit",
                                    },
                                  }}
                                >
                                  {codeText}
                                </SyntaxHighlighter>
                              </div>
                            );
                          }

                          return (
                            <div className="my-6">
                              <pre
                                className="overflow-x-auto rounded-md border border-border bg-muted p-6 my-0"
                                {...props}
                              >
                                <code className="font-mono text-sm">
                                  {codeText}
                                </code>
                              </pre>
                            </div>
                          );
                        }

                        return (
                          <div className="my-6">
                            <pre
                              className="overflow-x-auto rounded-md border border-border bg-muted p-6 my-0"
                              {...props}
                            >
                              {children}
                            </pre>
                          </div>
                        );
                      },
                      ul: ({ node, ...props }) => (
                        <ul
                          className="font-serif text-muted-foreground space-y-2 my-4 ml-6"
                          {...props}
                        />
                      ),
                      ol: ({ node, ...props }) => (
                        <ol
                          className="font-serif text-muted-foreground space-y-2 my-4 ml-6"
                          {...props}
                        />
                      ),
                      li: ({ node, ...props }) => (
                        <li
                          className="font-serif text-base leading-relaxed"
                          {...props}
                        />
                      ),
                      a: ({ node, ...props }) => {
                        const href = props.href || "";
                        const isInternal =
                          !href.startsWith("http") &&
                          !href.startsWith("//") &&
                          !href.startsWith("#");
                        if (isInternal) {
                          const to = hrefToDocsRoute(
                            href,
                            currentDoc.relativePath
                          );
                          return (
                            <Link
                              to={to}
                              className="text-primary hover:underline font-medium"
                            >
                              {props.children}
                            </Link>
                          );
                        }
                        return (
                          <a
                            className="text-primary hover:underline font-medium"
                            target="_blank"
                            rel="noopener noreferrer"
                            {...props}
                          />
                        );
                      },
                      table: ({ node, ...props }) => (
                        <div className="overflow-x-auto my-6">
                          <table
                            className="w-full border-collapse"
                            {...props}
                          />
                        </div>
                      ),
                      thead: ({ node, ...props }) => (
                        <thead className="bg-muted" {...props} />
                      ),
                      th: ({ node, ...props }) => (
                        <th
                          className="font-mono text-xs font-medium text-left p-3 border border-border"
                          {...props}
                        />
                      ),
                      td: ({ node, ...props }) => (
                        <td
                          className="font-mono text-xs text-muted-foreground p-3 border border-border"
                          {...props}
                        />
                      ),
                      blockquote: ({ node, ...props }) => (
                        <blockquote
                          className="border-l-4 border-primary/20 pl-4 italic text-muted-foreground my-6"
                          {...props}
                        />
                      ),
                    }}
                  >
                    {content}
                  </ReactMarkdown>
                </article>
              )}
            </Card>
          </main>
        </div>
      </div>
    </div>
  );
}
