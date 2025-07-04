import Navigation from "@/components/Navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";

const FullClaim = () => {
  const { toast } = useToast();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);

  const handleFileUpload = () => {
    setIsAnalyzing(true);
    // Simulate AI analysis
    setTimeout(() => {
      setIsAnalyzing(false);
      setAnalysisComplete(true);
      toast({
        title: "Documents Analyzed",
        description: "AI has successfully analyzed your medical documents.",
      });
    }, 3000);
  };

  const handleSubmit = () => {
    toast({
      title: "Claim Submitted",
      description: "Your full claim has been submitted for blockchain processing.",
    });
  };

  return (
    <div className="min-h-screen bg-[#0f061e]">
      <Navigation />
      
      <div className="max-w-6xl mx-auto p-6 pt-32 space-y-8">
        <Card className="bg-purple-900/10 border-purple-400/10 p-8">
          <h2 className="text-2xl font-bold mb-6 text-white">Full Claim Submission</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Upload Section */}
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4 text-white">Document Upload</h3>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="hospital-docs" className="text-white">Hospital Bill</Label>
                    <div className="mt-2 border-2 border-dashed border-purple-400/20 rounded-2xl p-6 text-center hover:border-purple-400/40 transition-colors">
                      <input type="file" multiple accept=".pdf,.jpg,.png" className="hidden" id="hospital-docs" />
                      <label htmlFor="hospital-docs" className="cursor-pointer">
                        <div className="space-y-2">
                          <div className="mx-auto w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center">
                            <span className="text-purple-300">🏥</span>
                          </div>
                          <p className="text-sm font-medium text-white">Upload Hospital Bill</p>
                          <p className="text-xs text-purple-200/80">PDF, JPG, PNG up to 10MB each</p>
                        </div>
                      </label>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="discharge-summary" className="text-white">Discharge Summary</Label>
                    <div className="mt-2 border-2 border-dashed border-purple-400/20 rounded-2xl p-6 text-center hover:border-purple-400/40 transition-colors">
                      <input type="file" accept=".pdf,.jpg,.png" className="hidden" id="discharge-summary" />
                      <label htmlFor="discharge-summary" className="cursor-pointer">
                        <div className="space-y-2">
                          <div className="mx-auto w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center">
                            <span className="text-purple-300">📋</span>
                          </div>
                          <p className="text-sm font-medium text-white">Upload Discharge Summary</p>
                          <p className="text-xs text-purple-200/80">Medical discharge documentation</p>
                        </div>
                      </label>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="digital-certificate" className="text-white">Digital Certificate</Label>
                    <div className="mt-2 border-2 border-dashed border-purple-400/20 rounded-2xl p-6 text-center hover:border-purple-400/40 transition-colors">
                      <input type="file" accept=".pdf,.jpg,.png" className="hidden" id="digital-certificate" />
                      <label htmlFor="digital-certificate" className="cursor-pointer">
                        <div className="space-y-2">
                          <div className="mx-auto w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center">
                            <span className="text-purple-300">🏆</span>
                          </div>
                          <p className="text-sm font-medium text-white">Upload Digital Certificate</p>
                          <p className="text-xs text-purple-200/80">Medical certification document</p>
                        </div>
                      </label>
                    </div>
                  </div>

                  <Button 
                    onClick={handleFileUpload}
                    className="w-full bg-purple-600 text-white hover:bg-purple-700 py-6 rounded-xl shadow-lg shadow-purple-500/20 text-lg"
                    disabled={isAnalyzing}
                  >
                    {isAnalyzing ? "Analyzing Documents..." : "Analyze Documents with AI"}
                  </Button>
                </div>
              </div>
            </div>

            {/* AI Analysis Results */}
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-white">AI Analysis Results</h3>
              
              {isAnalyzing && (
                <div className="bg-purple-900/20 p-6 rounded-2xl">
                  <div className="animate-pulse">
                    <p className="text-sm text-purple-300">🤖 Gemini AI is analyzing your documents...</p>
                    <div className="mt-4 space-y-2">
                      <div className="h-4 bg-purple-500/20 rounded w-3/4"></div>
                      <div className="h-4 bg-purple-500/20 rounded w-1/2"></div>
                    </div>
                  </div>
                </div>
              )}

              {analysisComplete && (
                <div className="space-y-4">
                  <div className="bg-purple-900/20 p-4 rounded-xl">
                    <h4 className="font-medium mb-2 text-white">Diagnosis Detected</h4>
                    <p className="text-sm text-purple-200/80">Acute Myocardial Infarction (Heart Attack)</p>
                    <Badge className="bg-green-500/20 text-green-300 mt-2">High Confidence</Badge>
                  </div>

                  <div className="bg-purple-900/20 p-4 rounded-xl">
                    <h4 className="font-medium mb-2 text-white">Estimated Medical Cost</h4>
                    <p className="text-2xl font-bold text-purple-300">$15,450</p>
                    <p className="text-sm text-purple-200/80">Based on treatment codes and hospital billing</p>
                  </div>

                  <div className="bg-purple-900/20 p-4 rounded-xl">
                    <h4 className="font-medium mb-2 text-white">Policy Eligibility</h4>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-green-300">Covered under Emergency Care Policy</span>
                    </div>
                    <p className="text-sm text-purple-200/80 mt-1">
                      Deductible: $500 | Coverage: 90%
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Form Fields */}
          {analysisComplete && (
            <div className="mt-8 space-y-6">
              <h3 className="text-lg font-semibold text-white">Claim Details (Auto-filled by AI)</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="diagnosis" className="text-white">Diagnosis</Label>
                  <Input 
                    id="diagnosis" 
                    value="Acute Myocardial Infarction" 
                    className="bg-purple-900/20 text-white border-purple-400/20"
                    readOnly 
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="treatment-date" className="text-white">Treatment Date</Label>
                  <Input 
                    id="treatment-date" 
                    value="2024-01-15" 
                    type="date"
                    className="bg-purple-900/20 text-white border-purple-400/20"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="hospital" className="text-white">Hospital/Clinic</Label>
                  <Input 
                    id="hospital" 
                    value="St. Mary's Medical Center" 
                    className="bg-purple-900/20 text-white border-purple-400/20"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="claim-amount" className="text-white">Claim Amount</Label>
                  <Input 
                    id="claim-amount" 
                    value="$15,450" 
                    className="bg-purple-900/20 text-white border-purple-400/20"
                    readOnly 
                  />
                </div>
              </div>

              <div className="flex justify-center mt-8">
                <Button 
                  onClick={handleSubmit}
                  className="bg-purple-600 text-white hover:bg-purple-700 px-8 py-6 rounded-xl shadow-lg shadow-purple-500/20 text-lg font-medium"
                >
                  Submit Full Claim
                </Button>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default FullClaim;