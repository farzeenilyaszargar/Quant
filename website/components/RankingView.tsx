"use client";

import React from 'react';
import { useRouter } from 'next/navigation';

export default function RankingView({ data }: { data: any[] }) {
    const router = useRouter();

    const fallbackOverval = (current: number, intrinsic: number) => {
        if (!intrinsic || intrinsic <= 0) return 0;
        return ((current / intrinsic) - 1) * 100;
    };

    return (
        <section id="full-ranking" className="space-y-10">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-200">
                <div>
                    <h2 className="text-2xl md:text-3xl font-bold text-slate-900 mb-1">Full Quantitative Ranking</h2>
                    <p className="text-slate-500 font-medium">Complete index of analyzed symbols including sub-component scores for DCF, Growth, and MOAT.</p>
                </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-slate-50 text-xs font-semibold uppercase tracking-wider text-slate-500 border-b border-slate-200">
                                <th className="px-6 py-4">Rank</th>
                                <th className="px-6 py-4">Symbol</th>
                                <th className="px-6 py-4 text-center">Quant Score</th>
                                <th className="px-6 py-4 text-center">DCF</th>
                                <th className="px-6 py-4 text-center">Growth</th>
                                <th className="px-6 py-4 text-center">ROCE</th>
                                <th className="px-6 py-4 text-center">Moat</th>
                                <th className="px-6 py-4 text-right">Relative Value</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {data.map((s, i) => {
                                const intrinsic = s["Intrinsic Price Per Share"];
                                const current = s["Current Price"];
                                const overvaluation = fallbackOverval(current, intrinsic);
                                const isTopPick = (s.portfolio_weight || 0) > 0;
                                return (
                                    <tr
                                        key={s.symbol}
                                        className={`group transition-colors cursor-pointer hover:bg-slate-50 ${isTopPick ? 'bg-blue-50/30' : ''}`}
                                        onClick={() => router.push(`/insights?symbol=${s.symbol}`)}
                                    >
                                        <td className="px-6 py-5 text-slate-400 font-medium text-sm group-hover:text-slate-600 transition-colors uppercase">{i + 1}</td>
                                        <td className="px-6 py-5 whitespace-nowrap">
                                            <div className="font-bold text-lg text-slate-900 group-hover:text-blue-600 transition-colors leading-tight">{s.symbol}</div>
                                            <div className="text-xs text-slate-500 font-medium uppercase mt-0.5">{s["Broad Sector"] || 'Other'} {isTopPick && <span className="text-blue-600 font-bold ml-2 tracking-wide text-[10px]">• TOP PICK</span>}</div>
                                        </td>
                                        <td className="px-6 py-5 text-center">
                                            <span className={`px-4 py-1.5 rounded-lg text-xs font-bold ${s.final_score > 60 ? 'bg-emerald-100 text-emerald-700' : s.final_score > 40 ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'}`}>
                                                {s.final_score}
                                            </span>
                                        </td>
                                        <td className="px-6 py-5 text-center text-sm font-semibold text-slate-600">{s.scores?.dcf_score?.toFixed(1) || '-'}</td>
                                        <td className="px-6 py-5 text-center text-sm font-semibold text-slate-600">{s.scores?.growth_score?.toFixed(1) || '-'}</td>
                                        <td className="px-6 py-5 text-center text-sm font-semibold text-slate-600">{s.scores?.roce_score?.toFixed(1) || '-'}</td>
                                        <td className="px-6 py-5 text-center text-sm font-semibold text-slate-600">{s.scores?.moat_score?.toFixed(1) || '-'}</td>
                                        <td className="px-6 py-5 text-right whitespace-nowrap">
                                            <span className={`text-xs font-bold uppercase tracking-wide ${overvaluation > 0 ? 'text-red-500' : 'text-emerald-600'}`}>
                                                {overvaluation > 0 ? `+${overvaluation.toFixed(1)}% PREM` : `${Math.abs(overvaluation).toFixed(1)}% DISC`}
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
