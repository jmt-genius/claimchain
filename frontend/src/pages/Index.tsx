import Navigation from "@/components/Navigation";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";

const Index = () => {
  const navigate = useNavigate();

  const recentClaims = [
    { id: "CL001", type: "Cardiac Event", status: "Approved", amount: "$2,450" },
    { id: "CL002", type: "Emergency Visit", status: "Pending", amount: "$850" },
    { id: "CL003", type: "Routine Check", status: "Processing", amount: "$320" },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Approved": return "bg-success/20 text-success";
      case "Pending": return "bg-warning/20 text-warning";
      case "Processing": return "bg-primary/20 text-primary";
      default: return "bg-muted/20 text-muted-foreground";
    }
  };

  return (
    <div className="min-h-screen p-6">
      <Navigation />
      
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Welcome Section */}
        <Card className="card-elegant p-8 text-center">
          <h2 className="text-3xl font-bold mb-4">Welcome to ClaimChain</h2>
          <p className="text-muted-foreground mb-6">
            Your AI-powered insurance claim portal with blockchain security
          </p>
          <div className="flex gap-4 justify-center">
            <button 
              onClick={() => navigate("/quick-claim")}
              className="btn-primary px-6 py-3 rounded-2xl font-medium"
            >
              Quick Claim
            </button>
            <button 
              onClick={() => navigate("/full-claim")}
              className="bg-secondary text-secondary-foreground hover:bg-secondary/80 px-6 py-3 rounded-2xl font-medium transition-all duration-300"
            >
              Full Claim
            </button>
          </div>
        </Card>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="card-elegant p-6">
            <h3 className="text-lg font-semibold mb-2">Total Claims</h3>
            <p className="text-3xl font-bold text-primary">12</p>
            <p className="text-sm text-muted-foreground">This year</p>
          </Card>
          <Card className="card-elegant p-6">
            <h3 className="text-lg font-semibold mb-2">Approved Amount</h3>
            <p className="text-3xl font-bold text-success">$8,450</p>
            <p className="text-sm text-muted-foreground">Total approved</p>
          </Card>
          <Card className="card-elegant p-6">
            <h3 className="text-lg font-semibold mb-2">Fitbit Status</h3>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-success rounded-full"></div>
              <p className="text-lg font-medium">Connected</p>
            </div>
            <p className="text-sm text-muted-foreground">Last sync: 2 minutes ago</p>
          </Card>
        </div>

        {/* Recent Claims */}
        <Card className="card-elegant p-6">
          <h3 className="text-xl font-semibold mb-4">Recent Claims</h3>
          <div className="space-y-3">
            {recentClaims.map((claim) => (
              <div key={claim.id} className="flex items-center justify-between p-4 bg-secondary/30 rounded-xl">
                <div>
                  <p className="font-medium">{claim.id}</p>
                  <p className="text-sm text-muted-foreground">{claim.type}</p>
                </div>
                <div className="text-right">
                  <Badge className={getStatusColor(claim.status)}>
                    {claim.status}
                  </Badge>
                  <p className="text-lg font-semibold mt-1">{claim.amount}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Index;
