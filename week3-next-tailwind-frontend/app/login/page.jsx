"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { User, Lock } from "lucide-react";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!username || !password) {
      setError("Both fields are required.");
      return;
    }
    setError("");
    router.push("/dashboard");
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F4F5FA] px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-md space-y-4">
        <Input
          icon={User}
          variant="filled"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <Input
          icon={Lock}
          variant="filled"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={error}
        />

        <div className="flex items-center justify-between text-sm">
          <label className="flex items-center gap-2 text-slate-500">
            <input
              type="checkbox"
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
              className="h-4 w-4 rounded border-slate-300"
            />
            Remember me
          </label>
          <a href="#" className="italic text-slate-400 hover:text-slate-600">
            Forgot Password?
          </a>
        </div>

        <Button type="submit" variant="success" size="lg" className="w-full uppercase tracking-wide">
          Login
        </Button>
      </form>
    </div>
  );
}
