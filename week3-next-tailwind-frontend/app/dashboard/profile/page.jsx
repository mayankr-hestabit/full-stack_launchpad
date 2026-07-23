"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Card from "@/components/ui/Card";
import Modal from "@/components/ui/Modal";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

const initialProfile = {
  name: "Intern Name",
  jobTitle: "Frontend Intern",
  email: "intern@example.com",
  linkedin: "linkedin.com",
  twitter: "www.x.com",
  facebook: "facebook.com",
  bio: "Frontend intern working through the Week 3 Advance Frontend track — Next.js App Router, TailwindCSS, and a reusable component system.",
};

function InfoRow({ label, value, isLink = false }) {
  return (
    <div className="border-b border-slate-100 py-3 last:border-0">
      <p className="text-xs text-slate-400">{label}</p>
      {isLink ? (
        <a href="#" className="text-sm text-blue-600 hover:underline">{value}</a>
      ) : (
        <p className="text-sm font-medium text-slate-800">{value}</p>
      )}
    </div>
  );
}

export default function ProfilePage() {
  const router = useRouter();
  const [editOpen, setEditOpen] = useState(false);
  const [profile, setProfile] = useState(initialProfile);
  const [draft, setDraft] = useState(initialProfile);

  function openEdit() {
    setDraft(profile);
    setEditOpen(true);
  }

  function saveEdit() {
    setProfile(draft);
    setEditOpen(false);
  }

  return (
    <div>
      <button
        onClick={() => router.back()}
        className="text-sm text-blue-600 hover:underline"
      >
        ← Go back
      </button>

      <Card className="mt-4">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-[200px_1fr_1fr]">
          <Image
            src="/profile-photo.png"
            alt={profile.name}
            width={200}
            height={200}
            className="h-48 w-full rounded-md object-cover md:h-full"
          />

          <div>
            <InfoRow label="Name" value={profile.name} />
            <InfoRow label="Job Title" value={profile.jobTitle} />
            <InfoRow label="Email" value={profile.email} isLink />
          </div>

          <div>
            <InfoRow label="LinkedIn" value={profile.linkedin} isLink />
            <InfoRow label="Twitter" value={profile.twitter} isLink />
            <InfoRow label="Facebook" value={profile.facebook} isLink />
          </div>
        </div>

        <div className="mt-4 border-t border-slate-100 pt-4">
          <p className="text-xs text-slate-400">Bio</p>
          <p className="mt-1 text-sm leading-relaxed text-slate-600">{profile.bio}</p>
        </div>

        <button
          onClick={openEdit}
          className="mt-4 text-sm text-blue-600 hover:underline"
        >
          Edit Profile
        </button>
      </Card>

      <Modal open={editOpen} onClose={() => setEditOpen(false)} title="Edit Profile">
        <div className="space-y-4">
          <Input label="Name" value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} />
          <Input label="Job Title" value={draft.jobTitle} onChange={(e) => setDraft({ ...draft, jobTitle: e.target.value })} />
          <Input label="Bio" value={draft.bio} onChange={(e) => setDraft({ ...draft, bio: e.target.value })} />
        </div>
        <div className="mt-6 flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setEditOpen(false)}>Cancel</Button>
          <Button variant="primary" onClick={saveEdit}>Save</Button>
        </div>
      </Modal>
    </div>
  );
}
