import { useNavigate } from 'react-router-dom'
import { PrimaryButton } from '../components/PrimaryButton'

export default function Login() {
  const navigate = useNavigate()
  const handleLogin = () => {
    navigate('/dashboard')
  }
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
            <h1 className='font-serif text-[44px] font-semibold leading-[48px]'>Hello!</h1>
            <p className='mt-1 text-[20px] font-light text-white/85'>Welcome back</p>
          </div>
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
            <input type='email' placeholder='name@example.com' aria-label='Email' autoComplete='username' className='min-w-0 flex-1 bg-transparent text-[15px] text-ink outline-none placeholder:text-slate/55' />
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
            <input type='password' placeholder='Enter password' aria-label='Password' autoComplete='current-password' className='min-w-0 flex-1 bg-transparent text-[15px] text-ink outline-none placeholder:text-slate/55' />
          </label>
        </div>
        <div className='mt-3 text-right'>
          <button type='button' className='h-9 text-[13.5px] font-medium text-slate'>Forgot Password?</button>
        </div>
        <div className='mt-4'>
          <button type='button' onClick={handleLogin} className='flex h-14 w-full items-center justify-center rounded-full bg-terracotta text-[16px] font-semibold text-white shadow-[0_12px_22px_-10px_rgba(181,88,58,0.7)]'>Log In</button>
        </div>
        <div className='mt-8 flex items-center gap-3 text-[12.5px] text-slate/80'>
          <i className='h-px flex-1 bg-slate/20'></i>
          or continue with
          <i className='h-px flex-1 bg-slate/20'></i>
        </div>
        <div className='mt-4 flex gap-3'>
          <button type='button' className='flex h-12 flex-1 items-center justify-center gap-2.5 rounded-full bg-surface text-[14px] font-medium text-ink shadow-[0_8px_18px_-12px_rgba(77,115,143,0.55),0_1px_3px_rgba(77,115,143,0.14)] ring-1 ring-slate/15'>
            <span className='flex h-6 w-6 items-center justify-center rounded-full bg-slate/10 text-[12px] font-semibold text-slate'>G</span>
            Google
          </button>
          <button type='button' className='flex h-12 flex-1 items-center justify-center gap-2.5 rounded-full bg-surface text-[14px] font-medium text-ink shadow-[0_8px_18px_-12px_rgba(77,115,143,0.55),0_1px_3px_rgba(77,115,143,0.14)] ring-1 ring-slate/15'>
            <span className='flex h-6 w-6 items-center justify-center rounded-full bg-slate/10 text-[12px] font-semibold text-slate'>A</span>
            Apple
          </button>
        </div>
        <p className='mt-auto pt-6 text-center text-[14px] text-slate/85'>
          New to MedOracle? <button type='button' onClick={() => navigate('/signup')} className='font-semibold text-slate underline underline-offset-4'>Sign Up</button>
        </p>
      </div>
    </div>
  )
}
