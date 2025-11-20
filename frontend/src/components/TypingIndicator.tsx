import { Bot } from 'lucide-react'

const TypingIndicator = () => {
  return (
    <div className="flex justify-start mb-4">
      <div className="flex flex-row items-start space-x-3">
        {/* Avatar */}
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-500 to-purple-600 text-white flex items-center justify-center flex-shrink-0">
          <Bot className="w-5 h-5" />
        </div>

        {/* Typing Animation */}
        <div className="bg-white border border-gray-200 rounded-2xl px-6 py-4 shadow-sm">
          <div className="flex items-center space-x-1">
            <div className="text-sm text-gray-500 mr-2">Analyzing</div>
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TypingIndicator
