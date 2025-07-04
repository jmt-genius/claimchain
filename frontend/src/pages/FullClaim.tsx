import Navigation from "@/components/Navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";

// API call for validating medical report
type ValidationResult = {
  is_valid_report: boolean;
  reason: string;
  timestamp: string;
};

async function validateMedicalReport(file: File): Promise<ValidationResult> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch("http://localhost:8000/api/validate-medical-report", {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

// API call for evaluating full claim
interface FullClaimResult {
  claimable_amount: number;
  reasoning: string;
  timestamp: string;
}

async function evaluateFullClaim(policyFile: File, dischargeFile: File, billFile: File): Promise<FullClaimResult> {
  const formData = new FormData();
  formData.append("policy_file", policyFile);
  formData.append("discharge_file", dischargeFile);
  formData.append("bill_file", billFile);
  const response = await fetch("http://localhost:8000/api/evaluate-full-claim", {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

const FullClaim = () => {
  const { toast } = useToast();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [dischargeSummaryFile, setDischargeSummaryFile] = useState<File | null>(null);
  const [policyFile, setPolicyFile] = useState<File | null>(null);
  const [billFile, setBillFile] = useState<File | null>(null);
  const [validationLog, setValidationLog] = useState<string | null>(null);
  const [validationStatus, setValidationStatus] = useState<"pending" | "success" | "error" | null>(null);
  const [analysisLog, setAnalysisLog] = useState<string | null>(null);
  const [claimResult, setClaimResult] = useState<FullClaimResult | null>(null);

  const handleFileUpload = async () => {
    setIsAnalyzing(true);
    setValidationStatus("pending");
    setValidationLog("Validating discharge summary...");
    setAnalysisLog(null);
    setClaimResult(null);
    setAnalysisComplete(false);
    try {
      if (!dischargeSummaryFile) {
        setValidationStatus("error");
        setValidationLog("No discharge summary file selected.");
        setIsAnalyzing(false);
        return;
      }
      if (!policyFile) {
        setValidationStatus("error");
        setValidationLog("No policy file selected.");
        setIsAnalyzing(false);
        return;
      }
      if (!billFile) {
        setValidationStatus("error");
        setValidationLog("No hospital bill file selected.");
        setIsAnalyzing(false);
        return;
      }
      // Step 1: Validate discharge summary
      const result = await validateMedicalReport(dischargeSummaryFile);
      if (result.is_valid_report) {
        setValidationStatus("success");
        setValidationLog(`Validation successful: ${result.reason}`);
        setAnalysisLog("Evaluating full claim with AI...");
        // Step 2: Evaluate full claim
        try {
          const claim = await evaluateFullClaim(policyFile, dischargeSummaryFile, billFile);
          setClaimResult(claim);
          setAnalysisLog("Full claim evaluated successfully.");
          setAnalysisComplete(true);
          setIsAnalyzing(false);
          toast({
            title: "Documents Analyzed",
            description: "AI has successfully analyzed your medical documents.",
          });
        } catch (claimErr: any) {
          setAnalysisLog(`Error evaluating full claim: ${claimErr.message}`);
          setIsAnalyzing(false);
        }
      } else {
        setValidationStatus("error");
        setValidationLog(`Validation failed: ${result.reason}`);
        setIsAnalyzing(false);
      }
    } catch (err: any) {
      setValidationStatus("error");
      setValidationLog(`Validation error: ${err.message}`);
      setIsAnalyzing(false);
    }
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
                      <input type="file" multiple accept=".pdf,.jpg,.png" className="hidden" id="hospital-docs" onChange={e => {
                        if (e.target.files && e.target.files[0]) {
                          setBillFile(e.target.files[0]);
                        }
                      }} />
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
                      <input type="file" accept=".pdf,.jpg,.png" className="hidden" id="discharge-summary" onChange={e => {
                        if (e.target.files && e.target.files[0]) {
                          setDischargeSummaryFile(e.target.files[0]);
                        }
                      }} />
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
                    <Label htmlFor="policy-docs" className="text-white">Policy Document</Label>
                    <div className="mt-2 border-2 border-dashed border-purple-400/20 rounded-2xl p-6 text-center hover:border-purple-400/40 transition-colors">
                      <input type="file" accept=".pdf,.jpg,.png" className="hidden" id="policy-docs" onChange={e => {
                        if (e.target.files && e.target.files[0]) {
                          setPolicyFile(e.target.files[0]);
                        }
                      }} />
                      <label htmlFor="policy-docs" className="cursor-pointer">
                        <div className="space-y-2">
                          <div className="mx-auto w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center">
                            <span className="text-purple-300">📄</span>
                          </div>
                          <p className="text-sm font-medium text-white">Policy Document</p>
                          <p className="text-xs text-purple-200/80">PDF up to 10MB</p>
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
              
              {validationStatus && (
                <div className="bg-purple-900/20 p-4 rounded-xl mb-2">
                  <p className={`text-sm ${validationStatus === "success" ? "text-green-300" : validationStatus === "pending" ? "text-purple-300" : "text-red-300"}`}>
                    {validationLog}
                  </p>
                </div>
              )}

              {analysisLog && (
                <div className="bg-purple-900/20 p-4 rounded-xl mb-2">
                  <p className="text-sm text-purple-300">{analysisLog}</p>
                </div>
              )}

              {isAnalyzing && validationStatus !== "error" && (
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

              {claimResult && (
                <div className="space-y-4">
                  <div className="bg-purple-900/20 p-4 rounded-xl">
                    <h4 className="font-medium mb-2 text-white">Claimable Amount</h4>
                    <p className="text-2xl font-bold text-purple-300">₹{claimResult.claimable_amount.toLocaleString()}</p>
                  </div>
                  <div className="bg-purple-900/20 p-4 rounded-xl">
                    <h4 className="font-medium mb-2 text-white">Reasoning</h4>
                    <p className="text-sm text-purple-200/80">{claimResult.reasoning}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default FullClaim;