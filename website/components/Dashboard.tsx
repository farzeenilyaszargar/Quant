"use client";

import React, { useState, useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, Radar
} from 'recharts';
import { TrendingUp, Shield, BarChart3, Star, AlertCircle, TrendingDown, Target, Zap, LayoutGrid } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f472b6'];

export default function Dashboard({ data }: { data: any[] }) {
  const [selectedStock, setSelectedStock] = useState(data[0]);

  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen text-gray-500 bg-[#050505]">
        <AlertCircle className="w-12 h-12 mb-4 text-gray-600" />
        <h2 className="text-xl font-bold">No Analysis Data Found</h2>
        <p className="mt-2 text-sm text-gray-600">Please run the Quant Bot to generate stock intelligence.</p>
      </div>
    );
  }

  const chartData = useMemo(() => data.map(s => ({
    name: s.symbol,
    score: s.final_score,
    intrinsic: s["Intrinsic Price Per Share"],
    current: s["Current Price"],
    weight: s.portfolio_weight || 0
  })), [data]);

  const sectorData = useMemo(() => {
    const sectors: Record<string, number> = {};
    data.forEach(s => {
      const sect = s.Sector || 'Others';
      sectors[sect] = (sectors[sect] || 0) + (s.portfolio_weight || 0);
    });
    return Object.entries(sectors).map(([name, value]) => ({ name, value }));
  }, [data]);

  const radarData = useMemo(() => [
    { subject: 'DCF', value: selectedStock.scores?.dcf_score || 0 },
    { subject: 'Growth', value: selectedStock.scores?.growth_score || 0 },
    { subject: 'ROCE', value: selectedStock.scores?.roce_score || 0 },
    { subject: 'Moat/Sat', value: selectedStock.scores?.moat_score || 0 },
    { subject: 'FII/DII', value: selectedStock.scores?.fii_dii_de_score || 0 },
    { subject: 'Sector', value: selectedStock.scores?.tailwind_score || 0 },
    { subject: 'Mgmt', value: selectedStock.scores?.management_score || 0 },
  ], [selectedStock]);

  return (
    <div className="p-6 md:p-10 space-y-10 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold gradient-text tracking-tight">Quant Strategy Dashboard</h1>
          <p className="text-gray-400 mt-2 font-medium">Smart Capital Allocation & Relative Value Analysis</p>
        </div>
        <div className="flex items-center gap-3 bg-white/5 p-2 rounded-xl border border-white/10">
          <span className="text-xs font-semibold px-3 py-1 bg-blue-500/20 text-blue-400 rounded-lg">PORTFOLIO v3.0</span>
          <span className="text-xs text-gray-500">{new Date().toLocaleDateString()}</span>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'TOP CONVICTION', val: data[0].symbol, icon: Star, color: 'text-amber-400' },
          { label: 'AVG QUANT SCORE', val: (data.reduce((acc, s) => acc + s.final_score, 0) / data.length).toFixed(1), icon: Target, color: 'text-blue-400' },
          { label: 'MOST UNDERVALUED', val: data.reduce((prev, curr) => (prev["Intrinsic Price Per Share"] / prev["Current Price"]) > (curr["Intrinsic Price Per Share"] / curr["Current Price"]) ? prev : curr).symbol, icon: Zap, color: 'text-green-400' },
          { label: 'ACTIVE SYMBOLS', val: data.length, icon: BarChart3, color: 'text-purple-400' },
        ].map((card, i) => (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            key={card.label}
            className="glass-card p-6"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">{card.label}</span>
              <card.icon className={`w-4 h-4 ${card.color}`} />
            </div>
            <div className="text-2xl font-bold">{card.val}</div>
          </motion.div>
        ))}
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-card p-6 min-h-[400px]">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <TrendingUp className="text-blue-400 w-5 h-5" />
            Quant Score Ranking
          </h2>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 12 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '12px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Bar dataKey="score" radius={[8, 8, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <LayoutGrid className="text-purple-400 w-5 h-5" />
            Stock Allocation (%)
          </h2>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="portfolio_weight"
                  nameKey="symbol"
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val: any) => `${(Number(val) * 100).toFixed(1)}%`}
                  contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Allocation Breakdown and Radar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <Zap className="text-amber-400 w-5 h-5" />
            Optimal Capital Distribution
          </h2>
          <div className="space-y-4 max-h-[400px] overflow-y-auto custom-scrollbar pr-2">
            {data.slice().sort((a, b) => b.portfolio_weight - a.portfolio_weight).map((s, i) => (
              <div key={s.symbol} className="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/5 hover:bg-white/10 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center text-xs font-bold">{i + 1}</div>
                  <div>
                    <div className="font-bold text-sm tracking-wide">{s.symbol}</div>
                    <div className="text-[10px] text-gray-500 uppercase tracking-tighter">{s.Sector} | {s.Industry}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-mono text-green-400 font-bold">{(s.portfolio_weight * 100).toFixed(2)}%</div>
                  <div className="text-[10px] text-gray-400">Target Hold</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <Shield className="text-green-400 w-5 h-5" />
            {selectedStock.symbol} Core Intelligence
          </h2>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid stroke="#ffffff20" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <Radar
                  name={selectedStock.symbol}
                  dataKey="value"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.5}
                />
                <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '12px' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Stock Selection & Insights */}
      <div className="glass-card overflow-hidden">
        <div className="flex border-b border-white/5 flex-nowrap overflow-x-auto custom-scrollbar bg-black/20">
          {data.map(stock => (
            <button
              key={stock.symbol}
              onClick={() => setSelectedStock(stock)}
              className={`px-8 py-4 text-sm font-semibold transition-all whitespace-nowrap ${selectedStock.symbol === stock.symbol
                ? 'bg-blue-500/10 text-blue-400 border-b-2 border-blue-500'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
            >
              {stock.symbol}
            </button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={selectedStock.symbol}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="p-8 grid grid-cols-1 lg:grid-cols-2 gap-10"
          >
            <div>
              <div className="flex items-center gap-4 mb-8">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-600 to-emerald-600 flex items-center justify-center text-2xl font-bold shadow-lg">
                  {selectedStock.symbol[0]}
                </div>
                <div>
                  <h3 className="text-3xl font-bold">{selectedStock.symbol}</h3>
                  <div className="flex items-center gap-3 text-sm mt-1">
                    <span className="text-gray-500 uppercase tracking-widest text-xs font-bold">QUANT SCORE:</span>
                    <span className="text-green-400 font-bold text-lg">{selectedStock.final_score}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/5 p-5 rounded-2xl border border-white/5">
                    <div className="text-gray-500 text-[10px] uppercase font-bold tracking-widest mb-1">CMP</div>
                    <div className="text-xl font-mono text-white">₹{selectedStock["Current Price"]}</div>
                  </div>
                  <div className="bg-white/5 p-5 rounded-2xl border border-white/5">
                    <div className="text-gray-500 text-[10px] uppercase font-bold tracking-widest mb-1">INTRINSIC (DCF)</div>
                    <div className="text-xl font-mono text-green-400">₹{selectedStock["Intrinsic Price Per Share"]}</div>
                  </div>
                </div>

                <div className="bg-blue-500/5 p-6 rounded-3xl border border-blue-500/10 relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-4 opacity-10">
                    <Target className="w-20 h-20" />
                  </div>
                  <div className="flex items-center gap-2 mb-4 text-blue-300">
                    <Shield className="w-4 h-4" />
                    <span className="text-xs font-bold uppercase tracking-[0.2em]">Alpha Research Notes</span>
                  </div>
                  <p className="text-gray-300 leading-relaxed text-sm">
                    {selectedStock.ai_notes}
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <h4 className="text-xs font-bold uppercase tracking-widest text-gray-500 ml-1">Key Fundamental Health</h4>
              <div className="grid grid-cols-2 gap-6">
                {[
                  { label: 'ROCE', val: `${selectedStock["ROCE (%)"]}%` },
                  { label: 'Debt/Equity', val: selectedStock["D/E"] },
                  { label: '3Y Sales CAGR', val: `${selectedStock["Rev CAGR (%)"]}%` },
                  { label: 'FII Float', val: `${selectedStock["FII (%)"]}%` },
                  { label: 'DII Float', val: `${selectedStock["DII (%)"]}%` },
                  { label: 'Ann. FCF (Cr)', val: `₹${selectedStock["FCF (Cr)"]}` },
                ].map(item => (
                  <div key={item.label} className="bg-white/2 p-4 rounded-xl border border-white/5 flex flex-col">
                    <span className="text-[10px] text-gray-500 font-bold mb-1 uppercase tracking-wider">{item.label}</span>
                    <span className="text-lg font-medium">{item.val}</span>
                  </div>
                ))}
              </div>

              <div className="pt-6">
                <div className={`flex items-center gap-3 p-5 rounded-2xl ${selectedStock["Intrinsic Price Per Share"] > selectedStock["Current Price"]
                  ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                  : 'bg-red-500/10 text-red-500 border border-red-500/20'
                  }`}>
                  {selectedStock["Intrinsic Price Per Share"] > selectedStock["Current Price"] ? (
                    <>
                      <TrendingUp className="w-6 h-6" />
                      <div>
                        <div className="font-bold text-sm tracking-wide">UNDERVALUED ASSET</div>
                        <div className="text-xs opacity-70">Trading {(100 - (selectedStock["Current Price"] / selectedStock["Intrinsic Price Per Share"] * 100)).toFixed(1)}% below intrinsic</div>
                      </div>
                    </>
                  ) : (
                    <>
                      <TrendingDown className="w-6 h-6" />
                      <div>
                        <div className="font-bold text-sm tracking-wide">PREMIUM VALUATION</div>
                        <div className="text-xs opacity-70">Trading {((selectedStock["Current Price"] / selectedStock["Intrinsic Price Per Share"] - 1) * 100).toFixed(1)}% above intrinsic</div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="text-center text-gray-600 text-xs py-10 opacity-40">
        QuantBot v3.2 • Portfolio Optimized • {new Date().getFullYear()} • Dynamic Risk Management
      </div>
    </div>
  );
}
