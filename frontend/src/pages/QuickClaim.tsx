import React, { useState, useEffect } from "react";
import Navigation from "@/components/Navigation";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { TransactionBlock } from '@mysten/sui.js/transactions';
import { useSignAndExecuteTransaction, useCurrentAccount, useSuiClient, ConnectButton } from '@mysten/dapp-kit';
// import CLAIMCHAIN_PACKAGE_ID from your constants
const CLAIMCHAIN_PACKAGE_ID = "0xa99c8b24de53973617958a26d2ea865c9528c748b69ffa3a49408a1dad678022";

const QuickClaim = () => {
  const { toast } = useToast();
  const [userId, setUserId] = useState("");
  const [loading, setLoading] = useState(false);
  const [claimResult, setClaimResult] = useState<null | {
    claimable_amount: number;
    quick_claim_amount: number;
    reason: string;
  }>(null);
  const [error, setError] = useState<string | null>(null);
  const [suiCoins, setSuiCoins] = useState([]);

  const { mutate: signAndExecute } = useSignAndExecuteTransaction();
  const account = useCurrentAccount();
  const suiClient = useSuiClient();

  useEffect(() => {
    if (!account?.address) return;
    suiClient.getCoins({ owner: account.address, coinType: "0x2::sui::SUI" })
      .then(res => setSuiCoins(res.data))
      .catch(() => setSuiCoins([]));
  }, [account?.address]);

  const handleSubmitClaim = async () => {
    setError(null);
    setClaimResult(null);
    if (!userId) {
      setError("Please enter your User ID to proceed.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/calculate-claim", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId }),
      });
      if (res.status === 404) {
        const data = await res.json();
        setError(data.detail || "No cardiac event found for this user.");
        setLoading(false);
        return;
      }
      if (!res.ok) {
        const data = await res.json();
        setError(data.detail || "An error occurred while calculating the claim.");
        setLoading(false);
        return;
      }
      const data = await res.json();
      setClaimResult(data);
    } catch (e) {
      setError("Could not connect to the server.");
    } finally {
      setLoading(false);
    }
  };

  const suiClaimAmount = (claimResult?.claimable_amount || 0) / 100000;

  const handleSendSuiClaim = (suiClaimAmount) => {
    if (!account?.address || suiCoins.length === 0) return;

    const tx = new TransactionBlock();
    tx.setGasBudget(100000000);

    // Pick the first coin (or let user select)
    const coinObjectId = suiCoins[0].coinObjectId;

    tx.moveCall({
      target: `${CLAIMCHAIN_PACKAGE_ID}::ClaimChain::send_sui`,
      arguments: [
        tx.object(coinObjectId), // Pass the coin object
        tx.pure.u64(Math.floor(suiClaimAmount * 1_000_000_000)), // SUI to MIST
        tx.pure.address(account.address),
      ],
    });

    signAndExecute({
      transaction: tx.serialize(),
    }, {
      onSuccess: (response) => {
        toast({ title: "SUI claim sent!", description: "Check your wallet for the transaction." });
      },
      onError: (error) => {
        toast({ title: "Failed to send SUI claim", description: error.message || String(error), variant: "destructive" });
      },
    });
  };

  return (
    <div className="min-h-screen bg-[#0f061e]">
      <Navigation />
      <div className="max-w-2xl mx-auto p-6 pt-32 space-y-8">
        <div className="mb-8 w-full flex justify-center">
          <ConnectButton />
        </div>
        <Card className="bg-purple-900/10 border-purple-400/10 p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Quick Claim</h2>
            <Badge className="bg-yellow-500/20 text-yellow-300">Auto-Triggered</Badge>
          </div>

          {/* User ID Input */}
          <div className="mb-8 flex flex-col md:flex-row md:items-center gap-4">
            <label className="text-purple-200/80 font-medium" htmlFor="user-id-input">
              User ID:
            </label>
            <input
              id="user-id-input"
              type="text"
              className="px-4 py-2 rounded-lg bg-purple-900/20 text-white border border-purple-400/30 focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter your User ID"
              value={userId}
              onChange={e => setUserId(e.target.value)}
              disabled={loading}
              autoComplete="off"
              style={{ minWidth: 200 }}
            />
          </div>

          {/* AI Analysis */}
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-4 text-white">AI Analysis Results</h3>
              <div className="bg-purple-900/20 p-4 rounded-xl min-h-[120px] flex flex-col justify-center">
                {error ? (
                  <p className="text-red-400 text-base font-medium">{error}</p>
                ) : claimResult ? (
                  <>
                    <h4 className="font-medium mb-2 text-white">Estimated Claim Amount</h4>
                    <p className="text-2xl font-bold text-purple-300">
                      ₹{claimResult.claimable_amount.toLocaleString()} (Quick: ₹{claimResult.quick_claim_amount.toLocaleString()})
                    </p>
                    <p className="text-sm text-purple-200/80 mt-2">{claimResult.reason}</p>
                  </>
                ) : (
                  <p className="text-purple-200/80">Enter User ID and click Quick Claim to calculate your claim amount.</p>
                )}
              </div>
            </div>
          </div>

          {claimResult && (
            <div className="mt-8">
              <h4 className="font-medium mb-2 text-white">SUI Claim Amount</h4>
              <p className="text-2xl font-bold text-purple-300">
                {suiClaimAmount.toFixed(6)} SUI
              </p>
              <Button
                onClick={() => handleSendSuiClaim(suiClaimAmount)}
                className="bg-purple-600 text-white hover:bg-purple-700 px-8 py-6 rounded-xl shadow-lg shadow-purple-500/20 text-lg font-medium mt-4"
                disabled={loading}
              >
                Claim SUI
              </Button>
            </div>
          )}

          <div className="mt-8 flex justify-center">
            <Button
              onClick={handleSubmitClaim}
              className="bg-purple-600 text-white hover:bg-purple-700 px-8 py-6 rounded-xl shadow-lg shadow-purple-500/20 text-lg font-medium"
              disabled={loading}
            >
              {loading ? "Calculating..." : "Quick Claim"}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default QuickClaim;