import { useNavigate } from 'react-router-dom'
import { PrimaryButton } from '../components/PrimaryButton'

export default function SignUp() {
  const navigate = useNavigate()
  return (
    <div className='box-border flex h-[844px] w-[390px] flex-col overflow-hidden bg-cream font-sans text-slate'>
      <header className='rounded-b-[28px] bg-slate px-5 pb-20 pt-4 text-white'>
        <div className='flex justify-center'>
          <span className='flex items-center gap-1.5 text-[16px] font-semibold'>
            <svg className='h-5 w-5' viewBox='0 0 20 20' fill='none' aria-hidden='true'>
              <path d='M10 2 L17 5 V10 C17 14 14 17 10 18 C6 17 3 14 3 10 V5 Z' stroke='currentColor' strokeWidth='1.5'></path>
              <path d='M10 7 V13 M7 10 H13' stroke='currentColor' strokeWidth='1.5' strokeLinecap='round'></path>
            </svg>
            MedOracle
          </span>
        </div>
        <div className='mt-9 flex items-start justify-between gap-3 px-1'>
          <div>
            <h1 className='font-serif text-[44px] font-semibold leading-[48px]'>Sign Up</h1>
            <p className='mt-1 text-[20px] font-light text-white/85'>Create your account</p>
          </div>
          <button type='button' onClick={() => navigate('/login')} className='mt-1.5 flex h-9 shrink-0 items-center gap-1 rounded-full border border-white/40 bg-white/15 pl-2.5 pr-3 text-[12px] font-medium text-white'>
            <svg className='h-4 w-4' viewBox='0 0 24 24' fill='none' aria-hidden='true'>
              <g stroke='currentColor' strokeWidth='2' strokeLinecap='round' strokeLinejoin='round'>
                <path d='M19 12H5M11 6l-6 6 6 6'></path>
              </g>
            </svg>
            Back to login
          </button>
        </div>
      </header>
      <div className='relative z-10 -mt-8 flex flex-1 flex-col rounded-t-[32px] bg-sheet px-6 pb-8 pt-10 shadow-[0_-12px_28px_-16px_rgba(30,42,51,0.45)]'>
        <div className='flex flex-col gap-5'>
          <label className='flex h-14 items-center gap-3 rounded-full bg-surface px-5 text-slate shadow-[0_10px_22px_-12px_rgba(77,115,143,0.55),0_1px_3px_rgba(77,115,143,0.14)] ring-1 ring-slate/15 focus-within:ring-2 focus-within:ring-slate'>
            <span className='shrink-0'>
              <svg className='h-5 w-5' viewBox='0 0 24 24' fill='none' aria-hidden='true'>
                <g stroke='currentColor' strokeWidth='1.7' strokeLinecap='round' strokeLinejoin='round'>
                  <rect x='3.5' y='5.5' width='17' height='13' rx='3'></rect>
                  <path d='M4 8l8 5.5L20 8'></path>
                </g>
              </svg>
            </span>
            <input type='email' placeholder='name@example.com' aria-label='Email' autoComplete='email' className='min-w-0 flex-1 bg-transparent text-[15px] text-ink outline-none placeholder:text-slate/55' />
          </label>
          <label className='flex h-14 items-center gap-3 rounded-full bg-surface px-5 text-slate shadow-[0_10px_22px_-12px_rgba(77,115,143,0.55),0_1px_3px_rgba(77,115,143,0.14)] ring-1 ring-slate/15 focus-within:ring-2 focus-within:ring-slate'>
            <span className='shrink-0'>
              <svg className='h-5 w-5' viewBox='0 0 24 24' fill='none' aria-hidden='true'>
                <g stroke='currentColor' strokeWidth='1.7' strokeLinecap='round' strokeLinejoin='round'>
                  <rect x='5' y='10.5' width='14' height='9.5' rx='3'></rect>
                  <path d='M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5'></path>
                </g>
              </svg>
            </span>
            <input type='password' placeholder='Create password' aria-label='Password' autoComplete='new-password' className='min-w-0 flex-1 bg-transparent text-[15px] text-ink outline-none placeholder:text-slate/55' />
          </label>
          <label className='flex h-14 items-center gap-3 rounded-full bg-surface px-5 text-slate shadow-[0_10px_22px_-12px_rgba(77,115,143,0.55),0_1px_3px_rgba(77,115,143,0.14)] ring-1 ring-slate/15 focus-within:ring-2 focus-within:ring-slate'>
            <span className='shrink-0'>
              <svg className='h-5 w-5' viewBox='0 0 24 24' fill='none' aria-hidden='true'>
                <g stroke='currentColor' strokeWidth='1.7' strokeLinecap='round' strokeLinejoin='round'>
                  <rect x='5' y='10.5' width='14' height='9.5' rx='3'></rect>
                  <path d='M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5'></path>
                </g>
              </svg>
            </span>
            <input type='password' placeholder='Confirm password' aria-label='Confirm password' autoComplete='new-password' className='min-w-0 flex-1 bg-transparent text-[15px] text-ink outline-none placeholder:text-slate/55' />
          </label>
        </div>
        <div className='mt-6'>
          <PrimaryButton onClick={() => navigate('/dashboard')}>Sign Up</PrimaryButton>
        </div>
        <p className='mt-auto pt-6 text-center text-[12.5px] leading-5 text-slate/80'>
          By signing up, you agree to our <b className='font-semibold text-slate'>Terms</b> and <b className='font-semibold text-slate'>Privacy Policy</b>.
        </p>
      </div>
    </div>
  )
}

