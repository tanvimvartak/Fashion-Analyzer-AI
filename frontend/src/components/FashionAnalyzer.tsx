import { useState, useRef, useCallback, useEffect } from 'react'
import axios from 'axios'
import { Send, Upload, X, Sparkles } from 'lucide-react'
import ImageUpload from './ImageUpload'
import ChatMessage from './ChatMessage'
import TypingIndicator from './TypingIndicator'
import Toast from './Toast'

interface Message {
  id: string
  text: string
  sender: 'user' | 'bot'
  images?: string[]
  timestamp: Date
}

interface ChatRequest {
  message: string
  images?: string[]
}

interface ChatResponse {
  response: string
  status: string
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const FashionAnalyzer = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: '✨ Welcome to Stylette! I\'m your AI fashion stylist. Upload outfit photos or ask me fashion questions - I\'m here to help you look absolutely stunning! 👗✨',
      sender: 'bot',
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [uploadedImages, setUploadedImages] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'error' | 'info' } | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Cleanup fullscreen state on unmount
  useEffect(() => {
    return () => {
      // Reset body overflow when component unmounts
      document.body.style.overflow = ''
    }
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const addMessage = useCallback((text: string, sender: 'user' | 'bot', images?: string[]) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender,
      images,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newMessage])
    // Only auto-scroll for user messages, not bot responses
    if (sender === 'user') {
      setTimeout(scrollToBottom, 100)
    }
  }, [])

  const sendMessage = async () => {
    if (!inputMessage.trim() && uploadedImages.length === 0) return

    const userMessage = inputMessage.trim()
    const messagesToSend = uploadedImages.length > 0 ? [...uploadedImages] : undefined

    // Add user message
    addMessage(userMessage || 'Image analysis', 'user', messagesToSend)
    
    setInputMessage('')
    setUploadedImages([])
    setIsLoading(true)

    try {
      const requestData: ChatRequest = {
        message: userMessage || 'Analyze this outfit and give me styling advice',
        images: messagesToSend
      }

      const response = await axios.post<ChatResponse>(`${API_BASE_URL}/api/chat`, requestData, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 120000, // Increased to 120 seconds for image processing and dataset analysis
      })

      if (response.data.response) {
        addMessage(response.data.response, 'bot')
        setToastMessage({ text: '✨ Stylette Analysis Complete!', type: 'success' })
        setTimeout(scrollToBottom, 100)
      } else {
        addMessage('I apologize, but I encountered an issue processing your request. Please try again!', 'bot')
        setToastMessage({ text: '⚠️ No analysis received', type: 'error' })
      }
    } catch (error) {
      console.error('Chat error:', error)
      
      let errorMessage = "I'm having trouble connecting to my analysis service right now."
      
      if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNABORTED') {
          errorMessage += " The request timed out - fashion analysis can take a moment with images."
        } else if (error.response?.status === 404) {
          errorMessage += " The service appears to be unavailable."
        } else if ((error.response?.status ?? 0) >= 500) {
          errorMessage += " There's a server issue - please try again later."
        }
      }
      
      errorMessage += " Here's some general fashion advice:\n\n"
      
      if (userMessage.toLowerCase().includes('cute')) {
        errorMessage += "**Cute Outfit Ideas! 🎀**\n\n• Pastel sweater + high-waisted jeans + white sneakers\n• Floral dress + denim jacket + ankle boots\n• Keep colors soft and add cute accessories!\n\nYou're going to look adorable! 💕"
      } else if (userMessage.toLowerCase().includes('party')) {
        errorMessage += "**Party Perfect! 🎉**\n\n• Sequin top + black pants + heels\n• Little black dress + statement jewelry\n• Bold makeup and confidence!\n\nDance the night away! ✨"
      } else {
        errorMessage += "**General Fashion Tips:**\n\n• Balance proportions (fitted + loose)\n• Stick to 2-3 colors max\n• Confidence is your best accessory!\n\nFeel free to ask more specific questions! 💕"
      }
      
      addMessage(errorMessage, 'bot')
      setToastMessage({ text: '⚠️ Stylette Connection Issue', type: 'error' })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }


  const handleImagesSelected = (images: string[]) => {
    setUploadedImages(images)
  }

  return (
    <div className="flex flex-col h-screen w-full bg-gradient-to-br from-rose-100 via-purple-100 to-sky-100 animate-gradient">
      {/* Header - Fixed height, responsive */}
      <header className="flex-none text-gray-800 shadow-sm bg-white/30 backdrop-blur-md border-b border-white/20">
        <div className="px-4 py-3 sm:px-6 sm:py-4">
          <div className="flex items-center justify-between">
            {/* Logo and Title */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white/80 backdrop-blur-sm rounded-full flex items-center justify-center border border-white/50 shadow-sm">
                <Sparkles className="w-5 h-5 text-pink-600" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight text-gray-900">Stylette</h1>
                <p className="text-sm text-gray-600 hidden sm:block">Your AI Fashion Stylist</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Messages Area - Flexible height with proper scrolling */}
      <main className="flex-1 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto px-4 py-4 sm:px-6 space-y-4">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <TypingIndicator />
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Image Upload Preview - Collapsible */}
        {uploadedImages.length > 0 && (
          <div className="flex-none px-4 py-3 bg-gray-50 border-t border-gray-200">
            <div className="flex items-center gap-2 mb-3">
              <Upload className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">
                {uploadedImages.length} image{uploadedImages.length > 1 ? 's' : ''} ready
              </span>
            </div>
            <div className="flex gap-2 overflow-x-auto pb-1">
              {uploadedImages.map((image, index) => (
                <div key={index} className="relative flex-none">
                  <img
                    src={image}
                    alt={`Upload ${index + 1}`}
                    className="w-16 h-16 sm:w-20 sm:h-20 object-cover rounded-lg border-2 border-gray-300 shadow-sm"
                  />
                  <button
                    onClick={() => setUploadedImages(prev => prev.filter((_, i) => i !== index))}
                    className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors shadow-lg"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Input Area - Fixed at bottom, responsive */}
      <footer className="flex-none bg-white/80 backdrop-blur-md border-t border-white/20 shadow-lg">
        <div className="px-4 py-4 sm:px-6">
          {/* Mobile Layout */}
          <div className="sm:hidden">
            <div className="flex gap-2">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about fashion or upload photos..."
                className="flex-1 resize-none border-2 border-gray-200 rounded-xl px-3 py-2 text-sm focus:border-pink-500 focus:outline-none focus:ring-2 focus:ring-pink-200 transition-all"
                rows={2}
                disabled={isLoading}
              />
              <div className="flex flex-col gap-2">
                <ImageUpload onImagesSelected={handleImagesSelected} isMobile={true} />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || (!inputMessage.trim() && uploadedImages.length === 0)}
                  className="w-12 h-12 text-white rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center shadow-lg hover:shadow-xl bg-gradient-to-r from-pink-500 to-purple-600"
                >
                  {isLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Desktop Layout */}
          <div className="hidden sm:flex items-end gap-4">
            <div className="flex-none">
              <ImageUpload onImagesSelected={handleImagesSelected} />
            </div>
            <div className="flex-1 flex gap-3">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about fashion, upload outfit photos, or get styling advice..."
                className="flex-1 resize-none border-2 border-gray-200 rounded-xl px-4 py-3 focus:border-pink-500 focus:outline-none focus:ring-2 focus:ring-pink-200 transition-all"
                rows={1}
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || (!inputMessage.trim() && uploadedImages.length === 0)}
                className="px-6 py-3 text-white rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center shadow-lg hover:shadow-xl font-medium bg-gradient-to-r from-pink-500 to-purple-600"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          {/* Tips */}
          <div className="mt-3 text-center space-y-1">
            <p className="text-xs text-gray-500">
              💡 Stylette Tip: Upload photos or ask questions like "Does this look good?" or "What should I wear?"
            </p>
            <p className="text-[10px] text-gray-400 font-medium tracking-wider">
              CREATED BY RADHE
            </p>
          </div>
        </div>
      </footer>

      {/* Toast Notification */}
      {toastMessage && (
        <Toast
          message={toastMessage.text}
          type={toastMessage.type}
          duration={3000}
          onClose={() => setToastMessage(null)}
        />
      )}
    </div>
  )
}

export default FashionAnalyzer
