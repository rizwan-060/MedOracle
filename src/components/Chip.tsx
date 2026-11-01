import React from 'react'

interface ChipProps {
  label: string
  selected?: boolean
  onClick?: () => void
}

export function Chip({ label, selected, onClick }: ChipProps) {
  return (
    <button
      onClick={onClick}
      className={ounded-full border px-3 py-1 text-[13.5px] font-medium }
    >
      {label}
    </button>
  )
}

export default Chip
