import { useNavigate } from 'react-router-dom'
import { AppHeader } from '../components/AppHeader'
import { ProgressBar } from '../components/ProgressBar'
import { StepFooter } from '../components/StepFooter'
import { PrimaryButton } from '../components/PrimaryButton'
import { useState } from 'react'

export default function Step2B() {
  const navigate = useNavigate()
  const [showDrawer, setShowDrawer] = useState(false)
  return (
    <div className='min-h-screen bg-cream flex flex-col'>
      <AppHeader />
      <ProgressBar currentStep={2} />
      <div className='px-5 pt-4 flex-1'>
        <h2 className='font-serif text-[28px] text-headerText'>Medications & Family History</h2>
        <p className='mt-1 text-[13px] text-headerText/80'>Step 2B</p>
        <div className='mt-4 flex gap-2'>
          <button className='px-4 py-2 rounded-full bg-headerText text-white text-[13px]'>Medication</button>
          <button className='px-4 py-2 rounded-full border border-headerText/40 text-headerText text-[13px]'>Family Record</button>
        </div>
        <button onClick={() => setShowDrawer(true)} className='mt-4 text-[14px] text-terracotta font-semibold'>+ Add</button>
      </div>
      <StepFooter onBack={() => navigate('/step/2a')} onNext={() => navigate('/step/3')} nextLabel='Next: Symptoms' />
      {showDrawer && (
        <div className='fixed inset-0 z-50 flex items-end justify-center'>
          <div className='absolute inset-0 bg-black/30' onClick={() => setShowDrawer(false)}></div>
          <div className='relative w-[390px] max-h-[90%] bg-sheet rounded-t-[28px] overflow-y-auto'>
            <div className='px-5 pt-4 pb-3 flex items-center justify-between'>
              <span className='text-[18px] font-semibold text-textPrimary font-serif'>Add Record</span>
              <button onClick={() => setShowDrawer(false)} className='text-headerText text-[14px]'>Close</button>
            </div>
            <div className='px-5 pb-6'>
              <PrimaryButton onClick={() => setShowDrawer(false)}>Save Record</PrimaryButton>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
