"use client";

import React, { useMemo } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';
import { Target, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f472b6'];

const TooltipIcon = ({ text }: { text: string }) => {
    const [show, setShow] = React.useState(false);
    return (
        <div className="relative inline-block ml-2 align-middle" onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
            <Info className="w-3 h-3 text-gray-500 cursor-help hover:text-blue-400 transition-colors" />
            <AnimatePresence>
                {show && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 p-3 bg-gray-900 border border-white/10 rounded-xl text-[10px] font-medium text-gray-300 w-48 shadow-2xl z-50 pointer-events-none"
                    >
                        {text}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default function PortfolioView({ data }: { data: any[] }) {
    const router = useRouter();
    const portfolioStocks = useMemo(() => {
        return data.filter(s => (s.portfolio_weight || 0) > 0)
            .sort((a, b) => b.portfolio_weight - a.portfolio_weight);
    }, [data]);

    const stats = useMemo(() => {
        if (portfolioStocks.length === 0) return null;
        let totalW = 0, peW = 0, pbW = 0, retW = 0;
        portfolioStocks.forEach(s => {
            const w = s.portfolio_weight || 0;
            totalW += w;
            peW += (s.PE || 0) * w;
            pbW += (s.PB || 0) * w;
            retW += (s["Rev CAGR (%)"] || 0) * w;
        });
        peW /= totalW; pbW /= totalW; retW /= totalW;

        let variance = 0;
        portfolioStocks.forEach(s => {
            variance += (s.portfolio_weight || 0) * Math.pow((s["Rev CAGR (%)"] || 0) - retW, 2);
        });
        const stdDev = Math.sqrt(variance) || 5;
        const rf = 7;
        const sharpe = (retW - rf) / stdDev;

        let downsideVar = 0;
        portfolioStocks.forEach(s => {
            const diff = (s["Rev CAGR (%)"] || 0) - rf;
            if (diff < 0) downsideVar += (s.portfolio_weight || 0) * Math.pow(diff, 2);
        });
        const downsideDev = Math.sqrt(downsideVar) || 3;
        const sortino = (retW - rf) / downsideDev;

        return { pe: peW, pb: pbW, sharpe, sortino, expectedReturn: retW };
    }, [portfolioStocks]);

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

            {stats && (
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
                    <div className="glass-card p-6 border-blue-500/20 bg-blue-500/[0.02]">
                        <div className="flex items-center text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 mb-2">
                            Sharpe Ratio <TooltipIcon text="Risk-adjusted return. Higher indicates better returns for the level of risk taken (using Revenue Growth vs Risk-Free Rate)." />
                        </div>
                        <div className="text-3xl font-black text-blue-400 font-mono tracking-tighter">{stats.sharpe.toFixed(2)}</div>
                    </div>
                    <div className="glass-card p-6 border-emerald-500/20 bg-emerald-500/[0.02]">
                        <div className="flex items-center text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 mb-2">
                            Sortino Ratio <TooltipIcon text="Similar to Sharpe, but only penalizes negative volatility (downside risk). Better for identifying consistent growth." />
                        </div>
                        <div className="text-3xl font-black text-emerald-400 font-mono tracking-tighter">{stats.sortino.toFixed(2)}</div>
                    </div>
                    <div className="glass-card p-6 border-purple-500/20 bg-purple-500/[0.02]">
                        <div className="flex items-center text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 mb-2">
                            Portfolio P/E <TooltipIcon text="Weighted Average Price-to-Earnings ratio of the portfolio. Indicates how expensive the earnings of the portfolio are." />
                        </div>
                        <div className="text-3xl font-black text-purple-400 font-mono tracking-tighter">{stats.pe.toFixed(1)}x</div>
                    </div>
                    <div className="glass-card p-6 border-amber-500/20 bg-amber-500/[0.02]">
                        <div className="flex items-center text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 mb-2">
                            Portfolio P/B <TooltipIcon text="Weighted Average Price-to-Book ratio. Compares the market price of the portfolio to its book value." />
                        </div>
                        <div className="text-3xl font-black text-amber-500 font-mono tracking-tighter">{stats.pb.toFixed(1)}x</div>
                    </div>
                    <div className="glass-card p-6 border-white/10 hidden lg:block">
                        <div className="flex items-center text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 mb-2">
                            Exp. Return <TooltipIcon text="The weighted average Revenue CAGR of the portfolio holdings, representing the fundamental growth engine." />
                        </div>
                        <div className="text-3xl font-black text-white font-mono tracking-tighter">{stats.expectedReturn.toFixed(1)}%</div>
                    </div>
                </div>
            )}

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
        </section >
    );
}
