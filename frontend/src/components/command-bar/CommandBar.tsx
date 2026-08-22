import { useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'
import useCommandBar from '../../hooks/useCommandBar'

interface CommandBarProps {
  onVerdict?: () => void
  onGraph?: () => void
  onNew?: () => void
}

function CommandBar({ onVerdict, onGraph, onNew }: CommandBarProps) {
  const { commands, isFocused, inputRef, focus, unfocus, execute } = useCommandBar({
    onVerdict,
    onGraph,
    onNew,
  })
  const [value, setValue] = useState('')
  const [unrecognized, setUnrecognized] = useState(false)

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!value.trim()) {
      return
    }
    if (execute(value)) {
      setValue('')
      setUnrecognized(false)
      unfocus()
    } else {
      setUnrecognized(true)
    }
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Escape') {
      setValue('')
      setUnrecognized(false)
      unfocus()
    }
  }

  if (!isFocused) {
    return (
      <button
        type="button"
        onClick={focus}
        className="panel-transition w-full rounded-sm border border-hairline bg-surface px-2 py-1 text-left font-mono text-metadata leading-[1.3] text-tertiary hover:border-accent"
      >
        Press / for commands
      </button>
    )
  }

  return (
    <form onSubmit={submit} className="panel-transition space-y-1">
      <input
        ref={inputRef}
        value={value}
        onChange={(event) => {
          setValue(event.target.value)
          setUnrecognized(false)
        }}
        onKeyDown={handleKeyDown}
        placeholder="Type a command…"
        aria-label="Command bar"
        className="panel-transition w-full rounded-sm border border-accent bg-base px-2 py-1 font-mono text-body-mono leading-[1.3] text-primary placeholder:text-tertiary"
      />
      <ul className="flex flex-wrap gap-x-4 gap-y-0.5 font-mono text-metadata leading-[1.3] text-secondary">
        {commands.map((command) => (
          <li key={command.name}>
            <span className="text-primary">{command.name}</span> — {command.description}
          </li>
        ))}
      </ul>
      {unrecognized && (
        <p className="font-mono text-metadata leading-[1.3] text-risk-elevated">
          Unrecognized command — valid commands: verdict, graph, new
        </p>
      )}
    </form>
  )
}

export default CommandBar
