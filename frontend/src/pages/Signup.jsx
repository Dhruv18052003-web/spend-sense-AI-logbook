import { useEffect, useRef, useState } from "react";
import { loginUser, registerUser } from "../services/auth";

const fallbackCurrencies = [
  "USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD", "CHF", "CNY", "SGD",
  "HKD", "NZD", "SEK", "NOK", "DKK", "ZAR", "BRL", "MXN", "AED", "SAR",
  "QAR", "KWD", "BHD", "OMR", "THB", "MYR", "IDR", "PHP", "KRW", "VND",
  "TRY", "PLN", "CZK", "HUF", "RON", "BGN", "HRK", "RSD", "ISK", "ILS",
  "EGP", "NGN", "KES", "GHS", "MAD", "TND", "PKR", "LKR", "BDT", "NPR",
  "UAH", "RUB", "CLP", "COP", "PEN", "ARS", "UYU"
];

const supportedCurrencies =
  typeof Intl !== "undefined" && typeof Intl.supportedValuesOf === "function"
    ? Intl.supportedValuesOf("currency").map((code) => code.toUpperCase())
    : fallbackCurrencies;

const currencyOptions = Array.from(new Set(supportedCurrencies)).sort();
const defaultCurrency = currencyOptions.includes("USD")
  ? "USD"
  : currencyOptions[0] || "USD";

const initialForm = {
  first_name: "",
  last_name: "",
  username: "",
  password: "",
  amount: "",
  currency: defaultCurrency,
};

export default function Signup() {
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCurrencyOpen, setIsCurrencyOpen] = useState(false);
  const [currencyQuery, setCurrencyQuery] = useState("");
  const currencyRef = useRef(null);

  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (currencyRef.current && !currencyRef.current.contains(event.target)) {
        setIsCurrencyOpen(false);
      }
    };

    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);

    const getApiErrorMessage = (err, fallbackMessage) => {
      const apiData = err?.response?.data;
      if (!apiData) {
        return "Request blocked before reaching API response. Ensure Django is running and CORS is configured for http://localhost:5173.";
      }

      if (typeof apiData === "string") {
        return apiData;
      }

      if (typeof apiData.detail === "string") {
        return apiData.detail;
      }

      if (typeof apiData.error === "string") {
        return apiData.error;
      }

      if (typeof apiData === "object") {
        const firstValue = Object.values(apiData)[0];
        if (Array.isArray(firstValue) && firstValue.length > 0) {
          return String(firstValue[0]);
        }
        if (typeof firstValue === "string") {
          return firstValue;
        }
      }

      return fallbackMessage;
    };

    try {
      await registerUser(form);
      localStorage.setItem("trackedAmount", form.amount);
      localStorage.setItem("trackedCurrency", form.currency);

      try {
        await loginUser({
          username: form.username,
          password: form.password,
        });
        window.location.href = "/chat";
      } catch (loginError) {
        setError(
          getApiErrorMessage(
            loginError,
            "Account created, but auto-login failed. Please login manually."
          )
        );
      }
    } catch (registerError) {
      setError(
        getApiErrorMessage(
          registerError,
          "Signup failed. Please check your details."
        )
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredCurrencies = currencyOptions.filter((code) =>
    code.includes(currencyQuery.trim().toUpperCase())
  );

  return (
    <div className="min-h-screen bg-slate-200 px-4 py-8">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-xl items-center">
        <div className="w-full rounded-3xl border border-slate-500 bg-slate-700 p-8 shadow-xl">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-100">
              Create your <span className="text-slate-200">SpendSense</span> account
            </h1>
            <p className="mt-2 text-sm text-slate-200">
              Add your profile and starting wallet details
            </p>
          </div>

          {error && (
            <div className="mb-4 rounded-xl border border-slate-400 bg-slate-600 px-4 py-3 text-sm text-slate-100">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-200">
                  First name
                </label>
                <input
                  name="first_name"
                  value={form.first_name}
                  onChange={handleChange}
                  required
                  className="w-full rounded-xl border border-slate-300 bg-slate-200 px-4 py-3 text-slate-900 placeholder:text-slate-500 focus:border-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-400"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-200">
                  Last name
                </label>
                <input
                  name="last_name"
                  value={form.last_name}
                  onChange={handleChange}
                  required
                  className="w-full rounded-xl border border-slate-300 bg-slate-200 px-4 py-3 text-slate-900 placeholder:text-slate-500 focus:border-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-400"
                />
              </div>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-200">
                Username
              </label>
              <input
                name="username"
                value={form.username}
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
                value={form.password}
                onChange={handleChange}
                required
                minLength={8}
                placeholder="At least 8 characters"
                className="w-full rounded-xl border border-slate-300 bg-slate-200 px-4 py-3 text-slate-900 placeholder:text-slate-500 focus:border-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-400"
              />
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-200">
                  Amount to track
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  name="amount"
                  value={form.amount}
                  onChange={handleChange}
                  required
                  className="w-full rounded-xl border border-slate-300 bg-slate-200 px-4 py-3 text-slate-900 placeholder:text-slate-500 focus:border-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-400"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-200">
                  Currency
                </label>
                <div className="relative" ref={currencyRef}>
                  <button
                    type="button"
                    onClick={() => setIsCurrencyOpen((prev) => !prev)}
                    className="flex w-full items-center justify-between rounded-xl border border-slate-300 bg-slate-200 px-4 py-3 text-slate-900 focus:border-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-400"
                  >
                    <span>{form.currency}</span>
                    <span className="text-slate-600">{isCurrencyOpen ? "^" : "v"}</span>
                  </button>

                  {isCurrencyOpen && (
                    <div className="absolute z-30 mt-2 w-full overflow-hidden rounded-xl border border-slate-500 bg-slate-700 shadow-xl">
                      <input
                        type="text"
                        value={currencyQuery}
                        onChange={(e) => setCurrencyQuery(e.target.value)}
                        placeholder="Search currency code"
                        className="w-full border-b border-slate-500 bg-slate-700 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-400 focus:outline-none"
                      />
                      <div className="max-h-56 overflow-y-auto py-1">
                        {filteredCurrencies.length === 0 && (
                          <p className="px-3 py-2 text-sm text-slate-200">No currency found</p>
                        )}
                        {filteredCurrencies.map((currencyCode) => (
                          <button
                            key={currencyCode}
                            type="button"
                            onClick={() => {
                              setForm((prev) => ({ ...prev, currency: currencyCode }));
                              setCurrencyQuery("");
                              setIsCurrencyOpen(false);
                            }}
                            className="block w-full px-3 py-2 text-left text-sm text-slate-100 hover:bg-slate-600"
                          >
                            {currencyCode}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full rounded-xl bg-slate-200 py-3 font-semibold text-slate-900 transition hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-slate-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting ? "Creating account..." : "Create account"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-200">
            Already have an account?{" "}
            <a href="/" className="font-medium text-slate-200 underline">
              Login
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}



