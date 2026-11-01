import { useNavigate } from 'react-router-dom'
import { AppHeader } from '../components/AppHeader'
import { ProgressBar } from '../components/ProgressBar'
import { PrimaryButton } from '../components/PrimaryButton'

export default function Step5() {
  const navigate = useNavigate()
  return (
    <div className='min-h-screen bg-cream flex flex-col'>
      <AppHeader />
      <ProgressBar currentStep={5} />
      <div className='px-5 pt-4 flex-1 overflow-y-auto'>
        <h2 className='font-serif text-[28px] text-headerText'>Review & Confirm</h2>
        <p className='mt-1 text-[13px] text-headerText/80'>Step 5</p>
      </div>
      <div className='px-5 pb-6 pt-4 flex gap-3'>
        <button onClick={() => navigate('/step/4')} className='flex h-[56px] flex-1 items-center justify-center rounded-[12px] border border-headerText/40 bg-white text-[16px] font-semibold text-headerText'>Back</button>
        <PrimaryButton onClick={() => navigate('/results/reports')} className='flex-1'>Submit Assessment</PrimaryButton>
      </div>
    </div>
  )
}
