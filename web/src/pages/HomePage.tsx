import {
  Activity,
  ArrowDown,
  ArrowRight,
  Code2,
  Network,
  Search,
} from "lucide-react";
import { isValidElement, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Link } from "react-router-dom";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneLight, oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import Header from "../components/Header";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { useTheme } from "../lib/ThemeProvider";

interface Example {
  id: string;
  title: string;
  mobileTitle: string;
  icon: typeof Search;
  agentIntent: string;
  flowSteps: { label: string; value: string; highlight?: boolean }[];
  processing: string[];
  resultMarkdown: string;
}

const EXAMPLES: Example[] = [
  {
    id: "locate",
    title: "Locate Symbol",
    mobileTitle: "Locate",
    icon: Search,
    agentIntent: "Find the implementation of the `process_data` function",
    flowSteps: [
      { label: "Method", value: "locate" },
      { label: "File", value: "src/processor.py", highlight: true },
      { label: "Pattern", value: "def process_data", highlight: true },
    ],
    processing: [
      "Fuzzy search in file",
      "AST-based resolution",
      "Exact position located",
    ],
    resultMarkdown: `### Found: \`process_data\`

**Location:** \`src/processor.py:42:4\`

\`\`\`python
def process_data(items: List[Item]) -> DataFrame:
    """Process items into dataframe format."""
    return pd.DataFrame([item.to_dict() for item in items])
\`\`\`

✓ Ready for navigation or inspection`,
  },
  {
    id: "symbol",
    title: "Symbol Deep Inspection",
    mobileTitle: "Symbol",
    icon: Code2,
    agentIntent: "Understand what `authenticate_user` does and how to use it",
    flowSteps: [
      { label: "Method", value: "symbol_info" },
      {
        label: "Symbol Path",
        value: "AuthService.authenticate_user",
        highlight: true,
      },
    ],
    processing: [
      "Resolve symbol path",
      "Fetch signature + docs",
      "Extract implementation",
      "Aggregate into snapshot",
    ],
    resultMarkdown: `### \`AuthService.authenticate_user\`

**Signature:**
\`\`\`python
async def authenticate_user(
    username: str, 
    password: str
) -> User
\`\`\`

**Documentation:**
> Authenticates a user with credentials. Validates username/password against the database, returns User object if successful, raises AuthenticationError otherwise.

**Implementation:** 12 lines  
**Location:** \`src/auth/service.py:78\`

✓ Full context available for agent reasoning`,
  },
  {
    id: "call-hierarchy",
    title: "Call Hierarchy Graph",
    mobileTitle: "Call",
    icon: Network,
    agentIntent: "Show me all functions that call `save_to_database`",
    flowSteps: [
      { label: "Method", value: "call_hierarchy" },
      { label: "Target", value: "save_to_database", highlight: true },
      { label: "Direction", value: "incoming" },
      { label: "Depth", value: "2" },
    ],
    processing: [
      "Prepare call hierarchy",
      "Traverse incoming calls",
      "Build relational graph",
      "Flatten to markdown",
    ],
    resultMarkdown: `### Call Hierarchy: \`save_to_database\`

**Incoming Calls (Depth 2):**

\`\`\`
save_to_database
├─ UserService.create_user
│  └─ UserController.register
├─ OrderService.place_order
│  ├─ CheckoutController.submit
│  └─ OrderWorker.process_queue
└─ CacheManager.persist
   └─ CacheWorker.flush_periodic
\`\`\`

**Total callers:** 3 direct, 5 transitive  
**Files affected:** 6

✓ Full dependency graph available`,
  },
];

