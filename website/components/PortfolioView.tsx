"use client";

import React, { useMemo } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';
import { Target } from 'lucide-react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f472b6'];

export default function PortfolioView({ data }: { data: any[] }) {
    const router = useRouter();
    const portfolioStocks = useMemo(() => {
        return data.filter(s => (s.portfolio_weight || 0) > 0)
            .sort((a, b) => b.portfolio_weight - a.portfolio_weight);
    }, [data]);

    const chartData = useMemo(() => portfolioStocks.map(s => ({
        name: s.symbol,
        score: s.final_score,
        intrinsic: s["Intrinsic Price Per Share"],
        current: s["Current Price"],
        weight: s.portfolio_weight || 0
    })), [portfolioStocks]);

    const sectorData = useMemo(() => {
        const sectors: Record<string, number> = {};
        portfolioStocks.forEach(s => {
            const sect = s["Broad Sector"] || 'Others';
            sectors[sect] = (sectors[sect] || 0) + (s.portfolio_weight || 0);
        });
        return Object.entries(sectors).map(([name, value]) => ({ name, value }));
    }, [portfolioStocks]);

    return (
        <section id="main-portfolio" className="space-y-12">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-l-4 border-blue-600 pl-8">
                <div>
                    <h2 className="text-4xl md:text-5xl font-black tracking-tighter uppercase mb-2">Main Quantitative Portfolio</h2>
                    <p className="text-gray-500 font-medium max-w-xl">Optimized capital allocation based on intrinsic relative value and qualitative moat assessment.</p>
                </div>
                <div className="bg-blue-600/10 border border-blue-500/20 px-6 py-3 rounded-2xl">
                    <div className="text-gray-500 text-[9px] font-black uppercase tracking-[0.3em] mb-1">Target Portfolio size</div>
                    <div className="text-2xl font-mono font-bold text-blue-400">{portfolioStocks.length} <span className="text-sm opacity-50">/ 50</span></div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="glass-card p-8 min-h-[450px]">
                    <h3 className="text-sm font-black uppercase tracking-[0.3em] mb-8 text-blue-300">Structural Alpha (Score Index)</h3>
                    <div className="h-[320px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                                <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 10, fontWeight: 700 }} />
                                <YAxis stroke="#64748b" tick={{ fontSize: 10, fontWeight: 700 }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '16px', boxShadow: '0 20px 40px rgba(0,0,0,0.5)' }}
                                    itemStyle={{ color: '#fff', fontSize: '12px', fontWeight: 700 }}
                                />
                                <Bar dataKey="score" radius={[6, 6, 0, 0]}>
                                    {chartData.map((_entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="glass-card p-8">
                    <h3 className="text-sm font-black uppercase tracking-[0.3em] mb-8 text-purple-300">Broad Sector Diversification</h3>
                    <div className="h-[320px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={sectorData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={80}
                                    outerRadius={110}
                                    paddingAngle={10}
                                    dataKey="value"
                                    nameKey="name"
                                >
                                    {sectorData.map((_entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} strokeWidth={0} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    formatter={(val: any) => `${(Number(val) * 100).toFixed(1)}%`}
                                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '16px' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            <div className="glass-card p-10 bg-gradient-to-br from-white/[0.03] to-transparent">
                <h3 className="text-xl font-black mb-10 flex items-center gap-3 text-white">
                    <Target className="w-6 h-6 text-emerald-400" />
                    Strategic Capital Allocation
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {portfolioStocks.map((s, i) => (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.98 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            key={s.symbol}
                            className="bg-white/[0.03] border border-white/5 p-6 rounded-[2rem] flex items-center justify-between group hover:border-blue-500/40 hover:bg-white/[0.05] transition-all cursor-pointer shadow-xl"
                            onClick={() => router.push(`/insights?symbol=${s.symbol}`)}
                        >
                            <div className="flex items-center gap-4">
                                <span className="text-3xl font-black text-white/5 group-hover:text-blue-500/10 transition-colors">{i + 1}</span>
                                <div>
                                    <div className="font-black text-xl leading-tight group-hover:text-blue-400 transition-colors">{s.symbol}</div>
                                    <div className="text-[9px] text-gray-500 uppercase font-black tracking-[0.2em] mt-1">{s["Broad Sector"] || 'CORE ASSET'}</div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-2xl font-mono font-black text-white tracking-widest">{(s.portfolio_weight * 100).toFixed(1)}%</div>
                                <div className="text-[10px] text-gray-500 font-black uppercase tracking-widest italic mt-1">Weight</div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
