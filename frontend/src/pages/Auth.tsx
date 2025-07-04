import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Sparkles } from "@/components/ui/sparkles";
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate authentication
    onLogin();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <Sparkles className="absolute inset-0" particleColor="hsl(var(--primary))">
        <div className="relative z-10 w-full max-w-md">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card className="card-elegant">
              <CardHeader className="text-center">
                <CardTitle className="text-3xl font-bold mb-4">
                  <ShinyText 
                    text="ClaimChain" 
                    className="bg-gradient-primary bg-clip-text text-transparent"
                  />
                </CardTitle>
                <p className="text-muted-foreground">
                  {isSignUp ? "Create your account" : "Welcome back"}
                </p>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  {isSignUp && (
                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name</Label>
                      <Input
                        id="name"
                        name="name"
                        type="text"
                        placeholder="Enter your full name"
                        value={formData.name}
                        onChange={handleInputChange}
                        required={isSignUp}
                        className="rounded-xl"
                      />
                    </div>
                  )}
                  
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      placeholder="Enter your email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      className="rounded-xl"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      name="password"
                      type="password"
                      placeholder="Enter your password"
                      value={formData.password}
                      onChange={handleInputChange}
                      required
                      className="rounded-xl"
                    />
                  </div>
                  
                  {isSignUp && (
                    <div className="space-y-2">
                      <Label htmlFor="confirmPassword">Confirm Password</Label>
                      <Input
                        id="confirmPassword"
                        name="confirmPassword"
                        type="password"
                        placeholder="Confirm your password"
                        value={formData.confirmPassword}
                        onChange={handleInputChange}
                        required={isSignUp}
                        className="rounded-xl"
                      />
                    </div>
                  )}
                  
                  <Button type="submit" className="w-full btn-primary rounded-xl">
                    {isSignUp ? "Sign Up" : "Sign In"}
                  </Button>
                </form>
                
                <div className="mt-6 text-center">
                  <p className="text-sm text-muted-foreground">
                    {isSignUp ? "Already have an account?" : "Don't have an account?"}
                  </p>
                  <Button
                    variant="ghost"
                    onClick={() => setIsSignUp(!isSignUp)}
                    className="text-primary hover:text-primary/80"
                  >
                    {isSignUp ? "Sign In" : "Sign Up"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </Sparkles>
    </div>
  );
};

export default Auth;