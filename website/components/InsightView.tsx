"use client";

import React, { useState, useMemo, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import {
    RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer
} from 'recharts';
import { TrendingUp, Shield, BarChart3, Star, Zap, LayoutGrid } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function InsightContent({ data }: { data: any[] }) {
    const searchParams = useSearchParams();
    const [selectedStock, setSelectedStock] = useState(data[0]);

    useEffect(() => {
        const symbol = searchParams.get('symbol');
        if (symbol) {
            const match = data.find(s => s.symbol === symbol);
            if (match) setSelectedStock(match);
        }
    }, [searchParams, data]);

    const radarData = useMemo(() => [
        { subject: 'DCF', value: selectedStock?.scores?.dcf_score || 0 },
        { subject: 'Growth', value: selectedStock?.scores?.growth_score || 0 },
        { subject: 'ROCE', value: selectedStock?.scores?.roce_score || 0 },
        { subject: 'Moat/Sat', value: selectedStock?.scores?.moat_score || 0 },
        { subject: 'FII/DII', value: selectedStock?.scores?.fii_dii_de_score || 0 },
        { subject: 'Sector', value: selectedStock?.scores?.tailwind_score || 0 },
        { subject: 'Mgmt', value: selectedStock?.scores?.management_score || 0 },
    ], [selectedStock]);

    if (!selectedStock) return null;

    return (
        <section id="insight-engine" className="space-y-12">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-l-4 border-emerald-500 pl-8">
                <div>
                    <h2 className="text-4xl md:text-5xl font-black tracking-tighter uppercase mb-2">Deep Insight Engine</h2>
                    <p className="text-gray-500 font-medium max-w-xl">Multi-dimensional analysis combining hard financials with AI-driven qualitative scoring.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Selector Panel */}
                <div className="lg:col-span-1 space-y-4 max-h-[800px] overflow-y-auto pr-4 custom-scrollbar">
                    {data.map((s) => (
                        <div
                            key={s.symbol}
                            onClick={() => setSelectedStock(s)}
                            className={`p-6 rounded-3xl border transition-all cursor-pointer group ${selectedStock.symbol === s.symbol
                                ? 'bg-emerald-500/10 border-emerald-500/50 shadow-[0_0_30px_rgba(16,185,129,0.1)]'
                                : 'bg-white/[0.02] border-white/5 hover:border-white/20'
                                }`}
                        >
                            <div className="flex justify-between items-center">
                                <div>
                                    <div className={`font-black text-xl ${selectedStock.symbol === s.symbol ? 'text-emerald-400' : 'text-white group-hover:text-emerald-400'}`}>{s.symbol}</div>
                                    <div className="text-[10px] text-gray-500 font-black uppercase tracking-widest mt-1">{s["Broad Sector"]}</div>
                                </div>
                                <div className={`text-2xl font-mono font-black ${s.final_score > 60 ? 'text-emerald-500' : 'text-gray-600'}`}>
                                    {s.final_score}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Intelligence Panel */}
                <AnimatePresence mode="wait">
                    <motion.div
                        key={selectedStock.symbol}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="lg:col-span-2 space-y-8"
                    >
                        <div className="glass-card p-10 relative overflow-hidden">
                            <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 blur-[100px] -mr-32 -mt-32"></div>

                            <div className="relative z-10 flex flex-col md:flex-row justify-between items-start gap-8">
                                <div className="flex-1 space-y-6">
                                    <div>
                                        <div className="flex items-center gap-4 mb-4">
                                            <h3 className="text-6xl font-black tracking-tighter">{selectedStock.symbol}</h3>
                                            <div className="flex flex-col">
                                                <div className="bg-emerald-500 text-black px-4 py-1.5 rounded-xl text-xs font-black uppercase tracking-widest shadow-lg">
                                                    SCORE: {selectedStock.final_score}
                                                </div>
                                                <span className="text-gray-500 text-[10px] font-black uppercase tracking-[0.3em]">{selectedStock["Broad Sector"]} | {selectedStock.Sector}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="p-6 rounded-3xl bg-white/[0.03] border border-emerald-500/20">
                                            <div className="flex items-center gap-2 text-emerald-400 text-[10px] font-black uppercase tracking-widest mb-2">
                                                <TrendingUp className="w-3 h-3" /> Growth Engine
                                            </div>
                                            <p className="text-sm text-gray-300 font-medium leading-relaxed">
                                                {selectedStock.ai_notes?.growth_thesis || "Solid growth trajectory supported by expanding market presence and operational efficiency."}
                                            </p>
                                        </div>
                                        <div className="p-6 rounded-3xl bg-white/[0.03] border border-blue-500/20">
                                            <div className="flex items-center gap-2 text-blue-400 text-[10px] font-black uppercase tracking-widest mb-2">
                                                <Shield className="w-3 h-3" /> Competitive Moat
                                            </div>
                                            <p className="text-sm text-gray-300 font-medium leading-relaxed">
                                                {selectedStock.ai_notes?.moat_analysis || "Strong structural barriers to entry reinforced by brand equity and distribution scale."}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <div className="w-full md:w-[350px] space-y-8">
                                    <div className="h-[300px] w-full">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                                                <PolarGrid stroke="#ffffff10" />
                                                <PolarAngleAxis dataKey="subject" tick={{ fill: '#475569', fontSize: 10, fontWeight: 800 }} />
                                                <Radar
                                                    name={selectedStock.symbol}
                                                    dataKey="value"
                                                    stroke="#10b981"
                                                    fill="#10b981"
                                                    fillOpacity={0.6}
                                                />
                                            </RadarChart>
                                        </ResponsiveContainer>
                                    </div>

                                    <div className="grid grid-cols-2 gap-6 px-10">
                                        {[
                                            { label: 'ROCE %', val: selectedStock["ROCE (%)"] },
                                            { label: 'D/E Ratio', val: selectedStock["D/E"] },
                                            { label: 'Sales CAGR', val: `${selectedStock["Rev CAGR (%)"]}%` },
                                            { label: 'Inst. Stake', val: `${(selectedStock["FII (%)"] + selectedStock["DII (%)"]).toFixed(1)}%` },
                                        ].map(item => (
                                            <div key={item.label} className="flex flex-col items-center p-6 bg-white/[0.01] rounded-[2rem] border border-white/5">
                                                <span className="text-[10px] text-gray-600 font-black mb-2 uppercase tracking-[0.3em]">{item.label}</span>
                                                <span className="text-2xl font-black text-white tracking-tighter">{item.val}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </AnimatePresence>
            </div>
        </section>
    );
}

export default function InsightView({ data }: { data: any[] }) {
    return (
        <Suspense fallback={<div className="text-white">Loading Engine...</div>}>
            <InsightContent data={data} />
        </Suspense>
    );
}
