import React from 'react'

interface PileCardProps {
  title: string
  items: string[]
  onEdit?: () => void
}

export function PileCard({ title, items, onEdit }: PileCardProps) {
  return (
    <div className='rounded-[12px] border border-borderSubtle bg-white p-4'>
      <div className='flex items-start justify-between'>
        <span className='text-[15px] font-semibold text-ink font-serif'>{title}</span>
        {onEdit && <button onClick={onEdit} className='text-headerText text-[12px]'>Edit</button>}
      </div>
      <div className='mt-2 flex flex-wrap gap-2'>
        {items.map((item, idx) => (
          <span key={idx} className='rounded-full border border-headerText/30 bg-headerText/10 px-3 py-1 text-[13px] text-ink'>
            {item}
          </span>
        ))}
      </div>
    </div>
  )
}

export default PileCard
