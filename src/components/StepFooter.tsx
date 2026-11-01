import React from 'react'

interface StepFooterProps {
  onBack?: () => void
  onNext?: () => void
  nextLabel?: string
  backLabel?: string
  showBack?: boolean
}

export function StepFooter({ onBack, onNext, nextLabel = 'Continue', backLabel = 'Back', showBack = true }: StepFooterProps) {
  return (
    <div className='px-5 pb-6 pt-4 flex gap-3'>
      {showBack && (
        <button onClick={onBack} className='flex h-[56px] flex-1 items-center justify-center rounded-[12px] border border-headerText/40 bg-white text-[16px] font-semibold text-headerText'>
          {backLabel}
        </button>
      )}
      <button onClick={onNext} className='flex h-[56px] flex-1 items-center justify-center rounded-[12px] bg-terracotta text-[16px] font-semibold text-white shadow-[0_12px_22px_-10px_rgba(181,88,58,0.7)]'>
        {nextLabel}
      </button>
    </div>
  )
}

export default StepFooter
