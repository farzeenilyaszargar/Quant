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
        <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200 overflow-x-auto no-scrollbar">
            <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between whitespace-nowrap gap-10">
                <Link href="/" className="flex items-center gap-2 group cursor-pointer">
                    <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white">Q</div>
                    <span className="font-bold tracking-tight text-xl text-slate-900">QuantBot</span>
                </Link>
                <div className="flex items-center gap-8">
                    {navItems.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`text-sm font-medium transition-all relative py-2 ${pathname === item.href ? 'text-blue-600' : 'text-slate-500 hover:text-slate-900'
                                }`}
                        >
                            {item.name}
                            {pathname === item.href && (
                                <motion.div
                                    layoutId="nav-underline"
                                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600"
                                />
                            )}
                        </Link>
                    ))}
                </div>
            </div>
        </nav>
    );
}
