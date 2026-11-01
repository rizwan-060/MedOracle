import React from 'react'

interface DeckProgressProps {
  current: number
  total: number
}

export function DeckProgress({ current, total }: DeckProgressProps) {
  return (
    <div className='px-5 pt-2 pb-2'>
      <div className='flex items-center gap-2'>
        <span className='text-[12px] text-headerText'>{current} of {total}</span>
        <div className='flex-1 h-[3px] bg-borderSubtle/60 rounded-full overflow-hidden'>
          <div className='h-full bg-headerText' style={{ width: ${(current / total) * 100}% }}></div>
        </div>
      </div>
    </div>
  )
}

export default DeckProgress
