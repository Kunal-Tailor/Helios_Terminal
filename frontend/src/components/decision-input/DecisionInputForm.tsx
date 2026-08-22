import { useState } from 'react'
import type { FormEvent } from 'react'
import OptionChipInput from './OptionChipInput'
import type { DecisionRequest } from '../../lib/api'

interface DecisionInputFormProps {
  onSubmit?: (brief: DecisionRequest) => void
}

function DecisionInputForm({ onSubmit }: DecisionInputFormProps) {
  const [entity, setEntity] = useState('')
  const [capability, setCapability] = useState('')
  const [options, setOptions] = useState<string[]>([])

  const canSubmit = entity.trim().length > 0 && capability.trim().length > 0

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!canSubmit) {
      return
    }
    onSubmit?.({
      entity: entity.trim(),
      capability: capability.trim(),
      ...(options.length > 0 ? { options } : {}),
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-sm border border-hairline bg-surface p-6">
      <div className="space-y-1">
        <label
          htmlFor="entity"
          className="block font-mono text-body-mono leading-[1.3] text-secondary"
        >
          Entity
        </label>
        <input
          id="entity"
          type="text"
          value={entity}
          onChange={(event) => setEntity(event.target.value)}
          className="w-full rounded-sm border border-hairline bg-base px-2 py-1.5 font-ui text-body-ui text-primary placeholder:text-tertiary"
        />
      </div>
      <div className="space-y-1">
        <label
          htmlFor="capability"
          className="block font-mono text-body-mono leading-[1.3] text-secondary"
        >
          Capability
        </label>
        <input
          id="capability"
          type="text"
          value={capability}
          onChange={(event) => setCapability(event.target.value)}
          className="w-full rounded-sm border border-hairline bg-base px-2 py-1.5 font-ui text-body-ui text-primary placeholder:text-tertiary"
        />
      </div>
      <fieldset className="space-y-2">
        <legend className="font-mono text-body-mono leading-[1.3] text-secondary">
          Candidate options
        </legend>
        <OptionChipInput options={options} onChange={setOptions} />
      </fieldset>
      <button
        type="submit"
        disabled={!canSubmit}
        className="rounded-sm bg-accent px-3 py-1.5 font-ui text-body-ui text-bg-base hover:opacity-90 disabled:bg-surface-raised disabled:text-tertiary"
      >
        Submit decision brief
      </button>
    </form>
  )
}

export default DecisionInputForm
