import { getStockData } from '@/lib/data';
import InsightView from '@/components/InsightView';
import Navbar from '@/components/Navbar';

export default function InsightsPage() {
    const data = getStockData();

    return (
        <div className="min-h-screen bg-slate-50 text-slate-900">
            <Navbar />
            <div className="p-6 md:p-10 space-y-16 max-w-7xl mx-auto pb-40">
                <header className="py-8">
                    <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-slate-900 mb-2">
                        Deep Insight Engine
                    </h1>
                    <p className="text-slate-500 text-lg">Multi-dimensional analysis combining hard financials with AI-driven qualitative scoring.</p>
                </header>
                <InsightView data={data} />
            </div>
        </div>
    );
}
