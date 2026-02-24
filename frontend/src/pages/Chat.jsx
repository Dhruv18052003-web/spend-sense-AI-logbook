import { useEffect, useMemo, useState } from "react";
import { fetchChatHistory, sendChatMessage } from "../services/chat";

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello. Tell me an expense you made, add money, or ask a spending query.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");

  const [remainingAmount, setRemainingAmount] = useState(
    localStorage.getItem("trackedAmount") || "--"
  );
  const [currency, setCurrency] = useState(
    localStorage.getItem("trackedCurrency") || "USD"
  );

  const hasAuthToken = useMemo(
    () => Boolean(localStorage.getItem("accessToken")),
    []
  );

  if (!hasAuthToken) {
    window.location.href = "/";
    return null;
  }

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const data = await fetchChatHistory(50);

        if (Array.isArray(data?.messages) && data.messages.length > 0) {
          setMessages(data.messages);
        }

        if (data?.remaining_balance !== undefined && data?.remaining_balance !== null) {
          const nextBalance = String(data.remaining_balance);
          setRemainingAmount(nextBalance);
          localStorage.setItem("trackedAmount", nextBalance);
        }

        if (typeof data?.currency === "string" && data.currency.trim()) {
          const nextCurrency = data.currency.trim().toUpperCase();
          setCurrency(nextCurrency);
          localStorage.setItem("trackedCurrency", nextCurrency);
        }
      } catch {
        setError("Could not load chat history.");
      }
    };

    loadHistory();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isSending) {
      return;
    }

    setError("");
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setIsSending(true);

    try {
      const data = await sendChatMessage(trimmed);
      const reply =
        typeof data?.reply === "string" && data.reply.trim()
          ? data.reply
          : "I received your message.";

      if (data?.remaining_balance !== undefined && data?.remaining_balance !== null) {
        const nextBalance = String(data.remaining_balance);
        setRemainingAmount(nextBalance);
        localStorage.setItem("trackedAmount", nextBalance);
      }

      if (typeof data?.currency === "string" && data.currency.trim()) {
        const nextCurrency = data.currency.trim().toUpperCase();
        setCurrency(nextCurrency);
        localStorage.setItem("trackedCurrency", nextCurrency);
      }

      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setError("Could not send message. Please try again.");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I could not process that due to a network or auth issue.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    window.location.href = "/";
  };

  return (
    <div className="min-h-screen bg-slate-200 px-4 py-6">
      <div className="mx-auto flex h-[calc(100vh-3rem)] w-full max-w-4xl flex-col rounded-3xl border border-slate-500 bg-slate-700 p-4 shadow-xl sm:p-6">
        <div className="mb-4 grid grid-cols-[1fr_auto] items-center gap-3 rounded-2xl border border-slate-500 bg-slate-600 px-4 py-3">
          <div className="text-center">
            <p className="text-xs uppercase tracking-wide text-slate-300">
              Amount Remaining
            </p>
            <p className="text-2xl font-bold text-slate-100">
              {currency} {remainingAmount}
            </p>
          </div>
          <div className="justify-self-end">
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-lg border border-slate-400 px-3 py-2 text-sm text-slate-100 transition hover:bg-slate-500"
            >
              Logout
            </button>
          </div>
        </div>

        <div className="mb-4 flex-1 space-y-3 overflow-y-auto rounded-2xl border border-slate-500 bg-slate-600 p-3">
          {messages.map((msg, index) => (
            <div
              key={`${msg.role}-${index}`}
              className={`max-w-[88%] rounded-2xl px-4 py-3 text-sm sm:text-base ${
                msg.role === "user"
                  ? "ml-auto bg-slate-200 text-slate-900"
                  : "mr-auto bg-slate-500 text-slate-100"
              }`}
            >
              {msg.content}
            </div>
          ))}
          {isSending && (
            <div className="mr-auto rounded-2xl bg-slate-500 px-4 py-3 text-sm text-slate-200">
              Thinking...
            </div>
          )}
        </div>

        {error && (
          <div className="mb-3 rounded-xl border border-slate-400 bg-slate-600 px-4 py-2 text-sm text-slate-100">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder='Try: "Today I spent 450 on groceries"'
            className="w-full rounded-xl border border-slate-300 bg-slate-200 px-4 py-3 text-slate-900 placeholder:text-slate-500 focus:border-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-400"
          />
          <button
            type="submit"
            disabled={isSending}
            className="rounded-xl bg-slate-200 px-5 py-3 font-semibold text-slate-900 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}



