import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import SignUp from './pages/SignUp'
import Dashboard from './pages/Dashboard'
import Step2AEmpty from './pages/Step2AEmpty'
import Step2B from './pages/Step2B'
import Step3 from './pages/Step3'
import Step4 from './pages/Step4'
import Step5 from './pages/Step5'
import Components from './pages/Components'
import ResultsReports from './pages/ResultsReports'
import { AssessmentStoreProvider } from './store/assessmentStore'

function App() {
  return (
    <AssessmentStoreProvider>
      <BrowserRouter>
        <div className=\"min-h-screen bg-cream flex justify-center\">
          <div className=\"w-[390px] min-h-screen bg-cream relative\">
            <Routes>
              <Route path=\"/\" element={<Navigate to=\"/login\" replace />} />
              <Route path=\"/login\" element={<Login />} />
              <Route path=\"/signup\" element={<SignUp />} />
              <Route path=\"/dashboard\" element={<Dashboard />} />
              <Route path=\"/step/2a\" element={<Step2AEmpty />} />
              <Route path=\"/step/2b\" element={<Step2B />} />
              <Route path=\"/step/3\" element={<Step3 />} />
              <Route path=\"/step/4\" element={<Step4 />} />
              <Route path=\"/step/5\" element={<Step5 />} />
              <Route path=\"/dev/components\" element={<Components />} />
            </Routes>
          </div>
        </div>
      </BrowserRouter>
    </AssessmentStoreProvider>
  )
}

export default App
              <Route path='/results/reports' element={<ResultsReports />} />
