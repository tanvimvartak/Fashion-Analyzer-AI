import { Bot, User } from 'lucide-react'

interface Message {
  id: string
  text: string
  sender: 'user' | 'bot'
  images?: string[]
  timestamp: Date
}

interface ChatMessageProps {
  message: Message
}

const ChatMessage = ({ message }: ChatMessageProps) => {
  const isBot = message.sender === 'bot'

  const formatMessage = (text: string) => {
    // Convert markdown-style formatting to React elements
    const lines = text.split('\n')
    
    return lines.map((line, index) => {
      // Handle headers
      if (line.startsWith('**') && line.endsWith('**')) {
        return (
          <h4 key={index} className="font-bold text-lg mt-3 mb-2 text-gray-800">
            {line.slice(2, -2)}
          </h4>
        )
      }
      
      // Handle bullet points
      if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
        return (
          <li key={index} className="ml-4 mb-1 text-gray-700">
            {line.trim().substring(1).trim()}
          </li>
        )
      }
      
      // Handle bold text
      let formattedLine = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      
      // Handle italic text
      formattedLine = formattedLine.replace(/\*(.*?)\*/g, '<em>$1</em>')
      
      if (line.trim() === '') {
        return <br key={index} />
      }
      
      return (
        <p 
          key={index} 
          className="mb-2 text-gray-700 leading-relaxed"
          dangerouslySetInnerHTML={{ __html: formattedLine }}
        />
      )
    })
  }

  return (
    <div className={`flex ${isBot ? 'justify-start' : 'justify-end'} mb-4`}>
      <div className={`flex max-w-[80%] ${isBot ? 'flex-row' : 'flex-row-reverse'} items-start space-x-3`}>
        {/* Avatar */}
        <div className={`
          w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0
          ${isBot ? 'bg-gradient-to-br from-pink-500 to-purple-600 text-white' : 'bg-gray-200 text-gray-600'}
        `}>
          {isBot ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
        </div>

        {/* Message Content */}
        <div className={`
          rounded-2xl px-4 py-3 shadow-sm
          ${isBot 
            ? 'bg-white border border-gray-200' 
            : 'bg-gradient-to-br from-pink-500 to-purple-600 text-white'
          }
        `}>
          {/* Images */}
          {message.images && message.images.length > 0 && (
            <div className="mb-3">
              <div className="grid grid-cols-2 gap-2 max-w-xs">
                {message.images.map((image, index) => (
                  <img
                    key={index}
                    src={image}
                    alt={`Upload ${index + 1}`}
                    className="w-full h-32 object-cover rounded-lg border border-gray-200"
                  />
                ))}
              </div>
            </div>
          )}

          {/* Text Content */}
          {message.text && (
            <div className={`prose prose-sm max-w-none ${isBot ? 'text-gray-700' : 'text-white'}`}>
              {formatMessage(message.text)}
            </div>
          )}

          {/* Timestamp */}
          <div className={`text-xs mt-2 ${isBot ? 'text-gray-400' : 'text-pink-100'}`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatMessage
