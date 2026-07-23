"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const data = [
  { month: "January", value: 4000 },
  { month: "February", value: 5200 },
  { month: "March", value: 6100 },
  { month: "April", value: 7800 },
  { month: "May", value: 9900 },
  { month: "June", value: 15000 },
];

export default function BarChartExample() {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#EEF2F7" />
        <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
        <Tooltip />
        <Bar dataKey="value" fill="#2563EB" radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
