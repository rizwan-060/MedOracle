import React from 'react'

interface DrawerProps {
  isOpen: boolean
  onClose: () => void
  children: React.ReactNode
  title?: string
}

export function Drawer({ isOpen, onClose, children, title }: DrawerProps) {
  if (!isOpen) return null
  return (
    <div className='fixed inset-0 z-50 flex items-end justify-center'>
      <div className='absolute inset-0 bg-black/30' onClick={onClose}></div>
      <div className='relative w-[390px] max-h-[90%] bg-sheet rounded-t-[28px] overflow-y-auto'>
        <div className='px-5 pt-4 pb-3 flex items-center justify-between'>
          {title && <span className='text-[18px] font-semibold text-ink font-serif'>{title}</span>}
          <button onClick={onClose} className='text-headerText text-[14px]'>Close</button>
        </div>
        <div className='px-5 pb-6'>
          {children}
        </div>
      </div>
    </div>
  )
}

export default Drawer
