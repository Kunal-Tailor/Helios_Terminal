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
    <div className="space-y-2">
      {options.length === 0 ? (
        <p className="font-mono text-metadata leading-[1.3] text-tertiary">
          Leave blank and Helios will infer the realistic option set
        </p>
      ) : (
        <ul className="flex flex-wrap gap-1.5">
          {options.map((option) => (
            <li
              key={option}
              className="inline-flex items-center gap-1 rounded-sm border border-hairline bg-surface-raised px-2 py-0.5 font-mono text-body-mono leading-[1.3] text-primary"
            >
              {option}
              <button
                type="button"
                onClick={() => removeOption(option)}
                aria-label={`Remove ${option}`}
                className="text-secondary hover:text-primary"
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
        className="w-full rounded-sm border border-hairline bg-base px-2 py-1.5 font-ui text-body-ui text-primary placeholder:text-tertiary disabled:text-tertiary"
      />
    </div>
  )
}

export default OptionChipInput
