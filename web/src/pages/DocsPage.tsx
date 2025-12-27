import { ChevronRight, FileText } from "lucide-react";
import { isValidElement, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Link, useParams } from "react-router-dom";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneLight, oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import remarkGfm from "remark-gfm";
import Header from "../components/Header";
import { Card } from "../components/ui/card";
import { useTheme } from "../lib/ThemeProvider";

const DOCS = [
  { id: "README", title: "Overview", path: "/docs/schemas/README.md" },
  { id: "locate", title: "Locate", path: "/docs/schemas/locate.md" },
  { id: "symbol", title: "Symbol", path: "/docs/schemas/symbol.md" },
  {
    id: "symbol_outline",
    title: "Symbol Outline",
    path: "/docs/schemas/symbol_outline.md",
  },
  {
    id: "definition",
    title: "Definition",
    path: "/docs/schemas/definition.md",
  },
  { id: "reference", title: "Reference", path: "/docs/schemas/reference.md" },
  {
    id: "implementation",
    title: "Implementation",
    path: "/docs/schemas/implementation.md",
  },
  {
    id: "call_hierarchy",
    title: "Call Hierarchy",
    path: "/docs/schemas/call_hierarchy.md",
  },
  {
    id: "type_hierarchy",
    title: "Type Hierarchy",
    path: "/docs/schemas/type_hierarchy.md",
  },
  { id: "workspace", title: "Workspace", path: "/docs/schemas/workspace.md" },
  {
    id: "completion",
    title: "Completion",
    path: "/docs/schemas/completion.md",
  },
  {
    id: "diagnostics",
    title: "Diagnostics",
    path: "/docs/schemas/diagnostics.md",
  },
  { id: "rename", title: "Rename", path: "/docs/schemas/rename.md" },
  {
    id: "inlay_hints",
    title: "Inlay Hints",
    path: "/docs/schemas/inlay_hints.md",
  },
];

export default function DocsPage() {
  const { docId } = useParams();
  const [content, setContent] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const { resolvedTheme } = useTheme();

  const cleanDocId = docId?.replace(/\.md$/, "");
  const currentDoc = DOCS.find((d) => d.id === cleanDocId) ?? DOCS[0];

  useEffect(() => {
    if (!currentDoc) return;

    setLoading(true);
    const baseUrl = (import.meta.env.BASE_URL || "/").replace(/\/$/, "");
    fetch(`${baseUrl}${currentDoc.path}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch");
        return res.text();
      })
      .then((text) => {
        setContent(text);
        setLoading(false);
      })
      .catch(() => {
        setContent(
          "# Documentation Not Found\n\nThe requested documentation could not be loaded."
        );
        setLoading(false);
      });
  }, [currentDoc?.path]);

  if (!currentDoc) return null;

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <div className="container max-w-7xl mx-auto px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <aside className="lg:col-span-1">
            <Card className="p-4 sticky top-24">
              <h2 className="font-mono text-sm font-medium mb-4 text-foreground">
                Documentation
              </h2>
              <nav className="space-y-1">
                {DOCS.map((doc) => (
                  <Link
                    key={doc.id}
                    to={`/docs/${doc.id}`}
                    className={`
                      flex items-center gap-2 px-3 py-2 rounded-sm text-sm transition-colors
                      ${
                        currentDoc.id === doc.id
                          ? "bg-primary/10 text-primary font-medium"
                          : "text-muted-foreground hover:text-foreground hover:bg-muted"
                      }
                    `}
                  >
                    <FileText className="h-3.5 w-3.5" />
                    <span className="font-mono text-xs">{doc.title}</span>
                    {currentDoc.id === doc.id && (
                      <ChevronRight className="h-3.5 w-3.5 ml-auto" />
                    )}
                  </Link>
                ))}
              </nav>
            </Card>
          </aside>

          {/* Main Content */}
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
                        />
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
                            return (
                              <div className="my-6">
                                <SyntaxHighlighter
                                  style={resolvedTheme === 'dark' ? oneDark : oneLight}
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
                          const to = href.startsWith("/")
                            ? href
                            : `/docs/${href.replace(/\.md$/, "")}`;
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
