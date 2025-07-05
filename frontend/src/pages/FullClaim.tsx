import Navigation from "@/components/Navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { useState, useEffect } from "react";
import { Plus, CheckCircle2, AlertCircle } from "lucide-react";

// API call for validating medical report
type ValidationResult = {
  is_valid_report: boolean;
  reason: string;
  timestamp: string;
};

// Log entry type
interface LogEntry {
  type: 'success' | 'error' | 'info';
  message: string;
  details?: string;
  timestamp: string;
}

async function validateMedicalReport(file: File): Promise<ValidationResult> {
  const formData = new FormData();
  formData.append("file", file);
  
  try {
    const response = await fetch("http://localhost:8000/api/validate-medical-report", {
      method: "POST",
      body: formData,
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error("Validation API error:", errorText);
      throw new Error(errorText);
    }
    
    return response.json();
  } catch (error) {
    console.error("Validation request failed:", error);
    throw error;
  }
}

// API call for evaluating full claim
interface FullClaimResult {
  claimable_amount: number;
  reasoning: string;
  timestamp: string;
  claim_id: string;
}

async function evaluateFullClaim(dischargeFile: File, billFile: File, userId: string): Promise<FullClaimResult> {
  const formData = new FormData();
  formData.append("user_id", userId);
  formData.append("discharge_file", dischargeFile);
  formData.append("bill_file", billFile);
  const response = await fetch("http://localhost:8000/api/evaluate-full-claim", {
    method: "POST",
    body: formData,
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

async function sendVerificationEmail(claimId: string, email: string) {
  const response = await fetch(`http://localhost:8000/api/send-hospital-verification-email/${claimId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

async function checkClaimStatus(claimId: string) {
  const response = await fetch(`http://localhost:8000/api/claim-status/${claimId}`);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

const FullClaim = () => {
  const { toast } = useToast();
  const [userId, setUserId] = useState("");
  const [hospitalEmail, setHospitalEmail] = useState("");
  const [dischargeSummaryFile, setDischargeSummaryFile] = useState<File | null>(null);
  const [billFile, setBillFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [claimResult, setClaimResult] = useState<FullClaimResult | null>(null);
  const [claimStatus, setClaimStatus] = useState<string | null>(() => {
    // Initialize from localStorage if available
    return localStorage.getItem("claim_status") || null;
  });
  const [statusLoading, setStatusLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [hospitalEmails] = useState([
    { email: "apollo@hospital.com", verified: true },
    { email: "fortis@hospital.com", verified: false },
    { email: "aswinraaj2405@gmail.com", verified: true },
  ]);

  const addLog = (type: 'success' | 'error' | 'info', message: string, details?: string) => {
    setLogs(prev => [...prev, {
      type,
      message,
      details,
      timestamp: new Date().toLocaleTimeString()
    }]);
  };

  useEffect(() => {
    const storedUserId = localStorage.getItem("user_id");
    if (storedUserId) setUserId(storedUserId);

    // Load stored claim data
    const storedClaim = localStorage.getItem("claim_data");
    if (storedClaim) {
      setClaimResult(JSON.parse(storedClaim));
      addLog('info', 'Loaded previous claim data', JSON.stringify(JSON.parse(storedClaim), null, 2));
    }

    // Load email sent status
    const storedEmailSent = localStorage.getItem("email_sent");
    if (storedEmailSent) {
      setEmailSent(true);
      addLog('info', 'Previous verification email was sent');
    }
  }, []);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      if (!userId) throw new Error("User ID is required");
      if (!dischargeSummaryFile) throw new Error("Discharge summary file is required");
      if (!billFile) throw new Error("Hospital bill file is required");
      
      addLog('info', 'Starting claim submission process');
      
      // Step 1: Validate discharge summary
      addLog('info', 'Validating discharge summary...');
      const validation = await validateMedicalReport(dischargeSummaryFile);
      if (!validation.is_valid_report) {
        addLog('error', 'Discharge summary validation failed', validation.reason);
        throw new Error("Discharge summary validation failed: " + validation.reason);
      }
      addLog('success', 'Discharge summary validated successfully', validation.reason);
      toast({
        title: "Discharge Summary Validated",
        description: validation.reason,
      });

      // Step 2: Evaluate and store claim
      addLog('info', 'Evaluating claim...');
      const claim = await evaluateFullClaim(dischargeSummaryFile, billFile, userId);
      setClaimResult(claim);
      addLog('success', `Claim evaluated - Amount: ₹${claim.claimable_amount}`, claim.reasoning);
      
      // Store claim data in localStorage
      localStorage.setItem("claim_data", JSON.stringify(claim));

      toast({
        title: "Claim Submitted",
        description: "Your full claim has been submitted and analyzed.",
      });

      // Step 3: Send verification email only if not sent before
      if (!emailSent) {
        if (!hospitalEmail) {
          addLog('error', 'Hospital email required');
          toast({ 
            title: "Hospital Email Required", 
            description: "Please enter the hospital email to send verification.", 
            variant: "destructive" 
          });
          setIsSubmitting(false);
          return;
        }
        addLog('info', `Sending verification email to ${hospitalEmail}...`);
        await sendVerificationEmail(claim.claim_id, hospitalEmail);
        setEmailSent(true);
        localStorage.setItem("email_sent", "true");
        addLog('success', `Verification email sent to ${hospitalEmail}`);
        toast({ 
          title: "Verification Email Sent", 
          description: `Sent to ${hospitalEmail}` 
        });
      }
    } catch (err: any) {
      addLog('error', 'Submission error', err.message);
      toast({
        title: "Submission Error",
        description: err.message,
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCheckStatus = async () => {
    if (!claimResult?.claim_id) {
      addLog('error', 'No claim ID found');
      toast({ title: "No Claim", description: "Submit a claim first.", variant: "destructive" });
      return;
    }
    setStatusLoading(true);
    addLog('info', 'Checking claim status...');
    try {
      const status = await checkClaimStatus(claimResult.claim_id);
      setClaimStatus(status.status);
      // Store status in localStorage
      localStorage.setItem("claim_status", status.status);
      addLog('success', `Claim status: ${status.status}`);
    } catch (err: any) {
      addLog('error', 'Status check failed', err.message);
      toast({ title: "Status Error", description: err.message, variant: "destructive" });
    } finally {
      setStatusLoading(false);
    }
  };

  const handleClaimInsurance = async () => {
    try {
      addLog('info', 'Processing insurance claim...');
      toast({
        title: "Processing Claim",
        description: "Your insurance claim is being processed.",
      });
      
      // Clear all claim-related data from localStorage
      localStorage.removeItem("claim_data");
      localStorage.removeItem("claim_status");
      localStorage.removeItem("email_sent");
      
      // Show success message
      toast({
        title: "Success",
        description: "Your insurance claim has been processed successfully.",
      });
      
      // Refresh the page after a short delay to show the toast
      setTimeout(() => {
        window.location.reload();
      }, 1500);
      
    } catch (err: any) {
      addLog('error', 'Insurance claim processing failed', err.message);
      toast({
        title: "Error",
        description: "Failed to process insurance claim: " + err.message,
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-[#0f061e]">
      <Navigation />
      
      <div className="max-w-7xl mx-auto p-6 pt-32 flex gap-8">
        {/* Left side - Form */}
        <div className="flex-1">
          <Card className="bg-purple-900/10 border-purple-400/10 p-8">
            <h2 className="text-2xl font-bold mb-6 text-white">Full Claim Submission</h2>
            
            <div className="space-y-6">
              {/* Upload Section */}
              <div>
                <h3 className="text-lg font-semibold mb-4 text-white">Document Upload</h3>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="discharge-summary" className="text-white">Discharge Summary</Label>
                    <div className="mt-2 border-2 border-dashed border-purple-400/20 rounded-2xl p-6 text-center hover:border-purple-400/40 transition-colors">
                      <input type="file" accept=".pdf,.jpg,.png" className="hidden" id="discharge-summary" onChange={e => {
                        if (e.target.files && e.target.files[0]) {
                          setDischargeSummaryFile(e.target.files[0]);
                          addLog('info', `Discharge summary selected: ${e.target.files[0].name}`);
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
                    <Label htmlFor="bill-file" className="text-white">Hospital Bill</Label>
                    <div className="mt-2 border-2 border-dashed border-purple-400/20 rounded-2xl p-6 text-center hover:border-purple-400/40 transition-colors">
                      <input type="file" multiple accept=".pdf,.jpg,.png" className="hidden" id="bill-file" onChange={e => {
                        if (e.target.files && e.target.files[0]) {
                          setBillFile(e.target.files[0]);
                          addLog('info', `Hospital bill selected: ${e.target.files[0].name}`);
                        }
                      }} />
                      <label htmlFor="bill-file" className="cursor-pointer">
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

                  <div className="space-y-2">
                    <Label htmlFor="hospital-email" className="text-white">Hospital Email</Label>
                    <select
                      id="hospital-email"
                      value={hospitalEmail}
                      onChange={e => {
                        setHospitalEmail(e.target.value);
                        addLog('info', `Hospital email selected: ${e.target.value}`);
                      }}
                      className="w-full rounded-lg px-3 py-2 bg-[#2d174d] text-purple-100 border border-purple-700 focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="" disabled>Select hospital email</option>
                      {hospitalEmails.map(h => (
                        <option key={h.email} value={h.email}>
                          {h.email} {h.verified ? '(Verified)' : ''}
                        </option>
                      ))}
                    </select>
                  </div>

                  <Button 
                    onClick={handleSubmit}
                    className="w-full bg-purple-600 text-white hover:bg-purple-700 py-6 rounded-xl shadow-lg shadow-purple-500/20 text-lg"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? "Submitting..." : "Submit Full Claim"}
                  </Button>
                </div>
              </div>
            </div>
          </Card>

          {/* AI Analysis Results */}
          {claimResult && (
            <Card className="bg-purple-900/10 border-purple-400/10 p-8 mt-8">
              <h3 className="text-lg font-semibold text-white mb-6">AI Analysis Results</h3>
              <div className="space-y-4">
                <div className="bg-purple-900/20 p-4 rounded-xl">
                  <h4 className="font-medium mb-2 text-white">Claimable Amount</h4>
                  <p className="text-2xl font-bold text-purple-300">₹{claimResult.claimable_amount.toLocaleString()}</p>
                </div>
                <div className="bg-purple-900/20 p-4 rounded-xl">
                  <h4 className="font-medium mb-2 text-white">Reasoning</h4>
                  <p className="text-sm text-purple-200/80">{claimResult.reasoning}</p>
                </div>
                <div className="bg-purple-900/20 p-4 rounded-xl">
                  <h4 className="font-medium mb-2 text-white">Claim ID</h4>
                  <p className="text-sm text-purple-200/80">{claimResult.claim_id}</p>
                </div>
              </div>

              <div className="space-y-2 mt-4">
                <Button onClick={handleCheckStatus} disabled={statusLoading || !claimResult?.claim_id} className="w-full">
                  {statusLoading ? "Checking Status..." : "Check Claim Status"}
                </Button>
                {claimStatus && (
                  <div className="text-white mt-2 space-y-2">
                    <div>Claim Status: <span className="font-bold text-purple-300">{claimStatus}</span></div>
                    {claimStatus === "approved" && (
                      <Button 
                        onClick={handleClaimInsurance}
                        className="w-full bg-green-600 hover:bg-green-700 text-white"
                      >
                        Claim Insurance
                      </Button>
                    )}
                  </div>
                )}
              </div>
            </Card>
          )}
        </div>

        {/* Right side - Logs */}
        <div className="w-96">
          <Card className="bg-purple-900/10 border-purple-400/10 p-6 sticky top-32">
            <h3 className="text-lg font-semibold text-white mb-4">Processing Logs</h3>
            <div className="space-y-3 max-h-[calc(100vh-200px)] overflow-y-auto">
              {logs.map((log, index) => (
                <div key={index} className="bg-purple-900/20 p-3 rounded-lg">
                  <div className="flex items-start gap-2">
                    {log.type === 'success' && <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />}
                    {log.type === 'error' && <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />}
                    {log.type === 'info' && <div className="w-5 h-5 rounded-full bg-blue-400/20 flex-shrink-0 mt-0.5" />}
                    <div className="flex-1">
                      <p className="text-sm text-white">{log.message}</p>
                      {log.details && (
                        <pre className="mt-2 text-xs text-purple-200/70 whitespace-pre-wrap">
                          {log.details}
                        </pre>
                      )}
                      <p className="text-xs text-purple-300/50 mt-1">{log.timestamp}</p>
                    </div>
                  </div>
                </div>
              ))}
              {logs.length === 0 && (
                <div className="text-center text-purple-200/50 py-4">
                  No logs yet. Start by uploading documents.
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default FullClaim;