"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';

export default function Navbar() {
    const pathname = usePathname();

    const navItems = [
        { name: 'Portfolio', href: '/portfolio' },
        { name: 'Insights', href: '/insights' },
        { name: 'Rankings', href: '/rankings' }
    ];

    return (
        <nav className="sticky top-0 z-50 bg-[#050505]/60 backdrop-blur-xl border-b border-white/5 overflow-x-auto no-scrollbar">
            <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between whitespace-nowrap gap-10">
                <Link href="/" className="flex items-center gap-2 group cursor-pointer">
                    <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-black italic shadow-[0_0_20px_rgba(37,99,235,0.4)] text-white">Q</div>
                    <span className="font-black tracking-tighter text-xl text-white">QUANTBOT</span>
                </Link>
                <div className="flex items-center gap-8">
                    {navItems.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`text-[10px] font-black uppercase tracking-[0.2em] transition-all relative py-2 ${pathname === item.href ? 'text-blue-400' : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            {item.name}
                            {pathname === item.href && (
                                <motion.div
                                    layoutId="nav-underline"
                                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 shadow-[0_0_10px_rgba(37,99,235,0.8)]"
                                />
                            )}
                        </Link>
                    ))}
                </div>
            </div>
        </nav>
    );
}
