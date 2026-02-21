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
            <Info className="w-4 h-4 text-slate-400 cursor-help hover:text-blue-500 transition-colors" />
            <AnimatePresence>
                {show && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 p-3 bg-slate-800 rounded-lg text-xs font-medium text-white w-56 shadow-xl z-50 pointer-events-none"
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
        <section id="main-portfolio" className="space-y-10">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-200">
                <div>
                    <h2 className="text-2xl md:text-3xl font-bold text-slate-900 mb-1">Main Quantitative Portfolio</h2>
                    <p className="text-slate-500 font-medium">Optimized capital allocation based on intrinsic relative value and qualitative moat assessment.</p>
                </div>
                <div className="bg-blue-50 border border-blue-100 px-6 py-3 rounded-xl flex items-center gap-4">
                    <div className="text-blue-800 text-xs font-semibold uppercase tracking-wider">Target Size</div>
                    <div className="text-2xl font-bold text-blue-600">{portfolioStocks.length} <span className="text-sm opacity-60 font-normal">/ 50</span></div>
                </div>
            </div>

            {stats && (
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 md:gap-6">
                    <div className="dashboard-card p-6">
                        <div className="flex items-center text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                            Sharpe Ratio <TooltipIcon text="Risk-adjusted return. Higher indicates better returns for the level of risk taken (using Revenue Growth vs Risk-Free Rate)." />
                        </div>
                        <div className="text-3xl font-bold text-slate-900 tracking-tight">{stats.sharpe.toFixed(2)}</div>
                    </div>
                    <div className="dashboard-card p-6">
                        <div className="flex items-center text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                            Sortino Ratio <TooltipIcon text="Similar to Sharpe, but only penalizes negative volatility (downside risk). Better for identifying consistent growth." />
                        </div>
                        <div className="text-3xl font-bold text-slate-900 tracking-tight">{stats.sortino.toFixed(2)}</div>
                    </div>
                    <div className="dashboard-card p-6">
                        <div className="flex items-center text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                            Portfolio P/E <TooltipIcon text="Weighted Average Price-to-Earnings ratio of the portfolio. Indicates how expensive the earnings of the portfolio are." />
                        </div>
                        <div className="text-3xl font-bold text-slate-900 tracking-tight">{stats.pe.toFixed(1)}x</div>
                    </div>
                    <div className="dashboard-card p-6">
                        <div className="flex items-center text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                            Portfolio P/B <TooltipIcon text="Weighted Average Price-to-Book ratio. Compares the market price of the portfolio to its book value." />
                        </div>
                        <div className="text-3xl font-bold text-slate-900 tracking-tight">{stats.pb.toFixed(1)}x</div>
                    </div>
                    <div className="dashboard-card p-6 hidden lg:block">
                        <div className="flex items-center text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                            Exp. Return <TooltipIcon text="The weighted average Revenue CAGR of the portfolio holdings, representing the fundamental growth engine." />
                        </div>
                        <div className="text-3xl font-bold text-slate-900 tracking-tight">{stats.expectedReturn.toFixed(1)}%</div>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8">
                <div className="dashboard-card p-6 md:p-8 min-h-[450px]">
                    <h3 className="text-sm font-semibold uppercase tracking-wider mb-6 text-slate-700">Structural Alpha (Score Index)</h3>
                    <div className="h-[320px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                                <XAxis dataKey="name" stroke="#64748b" tick={{ fill: '#475569', fontSize: 11, fontWeight: 500 }} axisLine={{ stroke: '#cbd5e1' }} tickLine={false} />
                                <YAxis stroke="#64748b" tick={{ fill: '#475569', fontSize: 11, fontWeight: 500 }} axisLine={false} tickLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                                    itemStyle={{ color: '#0f172a', fontSize: '12px', fontWeight: 600 }}
                                />
                                <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                                    {chartData.map((_entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="dashboard-card p-6 md:p-8">
                    <h3 className="text-sm font-semibold uppercase tracking-wider mb-6 text-slate-700">Broad Sector Diversification</h3>
                    <div className="h-[320px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={sectorData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={70}
                                    outerRadius={110}
                                    paddingAngle={5}
                                    dataKey="value"
                                    nameKey="name"
                                >
                                    {sectorData.map((_entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} strokeWidth={0} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    formatter={(val: any) => `${(Number(val) * 100).toFixed(1)}%`}
                                    contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm mt-8">
                <h3 className="text-xl font-bold mb-8 flex items-center gap-3 text-slate-900">
                    <Target className="w-6 h-6 text-blue-600" />
                    Strategic Capital Allocation
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                    {portfolioStocks.map((s, i) => (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            key={s.symbol}
                            className="bg-slate-50 border border-slate-200 p-5 rounded-xl flex items-center justify-between group hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
                            onClick={() => router.push(`/insights?symbol=${s.symbol}`)}
                        >
                            <div className="flex items-center gap-4">
                                <span className="text-2xl font-bold text-slate-300 group-hover:text-blue-500 transition-colors">{i + 1}</span>
                                <div>
                                    <div className="font-bold text-lg leading-tight text-slate-900 group-hover:text-blue-600 transition-colors">{s.symbol}</div>
                                    <div className="text-xs text-slate-500 font-medium uppercase mt-0.5">{s["Broad Sector"] || 'CORE ASSET'}</div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-xl font-bold text-slate-900 tracking-tight">{(s.portfolio_weight * 100).toFixed(1)}%</div>
                                <div className="text-xs text-slate-400 font-medium mt-0.5">Weight</div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section >
    );
}
