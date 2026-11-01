import { useNavigate } from 'react-router-dom'
import { AppHeader } from '../components/AppHeader'
import { ProgressBar } from '../components/ProgressBar'
import { StepFooter } from '../components/StepFooter'

export default function Step2AEmpty() {
  const navigate = useNavigate()
  return (
    <div className='min-h-screen bg-cream flex flex-col'>
      <AppHeader />
      <ProgressBar currentStep={2} />
      <div className='px-5 pt-4 flex-1'>
        <h2 className='font-serif text-[28px] text-headerText'>Clinical Status & History</h2>
        <p className='mt-1 text-[13px] text-headerText/80'>Step 2A - Conditions</p>
        <div className='mt-4'>
          <input 
            type='text' 
            placeholder='Search for conditions (e.g., Hypertension, Diabetes)' 
            className='w-full h-12 rounded-[12px] border border-borderSubtle px-4 text-[14px] text-textPrimary bg-white'
          />
        </div>
        <button onClick={() => navigate('/step/2b')} className='mt-4 text-[14px] text-headerText underline'>I don't have any</button>
      </div>
      <StepFooter onBack={() => navigate('/dashboard')} onNext={() => navigate('/step/2b')} nextLabel='Continue to medications' />
    </div>
  )
}
