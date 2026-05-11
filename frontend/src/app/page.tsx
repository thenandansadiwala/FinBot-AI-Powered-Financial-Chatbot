"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function ChatInterface() {
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; content: string }[]>([]);
  const [workingSymbols, setWorkingSymbols] = useState<string[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea as user types
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      const newHeight = Math.min(textarea.scrollHeight, 160); // Cap at 160px
      textarea.style.height = `${newHeight}px`;
    }
  }, [input]);

  // Auto-scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: "user" as const, content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage.content,
          working_ticker_symbols: workingSymbols,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to communicate with API");
      }

      const data = await response.json();
      
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
      setWorkingSymbols(data.updated_symbols || []);
      
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ Sorry, there was an error processing your request. Ensure FastAPI is running on port 8000." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-neutral-900 text-neutral-100 font-sans selection:bg-indigo-500 selection:text-white">
      
      {/* Sidebar Area */}
      <div className="hidden md:flex flex-col w-72 bg-neutral-950 border-r border-neutral-800 p-6 shadow-xl z-10">
        <div className="flex items-center gap-3 mb-10">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <span className="text-white font-bold">AI</span>
          </div>
          <h1 className="text-xl font-semibold tracking-tight text-white">FinBot</h1>
        </div>
        
        <h2 className="text-xs uppercase tracking-wider text-neutral-500 font-bold mb-4">Active Context</h2>
        
        <div className="flex-1 overflow-y-auto pr-2">
          {workingSymbols.length === 0 ? (
            <div className="text-sm text-neutral-600 italic p-4 bg-neutral-900 rounded-xl border border-dashed border-neutral-800">
              No active funds in context. Ask a query to load funds!
            </div>
          ) : (
            <div className="space-y-2">
              {workingSymbols.map((symbol) => (
                <div 
                  key={symbol} 
                  className="px-4 py-3 bg-neutral-900 border border-neutral-800 rounded-xl flex items-center justify-between group hover:border-indigo-500/50 transition-colors"
                >
                  <span className="font-medium text-neutral-200">{symbol}</span>
                  <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative bg-[#0a0a0a]">
        {/* Mobile Header */}
        <div className="md:hidden p-4 border-b border-neutral-800 flex items-center gap-3 bg-neutral-950 sticky top-0 z-20 shadow-md">
           <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center">
            <span className="text-white font-bold text-sm">AI</span>
          </div>
          <h1 className="text-lg font-semibold">FinBot</h1>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scroll-smooth scrollbar-hide">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center px-4 max-w-lg mx-auto">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-500 mb-6 flex items-center justify-center shadow-2xl shadow-indigo-500/20">
                <span className="text-2xl">📈</span>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Financial Intelligence</h2>
              <p className="text-neutral-400">
                Ask me about fund metrics, expense ratios, historical NAVs, or discover thematic strategies.
              </p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-in fade-in slide-in-from-bottom-4 duration-300`}>
              <div 
                className={`max-w-[85%] md:max-w-[75%] rounded-2xl px-5 py-4 ${
                  msg.role === "user" 
                    ? "bg-indigo-600 text-white rounded-br-none shadow-lg shadow-indigo-900/20" 
                    : "bg-neutral-900 border border-neutral-800 text-neutral-200 rounded-bl-none shadow-xl"
                }`}
              >
                <div className="prose prose-invert max-w-none text-sm md:text-base prose-p:leading-relaxed prose-headings:mb-4">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start animate-in fade-in duration-300">
              <div className="bg-neutral-900 border border-neutral-800 rounded-2xl rounded-bl-none px-6 py-5 shadow-xl flex gap-2 items-center">
                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce"></div>
                <span className="ml-3 text-sm text-neutral-400 font-medium tracking-wide uppercase">Analyzing Data...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} className="h-4" />
        </div>

        {/* Input Area */}
        <div className="p-4 md:p-6 bg-gradient-to-t from-[#0a0a0a] via-[#0a0a0a] to-transparent pt-10">
          <form 
            onSubmit={handleSubmit} 
            className="max-w-4xl mx-auto relative group flex items-center"
          >
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e as any);
                }
              }}
              placeholder="Ask about funds, metrics, or themes..."
              className="w-full bg-neutral-900 border border-neutral-700 text-white placeholder-neutral-500 rounded-2xl pl-6 pr-16 py-4 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all shadow-xl resize-none overflow-y-auto block scrollbar-hide"
              rows={1}
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-3 bottom-3 w-10 h-10 flex items-center justify-center bg-indigo-600 text-white rounded-xl hover:bg-indigo-500 disabled:opacity-50 disabled:hover:bg-indigo-600 transition-colors shadow-lg"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M3.478 2.404a.75.75 0 00-.926.941l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.404z" />
              </svg>
            </button>
          </form>
          <div className="text-center mt-3 text-xs text-neutral-600">
            FinBot uses advanced LangGraph architecture with real ETF data.
          </div>
        </div>
      </div>
    </div>
  );
}
