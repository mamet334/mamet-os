"use client";

import { useState, useEffect } from "react";

interface BudgetStatus {
  providers: {
    [key: string]: {
      monthly_cap: number;
      used: number;
      remaining: number;
      percentage: number;
      status: string;
    };
  };
  total_budget_used: number;
  total_budget_cap: number;
}

export default function BudgetDashboard() {
  const [budget, setBudget] = useState<BudgetStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchBudget();
  }, []);

  const fetchBudget = async () => {
    try {
      const res = await fetch("/api/budget?user_id=test@email.com");
      const data = await res.json();
      setBudget(data);
    } catch {
      setError("Gagal memuat data budget");
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "exceeded":
        return "text-red-500";
      case "warning":
        return "text-yellow-500";
      case "half":
        return "text-orange-400";
      default:
        return "text-green-500";
    }
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return "bg-red-600";
    if (percentage >= 80) return "bg-yellow-500";
    if (percentage >= 50) return "bg-orange-500";
    return "bg-green-500";
  };

  if (loading) return <div className="p-4 text-gray-400 text-sm">Memuat budget...</div>;
  if (error) return <div className="p-4 text-red-400 text-sm">{error}</div>;
  if (!budget) return null;

  return (
    <div className="p-4 space-y-4">
      <h3 className="text-sm font-semibold text-gray-200">💰 Budget Control</h3>

      {/* Total */}
      <div className="bg-[#111] border border-[#222] rounded-lg p-4">
        <div className="flex justify-between mb-2">
          <span className="text-xs text-gray-400">Total Pemakaian Bulan Ini</span>
          <span className="text-sm font-semibold text-white">
            Rp {budget.total_budget_used.toLocaleString()} / Rp {budget.total_budget_cap.toLocaleString()}
          </span>
        </div>
        <div className="w-full bg-[#222] rounded-full h-2">
          <div
            className={`h-2 rounded-full ${getProgressColor((budget.total_budget_used / budget.total_budget_cap) * 100)}`}
            style={{ width: `${Math.min((budget.total_budget_used / budget.total_budget_cap) * 100, 100)}%` }}
          />
        </div>
      </div>

      {/* Per Provider */}
      {Object.entries(budget.providers).map(([name, data]) => (
        <div key={name} className="bg-[#111] border border-[#222] rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-300 capitalize">{name}</span>
            <span className={`text-xs font-semibold ${getStatusColor(data.status)}`}>
              {data.percentage.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-[#222] rounded-full h-1.5 mb-2">
            <div
              className={`h-1.5 rounded-full ${getProgressColor(data.percentage)}`}
              style={{ width: `${Math.min(data.percentage, 100)}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500">
            <span>Rp {data.used.toLocaleString()}</span>
            <span>Cap: Rp {data.monthly_cap.toLocaleString()}</span>
          </div>
        </div>
      ))}
    </div>
  );
}