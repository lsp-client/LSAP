import { Link } from 'react-router-dom'
import { Github } from 'lucide-react'

export default function Header() {
  return (
    <header className="sticky top-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border/40">
      <div className="container max-w-6xl mx-auto px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link 
            to="/" 
            className="flex items-baseline gap-2 transition-opacity hover:opacity-70"
          >
            <span className="font-mono text-lg font-medium tracking-wider">
              LSAP
            </span>
            <span className="font-mono text-xs text-muted-foreground font-light">
              v1.0.0-α
            </span>
          </Link>
          
          <nav className="flex items-center gap-8">
            <Link 
              to="/docs" 
              className="font-mono text-sm text-muted-foreground hover:text-foreground transition-colors relative after:absolute after:bottom-0 after:left-0 after:h-px after:w-0 after:bg-primary after:transition-all hover:after:w-full"
            >
              Documentation
            </Link>
            <a 
              href="https://github.com/yourusername/lsap" 
              target="_blank" 
              rel="noopener noreferrer"
              className="font-mono text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2"
            >
              <Github className="h-4 w-4" />
              GitHub
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}
