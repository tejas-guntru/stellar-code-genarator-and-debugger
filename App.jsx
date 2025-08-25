import { useState } from 'react'
import CodeContainer from './components/CodeContainer'
import OutputContainer from './components/OutputContainer'
import ChatContainer from './components/ChatContainer'
import Toast from './components/Toast'

function App() {
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('python')
  const [output, setOutput] = useState('')
  const [toast, setToast] = useState({ show: false, message: '', isError: false })

  const showToast = (message, isError = false) => {
    setToast({ show: true, message, isError })
    setTimeout(() => setToast({ ...toast, show: false }), 3000)
  }

  return (
    <div className="container">
      <CodeContainer 
        code={code} 
        language={language} 
        showToast={showToast} 
      />
      <div className="right-panel">
        <OutputContainer 
          code={code} 
          language={language} 
          output={output} 
        />
        <ChatContainer 
          setCode={setCode}
          setOutput={setOutput}
          language={language}
          setLanguage={setLanguage}
          showToast={showToast}
        />
      </div>
      <Toast toast={toast} />
    </div>
  )
}

export default App
