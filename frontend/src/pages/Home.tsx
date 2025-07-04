import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Sparkles, SparklesCore } from "@/components/ui/sparkles";
import { ShinyText } from "@/components/ui/shiny-text";
import { motion } from "framer-motion";
import Navigation from "@/components/Navigation";
import AceternitySparkles from "@/components/ui/sparkles-demo";

export function HomeSparkles() {
  return (
    <div className="h-screen relative w-full bg-[#0f061e] flex flex-col items-center justify-center overflow-hidden">
      {/* Main title */}
      <motion.h1 
        className="md:text-8xl text-4xl lg:text-9xl font-bold text-center text-white relative z-20"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        ClaimChain
      </motion.h1>

      <div className="w-[40rem] h-40 relative">
        {/* Gradient Lines */}
        <div className="absolute inset-x-20 top-0 bg-gradient-to-r from-transparent via-purple-500 to-transparent h-[2px] w-3/4 blur-sm" />
        <div className="absolute inset-x-20 top-0 bg-gradient-to-r from-transparent via-purple-500 to-transparent h-px w-3/4" />
        <div className="absolute inset-x-60 top-0 bg-gradient-to-r from-transparent via-fuchsia-500 to-transparent h-[5px] w-1/4 blur-sm" />
        <div className="absolute inset-x-60 top-0 bg-gradient-to-r from-transparent via-fuchsia-500 to-transparent h-px w-1/4" />

        {/* Dense sparkles below text */}
        <SparklesCore
          id="tsparticlesfullpage"
          background="transparent"
          minSize={0.6}
          maxSize={1.4}
          particleDensity={20000}
          className="w-full h-full"
          particleColor="#f0abfc"
          speed={0.5}
        />

        {/* Radial mask for smooth edges */}
        <div className="absolute inset-0 w-full h-full bg-[#0f061e] [mask-image:radial-gradient(350px_200px_at_top,transparent_20%,white)]"></div>
      </div>

      {/* Background sparkles */}
      <div className="w-full absolute inset-0">
        <SparklesCore
          id="tsparticlesbackground"
          background="transparent"
          minSize={0.4}
          maxSize={0.8}
          particleDensity={70}
          className="w-full h-full"
          particleColor="#e879f9"
          speed={0.8}
        />
      </div>

      {/* Gradient overlays */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#0f061e] via-transparent to-transparent" />
      <div className="absolute inset-0 bg-gradient-to-b from-[#0f061e] via-transparent to-transparent" />

      {/* Horizontal line effect */}
      <div className="absolute left-0 right-0 bottom-1/3 h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent opacity-50" />
    </div>
  );
}

const Home = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: "📲",
      title: "Wearable Integration",
      description: "Automatic cardiac event detection through Fitbit integration"
    },
    {
      icon: "🤖",
      title: "AI Analysis",
      description: "Google Gemini AI analyzes policies and medical reports instantly"
    },
    {
      icon: "🔐",
      title: "Blockchain Security",
      description: "Ethereum blockchain ensures secure claim approvals and transfers"
    },
    {
      icon: "⚡",
      title: "Instant Claims",
      description: "Submit and process claims in minutes, not weeks"
    }
  ];

  return (
    <div className="min-h-screen bg-[#0f061e]">
      <Navigation />
      <HomeSparkles />

      {/* Hero Section */}
      <section className="relative -mt-40 px-6 z-20">
        <div className="max-w-6xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="space-y-6"
          >
            <div className="space-y-4">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <h2 className="text-5xl md:text-6xl font-bold text-white mb-2">
                  The Future of
                </h2>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.6 }}
              >
                <h2 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-purple-400 to-purple-200 bg-clip-text text-transparent">
                  Insurance Claims
                </h2>
              </motion.div>
            </div>
            
            <motion.p 
              className="text-lg md:text-xl text-purple-200/80 max-w-3xl mx-auto leading-relaxed"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.8 }}
            >
              ClaimChain revolutionizes insurance with AI-powered analysis, 
              blockchain security, and real-time wearable data integration. 
              Experience instant claim processing like never before.
            </motion.p>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1, duration: 0.6 }}
              className="pt-4"
            >
              <Button 
                onClick={() => navigate("/claims")}
                className="bg-purple-600 text-white hover:bg-purple-700 text-lg px-8 py-6 rounded-xl mr-4 transition-all duration-300 shadow-lg shadow-purple-500/20"
              >
                Start Your Claim
              </Button>
              <Button 
                variant="outline"
                className="text-lg px-8 py-6 rounded-xl border-purple-400/20 text-purple-100 hover:bg-purple-500/10 transition-all duration-300"
              >
                Learn More
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* About Section */}
      <section className="py-32 px-6 bg-purple-950/20 mt-32">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-20"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-8 text-white">What is ClaimChain?</h2>
            <p className="text-lg md:text-xl text-purple-200/80 max-w-4xl mx-auto leading-relaxed">
              ClaimChain is a revolutionary insurance platform that combines cutting-edge technology 
              to create the most efficient, transparent, and secure claims processing system ever built. 
              Our platform integrates wearable health data, artificial intelligence, and blockchain 
              technology to automate and accelerate the entire claims process.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
                viewport={{ once: true }}
              >
                <Card className="bg-purple-900/10 border-purple-400/10 hover:bg-purple-800/20 transition-all duration-300 backdrop-blur-sm">
                  <CardContent className="p-8 text-center">
                    <div className="text-5xl mb-6">{feature.icon}</div>
                    <h3 className="text-xl font-semibold mb-3 text-white">{feature.title}</h3>
                    <p className="text-purple-200/80">{feature.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <Card className="bg-gradient-to-br from-purple-900/30 via-purple-800/20 to-purple-900/30 border-purple-400/10 p-16 backdrop-blur-sm">
              <h2 className="text-3xl md:text-4xl font-bold mb-6 text-white">Ready to Experience the Future?</h2>
              <p className="text-lg text-purple-200/80 mb-10">
                Join thousands of users who have already revolutionized their insurance experience with ClaimChain.
              </p>
              <Button 
                onClick={() => navigate("/claims")}
                className="bg-purple-600 text-white hover:bg-purple-700 text-lg px-8 py-6 rounded-xl transition-all duration-300 shadow-lg shadow-purple-500/20"
              >
                Get Started Today
              </Button>
            </Card>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 px-6 bg-purple-950/20 border-t border-purple-400/10">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-8 md:mb-0">
              <h3 className="text-2xl font-bold bg-gradient-to-r from-purple-300 to-white bg-clip-text text-transparent">
                ClaimChain
              </h3>
              <p className="text-purple-200/80 mt-2">
                Revolutionizing insurance with blockchain technology
              </p>
            </div>
            <div className="text-purple-200/80">
              <p>© 2024 ClaimChain. All rights reserved.</p>
              <p className="mt-2">Created with ❤️ for the future of insurance</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;