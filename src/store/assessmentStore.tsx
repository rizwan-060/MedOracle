import React, { createContext, useContext, useState, useEffect } from 'react'

interface AssessmentData {
  conditions: string[]
  surgeries: any[]
  allergies: string[]
  medications: any[]
  familyRecords: any[]
  symptoms: string[]
  location: any[]
  severity: number
  duration: string
  triggers: string[]
  bodyMeasurements: any
  vitals: any
  labValues: any
  labRecordDetails: any
}

interface AssessmentStore {
  data: AssessmentData
  updateData: (updates: Partial<AssessmentData>) => void
}

const defaultData: AssessmentData = {
  conditions: [],
  surgeries: [],
  allergies: [],
  medications: [],
  familyRecords: [],
  symptoms: [],
  location: [],
  severity: 6,
  duration: '',
  triggers: [],
  bodyMeasurements: {},
  vitals: {},
  labValues: {},
  labRecordDetails: {},
}

const AssessmentStoreContext = createContext<AssessmentStore | null>(null)

export function AssessmentStoreProvider({ children }: { children: React.ReactNode }) {
  const [data, setData] = useState<AssessmentData>(() => {
    const saved = localStorage.getItem('medoracle-assessment')
    if (saved) {
      try {
        return { ...defaultData, ...JSON.parse(saved) }
      } catch {
        return defaultData
      }
    }
    return defaultData
  })

  useEffect(() => {
    localStorage.setItem('medoracle-assessment', JSON.stringify(data))
  }, [data])

  const updateData = (updates: Partial<AssessmentData>) => {
    setData(prev => ({ ...prev, ...updates }))
  }

  return (
    <AssessmentStoreContext.Provider value={{ data, updateData }}>
      {children}
    </AssessmentStoreContext.Provider>
  )
}

export function useAssessmentStore() {
  const context = useContext(AssessmentStoreContext)
  if (!context) throw new Error('useAssessmentStore must be used within AssessmentStoreProvider')
  return context
}
