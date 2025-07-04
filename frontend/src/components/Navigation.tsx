import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import React from "react";

const Navigation = ({ onLogout }: { onLogout?: () => void }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { path: "/", label: "Home" },
    { path: "/claims", label: "Claims" },
    { path: "/profile", label: "Profile" },
    { path: "/settings", label: "Settings" },
  ];

  return (
    <motion.nav 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="fixed top-0 left-0 right-0 z-50"
    >
      <div className="absolute inset-0 bg-[#0f061e]/80 backdrop-blur-md">
        {/* Glowing border effect */}
        <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-purple-500/50" />
        <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-purple-500 to-transparent" />
        <div className="absolute -bottom-[1px] left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-fuchsia-500 to-transparent blur-sm" />
        <div className="absolute -bottom-[2px] left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-purple-400 to-transparent blur-md" />
      </div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-24">
          {/* Logo/Brand */}
          <motion.div 
            className="flex-shrink-0"
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.2 }}
          >
            <h1 
              onClick={() => navigate("/")}
              className="text-3xl font-bold bg-gradient-to-r from-purple-200 via-white to-purple-200 bg-clip-text text-transparent cursor-pointer transition-all duration-500 hover:from-white hover:via-purple-200 hover:to-white"
            >
              ClaimChain
            </h1>
          </motion.div>

          {/* Navigation Items */}
          <div className="flex items-center gap-3">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Button
                  key={item.path}
                  variant="ghost"
                  onClick={() => navigate(item.path)}
                  className={cn(
                    "px-6 py-7 text-base font-medium transition-all duration-300",
                    "hover:bg-purple-500/10 hover:text-white",
                    "focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:ring-offset-0",
                    isActive
                      ? "bg-purple-500/20 text-white shadow-lg shadow-purple-500/10"
                      : "text-purple-100/80 hover:text-white"
                  )}
                >
                  {item.label}
                </Button>
              );
            })}

            {/* Action Button */}
            <Button
              onClick={() => navigate("/claims")}
              className="ml-6 bg-purple-600 text-white hover:bg-purple-700 px-8 py-7 text-base shadow-lg shadow-purple-500/20 transition-all duration-300"
            >
              Start Claim
            </Button>
            {onLogout && (
              <Button
                onClick={onLogout}
                className="ml-4 bg-red-600 text-white hover:bg-red-700 px-8 py-7 text-base shadow-lg shadow-red-500/20 transition-all duration-300"
              >
                Logout
              </Button>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navigation;