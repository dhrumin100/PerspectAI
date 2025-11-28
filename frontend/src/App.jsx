import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_URL = 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    
    // Add user message to chat
    const newUserMessage = { role: 'user', content: userMessage }
    setMessages(prev => [...prev, newUserMessage])
    setLoading(true)

    try {
      // Build conversation history (exclude the message we just added, we'll send it separately)
      const history = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      // Call chat API
      const response = await axios.post(`${API_URL}/api/chat`, {
        message: userMessage,
        conversation_history: history
      })

      // Add AI response to chat
      const aiMessage = {
        role: 'assistant',
        content: response.data.response,
        sources: response.data.sources || [],
        has_grounding: response.data.has_grounding || false
      }
      
      setMessages(prev => [...prev, aiMessage])
    } catch (err) {
      console.error('Error:', err)
      // Add error message
      const errorMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${err.response?.data?.detail || err.message}`,
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([])
  }

  return (
    <div className="app-container">
      <div className="chat-container">
        {/* Header */}
        <header className="chat-header">
          <div className="header-content">
            <h1 className="chat-title">
              <span className="gradient-text">PerspectAI</span>
            </h1>
            <p className="chat-subtitle">AI-Powered Fact-Checking with Grounded Search</p>
          </div>
          {messages.length > 0 && (
            <button onClick={clearChat} className="clear-button">
              Clear Chat
            </button>
          )}
        </header>

        {/* Messages Area */}
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <div className="welcome-content">
                <div className="ai-icon">🤖</div>
                <h2>Welcome to PerspectAI</h2>
                <p>Your intelligent assistant for fact-checking and research</p>
                
                <div className="example-prompts">
                  <h3>Try asking:</h3>
                  <button 
                    className="example-prompt"
                    onClick={() => setInput("Is the Earth flat?")}
                  >
                    "Is the Earth flat?"
                  </button>
                  <button 
                    className="example-prompt"
                    onClick={() => setInput("What caused the 2024 global tech outage?")}
                  >
                    "What caused the 2024 global tech outage?"
                  </button>
                  <button 
                    className="example-prompt"
                    onClick={() => setInput("Tell me about recent climate change news")}
                  >
                    "Tell me about recent climate change news"
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="messages-list">
              {messages.map((message, index) => (
                <div key={index} className={`message ${message.role}`}>
                  <div className="message-avatar">
                    {message.role === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="message-content">
                    <div className="message-text">
                      {message.content}
                    </div>
                    
                    {/* Show sources if available */}
                    {message.sources && message.sources.length > 0 && (
                      <div className="message-sources">
                        <div className="sources-header">
                          <span className="sources-icon">🔗</span>
                          <span className="sources-label">Sources ({message.sources.length})</span>
                        </div>
                        <div className="sources-list">
                          {message.sources.map((source, idx) => (
                            <a 
                              key={idx}
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="source-link"
                            >
                              <div className="source-number">{idx + 1}</div>
                              <div className="source-info">
                                <div className="source-title">
                                  {source.title || 'Source'}
                                </div>
                                <div className="source-url">
                                  {new URL(source.url).hostname}
                                </div>
                              </div>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    {message.isError && (
                      <div className="error-indicator">⚠️ Error</div>
                    )}
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="message assistant">
                  <div className="message-avatar">🤖</div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="input-container">
          <form onSubmit={handleSubmit} className="input-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything..."
              className="chat-input"
              disabled={loading}
              autoFocus
            />
            <button 
              type="submit" 
              className="send-button"
              disabled={loading || !input.trim()}
            >
              {loading ? '⏳' : '➤'}
            </button>
          </form>
          <div className="input-footer">
            <span className="powered-by">Powered by Gemini with Grounded Search</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
