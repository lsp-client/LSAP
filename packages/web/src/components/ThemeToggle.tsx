import { Moon, Sun, Monitor } from 'lucide-react'
import { useTheme } from '../lib/ThemeProvider'

export default function ThemeToggle() {
  const { theme, resolvedTheme, setTheme } = useTheme()

  const toggleTheme = () => {
    // Cycle through: system → light → dark → system
    if (theme === 'light') {
      setTheme('dark')
    } else if (theme === 'dark') {
      setTheme('system')
    } else {
      setTheme('light')
    }
  }

  const getIcon = () => {
    if (theme === 'system') {
      return <Monitor className="h-4 w-4" />
    }
    return resolvedTheme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />
  }

  const getAriaLabel = () => {
    if (theme === 'light') return 'Switch to dark mode'
    if (theme === 'dark') return 'Switch to system theme'
    return 'Switch to light mode'
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="relative inline-flex items-center justify-center w-9 h-9 rounded-md border border-border bg-background hover:bg-accent hover:text-accent-foreground transition-colors"
      aria-label={getAriaLabel()}
      title={theme === 'system' ? `System theme (currently ${resolvedTheme})` : `${theme} theme`}
    >
      {getIcon()}
    </button>
  )
}
