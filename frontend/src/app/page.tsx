"use client";

import { useState, useRef, useEffect, KeyboardEvent, ChangeEvent } from "react";
import ReactMarkdown from "react-markdown";
import { Send, Plus, ChevronRight, Trash2, MessageSquare, Radio, Flag } from "lucide-react";
import clsx from "clsx";

// ─── Types ────────────────────────────────────────────────────────────────────
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
}

// ─── Constants ────────────────────────────────────────────────────────────────
const GREETINGS = [
  { line1: "Box, box.", line2: "Ready when you are, Racer." },
  { line1: "DRS open.", line2: "What do you want to know?" },
  { line1: "Lights out.", line2: "Let's talk Formula 1." },
  { line1: "On the pace.", line2: "Fire your question." },
  { line1: "Green flag.", line2: "Ask me anything, Racer." },
];

const SUGGESTED = [
  { icon: "🏆", text: "Who won the 2021 F1 Championship?" },
  { icon: "🇧🇷", text: "Tell me about Ayrton Senna" },
  { icon: "🔧", text: "How does DRS work?" },
  { icon: "⚔️", text: "Hamilton vs Schumacher — titles compared" },
  { icon: "🕯️", text: "What happened at the 1994 San Marino GP?" },
  { icon: "⚡", text: "Explain F1 hybrid power units" },
];

const STORAGE_KEY = "veloce_conversations";

// ─── Logo ─────────────────────────────────────────────────────────────────────
function VeloceLogo({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="32" height="32" rx="7" fill="#E10600" />
      <path d="M8 9L16 23L24 9" stroke="white" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" fill="none" />
      <line x1="5" y1="18" x2="11" y2="18" stroke="white" strokeWidth="1.4" strokeLinecap="round" opacity="0.45" />
      <line x1="21" y1="18" x2="27" y2="18" stroke="white" strokeWidth="1.4" strokeLinecap="round" opacity="0.45" />
    </svg>
  );
}

// ─── Typing Indicator ─────────────────────────────────────────────────────────
function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 px-5 py-4">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="typing-dot w-1.5 h-1.5 rounded-full bg-f1red/60"
          style={{ animationDelay: `${i * 0.18}s` }}
        />
      ))}
      <span className="text-[11px] text-f1muted/50 font-mono ml-1">Computing…</span>
    </div>
  );
}

// ─── Message Bubble ───────────────────────────────────────────────────────────
function MessageBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === "user";

  return (
    <div className={clsx("msg-enter flex w-full gap-3", isUser ? "justify-end" : "justify-start")}>
      {/* Bot avatar */}
      {!isUser && (
        <div className="flex-shrink-0 mt-1">
          <VeloceLogo size={26} />
        </div>
      )}

      <div className={clsx("flex flex-col max-w-[70%]", isUser ? "items-end" : "items-start")}>
        <div
          className={clsx(
            "text-[14px] leading-[1.7] px-5 py-3.5",
            isUser
              ? "bg-f1red text-white rounded-2xl rounded-br-md font-sans"
              : "bg-[#111318] border border-white/[0.07] text-gray-100 rounded-2xl rounded-bl-md font-sans"
          )}
        >
          {isUser ? (
            <span>{msg.content}</span>
          ) : (
            <ReactMarkdown
              components={{
                p: ({ children }) => (
                  <p className="mb-2.5 last:mb-0 text-gray-200 leading-[1.75]">{children}</p>
                ),
                strong: ({ children }) => (
                  <strong className="text-white font-semibold">{children}</strong>
                ),
                ul: ({ children }) => (
                  <ul className="space-y-2 my-3">{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-inside space-y-2 my-3 text-gray-300">{children}</ol>
                ),
                li: ({ children }) => (
                  <li className="flex gap-2.5 items-start text-gray-300">
                    <span className="text-f1red mt-[5px] flex-shrink-0 text-[10px]">▶</span>
                    <span>{children}</span>
                  </li>
                ),
                h2: ({ children }) => (
                  <h2 className="text-white font-bold text-[15px] mt-4 mb-2 border-b border-white/10 pb-1">{children}</h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-white font-semibold text-[14px] mt-3 mb-1">{children}</h3>
                ),
                code: ({ children }) => (
                  <code className="bg-black/50 text-f1red/90 px-1.5 py-0.5 rounded text-[12px] font-mono border border-white/5">
                    {children}
                  </code>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-2 border-f1red/50 pl-4 my-3 text-gray-400 italic">
                    {children}
                  </blockquote>
                ),
              }}
            >
              {msg.content}
            </ReactMarkdown>
          )}
        </div>
        <span className="text-[10px] text-white/20 mt-1.5 px-1 font-mono">
          {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </span>
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="flex-shrink-0 mt-1 w-[26px] h-[26px] rounded-full bg-[#1e2130] border border-white/10 flex items-center justify-center">
          <span className="text-[9px] text-white/50 font-mono font-bold">YOU</span>
        </div>
      )}
    </div>
  );
}

