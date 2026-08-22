import { useState } from 'react'
import type { KeyboardEvent } from 'react'

const MAX_OPTIONS = 6

interface OptionChipInputProps {
  options: string[]
  onChange: (options: string[]) => void
}

function OptionChipInput({ options, onChange }: OptionChipInputProps) {
  const [draft, setDraft] = useState('')
  const maxReached = options.length >= MAX_OPTIONS

  const commitDraft = () => {
    const trimmed = draft.trim()
    if (!trimmed || maxReached || options.includes(trimmed)) {
      return
    }
    onChange([...options, trimmed])
    setDraft('')
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      event.preventDefault()
      commitDraft()
      return
    }
    if (event.key === 'Backspace' && draft === '' && options.length > 0) {
      onChange(options.slice(0, -1))
    }
  }

  const removeOption = (option: string) => {
    onChange(options.filter((candidate) => candidate !== option))
  }

  return (
    <div>
      {options.length === 0 ? (
        <p>Leave blank and Helios will infer the realistic option set</p>
      ) : (
        <ul>
          {options.map((option) => (
            <li key={option}>
              {option}
              <button
                type="button"
                onClick={() => removeOption(option)}
                aria-label={`Remove ${option}`}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
      <input
        type="text"
        value={draft}
        disabled={maxReached}
        placeholder={
          maxReached ? 'Maximum of 6 options reached' : 'Add an option and press Enter'
        }
        onChange={(event) => setDraft(event.target.value)}
        onKeyDown={handleKeyDown}
      />
    </div>
  )
}

export default OptionChipInput
