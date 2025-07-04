import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { ShinyText } from "@/components/ui/shiny-text";
import { motion } from "framer-motion";

interface AuthProps {
  onLogin: () => void;
}

const Auth = ({ onLogin }: AuthProps) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    name: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (isSignUp) {
        // Sign up
        if (formData.password !== formData.confirmPassword) {
          setError("Passwords do not match");
          setLoading(false);
          return;
        }
        const res = await fetch("http://localhost:8000/api/signup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
            name: formData.name,
          }),
        });
        if (!res.ok) {
          const data = await res.json();
          setError(data.detail || "Sign up failed");
          setLoading(false);
          return;
        }
        const data = await res.json();
        localStorage.setItem("user_id", data.user_id);
        onLogin();
      } else {
        // Login
        const res = await fetch("http://localhost:8000/api/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
          }),
        });
        if (!res.ok) {
          const data = await res.json();
          setError(data.detail || "Login failed");
          setLoading(false);
          return;
        }
        const data = await res.json();
        localStorage.setItem("user_id", data.user_id);
        onLogin();
      }
    } catch (err: any) {
      setError("Network error");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div
      className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-[#1a0826] via-[#2d174d] to-[#0d061a]"
      style={{ minHeight: "100vh" }}
    >
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="w-full max-w-2xl"
      >
        <Card
          className="w-full rounded-3xl shadow-2xl border-0 bg-gradient-to-br from-[#2d174d] via-[#3a2066] to-[#1a0826] p-0"
          style={{ boxShadow: "0 8px 32px 0 rgba(58,32,102,0.45), 0 1.5px 8px 0 rgba(26,8,38,0.25)" }}
        >
          <CardHeader className="text-center pb-0 pt-10">
            <CardTitle className="text-4xl font-extrabold mb-2 bg-gradient-to-r from-purple-300 via-purple-400 to-purple-600 bg-clip-text text-transparent drop-shadow-lg">
              <ShinyText
                text="ClaimChain"
                className="bg-gradient-to-r from-purple-300 via-purple-400 to-purple-600 bg-clip-text text-transparent"
              />
            </CardTitle>
            <p className="text-lg text-purple-200/80 font-medium mb-2">
              {isSignUp ? "Create your account" : "Welcome back"}
            </p>
          </CardHeader>
          <CardContent className="px-12 py-10">
            <form onSubmit={handleSubmit} className="space-y-6">
              {isSignUp && (
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-purple-200">Full Name</Label>
                  <Input
                    id="name"
                    name="name"
                    type="text"
                    placeholder="Enter your full name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required={isSignUp}
                    className="rounded-xl bg-[#2d174d] border border-purple-700 text-purple-100 placeholder-purple-400 focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="email" className="text-purple-200">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  className="rounded-xl bg-[#2d174d] border border-purple-700 text-purple-100 placeholder-purple-400 focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password" className="text-purple-200">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  className="rounded-xl bg-[#2d174d] border border-purple-700 text-purple-100 placeholder-purple-400 focus:ring-2 focus:ring-purple-500"
                />
              </div>
              {isSignUp && (
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword" className="text-purple-200">Confirm Password</Label>
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    placeholder="Confirm your password"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    required={isSignUp}
                    className="rounded-xl bg-[#2d174d] border border-purple-700 text-purple-100 placeholder-purple-400 focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              )}
              {error && (
                <div className="text-red-400 text-sm text-center font-medium">{error}</div>
              )}
              <Button
                type="submit"
                className="w-full py-4 text-lg font-bold rounded-2xl bg-gradient-to-r from-purple-600 via-purple-500 to-purple-700 text-white shadow-lg hover:from-purple-700 hover:to-purple-800 transition-all duration-200 border-0"
                disabled={loading}
              >
                {loading ? (isSignUp ? "Signing Up..." : "Signing In...") : (isSignUp ? "Sign Up" : "Sign In")}
              </Button>
            </form>
            <div className="mt-8 text-center">
              <p className="text-base text-purple-300">
                {isSignUp ? "Already have an account?" : "Don't have an account?"}
              </p>
              <Button
                variant="ghost"
                onClick={() => setIsSignUp(!isSignUp)}
                className="text-purple-400 hover:text-purple-200 text-lg font-semibold"
              >
                {isSignUp ? "Sign In" : "Sign Up"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default Auth;