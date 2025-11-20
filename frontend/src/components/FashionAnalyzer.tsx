import { useState, useRef, useCallback, useEffect } from 'react'
import axios from 'axios'
import { Send, Upload, X, Sparkles } from 'lucide-react'
import ImageUpload from './ImageUpload'
import ChatMessage from './ChatMessage'
import TypingIndicator from './TypingIndicator'

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
      text: 'Hi! I\'m your Fashion Analyzer AI! 👗✨ Upload photos of your outfits or ask me fashion questions - I\'m here to help you look amazing!',
      sender: 'bot',
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [uploadedImages, setUploadedImages] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
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
      } else {
        addMessage('I apologize, but I encountered an issue processing your request. Please try again!', 'bot')
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
    <div className="flex flex-col h-screen w-full bg-gradient-to-br from-rose-50 via-pink-50 to-rose-100">
      {/* Header - Fixed height, responsive */}
      <header className="flex-none bg-gradient-to-r from-[#6B1F1F] via-[#8B2F2F] to-[#6B1F1F] text-white shadow-xl">
        <div className="px-4 py-4 sm:px-6 sm:py-5">
          <div className="flex items-center justify-between">
            {/* Logo and Title */}
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-rose-200/30 backdrop-blur-sm rounded-full flex items-center justify-center border-2 border-rose-300/50">
                <Sparkles className="w-6 h-6 text-rose-100" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-rose-50">Fashion Analyzer AI</h1>
                <p className="text-sm text-rose-200 hidden sm:block">Your Personal AI Style Assistant</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Messages Area - Flexible height with proper scrolling */}
      <main className="flex-1 overflow-hidden flex flex-col bg-gradient-to-b from-transparent to-rose-50/30">
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
          <div className="flex-none px-4 py-3 bg-gradient-to-r from-rose-50 to-pink-100 border-t border-rose-200">
            <div className="flex items-center gap-2 mb-3">
              <Upload className="w-4 h-4 text-rose-700" />
              <span className="text-sm font-medium text-rose-900">
                {uploadedImages.length} image{uploadedImages.length > 1 ? 's' : ''} ready
              </span>
            </div>
            <div className="flex gap-2 overflow-x-auto pb-1">
              {uploadedImages.map((image, index) => (
                <div key={index} className="relative flex-none">
                  <img
                    src={image}
                    alt={`Upload ${index + 1}`}
                    className="w-16 h-16 sm:w-20 sm:h-20 object-cover rounded-lg border-2 border-rose-300 shadow-md"
                  />
                  <button
                    onClick={() => setUploadedImages(prev => prev.filter((_, i) => i !== index))}
                    className="absolute -top-2 -right-2 w-6 h-6 bg-[#8B2F2F] text-white rounded-full flex items-center justify-center hover:bg-[#6B1F1F] transition-colors shadow-lg"
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
      <footer className="flex-none bg-gradient-to-r from-rose-50 to-pink-100 border-t border-rose-200 shadow-xl">
        <div className="px-4 py-4 sm:px-6">
          {/* Mobile Layout */}
          <div className="sm:hidden">
            <div className="flex gap-2">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about fashion or upload photos..."
                className="flex-1 resize-none border-2 border-rose-200 rounded-xl px-3 py-2 text-sm focus:border-rose-400 focus:outline-none focus:ring-2 focus:ring-rose-200 transition-all bg-white"
                rows={2}
                disabled={isLoading}
              />
              <div className="flex flex-col gap-2">
                <ImageUpload onImagesSelected={handleImagesSelected} isMobile={true} />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || (!inputMessage.trim() && uploadedImages.length === 0)}
                  className="w-12 h-12 bg-gradient-to-r from-[#A85555] to-[#8B2F2F] text-white rounded-xl hover:from-[#8B2F2F] hover:to-[#6B1F1F] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center shadow-lg hover:shadow-xl"
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
                className="flex-1 resize-none border-2 border-rose-200 rounded-xl px-4 py-3 focus:border-rose-400 focus:outline-none focus:ring-2 focus:ring-rose-200 transition-all bg-white"
                rows={1}
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || (!inputMessage.trim() && uploadedImages.length === 0)}
                className="px-6 py-3 bg-gradient-to-r from-[#A85555] to-[#8B2F2F] text-white rounded-xl hover:from-[#8B2F2F] hover:to-[#6B1F1F] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center shadow-lg hover:shadow-xl font-medium"
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
          <div className="mt-3 text-center">
            <p className="text-xs text-rose-700">
              💡 Upload photos or ask questions like "Does this look good?" or "What should I wear?"
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default FashionAnalyzer
