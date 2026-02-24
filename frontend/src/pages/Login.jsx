import { useState } from "react";
import { loginUser } from "../services/auth";

export default function Login() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await loginUser(form);
      window.location.href = "/chat";
    } catch {
      setError("Invalid username or password");
    }
  };

  return (
    <div className="min-h-screen bg-slate-200 px-4 py-8">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-md items-center">
        <div className="w-full rounded-3xl border border-slate-500 bg-slate-700 p-8 shadow-xl">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-100">
              Spend<span className="text-slate-200">Sense</span>
            </h1>
            <p className="mt-2 text-sm text-slate-200">
              Smart expense tracking, chat-first
            </p>
          </div>

          {error && (
            <div className="mb-4 rounded-xl border border-slate-400 bg-slate-600 px-4 py-3 text-sm text-slate-100">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-200">
                Username
              </label>
              <input
                name="username"
                placeholder="Enter your username"
                onChange={handleChange}
                required
                className="w-full rounded-xl border border-slate-300 bg-slate-200 px-4 py-3 text-slate-900 placeholder:text-slate-500 focus:border-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-400"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-200">
                Password
              </label>
              <input
                type="password"
                name="password"
                placeholder="********"
                onChange={handleChange}
                required
                className="w-full rounded-xl border border-slate-300 bg-slate-200 px-4 py-3 text-slate-900 placeholder:text-slate-500 focus:border-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-400"
              />
            </div>

            <button
              type="submit"
              className="w-full rounded-xl bg-slate-200 py-3 font-semibold text-slate-900 transition hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-slate-400"
            >
              Login
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-200">
            New here?{" "}
            <a href="/signup" className="font-medium text-slate-200 underline">
              Create an account
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}



