import { useCallback, useEffect, useRef, useState } from 'react'

export interface CommandDefinition {
  name: string
  description: string
}

export const COMMANDS: CommandDefinition[] = [
  { name: 'verdict', description: 'Jump to the verdict pane' },
  { name: 'graph', description: 'Jump to the dependency graph' },
  { name: 'new', description: 'Start a new decision' },
]

interface UseCommandBarOptions {
  onVerdict?: () => void
  onGraph?: () => void
  onNew?: () => void
}

function useCommandBar({ onVerdict, onGraph, onNew }: UseCommandBarOptions) {
  const [isFocused, setIsFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (isFocused) {
      inputRef.current?.focus()
    }
  }, [isFocused])

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.key === '/' || event.key === ':') && !isFocused) {
        const target = event.target as HTMLElement | null
        const tag = target?.tagName?.toLowerCase()
        if (tag === 'input' || tag === 'textarea' || target?.isContentEditable) {
          return
        }
        event.preventDefault()
        setIsFocused(true)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isFocused])

  const focus = useCallback(() => {
    setIsFocused(true)
  }, [])

  const unfocus = useCallback(() => {
    setIsFocused(false)
  }, [])

  const execute = useCallback(
    (raw: string): boolean => {
      const name = raw.trim().toLowerCase()
      if (name === 'verdict') {
        onVerdict?.()
        return true
      }
      if (name === 'graph') {
        onGraph?.()
        return true
      }
      if (name === 'new') {
        onNew?.()
        return true
      }
      return false
    },
    [onVerdict, onGraph, onNew],
  )

  return { commands: COMMANDS, isFocused, inputRef, focus, unfocus, execute }
}

export default useCommandBar