export default function HomePage() {
  const [activeExample, setActiveExample] = useState(0);
  const [animationStep, setAnimationStep] = useState(0);
  const { resolvedTheme } = useTheme();

  useEffect(() => {
    const timer = setTimeout(() => {
      if (animationStep < 4) {
        setAnimationStep(animationStep + 1);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [animationStep, activeExample]);

  useEffect(() => {
    setAnimationStep(0);
  }, [activeExample]);

  const example = EXAMPLES[activeExample]!;
  const Icon = example.icon;

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main>
        <section className="py-16 lg:py-24 border-b border-border/40 bg-gradient-to-br from-primary/[0.15] via-primary/[0.08] to-background/50 relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,_var(--tw-gradient-stops))] from-primary/20 via-transparent to-transparent" />
          <div className="relative container max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl font-normal leading-tight mb-6">
                  Language Server
                  <br />
                  <span className="text-primary font-semibold">
                    Agent Protocol
                  </span>
                </h1>

                <p className="font-serif text-base sm:text-lg lg:text-xl text-muted-foreground leading-relaxed mb-10">
                  Semantic abstraction layer transforming LSP into an
                  agent-native cognitive framework. Progressive disclosure of
                  codebase intelligence for autonomous reasoning.
                </p>

                <div className="flex flex-wrap gap-4">
                  <Button asChild size="lg">
                    <Link to="/docs">Read Documentation</Link>
                  </Button>
                  <Button asChild variant="outline" size="lg">
                    <a
                      href="https://github.com/lsp-client/LSAP"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View on GitHub
                    </a>
                  </Button>
                </div>
              </div>

              <Card className="border-primary/20 shadow-lg bg-card">
                <CardHeader>
                  <div className="flex items-center gap-2 mb-1">
                    <div className="h-3 w-3 rounded-full bg-primary/20" />
                    <div className="h-3 w-3 rounded-full bg-primary/20" />
                    <div className="h-3 w-3 rounded-full bg-primary/20" />
                    <span className="font-mono text-xs text-muted-foreground ml-auto">
                      lsap-demo.py
                    </span>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2 bg-muted/30 p-4 rounded-sm border border-border/20">
                    <div className="font-mono text-xs text-muted-foreground">
                      <span className="text-primary">from</span> lsap{" "}
                      <span className="text-primary">import</span> Client
                    </div>
                    <div className="h-px bg-border/40" />
                    <div className="font-mono text-xs text-muted-foreground">
                      client = Client(
                      <span className="text-amber-500">"workspace/"</span>)
                    </div>
                    <div className="font-mono text-xs text-muted-foreground pl-4">
                      <span className="opacity-50">
                        # Natural language intent
                      </span>
                    </div>
                    <div className="font-mono text-xs text-muted-foreground">
                      result = client.locate(
                    </div>
                    <div className="font-mono text-xs text-muted-foreground pl-4">
                      text=
                      <span className="text-amber-500">"def authenticate"</span>
                    </div>
                    <div className="font-mono text-xs text-muted-foreground">
                      )
                    </div>
                    <div className="h-px bg-border/40" />
                    <div className="font-mono text-xs text-primary/70 pl-4">
                      <span className="opacity-50">
                        # → Position, context, source
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground pt-2">
                    <ArrowDown className="h-3 w-3 text-primary" />
                    <span>Agent-ready structured output</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        <div className="container max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <section className="py-16 lg:py-24 border-b border-border/40">
            <div className="mb-16">
              <h2 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-normal mb-4">
                See It In Action
              </h2>
              <p className="font-serif text-sm sm:text-base text-muted-foreground max-w-2xl">
                Real-world examples of how LSAP transforms agent-codebase
                interaction
              </p>
            </div>

            <div className="flex gap-2 mb-8 border-b border-border/40 overflow-x-auto">
              {EXAMPLES.map((ex, idx) => {
                const TabIcon = ex.icon;
                return (
                  <button
                    key={ex.id}
                    onClick={() => setActiveExample(idx)}
                    aria-label={ex.title}
                    className={`
                    font-mono text-xs sm:text-sm px-3 sm:px-4 py-3 border-b-2 transition-all whitespace-nowrap
                    flex items-center gap-1.5 sm:gap-2 flex-shrink-0
                    ${
                      activeExample === idx
                        ? "border-primary text-primary"
                        : "border-transparent text-muted-foreground hover:text-foreground"
                    }
                  `}
                  >
                    <TabIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                    <span className="hidden sm:inline">{ex.title}</span>
                    <span className="sm:hidden">{ex.mobileTitle}</span>
                  </button>
                );
              })}
            </div>

            <div className="space-y-6">
              {/* Row 1: Intent + Request */}
              <div className="grid lg:grid-cols-2 gap-2 sm:gap-3 md:gap-4">
                <Card
                  className={`transition-all duration-300 ${
                    animationStep >= 0
                      ? "opacity-100 translate-y-0"
                      : "opacity-0 translate-y-4"
                  }`}
                >
                  <CardHeader className="pb-4">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-xs text-muted-foreground font-medium">
                        01
                      </span>
                      <CardTitle>Agent Intent</CardTitle>
                      <Icon className="h-4 w-4 text-primary ml-auto" />
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="font-serif text-sm italic text-foreground leading-relaxed">
                      {example.agentIntent}
                    </p>
                  </CardContent>
                </Card>

                <Card
                  className={`transition-all duration-300 delay-75 ${
                    animationStep >= 1
                      ? "opacity-100 translate-y-0"
                      : "opacity-0 translate-y-4"
                  }`}
                >
                  <CardHeader className="pb-4">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-xs text-muted-foreground font-medium">
                        02
                      </span>
                      <CardTitle>LSAP Request</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="space-y-2">
                      {example.flowSteps.map((step, idx) => (
                        <div
                          key={idx}
                          className="flex items-center gap-2 transition-all duration-200"
                          style={{
                            opacity: animationStep >= 1 ? 1 : 0,
                            transform:
                              animationStep >= 1
                                ? "translateX(0)"
                                : "translateX(-10px)",
                            transitionDelay: `${idx * 50}ms`,
                          }}
                        >
                          <span className="font-mono text-xs text-muted-foreground min-w-[70px]">
                            {step.label}:
                          </span>
                          <ArrowRight className="h-3 w-3 text-border flex-shrink-0" />
                          <code
                            className={`font-mono text-xs flex-1 truncate ${
                              step.highlight
                                ? "text-primary font-medium bg-primary/5 px-2 py-0.5 rounded"
                                : "text-foreground"
                            }`}
                          >
                            {step.value}
                          </code>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="flex justify-center py-2">
                <ArrowDown
                  className="h-5 w-5 text-border transition-all duration-300"
                  style={{
                    opacity: animationStep >= 2 ? 1 : 0.2,
                    transform:
                      animationStep >= 2 ? "translateY(0)" : "translateY(-8px)",
                  }}
                />
              </div>

              {/* Row 2: Processing + Result */}
              <div className="grid lg:grid-cols-2 gap-2 sm:gap-3 md:gap-4">
                <Card
                  className={`transition-all duration-300 delay-100 ${
                    animationStep >= 2
                      ? "opacity-100 translate-y-0"
                      : "opacity-0 translate-y-4"
                  }`}
                >
                  <CardHeader className="pb-4">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-xs text-muted-foreground font-medium">
                        03
                      </span>
                      <CardTitle>Processing Pipeline</CardTitle>
                      <Activity className="h-4 w-4 text-primary ml-auto animate-pulse" />
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="space-y-2">
                      {example.processing.map((step, idx) => (
                        <div
                          key={idx}
                          className="font-mono text-xs text-muted-foreground flex items-center gap-2 transition-all duration-200"
                          style={{
                            opacity: animationStep >= 2 ? 1 : 0,
                            transform:
                              animationStep >= 2
                                ? "translateX(0)"
                                : "translateX(-10px)",
                            transitionDelay: `${idx * 50}ms`,
                          }}
                        >
                          <span className="text-primary">•</span>
                          {step}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card
                  className={`transition-all duration-300 delay-150 border-primary/20 ${
                    animationStep >= 3
                      ? "opacity-100 translate-y-0"
                      : "opacity-0 translate-y-4"
                  }`}
                >
                  <CardHeader className="pb-4">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-xs text-muted-foreground font-medium">
                        04
                      </span>
                      <CardTitle>Agent-Ready Result</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="text-xs leading-relaxed">
                      <ReactMarkdown
                        components={{
                          h3: ({ className, ...props }) => (
                            <h3
                              className={`font-mono text-xs font-semibold text-foreground mt-0 mb-2 ${
                                className || ""
                              }`}
                              {...props}
                            />
                          ),
                          p: ({ className, children, ...props }: any) => {
                            const rawText = Array.isArray(children)
                              ? children
                                  .filter(
                                    (c: any) =>
                                      typeof c === "string" ||
                                      typeof c === "number"
                                  )
                                  .join("")
                              : typeof children === "string" ||
                                typeof children === "number"
                              ? String(children)
                              : "";

                            const looksLikeTree =
                              rawText.includes("\n") &&
                              (rawText.includes("├") ||
                                rawText.includes("│") ||
                                rawText.includes("└"));

                            if (looksLikeTree) {
                              return (
                                <pre className="overflow-x-auto whitespace-pre rounded-sm border border-border/40 bg-muted p-2.5 text-[11px] leading-tight my-2">
                                  <code className="font-mono whitespace-pre">
                                    {rawText.replace(/\n$/, "")}
                                  </code>
                                </pre>
                              );
                            }

                            return (
                              <p
                                className={`font-mono text-xs text-muted-foreground my-1 whitespace-pre-wrap break-words ${
                                  className || ""
                                }`}
                                {...props}
                              >
                                {children}
                              </p>
                            );
                          },
                          strong: ({ className, ...props }) => (
                            <strong
                              className={`text-foreground font-mono font-semibold ${
                                className || ""
                              }`}
                              {...props}
                            />
                          ),
                          ul: ({ className, ...props }) => (
                            <ul
                              className={`list-none pl-0 my-1 ${
                                className || ""
                              }`}
                              {...props}
                            />
                          ),
                          blockquote: ({ className, ...props }) => (
                            <blockquote
                              className={`border-l-2 border-primary/20 pl-3 italic text-muted-foreground my-2 ${
                                className || ""
                              }`}
                              {...props}
                            />
                          ),
                          pre: ({ children, ...props }) => {
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
                                  <div className="my-2 rounded-sm border border-border/40 bg-muted p-2.5">
                                    <SyntaxHighlighter
                                      style={resolvedTheme === 'dark' ? oneDark : oneLight}
                                      language={match[1]}
                                      PreTag="div"
                                      wrapLines
                                      lineProps={() => ({
                                        style: {
                                          backgroundColor: "transparent",
                                        },
                                      })}
                                      customStyle={{
                                        margin: 0,
                                        padding: 0,
                                        background: "transparent",
                                        fontSize: "11px",
                                        lineHeight: "1.3",
                                        fontFamily:
                                          "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
                                      }}
                                      codeTagProps={{
                                        style: {
                                          background: "transparent",
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
                                <pre
                                  className="overflow-x-auto whitespace-pre rounded-sm border border-border/40 bg-muted p-2.5 text-[11px] leading-tight my-2"
                                  {...props}
                                >
                                  <code className="font-mono whitespace-pre">
                                    {codeText}
                                  </code>
                                </pre>
                              );
                            }

                            return (
                              <pre
                                className="overflow-x-auto whitespace-pre rounded-sm border border-border/40 bg-muted p-2.5 text-[11px] leading-tight my-2"
                                {...props}
                              >
                                {children}
                              </pre>
                            );
                          },
                          code: ({ className, ...props }: any) => (
                            <code
                              className={`text-primary bg-primary/5 px-1 py-0.5 rounded font-mono text-[11px] ${
                                className || ""
                              }`}
                              {...props}
                            />
                          ),
                        }}
                      >
                        {example.resultMarkdown}
                      </ReactMarkdown>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </section>

          <section className="py-16 lg:py-24">
            <h2 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-normal mb-12">
              Core Capabilities
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 md:gap-6">
              <FeatureCard
                icon="🌐"
                title="Discovery & Resolution"
                items={[
                  { label: "Workspace Search", href: "/docs/workspace" },
                  { label: "Locate Symbols", href: "/docs/locate" },
                ]}
              />
              <FeatureCard
                icon="🔍"
                title="Deep Inspection"
                items={[
                  { label: "Symbol Info", href: "/docs/symbol" },
                  { label: "Symbol Outline", href: "/docs/symbol_outline" },
                  { label: "Inlay Hints", href: "/docs/inlay_hints" },
                ]}
              />
              <FeatureCard
                icon="🔗"
                title="Relational Mapping"
                items={[
                  { label: "References", href: "/docs/reference" },
                  { label: "Call Hierarchy", href: "/docs/call_hierarchy" },
                  { label: "Type Hierarchy", href: "/docs/type_hierarchy" },
                ]}
              />
              <FeatureCard
                icon="🩺"
                title="Environmental Awareness"
                items={[
                  { label: "Diagnostics", href: "/docs/diagnostics" },
                  { label: "Rename Analysis", href: "/docs/rename" },
                ]}
              />
            </div>
          </section>

          <footer className="py-12 border-t border-border/40 text-center">
            <p className="font-serif text-muted-foreground/80 mb-2">
              Built for the next generation of AI Software Engineers
            </p>
            <p className="font-mono text-xs text-foreground/60">
              MIT License · LSAP v1.0.0-alpha
            </p>
          </footer>
        </div>
      </main>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  items,
}: {
  icon: string;
  title: string;
  items: { label: string; href: string }[];
}) {
  return (
    <Card className="hover:border-primary/20 transition-colors">
      <CardHeader>
        <div className="text-3xl mb-3">{icon}</div>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {items.map((item, idx) => (
            <li
              key={idx}
              className="font-mono text-xs text-muted-foreground pl-4 relative before:content-['·'] before:absolute before:left-0 before:text-primary"
            >
              <Link
                to={item.href}
                className="hover:text-primary transition-colors"
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
