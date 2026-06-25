"use client";

import {
  useState,
  useRef,
  useEffect,
  useCallback,
  FormEvent,
  KeyboardEvent,
} from "react";
import { useRouter } from "next/navigation";
import { askQuestionRequest, logoutRequest, ApiError } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  isError?: boolean;
}

function makeId(): string {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

const SUGGESTED_QUESTIONS = [
  "สรุป net income ปี 2022-2025 ของบริษัท Apple",
  "เปรียบเทียบโครงสร้างรายได้และกลยุทธ์ทางธุรกิจของ Google และ Facebook เพื่อประเมินจุดแข็งและจุดอ่อนในการแข่งขันในตลาดปี 2025",
  "จากรายได้ของบริษัท Microsoft, Apple, Google, Facebook ในปี 2024-2025 บริษัทใดที่มีอัตราการเติบโตต่อสูงสุด และอะไรเป็นปัจจัยหลัก",
];

export default function ChatClient({ username }: { username: string }) {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: makeId(),
      role: "assistant",
      content: `Hey ${username}! I'm your AI assistant. Ask me anything to get started.`,
    },
  ]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  const handleLogout = useCallback(async () => {
    await logoutRequest();
    router.push("/login");
    router.refresh();
  }, [router]);

  async function submitQuestion(question: string) {
    const trimmed = question.trim();
    if (!trimmed || isSending) return;

    const userMessage: Message = { id: makeId(), role: "user", content: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";

    const pendingId = makeId();
    setMessages((prev) => [...prev, { id: pendingId, role: "assistant", content: "" }]);
    setIsSending(true);

    try {
      await askQuestionRequest(trimmed, (chunkText) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === pendingId ? { ...m, content: m.content + chunkText } : m
          )
        );
      });
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        router.refresh();
        return;
      }
      const msg =
        err instanceof ApiError ? err.message : "Something went wrong. Please try again.";
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingId
            ? {
                ...m,
                content: m.content ? `${m.content}\n\n[${msg}]` : msg,
                isError: true,
              }
            : m
        )
      );
    } finally {
      setIsSending(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    submitQuestion(input);
  }

  function handleSuggestionClick(question: string) {
    submitQuestion(question);
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent);
    }
  }

  function handleTextareaInput(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setInput(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  const showSuggestions = !isSending && messages.length <= 1;

  return (
    <div className="flex h-screen flex-col bg-[#0f0f14]">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-white/10 bg-white/[0.02] px-4 py-3 sm:px-6">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-amber-400 text-sm font-bold text-[#0f0f14]">
            AI
          </div>
          <div>
            <p className="font-serif text-base leading-tight text-white">
              AI Assistant
            </p>
            <p className="text-xs leading-tight text-slate-500">
              Chatting as {username}
            </p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="rounded-lg border border-white/10 px-3 py-1.5 text-sm text-slate-300 transition hover:border-white/20 hover:bg-white/5"
        >
          Log out
        </button>
      </header>

      {/* Messages */}
      <div
        ref={scrollRef}
        className="chat-scroll flex-1 overflow-y-auto px-4 py-6 sm:px-6"
      >
        <div className="mx-auto flex max-w-2xl flex-col gap-5">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex animate-fade-in ${
                m.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed sm:max-w-[75%] ${
                  m.role === "user"
                    ? "bg-brand-600 text-white"
                    : m.isError
                    ? "border border-red-500/30 bg-red-500/10 text-red-300"
                    : "border border-white/10 bg-white/[0.04] text-slate-100"
                }`}
              >
                {m.content.length > 0 ? (
                  <span className="whitespace-pre-wrap">{m.content}</span>
                ) : (
                  <span className="flex gap-1 py-1">
                    <span className="typing-dot h-1.5 w-1.5 rounded-full bg-slate-400" />
                    <span
                      className="typing-dot h-1.5 w-1.5 rounded-full bg-slate-400"
                      style={{ animationDelay: "0.15s" }}
                    />
                    <span
                      className="typing-dot h-1.5 w-1.5 rounded-full bg-slate-400"
                      style={{ animationDelay: "0.3s" }}
                    />
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Composer */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-white/10 bg-white/[0.02] px-4 py-4 sm:px-6"
      >
        {showSuggestions && (
          <div className="mx-auto mb-3 flex max-w-2xl flex-wrap gap-2">
            {SUGGESTED_QUESTIONS.map((question) => (
              <button
                key={question}
                type="button"
                onClick={() => handleSuggestionClick(question)}
                className="rounded-full border border-white/10 bg-white/5 px-3.5 py-1.5 text-left text-xs leading-snug text-slate-300 transition hover:border-brand-400/40 hover:bg-brand-500/10 hover:text-brand-200"
              >
                {question}
              </button>
            ))}
          </div>
        )}
        <div className="mx-auto flex max-w-2xl items-end gap-2.5">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleTextareaInput}
            onKeyDown={handleKeyDown}
            placeholder="Send a message…"
            rows={1}
            className="max-h-40 flex-1 resize-none rounded-xl border border-white/10 bg-white/5 px-3.5 py-2.5 text-sm text-white placeholder-slate-500 outline-none transition focus:border-brand-400 focus:ring-2 focus:ring-brand-400/30"
          />
          <button
            type="submit"
            disabled={isSending || input.trim().length === 0}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-600 text-white transition hover:bg-brand-500 disabled:cursor-not-allowed disabled:opacity-40"
            aria-label="Send message"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-4.5 w-4.5"
            >
              <path d="M5 12h14" />
              <path d="m13 6 6 6-6 6" />
            </svg>
          </button>
        </div>
        <p className="mx-auto mt-2 max-w-2xl text-center text-xs text-slate-500">
          Press Enter to send, Shift + Enter for a new line.
        </p>
      </form>
    </div>
  );
}
