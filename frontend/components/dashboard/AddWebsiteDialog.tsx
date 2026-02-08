"use client";

import { useState } from "react";
import { useAuth, useUser } from "@clerk/nextjs";
import { Plus } from "lucide-react";
import toast from "react-hot-toast";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { websitesAPI } from "@/lib/api";
import { cache, CacheKeys } from "@/lib/cache";

interface AddWebsiteDialogProps {
  onWebsiteAdded?: () => void;
}

export function AddWebsiteDialog({ onWebsiteAdded }: AddWebsiteDialogProps) {
  const { getToken } = useAuth();
  const { user } = useUser();
  const [open, setOpen] = useState(false);
  const [domain, setDomain] = useState("");
  const [name, setName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const token = await getToken();
      if (!token) {
        throw new Error("Not authenticated");
      }

      await websitesAPI.create(token, {
        domain: domain.trim(),
        name: name.trim() || undefined,
      });

      // Reset form and close dialog
      setDomain("");
      setName("");
      setOpen(false);

      // Show success toast
      toast.success("Website added successfully!");

      // Invalidate dashboard stats cache since website count changed
      if (user) {
        cache.invalidate(CacheKeys.dashboardStats(user.id));
      }

      // Notify parent
      if (onWebsiteAdded) {
        onWebsiteAdded();
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to add website";
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Website
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Add Website</DialogTitle>
          <DialogDescription>
            Add a website to monitor its SEO performance.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            {error && (
              <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 rounded-md">
                {error}
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="domain">
                Domain <span className="text-red-500">*</span>
              </Label>
              <Input
                id="domain"
                placeholder="example.com"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                required
                disabled={isLoading}
              />
              <p className="text-xs text-muted-foreground">
                Enter just the domain (e.g., example.com) without http:// or www
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="name">Display Name (optional)</Label>
              <Input
                id="name"
                placeholder="My Website"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={isLoading}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading || !domain.trim()}>
              {isLoading ? "Adding..." : "Add Website"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
