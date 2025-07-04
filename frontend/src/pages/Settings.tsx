import Navigation from "@/components/Navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";

const Settings = ({ onLogout }: { onLogout?: () => void }) => {
  const { toast } = useToast();
  const [aiConsent, setAiConsent] = useState(true);
  const [dataSharing, setDataSharing] = useState(true);

  const handleSaveSettings = () => {
    toast({
      title: "Settings Saved",
      description: "Your preferences have been updated successfully.",
    });
  };

  return (
    <div className="min-h-screen bg-[#0f061e]">
      <Navigation onLogout={onLogout} />
      
      <div className="max-w-4xl mx-auto p-6 pt-32 space-y-8">
        {/* Privacy & AI Settings */}
        <Card className="bg-purple-900/10 border-purple-400/10 p-6">
          <h3 className="text-lg font-semibold mb-6 text-white">Privacy & AI Settings</h3>
          
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="ai-consent" className="text-white">AI Analysis Consent</Label>
                <p className="text-sm text-purple-200/80">
                  Allow Gemini AI to analyze your medical documents and provide claim insights
                </p>
              </div>
              <Switch 
                id="ai-consent"
                checked={aiConsent}
                onCheckedChange={setAiConsent}
                className="data-[state=checked]:bg-purple-600"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="data-sharing" className="text-white">Data Sharing with Insurer</Label>
                <p className="text-sm text-purple-200/80">
                  Share health data and claim information with your insurance provider
                </p>
              </div>
              <Switch 
                id="data-sharing"
                checked={dataSharing}
                onCheckedChange={setDataSharing}
                className="data-[state=checked]:bg-purple-600"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="auto-claims" className="text-white">Automatic Claim Triggering</Label>
                <p className="text-sm text-purple-200/80">
                  Automatically trigger claims when critical health events are detected
                </p>
              </div>
              <Switch 
                id="auto-claims" 
                defaultChecked 
                className="data-[state=checked]:bg-purple-600"
              />
            </div>
          </div>
        </Card>

        {/* Blockchain Settings */}
        <Card className="card-elegant p-6">
          <h3 className="text-lg font-semibold mb-6">Blockchain Configuration</h3>
          
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="wallet-address">Ethereum Wallet Address</Label>
              <Input 
                id="wallet-address" 
                value="0x742d35Cc6671C0532925a3b8D5c0894f8B9bc8b4"
                className="font-mono text-sm bg-secondary/30"
                readOnly
              />
              <p className="text-xs text-muted-foreground">
                This wallet will receive approved claim funds
              </p>
            </div>

            <div className="flex items-center gap-4">
              <Button variant="outline" className="border-primary text-primary hover:bg-primary/10">
                Change Wallet
              </Button>
              <Button variant="outline">
                View on Etherscan
              </Button>
            </div>

            <div className="bg-primary/10 p-4 rounded-xl">
              <h4 className="font-medium mb-2">Smart Contract Status</h4>
              <div className="flex items-center justify-between">
                <span className="text-sm">Contract Address:</span>
                <code className="text-xs bg-secondary/50 px-2 py-1 rounded">0x1a2b...c9d8</code>
              </div>
              <div className="flex items-center justify-between mt-2">
                <span className="text-sm">Network:</span>
                <span className="text-sm font-medium">Ethereum Mainnet</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Language & Localization */}
        <Card className="card-elegant p-6">
          <h3 className="text-lg font-semibold mb-6">Language & Localization</h3>
          
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="language">Interface Language</Label>
              <Select defaultValue="en">
                <SelectTrigger>
                  <SelectValue placeholder="Select language" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="es">Español</SelectItem>
                  <SelectItem value="fr">Français</SelectItem>
                  <SelectItem value="de">Deutsch</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="timezone">Timezone</Label>
              <Select defaultValue="pst">
                <SelectTrigger>
                  <SelectValue placeholder="Select timezone" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pst">Pacific Standard Time (PST)</SelectItem>
                  <SelectItem value="est">Eastern Standard Time (EST)</SelectItem>
                  <SelectItem value="cst">Central Standard Time (CST)</SelectItem>
                  <SelectItem value="mst">Mountain Standard Time (MST)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="currency">Currency Display</Label>
              <Select defaultValue="usd">
                <SelectTrigger>
                  <SelectValue placeholder="Select currency" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="usd">USD ($)</SelectItem>
                  <SelectItem value="eur">EUR (€)</SelectItem>
                  <SelectItem value="gbp">GBP (£)</SelectItem>
                  <SelectItem value="cad">CAD (C$)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </Card>

        {/* Notification Settings */}
        <Card className="card-elegant p-6">
          <h3 className="text-lg font-semibold mb-6">Notifications</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label>Claim Status Updates</Label>
                <p className="text-sm text-muted-foreground">Get notified about claim processing status</p>
              </div>
              <Switch defaultChecked />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label>Health Event Alerts</Label>
                <p className="text-sm text-muted-foreground">Receive alerts for detected health events</p>
              </div>
              <Switch defaultChecked />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label>Blockchain Confirmations</Label>
                <p className="text-sm text-muted-foreground">Notifications for blockchain transactions</p>
              </div>
              <Switch defaultChecked />
            </div>
          </div>
        </Card>

        {/* Save Settings */}
        <div className="flex justify-center">
          <Button 
            onClick={handleSaveSettings} 
            className="bg-purple-600 text-white hover:bg-purple-700 px-8 py-6 rounded-xl shadow-lg shadow-purple-500/20"
          >
            Save All Settings
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Settings;