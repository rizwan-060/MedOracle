import React from 'react'

interface PrimaryButtonProps {
  children: React.ReactNode
  onClick?: () => void
  className?: string
  disabled?: boolean
}

export function PrimaryButton({ children, onClick, className = '', disabled }: PrimaryButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={lex h-[56px] w-full items-center justify-center rounded-[12px] bg-terracotta text-[16px] font-semibold text-white shadow-[0_12px_22px_-10px_rgba(181,88,58,0.7)]  }
    >
      {children}
    </button>
  )
}

export default PrimaryButton
