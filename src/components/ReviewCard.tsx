import React from 'react'

interface ReviewCardProps {
  title: string
  subtitle?: string
  children: React.ReactNode
  onEdit?: () => void
}

export function ReviewCard({ title, subtitle, children, onEdit }: ReviewCardProps) {
  return (
    <div className='relative flex flex-col overflow-hidden rounded-[20px] border border-borderSubtle bg-soft p-5 pt-6 shadow-[0_22px_34px_-18px_rgba(30,42,51,0.55),0_3px_8px_rgba(30,42,51,0.12)]'>
      <div className='flex items-start justify-between gap-3'>
        <div>
          <h3 className='font-serif text-[22px] font-semibold leading-7 text-ink'>{title}</h3>
          {subtitle && <p className='mt-0.5 text-[12.5px] text-headerText'>{subtitle}</p>}
        </div>
        {onEdit && (
          <button onClick={onEdit} className='-mr-2 -mt-1.5 flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-headerText' aria-label='Edit'>
            <svg className='h-[18px] w-[18px]' viewBox='0 0 20 20' fill='none' aria-hidden='true'>
              <g stroke='currentColor' strokeWidth='1.7' strokeLinecap='round' strokeLinejoin='round'>
                <path d='M3.5 16.5 L4.2 13 L13.2 4 C13.9 3.3 15 3.3 15.7 4 L16 4.3 C16.7 5 16.7 6.1 16 6.8 L7 15.8 Z'></path>
              </g>
            </svg>
          </button>
        )}
      </div>
      <div className='mt-4 flex flex-1 flex-col gap-4 border-t border-headerText/15 pt-4'>
        {children}
      </div>
    </div>
  )
}

export default ReviewCard
