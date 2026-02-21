import { getStockData } from '@/lib/data';
import InsightView from '@/components/InsightView';
import Navbar from '@/components/Navbar';

export default function InsightsPage() {
    const data = getStockData();

    return (
        <div className="min-h-screen bg-[#050505] text-white">
            <Navbar />
            <div className="p-6 md:p-10 space-y-24 max-w-7xl mx-auto pb-40">
                <header className="py-10">
                    <h1 className="text-6xl md:text-8xl font-black tracking-tighter gradient-text leading-tight mb-4">
                        Deep Insight<br />Engine.
                    </h1>
                </header>
                <InsightView data={data} />
            </div>
        </div>
    );
}
