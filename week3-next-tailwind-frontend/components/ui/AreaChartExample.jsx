"use client";

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const data = [
  { date: "Mar 1", value: 10000 },
  { date: "Mar 2", value: 30500 },
  { date: "Mar 3", value: 27500 },
  { date: "Mar 4", value: 18000 },
  { date: "Mar 5", value: 18500 },
  { date: "Mar 6", value: 29500 },
  { date: "Mar 7", value: 31000 },
  { date: "Mar 8", value: 33500 },
  { date: "Mar 9", value: 24000 },
  { date: "Mar 10", value: 22500 },
  { date: "Mar 11", value: 33000 },
  { date: "Mar 12", value: 31500 },
  { date: "Mar 13", value: 37500 },
];

export default function AreaChartExample() {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#EEF2F7" />
        <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
        <Tooltip />
        <Area type="monotone" dataKey="value" stroke="#2563EB" strokeWidth={2} fill="#DBEAFE" dot={{ r: 3, fill: "#2563EB" }} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
