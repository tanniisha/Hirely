import { useState, useRef, useEffect } from 'react'
import './index.css'

function App() {
  const [file, setFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [resumeText, setResumeText] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [speechSupported, setSpeechSupported] = useState(true)

  const fileInputRef = useRef(null)
  const messagesEndRef = useRef(null)
  const mediaRecorder = useRef(null)
  const audioChunks = useRef([])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setSpeechSupported(false)
    }

    if ('speechSynthesis' in window) {
      window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices()
      }
    }
  }, [])

  const speakMessage = (text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      const voices = window.speechSynthesis.getVoices()
      const voice = voices.find(v => v.lang.startsWith('en') && v.name.toLowerCase().includes('female'))
        || voices.find(v => v.lang.startsWith('en'))
      if (voice) utterance.voice = voice
      window.speechSynthesis.speak(utterance)
    }
  }

  const toggleListening = async () => {
    if (isListening) {
      if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
        mediaRecorder.current.stop()
      }
      setIsListening(false)
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        mediaRecorder.current = new MediaRecorder(stream)
        audioChunks.current = []

        mediaRecorder.current.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunks.current.push(event.data)
          }
        }

        mediaRecorder.current.onstop = async () => {
          const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' })
          const audioFile = new File([audioBlob], "recording.webm", { type: 'audio/webm' })
          
          setIsLoading(true)
          const formData = new FormData()
          formData.append('file', audioFile)

          try {
            const response = await fetch('http://localhost:5000/api/resume-chat/transcribe', {
              method: 'POST',
              body: formData,
            })
            const data = await response.json()
            if (response.ok) {
              setInputValue((prev) => (prev + ' ' + data.transcript).trim())
            } else {
              console.error('Transcription error:', data.error)
              alert('Error transcribing audio. Please try again.')
            }
          } catch (error) {
            console.error('Error uploading audio:', error)
          } finally {
            setIsLoading(false)
            stream.getTracks().forEach(track => track.stop())
          }
        }

        mediaRecorder.current.start()
        setIsListening(true)
      } catch (error) {
        console.error('Error accessing microphone:', error)
        alert('Could not access microphone. Please check permissions.')
        setIsListening(false)
      }
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile)
      } else {
        alert('Please upload a PDF file')
      }
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setIsLoading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {


      const response = await fetch('http://localhost:5000/api/resume-chat/upload', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (response.ok) {
        setResumeText(data.resume_text)
        setMessages([{ role: 'model', text: data.message }])
        speakMessage(data.message)
      } else {
        alert(data.error || 'Failed to upload resume')
        setFile(null)
      }
    } catch (error) {
      console.error('Error uploading:', error)
      alert('Error connecting to the server. Make sure the backend is running.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !resumeText || isLoading) return

    const userMessage = { role: 'user', text: inputValue }
    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:5000/api/resume-chat/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_text: resumeText,
          history: newMessages,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setMessages([...newMessages, { role: 'model', text: data.message }])
        speakMessage(data.message)
      } else {
        alert(data.error || 'Failed to send message')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      alert('Error connecting to the server.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app-container">
      <div className="header">
        <h1>HIRELY</h1>
        <p>Start your test.</p>
      </div>

      <div className="glass-panel">
        {!resumeText ? (
          <div
            className={`upload-area ${isDragging ? 'drag-active' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              accept=".pdf"
              onChange={handleFileChange}
            />
            <div className="upload-icon">📄</div>
            <h3>{file ? file.name : 'Drag & drop your resume PDF here'}</h3>
            <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem', fontSize: '0.9rem' }}>
              {file ? 'Click upload to begin' : 'or click to browse'}
            </p>
            {file && (
              <button
                className="upload-btn"
                onClick={(e) => {
                  e.stopPropagation()
                  handleUpload()
                }}
                disabled={isLoading}
              >
                {isLoading ? <span className="loader"></span> : 'Start Interview'}
              </button>
            )}
            {isLoading && !file && (
              <div style={{ marginTop: '1.5rem' }}><span className="loader"></span></div>
            )}
          </div>
        ) : (
          <div className="chat-container">
            <div className="chat-messages">
              {messages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role === 'user' ? 'user' : 'ai'}`}>
                  <div className="message-bubble">
                    {msg.text}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message ai">
                  <div className="message-bubble" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span className="loader" style={{ width: '15px', height: '15px', borderWidth: '2px' }}></span>
                    <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Thinking...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            <div className="input-area">
              <input
                type="text"
                className="chat-input"
                placeholder="Type your answer..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSendMessage()
                }}
                disabled={isLoading}
              />
              {speechSupported && (
                <button
                  className={`mic-btn ${isListening ? 'listening' : ''}`}
                  onClick={toggleListening}
                  title={isListening ? "Stop listening" : "Start listening"}
                >
                  {isListening ? '🛑' : '🎤'}
                </button>
              )}
              <button
                className="send-btn"
                onClick={handleSendMessage}
                disabled={isLoading || !inputValue.trim()}
              >
                ➤
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
