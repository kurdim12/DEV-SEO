/**
 * Keywords page - Keyword tracking and analysis
 */
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Key, Plus } from "lucide-react";

export default function KeywordsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Keywords</h2>
          <p className="text-muted-foreground">
            Track and monitor your keyword rankings
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Keywords
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Key className="h-5 w-5 text-primary" />
            <CardTitle>Keyword Tracking</CardTitle>
          </div>
          <CardDescription>
            Monitor your website&apos;s ranking for target keywords
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <Key className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Keywords Tracked</h3>
            <p className="text-sm text-muted-foreground max-w-md mb-4">
              Start tracking keywords to monitor your search engine rankings and SEO performance over time.
            </p>
            <Button variant="outline">
              <Plus className="h-4 w-4 mr-2" />
              Add Your First Keyword
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
