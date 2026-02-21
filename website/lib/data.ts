import fs from 'fs';
import path from 'path';

export function getStockData() {
    const filePath = path.join(process.cwd(), 'data', 'stockData.json');
    if (!fs.existsSync(filePath)) return [];
    const fileData = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(fileData);
}
