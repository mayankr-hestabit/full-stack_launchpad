"use client";

import { useRouter } from "next/navigation";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { UserCircle } from "lucide-react";

// useRouter vs Link — Link is for user-clickable navigation (renders an <a> tag,
// good for SEO/accessibility). useRouter is for PROGRAMMATIC navigation —
// e.g. redirecting after a form submits, or a "Back" action, where there's
// no natural link to click.

export default function ProfilePage() {
  const router = useRouter();

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-800">Profile</h1>
      <p className="mt-1 text-sm text-slate-500">/dashboard/profile</p>

      <Card className="mt-6 max-w-md">
        <div className="flex items-center gap-4">
          <UserCircle size={48} className="text-slate-400" />
          <div>
            <p className="font-semibold text-slate-800">Mayank Raj</p>
            <p className="text-sm text-slate-500">mayank@example.com</p>
          </div>
        </div>

        <div className="mt-6 flex gap-2">
          <Button variant="secondary" onClick={() => router.back()}>
            Go Back
          </Button>
          <Button variant="primary" onClick={() => router.push("/dashboard")}>
            Back to Dashboard
          </Button>
        </div>
      </Card>
    </div>
  );
}
