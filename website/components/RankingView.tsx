"use client";

import React from 'react';
import { useRouter } from 'next/navigation';

export default function RankingView({ data }: { data: any[] }) {
    const router = useRouter();

    return (
        <section id="full-ranking" className="space-y-12">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-l-4 border-white/10 pl-8">
                <div>
                    <h2 className="text-4xl md:text-5xl font-black tracking-tighter uppercase mb-2 text-white/50">Full Quantitative Ranking</h2>
                    <p className="text-gray-500 font-medium max-w-xl">Complete index of analyzed symbols including sub-component scores for DCF, Growth, and MOAT.</p>
                </div>
            </div>

            <div className="glass-card overflow-hidden border-white/5 shadow-black shadow-2xl">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-white/5 text-[10px] uppercase font-black tracking-[0.3em] text-gray-500">
                                <th className="p-8 border-b border-white/10">Rank</th>
                                <th className="p-8 border-b border-white/10">Symbol</th>
                                <th className="p-8 border-b border-white/10 text-center">Quant Score</th>
                                <th className="p-8 border-b border-white/10 text-center">DCF</th>
                                <th className="p-8 border-b border-white/10 text-center">Growth</th>
                                <th className="p-8 border-b border-white/10 text-center">ROCE</th>
                                <th className="p-8 border-b border-white/10 text-center">Moat</th>
                                <th className="p-8 border-b border-white/10 text-right">Relative Value</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {data.map((s, i) => {
                                const overvaluation = ((s["Current Price"] / s["Intrinsic Price Per Share"] || 1) - 1) * 100;
                                const isTopPick = (s.portfolio_weight || 0) > 0;
                                return (
                                    <tr
                                        key={s.symbol}
                                        className={`group transition-all cursor-pointer ${isTopPick ? 'bg-blue-500/[0.02] hover:bg-blue-500/[0.05]' : 'hover:bg-white/[0.03]'}`}
                                        onClick={() => router.push(`/insights?symbol=${s.symbol}`)}
                                    >
                                        <td className="p-8 text-gray-700 font-mono text-sm group-hover:text-gray-400 transition-colors uppercase">{i + 1}</td>
                                        <td className="p-8 whitespace-nowrap">
                                            <div className="font-black text-xl group-hover:text-blue-400 transition-colors">{s.symbol}</div>
                                            <div className="text-[10px] text-gray-600 uppercase font-black tracking-[0.2em] mt-1">{s["Broad Sector"] || 'Other'} {isTopPick && <span className="text-emerald-400 ml-2">• TOP PICK</span>}</div>
                                        </td>
                                        <td className="p-8 text-center">
                                            <span className={`px-6 py-2.5 rounded-2xl text-sm font-black shadow-xl ${s.final_score > 60 ? 'bg-emerald-500/20 text-emerald-400' : s.final_score > 45 ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-500'}`}>
                                                {s.final_score}
                                            </span>
                                        </td>
                                        <td className="p-8 text-center text-xs font-black text-gray-500 font-mono tracking-tighter">{s.scores?.dcf_score?.toFixed(1)}</td>
                                        <td className="p-8 text-center text-xs font-black text-gray-500 font-mono tracking-tighter">{s.scores?.growth_score?.toFixed(1)}</td>
                                        <td className="p-8 text-center text-xs font-black text-gray-500 font-mono tracking-tighter">{s.scores?.roce_score?.toFixed(1)}</td>
                                        <td className="p-8 text-center text-xs font-black text-gray-500 font-mono tracking-tighter">{s.scores?.moat_score?.toFixed(1)}</td>
                                        <td className="p-8 text-right whitespace-nowrap">
                                            <span className={`text-xs font-black uppercase tracking-widest ${overvaluation > 0 ? 'text-red-500' : 'text-emerald-400 font-black'}`}>
                                                {overvaluation > 0 ? `+${overvaluation.toFixed(1)}% OVERVAL` : `${Math.abs(overvaluation).toFixed(1)}% DISCOUNT`}
                                            </span>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    );
}
