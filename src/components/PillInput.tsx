import React from 'react'

interface PillInputProps {
  placeholder?: string
  value?: string
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  icon?: React.ReactNode
}

export function PillInput({ placeholder, value, onChange, icon }: PillInputProps) {
  return (
    <label className='flex h-14 items-center gap-3 rounded-full bg-surface px-5 text-headerText shadow-[0_10px_22px_-12px_rgba(77,115,143,0.55),0_1px_3px_rgba(77,115,143,0.14)] ring-1 ring-headerText/15 focus-within:ring-2 focus-within:ring-headerText'>
      {icon && <span className='shrink-0'>{icon}</span>}
      <input 
        type='text' 
        placeholder={placeholder} 
        value={value}
        onChange={onChange}
        className='min-w-0 flex-1 bg-transparent text-[15px] text-ink outline-none placeholder:text-headerText/55' 
      />
    </label>
  )
}

export default PillInput
