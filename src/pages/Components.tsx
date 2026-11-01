import { AppHeader } from '../components/AppHeader'
import { ProgressBar } from '../components/ProgressBar'
import { PrimaryButton } from '../components/PrimaryButton'
import { SecondaryButton } from '../components/SecondaryButton'
import { StepFooter } from '../components/StepFooter'
import { PillInput } from '../components/PillInput'
import { Chip } from '../components/Chip'
import { Stepper } from '../components/Stepper'
import { AccordionCard } from '../components/AccordionCard'
import { Drawer } from '../components/Drawer'
import { PileCard } from '../components/PileCard'
import { ReviewCard } from '../components/ReviewCard'
import { DeckProgress } from '../components/DeckProgress'
import { useState } from 'react'

export default function Components() {
  const [drawerOpen, setDrawerOpen] = useState(false)
  return (
    <div className='min-h-screen bg-cream pb-10'>
      <div className='px-5 pt-6'>
        <h1 className='font-serif text-[28px] text-headerText mb-6'>Components</h1>
        
        <section className='mb-8'>
          <h2 className='text-[18px] font-semibold text-ink mb-3 font-serif'>AppHeader</h2>
          <AppHeader />
          <div className='mt-2'><AppHeader showBack onBack={() => {}} /></div>
        </section>

        <section className='mb-8'>
          <h2 className='text-[18px] font-semibold text-ink mb-3 font-serif'>ProgressBar (5 segments)</h2>
          <ProgressBar currentStep={1} />
          <ProgressBar currentStep={3} />
          <ProgressBar currentStep={5} />
        </section>

        <section className='mb-8'>
          <h2 className='text-[18px] font-semibold text-ink mb-3 font-serif'>PrimaryButton</h2>
          <PrimaryButton>Primary Action</PrimaryButton>
          <div className='mt-2'><PrimaryButton disabled>Disabled</PrimaryButton></div>
        </section>

        <section className='mb-8'>
          <h2 className='text-[18px] font-semibold text-ink mb-3 font-serif'>SecondaryButton</h2>
          <SecondaryButton>Secondary Action</SecondaryButton>
        </section>

        <section className='mb-8'>
          <h2 className='text-[18px] font-semibold text-ink mb-3 font-serif'>StepFooter</h2>
          <StepFooter onBack={() => {}} onNext={() => {}} />
          <div className='mt-2'><StepFooter showBack={false} onNext={() => {}} /></div>
        </section>

        <section className='mb-8'>
          <h2 className='text-[18px] font-semibold text-ink mb-3 font-serif'>PillInput</h2>
          <PillInput placeholder='Enter text...' />
        </section>

        <section className='mb-8'>
          <h2 className='text-[18px] font-semibold text-ink mb-3 font-serif'>Chip</h2>
          <div className='flex gap-2 flex-wrap'>
            <Chip label='Default' />
            <Chip label='Selected' selected />
          </div>
        </section>

        <section className='mb-8'>
          <h2 className='text-[18px] font-semibold text-ink mb-3 font-serif'>Stepper</h2>
          <Stepper steps={['A', 'B', 'C']} currentStep={2} />
        </section>

        <section className='mb-8'>
          <h2 className='text-[18px] font-semibold text-ink mb-3 font-serif'>AccordionCard</h2>
          <AccordionCard title='Section Title' defaultOpen>
            <p className='text-[13px] text-ink'>Content here</p>
          </AccordionCard>
        </section>

        <section className='mb-8'>
          <h2 className='text-[18px] font-semibold text-ink mb-3 font-serif'>Drawer</h2>
          <PrimaryButton onClick={() => setDrawerOpen(true)}>Open Drawer</PrimaryButton>
          <Drawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} title='Drawer'>
            <p className='text-[13px] text-ink'>Drawer content</p>
          </Drawer>
        </section>

        <section className='mb-8'>
          <h2 className='text-[18px] font-semibold text-ink mb-3 font-serif'>PileCard</h2>
          <PileCard title='Medications' items={['Amlodipine 5mg', 'Metformin 500mg']} />
        </section>

        <section className='mb-8'>
          <h2 className='text-[18px] font-semibold text-ink mb-3 font-serif'>ReviewCard</h2>
          <ReviewCard title='Symptoms' subtitle='From Step 3'>
            <p className='text-[13px] text-ink'>Review content</p>
          </ReviewCard>
        </section>

        <section className='mb-8'>
          <h2 className='text-[18px] font-semibold text-ink mb-3 font-serif'>DeckProgress</h2>
          <DeckProgress current={2} total={5} />
        </section>
      </div>
    </div>
  )
}
