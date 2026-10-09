import React, { useState, useRef, useEffect } from 'react';
import { Bot, X, Send } from 'lucide-react';
import api from '../services/api';

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Hello, I am the SAHYAT AI Assistant. How can I help you with disaster reunification today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!input.trim()) return;

    const userText = input.trim();
    setMessages(prev => [...prev, { role: 'user', text: userText }]);
    setInput('');
    setLoading(true);

    try {
      const match = window.location.pathname.match(/\/cases\/(VRN-\d+)/);
      const vrn = match ? match[1] : null;

      const res = await api.post('/chatbot/message', {
        message: userText,
        case_vrn: vrn
      });
      
      setMessages(prev => [...prev, { role: 'assistant', text: res.data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', text: 'Sorry, I am having trouble connecting right now.' }]);
    } finally {
      setLoading(false);
    }
  };

  const suggestions = [
    "What is SAHYAT?",
    "How does AI matching work?",
    "How do I report a missing person?",
    "How does verification work?",
    "Show my cases."
  ];

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-xl hover:bg-blue-700 transition-colors"
      >
        <Bot className="h-6 w-6" />
      </button>

      {isOpen && (
        <div className="fixed bottom-24 right-6 flex h-[500px] w-[350px] flex-col overflow-hidden rounded-2xl bg-white shadow-2xl border border-gray-200">
          <div className="flex items-center justify-between bg-blue-600 p-4 text-white">
            <h3 className="font-semibold">SAHYAT AI Assistant</h3>
            <button onClick={() => setIsOpen(false)}><X className="h-5 w-5" /></button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
            {messages.map((msg, i) => (
              <div key={i} className={`max-w-[80%] rounded-xl p-3 text-sm ${msg.role === 'user' ? 'bg-blue-600 text-white self-end' : 'bg-gray-100 text-gray-900 self-start'}`}>
                {msg.text}
              </div>
            ))}
            {loading && (
              <div className="max-w-[80%] rounded-xl p-3 text-sm bg-gray-100 text-gray-900 self-start">
                Thinking...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-2 overflow-x-auto whitespace-nowrap hide-scrollbar flex gap-2">
            {suggestions.map((sug, i) => (
              <button 
                key={i}
                onClick={() => setInput(sug)}
                className="inline-block rounded-full bg-blue-50 px-3 py-1 text-xs text-blue-600 hover:bg-blue-100"
              >
                {sug}
              </button>
            ))}
          </div>
          
          <form onSubmit={handleSend} className="border-t p-3 flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything..."
              className="flex-1 rounded-lg bg-gray-100 px-3 py-2 text-sm focus:outline-none"
            />
            <button type="submit" disabled={!input.trim() || loading} className="rounded-lg bg-blue-600 p-2 text-white disabled:bg-blue-300">
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
