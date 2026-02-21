import { getStockData } from '@/lib/data';
import PortfolioView from '@/components/PortfolioView';
import Navbar from '@/components/Navbar';

export default function PortfolioPage() {
    const data = getStockData();

    return (
        <div className="min-h-screen bg-[#050505] text-white">
            <Navbar />
            <div className="p-6 md:p-10 space-y-24 max-w-7xl mx-auto pb-40">
                <header className="py-10">
                    <h1 className="text-6xl md:text-8xl font-black tracking-tighter gradient-text leading-tight mb-4">
                        Alpha Generation<br />Dashboard.
                    </h1>
                </header>
                <PortfolioView data={data} />
            </div>
        </div>
    );
}
