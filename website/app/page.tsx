import Dashboard from '@/components/Dashboard';
import fs from 'fs';
import path from 'path';

export default function Home() {
  const filePath = path.join(process.cwd(), 'data', 'stockData.json');
  const fileData = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(fileData);

  return (
    <main className="min-h-screen bg-background">
      <Dashboard data={data} />
    </main>
  );
}