// ─── Sidebar ──────────────────────────────────────────────────────────────────
function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
  isOpen,
}: {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
  isOpen: boolean;
}) {
  return (
    <aside
      className={clsx(
        "flex-shrink-0 flex flex-col border-r border-white/[0.06] transition-all duration-300 overflow-hidden bg-[#080909]",
        isOpen ? "w-[240px]" : "w-0"
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 pt-5 pb-4">
        <div className="flex items-center gap-2.5">
          <VeloceLogo size={24} />
          <span className="text-white font-bold text-[15px] tracking-tight">Veloce</span>
        </div>
        <button
          onClick={onNew}
          className="w-7 h-7 rounded-lg bg-white/5 hover:bg-white/10 border border-white/[0.08] flex items-center justify-center transition-colors group"
          title="New chat"
        >
          <Plus size={13} className="text-white/40 group-hover:text-white transition-colors" />
        </button>
      </div>

      {/* Section label */}
      <div className="px-4 pb-2">
        <span className="text-[9px] text-white/20 font-mono tracking-[0.15em] uppercase">Recent</span>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto px-2 space-y-0.5">
        {conversations.length === 0 && (
          <p className="text-[11px] text-white/20 text-center mt-8 font-mono px-3 leading-relaxed">
            No sessions yet.<br />Start a new chat.
          </p>
        )}
        {conversations
          .slice()
          .sort((a, b) => b.createdAt - a.createdAt)
          .map((conv) => (
            <div
              key={conv.id}
              className={clsx(
                "group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-150",
                activeId === conv.id
                  ? "bg-white/[0.07] border border-white/[0.1]"
                  : "hover:bg-white/[0.04] border border-transparent"
              )}
              onClick={() => onSelect(conv.id)}
            >
              <MessageSquare
                size={11}
                className={clsx(
                  "flex-shrink-0",
                  activeId === conv.id ? "text-f1red" : "text-white/25"
                )}
              />
              <span
                className={clsx(
                  "flex-1 text-[12px] truncate leading-snug",
                  activeId === conv.id ? "text-white/90" : "text-white/40 group-hover:text-white/60"
                )}
              >
                {conv.title}
              </span>
              <button
                onClick={(e) => { e.stopPropagation(); onDelete(conv.id); }}
                className="opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
              >
                <Trash2 size={11} className="text-white/25 hover:text-f1red transition-colors" />
              </button>
            </div>
          ))}
      </div>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-white/[0.05]">
        <div className="flex items-center gap-2">
          <Radio size={9} className="text-f1red animate-pulse" />
          <span className="text-[9px] text-white/20 font-mono tracking-[0.12em] uppercase">
            Engine online
          </span>
        </div>
      </div>
    </aside>
  );
}

// ─── Main ─────────────────────────────────────────────────────────────────────
export default function Home() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  // Greeting state initialized to null to match server-side HTML
  const [greeting, setGreeting] = useState<{ line1: string; line2: string } | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const activeConversation = conversations.find((c) => c.id === activeId) ?? null;
  const messages = activeConversation?.messages ?? [];

  // Load from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed: Conversation[] = JSON.parse(stored);
        const hydrated = parsed.map((c) => ({
          ...c,
          messages: c.messages.map((m) => ({ ...m, timestamp: new Date(m.timestamp) })),
        }));
        setConversations(hydrated);
      }
    } catch {}
  }, []);

  // Set the random greeting on the client side only
  useEffect(() => {
    const randomGreeting = GREETINGS[Math.floor(Math.random() * GREETINGS.length)];
    setGreeting(randomGreeting);
  }, []);

  // Persist to localStorage
  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
    }
  }, [conversations]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const createNew = () => {
    setActiveId(null);
    setInput("");
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  const selectConversation = (id: string) => {
    setActiveId(id);
    setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: "auto" }), 60);
  };

  const deleteConversation = (id: string) => {
    setConversations((prev) => {
      const updated = prev.filter((c) => c.id !== id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
    if (activeId === id) setActiveId(null);
  };

  const handleInput = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 140) + "px";
  };

  const sendMessage = async (text: string = input) => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: trimmed,
      timestamp: new Date(),
    };

    let targetId = activeId;

    if (!targetId) {
      const newId = `conv_${Date.now()}`;
      const title = trimmed.length > 42 ? trimmed.slice(0, 42) + "…" : trimmed;
      const newConv: Conversation = { id: newId, title, messages: [userMsg], createdAt: Date.now() };
      setConversations((prev) => [newConv, ...prev]);
      setActiveId(newId);
      targetId = newId;
    } else {
      setConversations((prev) =>
        prev.map((c) => c.id === targetId ? { ...c, messages: [...c.messages, userMsg] } : c)
      );
    }

    setInput("");
    setIsLoading(true);
    if (inputRef.current) inputRef.current.style.height = "auto";

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong.");

      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer,
        timestamp: new Date(),
      };
      setConversations((prev) =>
        prev.map((c) => c.id === targetId ? { ...c, messages: [...c.messages, botMsg] } : c)
      );
    } catch {
      setConversations((prev) =>
        prev.map((c) =>
          c.id === targetId
            ? {
                ...c,
                messages: [
                  ...c.messages,
                  {
                    id: (Date.now() + 1).toString(),
                    role: "assistant" as const,
                    content: "Unable to reach the server. Make sure the backend is running.",
                    timestamp: new Date(),
                  },
                ],
              }
            : c
        )
      );
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-screen bg-[#0a0b0d] overflow-hidden">

      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={selectConversation}
        onNew={createNew}
        onDelete={deleteConversation}
        isOpen={sidebarOpen}
      />

      <div className="flex flex-col flex-1 min-w-0">
        {/* Speed line */}
        <div className="h-[2px] w-full bg-gradient-to-r from-transparent via-f1red to-transparent flex-shrink-0" />

        {/* Topbar */}
        <header className="flex-shrink-0 flex items-center gap-3 px-5 py-3 border-b border-white/[0.05] bg-[#0a0b0d]">
          {/* Hamburger */}
          <button
            onClick={() => setSidebarOpen((v) => !v)}
            className="flex flex-col gap-[5px] p-1.5 rounded-lg hover:bg-white/5 transition-colors group flex-shrink-0"
          >
            <span className="block h-px w-4 bg-white/30 group-hover:bg-white/70 transition-colors" />
            <span className="block h-px w-2.5 bg-white/30 group-hover:bg-white/70 transition-colors" />
            <span className="block h-px w-4 bg-white/30 group-hover:bg-white/70 transition-colors" />
          </button>

          {!sidebarOpen && (
            <div className="flex items-center gap-2">
              <VeloceLogo size={20} />
              <span className="text-white font-bold text-[14px]">Veloce</span>
            </div>
          )}

          <div className="flex-1" />

          <button
            onClick={createNew}
            className="flex items-center gap-1.5 text-[11px] text-white/40 hover:text-white/80 border border-white/[0.08] hover:border-white/20 rounded-lg px-3 py-1.5 transition-all duration-150 font-mono"
          >
            <Plus size={11} />
            New chat
          </button>
        </header>

        {/* Messages */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-[680px] mx-auto px-5 py-10 flex flex-col gap-7">

            {/* Empty state — Only shows when greeting is loaded on client */}
            {messages.length === 0 && greeting && (
              <div className="flex flex-col items-center gap-10 pt-4">

                {/* Hero — logo + greeting SIDE BY SIDE */}
                <div className="flex items-center gap-6">
                  <div className="flex-shrink-0">
                    <div className="w-16 h-16 rounded-2xl bg-f1red flex items-center justify-center shadow-[0_0_40px_rgba(225,6,0,0.25)]">
                      <svg width="36" height="36" viewBox="0 0 32 32" fill="none">
                        <path d="M6 8L16 24L26 8" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                        <line x1="3" y1="18" x2="10" y2="18" stroke="white" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" />
                        <line x1="22" y1="18" x2="29" y2="18" stroke="white" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" />
                      </svg>
                    </div>
                  </div>
                  <div className="flex flex-col gap-1">
                    <div className="flex items-baseline gap-2">
                      <span className="text-[11px] text-f1red font-mono tracking-[0.15em] uppercase">
                        {greeting.line1}
                      </span>
                    </div>
                    <h2 className="text-[28px] font-bold text-white tracking-tight leading-tight">
                      {greeting.line2}
                    </h2>
                    <p className="text-[13px] text-white/35 mt-1 leading-relaxed">
                      Every F1 driver, race, and championship — ask anything.
                    </p>
                  </div>
                </div>

                {/* Divider */}
                <div className="relative w-full overflow-hidden h-px bg-white/[0.06]">
                  <div className="track-line absolute inset-y-0 w-20 bg-gradient-to-r from-transparent via-f1red/60 to-transparent" />
                </div>

                {/* Suggestions */}
                <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {SUGGESTED.map(({ icon, text }) => (
                    <button
                      key={text}
                      onClick={() => sendMessage(text)}
                      className="group flex items-center gap-3 text-left bg-[#0f1014] border border-white/[0.07] hover:border-f1red/30 hover:bg-[#13141a] rounded-xl px-4 py-3.5 transition-all duration-200"
                    >
                      <span className="text-[18px] flex-shrink-0">{icon}</span>
                      <span className="text-[12.5px] text-white/50 group-hover:text-white/80 transition-colors leading-snug">
                        {text}
                      </span>
                      <ChevronRight
                        size={12}
                        className="ml-auto text-white/15 group-hover:text-f1red/60 group-hover:translate-x-0.5 transition-all duration-150 flex-shrink-0"
                      />
                    </button>
                  ))}
                </div>

                {/* Flag decoration */}
                <div className="flex items-center gap-2 text-white/10">
                  <Flag size={11} />
                  <span className="text-[10px] font-mono tracking-widest uppercase">
                    Formula 1 · Since 1950
                  </span>
                  <Flag size={11} />
                </div>

              </div>
            )}

            {/* Messages */}
            {messages.map((msg) => (
              <MessageBubble key={msg.id} msg={msg} />
            ))}

            {isLoading && (
              <div className="msg-enter flex justify-start gap-3">
                <div className="flex-shrink-0 mt-1">
                  <VeloceLogo size={26} />
                </div>
                <div className="bg-[#111318] border border-white/[0.07] rounded-2xl rounded-bl-md">
                  <TypingIndicator />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </main>

        {/* Input — F1 HUD */}
        <div className="flex-shrink-0 px-5 pb-5 pt-2 bg-[#0a0b0d]">
          <div className="max-w-[680px] mx-auto">
            <div className="relative group">
              {/* Corner brackets */}
              <span className="absolute -top-px -left-px w-4 h-4 border-t-[1.5px] border-l-[1.5px] border-f1red/30 rounded-tl pointer-events-none transition-colors group-focus-within:border-f1red/60" />
              <span className="absolute -top-px -right-px w-4 h-4 border-t-[1.5px] border-r-[1.5px] border-f1red/30 rounded-tr pointer-events-none transition-colors group-focus-within:border-f1red/60" />
              <span className="absolute -bottom-px -left-px w-4 h-4 border-b-[1.5px] border-l-[1.5px] border-f1red/30 rounded-bl pointer-events-none transition-colors group-focus-within:border-f1red/60" />
              <span className="absolute -bottom-px -right-px w-4 h-4 border-b-[1.5px] border-r-[1.5px] border-f1red/30 rounded-br pointer-events-none transition-colors group-focus-within:border-f1red/60" />

              <div className="flex items-end gap-3 bg-[#0f1014] border border-white/[0.08] rounded-xl px-4 py-3.5 focus-within:border-white/[0.15] transition-colors duration-200">
                {/* Status dot */}
                <div className="flex-shrink-0 mb-[2px]">
                  <div className={clsx(
                    "w-[7px] h-[7px] rounded-full transition-all duration-300",
                    isLoading
                      ? "bg-yellow-400 shadow-[0_0_6px_rgba(250,204,21,0.6)] animate-pulse"
                      : input.trim()
                      ? "bg-f1red shadow-[0_0_6px_rgba(225,6,0,0.5)]"
                      : "bg-white/10"
                  )} />
                </div>

                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={handleInput}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about any race, driver, or championship…"
                  rows={1}
                  disabled={isLoading}
                  className={clsx(
                    "flex-1 bg-transparent text-[14px] text-white/85 placeholder:text-white/20",
                    "font-sans resize-none leading-relaxed focus:outline-none",
                    "disabled:opacity-40 disabled:cursor-not-allowed",
                    "min-h-[22px] max-h-[140px]"
                  )}
                />

                <button
                  onClick={() => sendMessage()}
                  disabled={isLoading || !input.trim()}
                  className={clsx(
                    "flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center transition-all duration-200 mb-0.5",
                    input.trim() && !isLoading
                      ? "bg-f1red text-white hover:bg-[#ff1500] shadow-[0_0_16px_rgba(225,6,0,0.35)]"
                      : "bg-white/[0.05] text-white/15 cursor-not-allowed"
                  )}
                >
                  <Send size={14} />
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between mt-2 px-1">
              <span className="text-[9px] text-white/15 font-mono tracking-widest">↵ SEND · ⇧↵ NEWLINE</span>
              <span className="text-[9px] text-white/15 font-mono tracking-widest">VELOCE AI</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}