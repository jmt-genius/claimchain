import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";
import Navigation from "@/components/Navigation";

const Claims = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#0f061e]">
      <Navigation />
      
      <div className="max-w-4xl mx-auto p-6 pt-32">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold mb-4 text-white">Choose Your Claim Type</h1>
          <p className="text-purple-200/80 text-lg">
            Select the type of claim that best fits your situation
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Quick Claim */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            <Card className="card-elegant h-full hover:shadow-glow transition-all duration-300 cursor-pointer group bg-purple-900/10 border-purple-400/10 hover:bg-purple-800/20"
                  onClick={() => navigate("/quick-claim")}>
              <CardHeader className="text-center pb-4">
                <div className="text-6xl mb-4 group-hover:scale-110 transition-transform duration-300">⚡</div>
                <CardTitle className="text-2xl text-white">Quick Claim</CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <p className="text-purple-200/80 mb-6">
                  For cardiac events detected automatically by your Fitbit. 
                  AI analyzes your data and submits claims instantly.
                </p>
                <div className="space-y-2 text-sm text-left mb-6 text-purple-200/80">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span>Automatic heart event detection</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span>AI policy analysis with Gemini</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span>Blockchain claim submission</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span>Real-time status updates</span>
                  </div>
                </div>
                <Button className="w-full bg-purple-600 hover:bg-purple-700 text-white rounded-xl py-6 shadow-lg shadow-purple-500/20 text-lg">
                  Start Quick Claim
                </Button>
              </CardContent>
            </Card>
          </motion.div>

          {/* Full Claim */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            <Card className="card-elegant h-full hover:shadow-glow transition-all duration-300 cursor-pointer group bg-purple-900/10 border-purple-400/10 hover:bg-purple-800/20"
                  onClick={() => navigate("/full-claim")}>
              <CardHeader className="text-center pb-4">
                <div className="text-6xl mb-4 group-hover:scale-110 transition-transform duration-300">📋</div>
                <CardTitle className="text-2xl text-white">Full Claim</CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <p className="text-purple-200/80 mb-6">
                  Complete claim submission with document uploads. 
                  Perfect for complex medical situations requiring documentation.
                </p>
                <div className="space-y-2 text-sm text-left mb-6 text-purple-200/80">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span>Hospital bill upload</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span>Discharge summary analysis</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span>Digital certificate verification</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span>AI form auto-fill</span>
                  </div>
                </div>
                <Button className="w-full bg-purple-600 hover:bg-purple-700 text-white rounded-xl py-6 shadow-lg shadow-purple-500/20 text-lg">
                  Start Full Claim
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.6 }}
          className="mt-12 text-center"
        >
          <Card className="card-elegant p-6 bg-purple-900/10 border-purple-400/10">
            <h3 className="text-lg font-semibold mb-2 text-white">Need Help Choosing?</h3>
            <p className="text-purple-200/80 mb-4">
              Not sure which claim type is right for you? Our AI assistant can help you decide.
            </p>
            <Button variant="ghost" className="text-purple-200 hover:text-white hover:bg-purple-500/10">
              Talk to AI Assistant
            </Button>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default Claims;