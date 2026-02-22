"use client";

import React, { useState, useMemo, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import {
    RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer
} from 'recharts';
import { TrendingUp, Shield, BarChart3, Star, Zap, LayoutGrid, Info } from 'lucide-react';
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
        <section id="insight-engine" className="space-y-10">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-200">
                <div>
                    <h2 className="text-2xl md:text-3xl font-bold text-slate-900 mb-1">Company Deep Dive</h2>
                    <p className="text-slate-500 font-medium">Detailed breakdown of quantitative edge and qualitative moat scores.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Selector Panel */}
                <div className="lg:col-span-1 space-y-4 max-h-[800px] overflow-y-auto pr-4 custom-scrollbar">
                    {data.map((s) => (
                        <div
                            key={s.symbol}
                            onClick={() => setSelectedStock(s)}
                            className={`p-5 rounded-xl border transition-all cursor-pointer group ${selectedStock.symbol === s.symbol
                                ? 'bg-blue-50 border-blue-200 shadow-sm'
                                : 'bg-white border-slate-200 hover:border-slate-300'
                                }`}
                        >
                            <div className="flex justify-between items-center">
                                <div>
                                    <div className={`font-bold text-lg leading-tight ${selectedStock.symbol === s.symbol ? 'text-blue-600' : 'text-slate-900 group-hover:text-blue-600'}`}>
                                        {s["Company Name"] && s["Company Name"] !== "values missing" ? (
                                            <>{s["Company Name"]}</>
                                        ) : (
                                            <span className="line-through text-slate-400">{s.symbol} <span className="text-xs text-red-400 font-bold lowercase italic no-underline ml-1">values missing</span></span>
                                        )}
                                    </div>
                                    <div className="text-xs text-slate-500 font-medium uppercase mt-0.5">{s["Company Name"] && s["Company Name"] !== "values missing" ? s.symbol + ' • ' : ''}{s["Broad Sector"]}</div>
                                </div>
                                <div className={`text-xl font-bold tracking-tight ${s.final_score > 60 ? 'text-emerald-600' : 'text-slate-600'}`}>
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
                        className="lg:col-span-2 space-y-6"
                    >
                        <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm relative overflow-hidden">
                            <div className="relative z-10 flex flex-col md:flex-row justify-between items-start gap-8">
                                <div className="flex-1 space-y-8">
                                    <div>
                                        <div className="flex items-center gap-4 mb-2">
                                            <h3 className="text-4xl md:text-5xl font-bold tracking-tight text-slate-900">
                                                {selectedStock["Company Name"] && selectedStock["Company Name"] !== "values missing" ? (
                                                    selectedStock["Company Name"]
                                                ) : (
                                                    <span className="line-through text-slate-400">{selectedStock.symbol} <span className="text-sm text-red-400 font-bold lowercase italic no-underline ml-2">values missing</span></span>
                                                )}
                                            </h3>
                                            <div className="flex flex-col">
                                                <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-md text-xs font-semibold uppercase w-max">
                                                    SCORE: {selectedStock.final_score}
                                                </div>
                                            </div>
                                        </div>
                                        <span className="text-slate-500 text-sm font-medium uppercase tracking-wider">{selectedStock.symbol} | {selectedStock["Broad Sector"]} | {selectedStock.Sector}</span>
                                    </div>

                                    {selectedStock.About && selectedStock.About !== 'values missing' && (
                                        <div className="p-6 rounded-xl bg-slate-50 border border-slate-200 mt-4 mb-4">
                                            <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
                                                <Info className="w-4 h-4" /> About Company
                                            </div>
                                            <p className="text-sm text-slate-600 leading-relaxed font-medium">
                                                {selectedStock.About}
                                            </p>
                                        </div>
                                    )}

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="p-6 rounded-xl bg-slate-50 border border-slate-200">
                                            <div className="flex items-center gap-2 text-blue-600 text-xs font-semibold uppercase tracking-wider mb-3">
                                                <TrendingUp className="w-4 h-4" /> Growth Engine
                                            </div>
                                            <p className="text-sm text-slate-700 font-medium leading-relaxed">
                                                {selectedStock.ai_notes?.growth_thesis || "Solid growth trajectory supported by expanding market presence and operational efficiency."}
                                            </p>
                                        </div>
                                        <div className="p-6 rounded-xl bg-slate-50 border border-slate-200">
                                            <div className="flex items-center gap-2 text-indigo-600 text-xs font-semibold uppercase tracking-wider mb-3">
                                                <Shield className="w-4 h-4" /> Competitive Moat
                                            </div>
                                            <p className="text-sm text-slate-700 font-medium leading-relaxed">
                                                {selectedStock.ai_notes?.moat_analysis || "Strong structural barriers to entry reinforced by brand equity and distribution scale."}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <div className="w-full md:w-[350px] space-y-6">
                                    <div className="h-[280px] w-full bg-slate-50 rounded-xl border border-slate-200 py-4">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                                                <PolarGrid stroke="#e2e8f0" />
                                                <PolarAngleAxis dataKey="subject" tick={{ fill: '#475569', fontSize: 11, fontWeight: 600 }} />
                                                <Radar
                                                    name={selectedStock.symbol}
                                                    dataKey="value"
                                                    stroke="#3b82f6"
                                                    fill="#3b82f6"
                                                    fillOpacity={0.4}
                                                />
                                            </RadarChart>
                                        </ResponsiveContainer>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        {[
                                            { label: 'ROCE %', val: selectedStock["ROCE (%)"] },
                                            { label: 'D/E Ratio', val: selectedStock["D/E"] },
                                            { label: 'Sales CAGR', val: `${selectedStock["Rev CAGR (%)"]}%` },
                                            { label: 'Inst. Stake', val: `${(selectedStock["FII (%)"] + selectedStock["DII (%)"]).toFixed(1)}%` },
                                        ].map(item => (
                                            <div key={item.label} className="flex flex-col items-center p-4 bg-slate-50 rounded-xl border border-slate-200">
                                                <span className="text-[10px] md:text-xs text-slate-500 font-bold mb-1 uppercase tracking-wider">{item.label}</span>
                                                <span className="text-xl font-bold text-slate-900 tracking-tight">{item.val}</span>
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
        <Suspense fallback={<div className="text-slate-500">Loading Engine...</div>}>
            <InsightContent data={data} />
        </Suspense>
    );
}
