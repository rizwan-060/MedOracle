import React from 'react'

interface AppHeaderProps {
  showBack?: boolean
  onBack?: () => void
  showSave?: boolean
}

export function AppHeader({ showBack, onBack, showSave = true }: AppHeaderProps) {
  return (
    <header className='rounded-b-[28px] bg-slate px-5 pb-3 pt-4 text-white'>
      <div className='grid grid-cols-[1fr_auto_1fr] items-center'>
        <span className='flex items-center gap-1.5 text-[11px] font-medium'>
          <svg className='h-4 w-4 shrink-0' viewBox='0 0 16 16' fill='none' aria-hidden='true'>
            <path d='M3 8.5 L6.5 12 L13 4.5' stroke='currentColor' strokeWidth='2' strokeLinecap='round' strokeLinejoin='round'></path>
          </svg>
          Autosaved
        </span>
        <span className='flex items-center gap-1.5 text-[16px] font-semibold'>
          <svg className='h-5 w-5' viewBox='0 0 20 20' fill='none' aria-hidden='true'>
            <path d='M10 2 L17 5 V10 C17 14 14 17 10 18 C6 17 3 14 3 10 V5 Z' stroke='currentColor' strokeWidth='1.5'></path>
            <path d='M10 7 V13 M7 10 H13' stroke='currentColor' strokeWidth='1.5' strokeLinecap='round'></path>
          </svg>
          MedOracle
        </span>
        {showSave ? (
          <span className='justify-self-end rounded-full border border-white/40 bg-white/15 px-3 py-1.5 text-[12px] font-medium'>Save & Exit</span>
        ) : (
          <span></span>
        )}
      </div>
    </header>
  )
}

export default AppHeader
