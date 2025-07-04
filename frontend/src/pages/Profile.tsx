import Navigation from "@/components/Navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";

const Profile = () => {
  const { toast } = useToast();
  const [isEditing, setIsEditing] = useState(false);

  const handleSave = () => {
    setIsEditing(false);
    toast({
      title: "Profile Updated",
      description: "Your profile information has been saved successfully.",
    });
  };

  return (
    <div className="min-h-screen bg-[#0f061e]">
      <Navigation />
      
      <div className="max-w-4xl mx-auto p-6 pt-32 space-y-8">
        {/* Profile Header */}
        <Card className="bg-purple-900/10 border-purple-400/10 p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">User Profile</h2>
            <Button 
              onClick={() => setIsEditing(!isEditing)}
              variant="outline"
              className="border-purple-400/20 text-purple-100 hover:bg-purple-500/10"
            >
              {isEditing ? "Cancel" : "Edit Profile"}
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Personal Information */}
            <div className="space-y-6">
              <h3 className="text-lg font-semibold">Personal Information</h3>
              
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="full-name">Full Name</Label>
                  <Input 
                    id="full-name" 
                    value="John Michael Smith" 
                    readOnly={!isEditing}
                    className={!isEditing ? "bg-secondary/30" : ""}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input 
                    id="email" 
                    value="john.smith@email.com" 
                    readOnly={!isEditing}
                    className={!isEditing ? "bg-secondary/30" : ""}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input 
                    id="phone" 
                    value="+1 (555) 123-4567" 
                    readOnly={!isEditing}
                    className={!isEditing ? "bg-secondary/30" : ""}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="dob">Date of Birth</Label>
                  <Input 
                    id="dob" 
                    value="1985-03-15" 
                    type="date"
                    readOnly={!isEditing}
                    className={!isEditing ? "bg-secondary/30" : ""}
                  />
                </div>
              </div>
            </div>

            {/* Insurance Information */}
            <div className="space-y-6">
              <h3 className="text-lg font-semibold">Insurance Information</h3>
              
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="policy-number">Policy Number</Label>
                  <Input 
                    id="policy-number" 
                    value="HC-2024-0892-JS" 
                    readOnly
                    className="bg-secondary/30"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="provider">Insurance Provider</Label>
                  <Input 
                    id="provider" 
                    value="HealthGuard Insurance Co." 
                    readOnly
                    className="bg-secondary/30"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="coverage-type">Coverage Type</Label>
                  <Input 
                    id="coverage-type" 
                    value="Comprehensive Health & Cardiac Care" 
                    readOnly
                    className="bg-secondary/30"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="expiry">Policy Expiry</Label>
                  <Input 
                    id="expiry" 
                    value="2024-12-31" 
                    type="date"
                    readOnly
                    className="bg-secondary/30"
                  />
                </div>
              </div>
            </div>
          </div>

          {isEditing && (
            <div className="mt-6 flex justify-center">
              <Button onClick={handleSave} className="btn-primary px-6">
                Save Changes
              </Button>
            </div>
          )}
        </Card>

        {/* Connected Devices */}
        <Card className="bg-purple-900/10 border-purple-400/10 p-6">
          <h3 className="text-lg font-semibold mb-4 text-white">Connected Devices</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-secondary/30 rounded-xl">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center">
                  <span className="text-primary text-xl">⌚</span>
                </div>
                <div>
                  <h4 className="font-medium text-white">Fitbit Charge 6</h4>
                  <p className="text-sm text-muted-foreground">Connected • Last sync: 2 minutes ago</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge className="bg-success/20 text-success">Active</Badge>
                <Button variant="outline" size="sm">Manage</Button>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 border border-dashed border-border rounded-xl">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-muted/20 rounded-full flex items-center justify-center">
                  <span className="text-muted-foreground text-xl">+</span>
                </div>
                <div>
                  <h4 className="font-medium text-muted-foreground">Add New Device</h4>
                  <p className="text-sm text-muted-foreground">Connect additional wearables</p>
                </div>
              </div>
              <Button variant="outline" size="sm" disabled>
                Coming Soon
              </Button>
            </div>
          </div>
        </Card>

        {/* Fitbit Sync Status */}
        <Card className="bg-purple-900/10 border-purple-400/10 p-6">
          <h3 className="text-lg font-semibold mb-4 text-white">Health Data Overview</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-primary/10 p-4 rounded-xl text-center">
              <p className="text-2xl font-bold text-primary">72</p>
              <p className="text-sm text-muted-foreground">Avg Resting HR</p>
            </div>
            <div className="bg-accent/10 p-4 rounded-xl text-center">
              <p className="text-2xl font-bold text-accent">8,542</p>
              <p className="text-sm text-muted-foreground">Daily Steps</p>
            </div>
            <div className="bg-success/10 p-4 rounded-xl text-center">
              <p className="text-2xl font-bold text-success">7.2h</p>
              <p className="text-sm text-muted-foreground">Sleep Duration</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Profile;