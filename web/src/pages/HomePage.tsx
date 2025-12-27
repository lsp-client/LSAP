import { useState, useEffect } from 'react'
import Header from '../components/Header'
import { Link } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { ArrowDown, Search, Code2, Network, Activity } from 'lucide-react'

const EXAMPLES = [
  {
    id: 'locate',
    title: 'Locate Symbol',
    icon: Search,
    agentIntent: 'Find the implementation of the `process_data` function',
    request: {
      method: 'locate',
      params: {
        locate: {
          file_path: 'src/processor.py',
          text: 'def process_data'
        }
      }
    },
    processing: [
      'Fuzzy search in file',
      'AST-based resolution',
      'Exact position located'
    ],
    result: {
      position: { line: 42, character: 4 },
      context: 'Found in src/processor.py:42'
    }
  },
  {
    id: 'symbol',
    title: 'Symbol Deep Inspection',
    icon: Code2,
    agentIntent: 'Understand what `authenticate_user` does and how to use it',
    request: {
      method: 'symbol_info',
      params: {
        locate: {
          symbol_path: ['AuthService', 'authenticate_user']
        }
      }
    },
    processing: [
      'Resolve symbol path',
      'Fetch signature + docs',
      'Extract implementation',
      'Aggregate into snapshot'
    ],
    result: {
      signature: 'async def authenticate_user(username: str, password: str) -> User',
      docs: 'Authenticates a user with credentials...',
      source: '12 lines of implementation'
    }
  },
  {
    id: 'call-hierarchy',
    title: 'Call Hierarchy Graph',
    icon: Network,
    agentIntent: 'Show me all functions that call `save_to_database`',
    request: {
      method: 'call_hierarchy',
      params: {
        locate: { text: 'save_to_database' },
        depth: 2,
        direction: 'incoming'
      }
    },
    processing: [
      'Prepare call hierarchy',
      'Traverse incoming calls',
      'Build relational graph',
      'Flatten to markdown'
    ],
    result: {
      callers: [
        'UserService.create_user',
        'OrderService.place_order',
        'CacheManager.persist'
      ],
      depth: 2,
      format: 'Relational graph'
    }
  }
]

