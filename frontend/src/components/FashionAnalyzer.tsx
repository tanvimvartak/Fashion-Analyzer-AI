import { useState, useRef, useCallback } from 'react'
import axios from 'axios'
import { Send, Upload, X, Maximize2, Minimize2, Sparkles } from 'lucide-react'
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

const API_BASE_URL = 'http://localhost:8000'

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
  const [isFullscreen, setIsFullscreen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

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
    setTimeout(scrollToBottom, 100)
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
        timeout: 30000,
      })

      if (response.data.response) {
        addMessage(response.data.response, 'bot')
      } else {
        addMessage('I apologize, but I encountered an issue processing your request. Please try again!', 'bot')
      }
    } catch (error) {
      console.error('Chat error:', error)
      
      // Fallback response for network/server errors
      let fallbackResponse = "I'm having trouble connecting to my analysis service right now. Here's some general fashion advice:\n\n"
      
      if (userMessage.toLowerCase().includes('cute')) {
        fallbackResponse += "**Cute Outfit Ideas! 🎀**\n\n• Pastel sweater + high-waisted jeans + white sneakers\n• Floral dress + denim jacket + ankle boots\n• Keep colors soft and add cute accessories!\n\nYou're going to look adorable! 💕"
      } else if (userMessage.toLowerCase().includes('party')) {
        fallbackResponse += "**Party Perfect! 🎉**\n\n• Sequin top + black pants + heels\n• Little black dress + statement jewelry\n• Bold makeup and confidence!\n\nDance the night away! ✨"
      } else {
        fallbackResponse += "**General Fashion Tips:**\n\n• Balance proportions (fitted + loose)\n• Stick to 2-3 colors max\n• Confidence is your best accessory!\n\nFeel free to ask more specific questions! 💕"
      }
      
      addMessage(fallbackResponse, 'bot')
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

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
  }

  const handleImagesSelected = (images: string[]) => {
    setUploadedImages(images)
  }

  return (
    <div className={`flex flex-col transition-all duration-300 ${
      isFullscreen 
        ? 'fixed inset-0 z-50 bg-white' 
        : 'max-w-4xl mx-auto my-8 bg-white rounded-2xl shadow-2xl overflow-hidden'
    }`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-pink-500 to-purple-600 text-white p-6 relative">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-pink-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Fashion Analyzer AI</h1>
              <p className="text-pink-100 text-sm">Your personal styling assistant</p>
            </div>
          </div>
          <button
            onClick={toggleFullscreen}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            title={isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}
          >
            {isFullscreen ? (
              <Minimize2 className="w-5 h-5" />
            ) : (
              <Maximize2 className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 min-h-[400px] max-h-[500px]">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        
        {isLoading && <TypingIndicator />}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Image Upload Area */}
      {uploadedImages.length > 0 && (
        <div className="p-4 bg-gray-50 border-t">
          <div className="flex items-center space-x-2 mb-2">
            <Upload className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">Uploaded Images ({uploadedImages.length})</span>
          </div>
          <div className="flex space-x-2 overflow-x-auto">
            {uploadedImages.map((image, index) => (
              <div key={index} className="relative flex-shrink-0">
                <img
                  src={image}
                  alt={`Upload ${index + 1}`}
                  className="w-20 h-20 object-cover rounded-lg border-2 border-gray-200"
                />
                <button
                  onClick={() => setUploadedImages(prev => prev.filter((_, i) => i !== index))}
                  className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="p-6 bg-gray-50 border-t">
        <div className="flex space-x-4">
          <ImageUpload onImagesSelected={handleImagesSelected} />
          
          <div className="flex-1 flex space-x-2">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about fashion, upload outfit photos, or get styling advice..."
              className="flex-1 resize-none border-2 border-gray-200 rounded-xl px-4 py-3 focus:border-pink-500 focus:outline-none transition-colors"
              rows={2}
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || (!inputMessage.trim() && uploadedImages.length === 0)}
              className="px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-xl hover:from-pink-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center min-w-[80px]"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
        
        <div className="mt-3 text-xs text-gray-500 text-center">
          💡 Tip: Upload multiple outfit photos or ask questions like "Does this look good together?" or "What should I wear to a party?"
        </div>
      </div>
    </div>
  )
}

export default FashionAnalyzer
