import React from 'react'

interface AccordionCardProps {
  title: string
  children: React.ReactNode
  defaultOpen?: boolean
}

export function AccordionCard({ title, children, defaultOpen = false }: AccordionCardProps) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className='rounded-[12px] border border-borderSubtle bg-white overflow-hidden'>
      <button
        onClick={() => setOpen(!open)}
        className='w-full px-4 py-3 flex items-center justify-between text-left'
      >
        <span className='text-[15px] font-semibold text-ink font-serif'>{title}</span>
        <span className='text-headerText'>{open ? '-' : '+'}</span>
      </button>
      {open && <div className='px-4 pb-4 border-t border-borderSubtle/40'>{children}</div>}
    </div>
  )
}

export default AccordionCard
