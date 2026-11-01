import { useNavigate } from 'react-router-dom'
import { AppHeader } from '../components/AppHeader'
import { PrimaryButton } from '../components/PrimaryButton'

export default function Dashboard() {
  const navigate = useNavigate()
  return (
    <div className='min-h-screen bg-cream flex flex-col'>
      <AppHeader showSave={false} />
      <div className='px-5 pt-6 flex-1'>
        <h1 className='font-serif text-[28px] text-headerText'>Dashboard</h1>
        <p className='mt-2 text-[14px] text-headerText/80'>Welcome to MedOracle</p>
        <div className='mt-6'>
          <PrimaryButton onClick={() => navigate('/step/2a')}>Start New Assessment</PrimaryButton>
        </div>
      </div>
    </div>
  )
}
