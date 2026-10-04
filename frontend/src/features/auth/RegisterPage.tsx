"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
    confirmPassword: "",
    org_id: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) return "Password must be at least 8 characters";
    if (!/[A-Z]/.test(pwd)) return "Password must contain uppercase letter";
    if (!/[a-z]/.test(pwd)) return "Password must contain lowercase letter";
    if (!/[0-9]/.test(pwd)) return "Password must contain a number";
    return null;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      setIsLoading(false);
      return;
    }

    const pwdError = validatePassword(formData.password);
    if (pwdError) {
      setError(pwdError);
      setIsLoading(false);
      return;
    }

    try {
      await new Promise((r) => setTimeout(r, 1000));
      localStorage.setItem("token", "mock-jwt-token");
      router.push("/");
    } catch {
      setError("Registration failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="glass-card w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">👑</div>
          <h1 className="text-3xl font-bold">Create Account</h1>
          <p className="text-muted-foreground mt-2">Join DataMind-King</p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded bg-destructive/10 text-destructive text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Email</label>
            <input
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-4 py-2.5 rounded bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary/50"
              placeholder="you@company.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Username</label>
            <input
              name="username"
              type="text"
              value={formData.username}
              onChange={handleChange}
              className="w-full px-4 py-2.5 rounded bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary/50"
              placeholder="johndoe"
              minLength={3}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Organization ID</label>
            <input
              name="org_id"
              type="text"
              value={formData.org_id}
              onChange={handleChange}
              className="w-full px-4 py-2.5 rounded bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary/50"
              placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
              pattern="^[a-f0-9\-]{36}$"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Password</label>
            <input
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-4 py-2.5 rounded bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary/50"
              placeholder="••••••••"
              minLength={8}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Confirm Password</label>
            <input
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              className="w-full px-4 py-2.5 rounded bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary/50"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 bg-primary text-white rounded font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {isLoading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-muted-foreground">
          <p>Already have an account? <a href="/login" className="text-primary hover:underline">Sign in</a></p>
        </div>
      </div>
    </div>
  );
}