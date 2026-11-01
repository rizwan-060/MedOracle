import React from 'react'

interface ProgressBarProps {
  currentStep: number
}

export function ProgressBar({ currentStep }: ProgressBarProps) {
  return (
    <div className=\"px-5 pt-4\">
      <div className=\"flex items-center justify-between\">
        {[1, 2, 3, 4, 5].map((step, idx) => (
          <React.Fragment key={step}>
            <div className=\"flex flex-col items-center\">
              <div className={lex h-8 w-8 items-center justify-center rounded-full text-[13px] font-semibold }>
                {step}
              </div>
            </div>
            {idx < 4 && (
              <div className={lex-1 h-[2px] mx-1 }></div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  )
}

export default ProgressBar
