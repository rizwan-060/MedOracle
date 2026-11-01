import React from 'react'

interface SecondaryButtonProps {
  children: React.ReactNode
  onClick?: () => void
  className?: string
}

export function SecondaryButton({ children, onClick, className = '' }: SecondaryButtonProps) {
  return (
    <button
      onClick={onClick}
      className={lex h-[56px] w-full items-center justify-center rounded-[12px] border border-headerText/40 bg-white text-[16px] font-semibold text-headerText }
    >
      {children}
    </button>
  )
}

export default SecondaryButton
