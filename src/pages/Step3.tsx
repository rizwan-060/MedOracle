import { useNavigate } from 'react-router-dom'
import { AppHeader } from '../components/AppHeader'
import { ProgressBar } from '../components/ProgressBar'
import { StepFooter } from '../components/StepFooter'

export default function Step3() {
  const navigate = useNavigate()
  return (
    <div className='min-h-screen bg-cream flex flex-col'>
      <AppHeader />
      <ProgressBar currentStep={3} />
      <div className='px-5 pt-4 flex-1'>
        <h2 className='font-serif text-[28px] text-headerText'>Symptoms</h2>
        <p className='mt-1 text-[13px] text-headerText/80'>Step 3</p>
      </div>
      <StepFooter onBack={() => navigate('/step/2b')} onNext={() => navigate('/step/4')} nextLabel='Next: Labs & Vitals' />
    </div>
  )
}