export default function HomePage() {
  const [activeExample, setActiveExample] = useState(0)
  const [animationStep, setAnimationStep] = useState(0)
  
  useEffect(() => {
    const timer = setTimeout(() => {
      if (animationStep < 4) {
        setAnimationStep(animationStep + 1)
      }
    }, 800)
    return () => clearTimeout(timer)
  }, [animationStep, activeExample])
  
  useEffect(() => {
    setAnimationStep(0)
  }, [activeExample])

  const example = EXAMPLES[activeExample]
  const Icon = example.icon

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container max-w-6xl mx-auto px-6 lg:px-8">
        {/* Hero Section */}
        <section className="py-16 lg:py-24 border-b border-border/40">
          <div className="max-w-3xl">
            <h1 className="font-serif text-5xl lg:text-6xl font-light leading-tight mb-6">
              Language Server
              <br />
              <span className="text-primary">Agent Protocol</span>
            </h1>
            
            <p className="font-serif text-lg lg:text-xl text-muted-foreground leading-relaxed mb-10">
              Semantic abstraction layer transforming LSP into an agent-native cognitive framework.
              Progressive disclosure of codebase intelligence for autonomous reasoning.
            </p>

            <div className="flex flex-wrap gap-4">
              <Button asChild size="lg">
                <Link to="/docs">Read Documentation</Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <a 
                  href="https://github.com/yourusername/lsap"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View on GitHub
                </a>
              </Button>
            </div>
          </div>
        </section>

        {/* Examples Section */}
        <section className="py-16 lg:py-24 border-b border-border/40">
          <div className="mb-12">
            <h2 className="font-serif text-3xl lg:text-4xl font-light mb-4">
              See It In Action
            </h2>
            <p className="font-serif text-muted-foreground max-w-2xl">
              Real-world examples of how LSAP transforms agent-codebase interaction
            </p>
          </div>

          {/* Example Tabs */}
          <div className="flex gap-2 mb-8 border-b border-border/40 overflow-x-auto">
            {EXAMPLES.map((ex, idx) => {
              const TabIcon = ex.icon
              return (
                <button
                  key={ex.id}
                  onClick={() => setActiveExample(idx)}
                  className={`
                    font-mono text-sm px-4 py-3 border-b-2 transition-all whitespace-nowrap
                    flex items-center gap-2
                    ${activeExample === idx 
                      ? 'border-primary text-primary' 
                      : 'border-transparent text-muted-foreground hover:text-foreground'
                    }
                  `}
                >
                  <TabIcon className="h-4 w-4" />
                  {ex.title}
                </button>
              )
            })}
          </div>

          {/* Example Flow */}
          <div className="space-y-4">
            {/* Step 1: Agent Intent */}
            <Card className={`transition-all duration-500 ${animationStep >= 0 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <span className="font-mono text-xs text-muted-foreground font-medium">01</span>
                  <CardTitle>Agent Intent</CardTitle>
                  <Icon className="h-4 w-4 text-primary ml-auto" />
                </div>
              </CardHeader>
              <CardContent>
                <p className="font-serif text-lg italic text-foreground">
                  {example.agentIntent}
                </p>
              </CardContent>
            </Card>

            {/* Arrow */}
            <div className="flex justify-center py-2">
              <ArrowDown 
                className="h-6 w-6 text-border transition-all duration-500"
                style={{
                  opacity: animationStep >= 1 ? 1 : 0.2,
                  transform: animationStep >= 1 ? 'translateY(0)' : 'translateY(-10px)'
                }}
              />
            </div>

            {/* Step 2: LSAP Request */}
            <Card className={`transition-all duration-500 delay-200 ${animationStep >= 1 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <span className="font-mono text-xs text-muted-foreground font-medium">02</span>
                  <CardTitle>LSAP Request</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <pre className="font-mono text-xs bg-muted p-4 rounded-sm overflow-auto text-muted-foreground leading-relaxed">
                  {JSON.stringify(example.request, null, 2)}
                </pre>
              </CardContent>
            </Card>

            {/* Arrow */}
            <div className="flex justify-center py-2">
              <ArrowDown 
                className="h-6 w-6 text-border transition-all duration-500"
                style={{
                  opacity: animationStep >= 2 ? 1 : 0.2,
                  transform: animationStep >= 2 ? 'translateY(0)' : 'translateY(-10px)'
                }}
              />
            </div>

            {/* Step 3: Processing */}
            <Card className={`transition-all duration-500 delay-300 ${animationStep >= 2 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <span className="font-mono text-xs text-muted-foreground font-medium">03</span>
                  <CardTitle>Processing Pipeline</CardTitle>
                  <Activity className="h-4 w-4 text-primary ml-auto animate-pulse" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {example.processing.map((step, idx) => (
                    <div 
                      key={idx}
                      className="font-mono text-sm text-muted-foreground flex items-center gap-3 transition-all duration-300"
                      style={{
                        opacity: animationStep >= 2 ? 1 : 0,
                        transform: animationStep >= 2 ? 'translateX(0)' : 'translateX(-10px)',
                        transitionDelay: `${idx * 100}ms`
                      }}
                    >
                      <span className="text-primary">•</span>
                      {step}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Arrow */}
            <div className="flex justify-center py-2">
              <ArrowDown 
                className="h-6 w-6 text-border transition-all duration-500"
                style={{
                  opacity: animationStep >= 3 ? 1 : 0.2,
                  transform: animationStep >= 3 ? 'translateY(0)' : 'translateY(-10px)'
                }}
              />
            </div>

            {/* Step 4: Result */}
            <Card className={`transition-all duration-500 delay-500 border-primary/20 ${animationStep >= 3 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <span className="font-mono text-xs text-muted-foreground font-medium">04</span>
                  <CardTitle>Agent-Ready Result</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <pre className="font-mono text-xs bg-muted p-4 rounded-sm overflow-auto text-muted-foreground leading-relaxed">
                  {JSON.stringify(example.result, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16 lg:py-24">
          <h2 className="font-serif text-3xl lg:text-4xl font-light mb-12">
            Core Capabilities
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <FeatureCard 
              icon="🌐"
              title="Discovery & Resolution"
              items={['Workspace Search', 'Locate Symbols']}
            />
            <FeatureCard 
              icon="🔍"
              title="Deep Inspection"
              items={['Symbol Info', 'Symbol Outline', 'Inlay Hints']}
            />
            <FeatureCard 
              icon="🔗"
              title="Relational Mapping"
              items={['References', 'Call Hierarchy', 'Type Hierarchy']}
            />
            <FeatureCard 
              icon="🩺"
              title="Environmental Awareness"
              items={['Diagnostics', 'Rename Analysis']}
            />
          </div>
        </section>

        {/* Footer */}
        <footer className="py-12 border-t border-border/40 text-center">
          <p className="font-serif text-muted-foreground mb-2">
            Built for the next generation of AI Software Engineers
          </p>
          <p className="font-mono text-xs text-muted-foreground">
            MIT License · LSAP v1.0.0-alpha
          </p>
        </footer>
      </main>
    </div>
  )
}

function FeatureCard({ icon, title, items }: { icon: string; title: string; items: string[] }) {
  return (
    <Card className="hover:border-primary/20 transition-colors">
      <CardHeader>
        <div className="text-3xl mb-3">{icon}</div>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {items.map((item, idx) => (
            <li key={idx} className="font-mono text-xs text-muted-foreground pl-4 relative before:content-['·'] before:absolute before:left-0 before:text-primary">
              {item}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
