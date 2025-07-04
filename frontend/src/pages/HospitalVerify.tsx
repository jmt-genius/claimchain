import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useToast } from "@/components/ui/use-toast";

export default function HospitalVerify() {
  const [searchParams] = useSearchParams();
  const claimId = searchParams.get("claim_id");
  const [dischargeFile, setDischargeFile] = useState<File | null>(null);
  const [billFile, setBillFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (!claimId) {
      setError("No claim ID provided in URL");
    }
  }, [claimId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!claimId || !dischargeFile || !billFile) {
      setError("Please provide both discharge summary and bill files");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setSuccess(null);

    const formData = new FormData();
    formData.append("discharge_file", dischargeFile);
    formData.append("bill_file", billFile);

    try {
      const response = await fetch(`http://localhost:8000/api/verify-hospital-upload/${claimId}`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Verification failed");
      }

      if (data.success) {
        setSuccess(data.message);
        toast({
          title: "Success",
          description: data.message,
        });
      } else {
        setError(data.reason || "Verification failed");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to verify documents");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <Card className="max-w-2xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-6">Hospital Claim Verification</h1>
        
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-4">
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">
              Discharge Summary
            </label>
            <Input
              type="file"
              onChange={(e) => setDischargeFile(e.target.files?.[0] || null)}
              accept=".pdf"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Medical Bill
            </label>
            <Input
              type="file"
              onChange={(e) => setBillFile(e.target.files?.[0] || null)}
              accept=".pdf"
              required
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={isSubmitting || !claimId || !dischargeFile || !billFile}
          >
            {isSubmitting ? "Verifying..." : "Submit for Verification"}
          </Button>
        </form>
      </Card>
    </div>
  );
}