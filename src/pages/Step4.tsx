import { useNavigate } from 'react-router-dom'
import { AppHeader } from '../components/AppHeader'
import { ProgressBar } from '../components/ProgressBar'
import { StepFooter } from '../components/StepFooter'

export default function Step4() {
  const navigate = useNavigate()
  return (
    <div className='min-h-screen bg-cream flex flex-col'>
      <AppHeader />
      <ProgressBar currentStep={4} />
      <div className='px-5 pt-4 flex-1'>
        <h2 className='font-serif text-[28px] text-headerText'>Labs & Vitals</h2>
        <p className='mt-1 text-[13px] text-headerText/80'>Step 4</p>
      </div>
      <StepFooter onBack={() => navigate('/step/3')} onNext={() => navigate('/step/5')} nextLabel='Next: Review & Confirm' />
    </div>
  )
}
