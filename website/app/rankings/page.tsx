import { getStockData } from '@/lib/data';
import RankingView from '@/components/RankingView';
import Navbar from '@/components/Navbar';

export default function RankingsPage() {
    const data = getStockData();

    return (
        <div className="min-h-screen bg-[#050505] text-white">
            <Navbar />
            <div className="p-6 md:p-10 space-y-24 max-w-7xl mx-auto pb-40">
                <header className="py-10">
                    <h1 className="text-6xl md:text-8xl font-black tracking-tighter gradient-text leading-tight mb-4">
                        Full Quant<br />Rankings.
                    </h1>
                </header>
                <RankingView data={data} />
            </div>
        </div>
    );
}
