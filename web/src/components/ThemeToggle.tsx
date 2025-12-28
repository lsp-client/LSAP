import { Moon, Sun } from 'lucide-react'
import { useTheme } from '../lib/ThemeProvider'

export default function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme()

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')
  }

  const isDarkTheme = resolvedTheme === 'dark'
  const ariaLabel = isDarkTheme ? 'Switch to light mode' : 'Switch to dark mode'

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="relative inline-flex items-center justify-center w-9 h-9 rounded-md border border-border bg-background hover:bg-accent hover:text-accent-foreground transition-colors"
      aria-label={ariaLabel}
      aria-pressed={isDarkTheme}
    >
      {isDarkTheme ? (
        <Sun className="h-4 w-4" />
      ) : (
        <Moon className="h-4 w-4" />
      )}
    </button>
  )
}
