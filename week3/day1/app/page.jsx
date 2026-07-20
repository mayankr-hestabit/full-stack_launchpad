"use client";

import { useState } from "react";
import { ChevronRight } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import Modal from "@/components/ui/Modal";

const stats = [
  { label: "Primary Card", color: "primary" },
  { label: "Warning Card", color: "warning" },
  { label: "Success Card", color: "success" },
  { label: "Danger Card", color: "danger" },
];

export default function DashboardPage() {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
      <p className="mt-1 text-sm text-slate-500">Day 2 — reusable component library in action</p>

      {/* GRID: 1 column on mobile, 2 on small screens, 4 on large — two-dimensional layout */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card
            key={stat.label}
            color={stat.color}
            footer={
              // FLEX: single row, space-between — one-dimensional layout
              <div className="flex w-full items-center justify-between">
                <span>View Details</span>
                <ChevronRight size={14} />
              </div>
            }
          >
            <p className="text-lg font-semibold">{stat.label}</p>
          </Card>
        ))}
      </div>

      {/* Component demo section */}
      <div className="mt-8 space-y-4">
        <Card>
          <div className="flex flex-wrap items-center gap-3">
            <Button variant="primary">Primary</Button>
            <Button variant="warning">Warning</Button>
            <Button variant="success">Success</Button>
            <Button variant="danger">Danger</Button>
            <Button variant="secondary" onClick={() => setModalOpen(true)}>
              Open Modal
            </Button>
          </div>

          <div className="mt-4 flex gap-2">
            <Badge variant="primary">New</Badge>
            <Badge variant="success">Active</Badge>
            <Badge variant="danger">Overdue</Badge>
          </div>
        </Card>
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Example Modal">
        <p className="text-sm text-slate-600">
          This modal is controlled by state in the parent page — same pattern as the
          Day 1 sidebar toggle.
        </p>
        <div className="mt-4 flex justify-end">
          <Button variant="primary" onClick={() => setModalOpen(false)}>
            Close
          </Button>
        </div>
      </Modal>
    </div>
  );
}