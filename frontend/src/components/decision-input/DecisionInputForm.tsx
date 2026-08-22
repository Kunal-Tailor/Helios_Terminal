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
    <form onSubmit={handleSubmit}>
      <label>
        Entity
        <input
          type="text"
          value={entity}
          onChange={(event) => setEntity(event.target.value)}
        />
      </label>
      <label>
        Capability
        <input
          type="text"
          value={capability}
          onChange={(event) => setCapability(event.target.value)}
        />
      </label>
      <fieldset>
        <legend>Candidate options</legend>
        <OptionChipInput options={options} onChange={setOptions} />
      </fieldset>
      <button type="submit" disabled={!canSubmit}>
        Submit decision brief
      </button>
    </form>
  )
}

export default DecisionInputForm
