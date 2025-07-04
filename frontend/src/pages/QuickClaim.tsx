import Navigation from "@/components/Navigation";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

const QuickClaim = () => {
  const { toast } = useToast();

  const handleSubmitClaim = () => {
    toast({
      title: "Claim Submitted Successfully",
      description: "Your claim has been submitted to the blockchain for processing.",
    });
  };

  return (
    <div className="min-h-screen bg-[#0f061e]">
      <Navigation />
      
      <div className="max-w-4xl mx-auto p-6 pt-32 space-y-8">
        <Card className="bg-purple-900/10 border-purple-400/10 p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Quick Claim - Cardiac Event Detected</h2>
            <Badge className="bg-yellow-500/20 text-yellow-300">Auto-Triggered</Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Event Details */}
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4 text-white">Event Details</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-purple-200/80">Timestamp:</span>
                    <span className="font-medium text-white">2024-01-15 14:32:18</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-purple-200/80">Heart Rate Spike:</span>
                    <span className="font-medium text-yellow-300">165 BPM → 195 BPM</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-purple-200/80">Duration:</span>
                    <span className="font-medium text-white">4 minutes 32 seconds</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-purple-200/80">Location:</span>
                    <span className="font-medium text-white">Home (GPS verified)</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4 text-white">Device Data</h3>
                <div className="bg-purple-900/20 p-4 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-purple-200/80">Fitbit Charge 6</span>
                    <Badge className="bg-green-500/20 text-green-300">Connected</Badge>
                  </div>
                  <p className="text-sm text-purple-200/80">Irregular heart rhythm detected with sustained high BPM reading</p>
                </div>
              </div>
            </div>

            {/* AI Analysis */}
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4 text-white">AI Analysis Results</h3>
                <div className="space-y-4">
                  <div className="bg-purple-900/20 p-4 rounded-xl">
                    <h4 className="font-medium mb-2 text-white">Policy Match</h4>
                    <p className="text-sm text-purple-200/80">
                      Cardiac Event Coverage (Policy #HC-2024-0892)
                    </p>
                    <div className="flex items-center mt-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      <span className="text-sm text-green-300">Eligible for claim</span>
                    </div>
                  </div>

                  <div className="bg-purple-900/20 p-4 rounded-xl">
                    <h4 className="font-medium mb-2 text-white">Estimated Claim Amount</h4>
                    <p className="text-2xl font-bold text-purple-300">$2,850</p>
                    <p className="text-sm text-purple-200/80">
                      Based on policy terms and event severity
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4 text-white">Blockchain Status</h3>
                <div className="bg-purple-900/20 p-4 rounded-xl">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-purple-200/80">Smart Contract:</span>
                    <Badge className="bg-purple-500/20 text-purple-300">Ready</Badge>
                  </div>
                  <p className="text-xs text-purple-200/80 mt-2">
                    0x742d35Cc6671C0532925a3b8D5c0894f8B9bc8b4
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 flex justify-center">
            <Button 
              onClick={handleSubmitClaim}
              className="bg-purple-600 text-white hover:bg-purple-700 px-8 py-6 rounded-xl shadow-lg shadow-purple-500/20 text-lg font-medium"
            >
              Submit Claim to Blockchain
            </Button>
          </div>
        </Card>

        {/* Status Tracking */}
        <Card className="bg-purple-900/10 border-purple-400/10 p-6">
          <h3 className="text-lg font-semibold mb-4 text-white">Claim Status</h3>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm text-purple-200/80">Event Detected</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm text-purple-200/80">AI Analysis Complete</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <span className="text-sm text-purple-200/80">Awaiting Submission</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-purple-500/40 rounded-full"></div>
              <span className="text-sm text-purple-200/60">Blockchain Processing</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default QuickClaim;