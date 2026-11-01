import React from 'react'

interface StepperProps {
  steps: string[]
  currentStep: number
}

export function Stepper({ steps, currentStep }: StepperProps) {
  return (
    <div className='px-5 pt-3'>
      <div className='flex items-center'>
        {steps.map((step, idx) => (
          <React.Fragment key={idx}>
            <div className='flex flex-col items-center flex-1'>
              <div className={lex h-7 w-7 items-center justify-center rounded-full text-[12px] font-semibold }>
                {idx + 1}
              </div>
              <span className='mt-1 text-[10px] text-headerText text-center'>{step}</span>
            </div>
            {idx < steps.length - 1 && (
              <div className={h-[1px] flex-1 mb-4 }></div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  )
}

export default Stepper
