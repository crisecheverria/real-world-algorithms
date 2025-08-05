interface Stock {
    day: number;
    price: number;
}

class StockTrader {
    private prices: number[];
    private memo: Map<string, number>;

    constructor(prices: number[]) {
        this.prices = prices;
        this.memo = new Map();
    }

    maxProfit(): number {
        if (this.prices.length < 2) return 0;
        return this.maxProfitRecursive(0, false);
    }

    private maxProfitRecursive(day: number, holding: boolean): number {
        if (day >= this.prices.length) return 0;

        const key = `${day}_${holding}`;
        if (this.memo.has(key)) {
            return this.memo.get(key)!;
        }

        let result: number;

        if (holding) {
            // Can sell or hold
            const sellProfit = this.prices[day] + this.maxProfitRecursive(day + 1, false);
            const holdProfit = this.maxProfitRecursive(day + 1, true);
            result = Math.max(sellProfit, holdProfit);
        } else {
            // Can buy or wait
            const buyProfit = -this.prices[day] + this.maxProfitRecursive(day + 1, true);
            const waitProfit = this.maxProfitRecursive(day + 1, false);
            result = Math.max(buyProfit, waitProfit);
        }

        this.memo.set(key, result);
        return result;
    }

    maxProfitWithCooldown(): number {
        if (this.prices.length < 2) return 0;

        const n = this.prices.length;
        const hold = new Array(n).fill(0);
        const sold = new Array(n).fill(0);
        const rest = new Array(n).fill(0);

        hold[0] = -this.prices[0];
        sold[0] = 0;
        rest[0] = 0;

        for (let i = 1; i < n; i++) {
            hold[i] = Math.max(hold[i - 1], rest[i - 1] - this.prices[i]);
            sold[i] = hold[i - 1] + this.prices[i];
            rest[i] = Math.max(rest[i - 1], sold[i - 1]);
        }

        return Math.max(sold[n - 1], rest[n - 1]);
    }

    findBestTradingDays(): { buyDay: number; sellDay: number; profit: number } {
        if (this.prices.length < 2) {
            return { buyDay: -1, sellDay: -1, profit: 0 };
        }

        let minPrice = this.prices[0];
        let maxProfit = 0;
        let buyDay = 0;
        let sellDay = 0;
        let tempBuyDay = 0;

        for (let i = 1; i < this.prices.length; i++) {
            if (this.prices[i] < minPrice) {
                minPrice = this.prices[i];
                tempBuyDay = i;
            } else if (this.prices[i] - minPrice > maxProfit) {
                maxProfit = this.prices[i] - minPrice;
                buyDay = tempBuyDay;
                sellDay = i;
            }
        }

        return { buyDay, sellDay, profit: maxProfit };
    }

    getPortfolioAnalysis(): {
        volatility: number;
        trend: 'bullish' | 'bearish' | 'sideways';
        averagePrice: number;
        priceRange: { min: number; max: number };
    } {
        const min = Math.min(...this.prices);
        const max = Math.max(...this.prices);
        const average = this.prices.reduce((sum, price) => sum + price, 0) / this.prices.length;
        
        // Calculate volatility (standard deviation)
        const variance = this.prices.reduce((sum, price) => sum + Math.pow(price - average, 2), 0) / this.prices.length;
        const volatility = Math.sqrt(variance);

        // Determine trend
        const firstHalf = this.prices.slice(0, Math.floor(this.prices.length / 2));
        const secondHalf = this.prices.slice(Math.floor(this.prices.length / 2));
        const firstAvg = firstHalf.reduce((sum, price) => sum + price, 0) / firstHalf.length;
        const secondAvg = secondHalf.reduce((sum, price) => sum + price, 0) / secondHalf.length;
        
        let trend: 'bullish' | 'bearish' | 'sideways';
        const trendThreshold = average * 0.05; // 5% threshold
        
        if (secondAvg > firstAvg + trendThreshold) {
            trend = 'bullish';
        } else if (secondAvg < firstAvg - trendThreshold) {
            trend = 'bearish';
        } else {
            trend = 'sideways';
        }

        return {
            volatility: Number(volatility.toFixed(2)),
            trend,
            averagePrice: Number(average.toFixed(2)),
            priceRange: { min, max }
        };
    }
}

class LZWCompressor {
    private dictionary: Map<string, number>;
    private nextCode: number;

    constructor() {
        this.dictionary = new Map();
        this.nextCode = 256;

        // Initialize dictionary with single characters
        for (let i = 0; i < 256; i++) {
            this.dictionary.set(String.fromCharCode(i), i);
        }
    }

    compress(input: string): number[] {
        if (input.length === 0) return [];

        const result: number[] = [];
        let current = '';

        for (const char of input) {
            const candidate = current + char;

            if (this.dictionary.has(candidate)) {
                current = candidate;
            } else {
                if (this.dictionary.has(current)) {
                    result.push(this.dictionary.get(current)!);
                }

                this.dictionary.set(candidate, this.nextCode++);
                current = char;
            }
        }

        if (current !== '' && this.dictionary.has(current)) {
            result.push(this.dictionary.get(current)!);
        }

        return result;
    }

    decompress(compressed: number[]): string {
        if (compressed.length === 0) return '';

        // Rebuild dictionary for decompression
        const reverseDictionary = new Map<number, string>();
        for (let i = 0; i < 256; i++) {
            reverseDictionary.set(i, String.fromCharCode(i));
        }

        let nextCode = 256;
        let result = '';
        let previous = '';

        for (let i = 0; i < compressed.length; i++) {
            const code = compressed[i];
            let entry: string;

            if (reverseDictionary.has(code)) {
                entry = reverseDictionary.get(code)!;
            } else if (code === nextCode) {
                entry = previous + previous[0];
            } else {
                throw new Error(`Invalid compression code: ${code}`);
            }

            result += entry;

            if (i > 0) {
                reverseDictionary.set(nextCode++, previous + entry[0]);
            }

            previous = entry;
        }

        return result;
    }

    getCompressionRatio(original: string, compressed: number[]): number {
        const originalSize = original.length * 8; // 8 bits per character
        const compressedSize = compressed.length * 16; // 16 bits per code

        if (originalSize === 0) return 0;
        return 1 - (compressedSize / originalSize);
    }

    analyzeCompression(text: string): {
        originalSize: number;
        compressedSize: number;
        compressionRatio: number;
        spaceSaved: number;
        dictionarySize: number;
    } {
        const compressed = this.compress(text);
        const ratio = this.getCompressionRatio(text, compressed);
        
        return {
            originalSize: text.length,
            compressedSize: compressed.length,
            compressionRatio: Number(ratio.toFixed(4)),
            spaceSaved: Number((ratio * 100).toFixed(2)),
            dictionarySize: this.dictionary.size
        };
    }
}

class DNAAligner {
    private match: number;
    private mismatch: number;
    private gap: number;
    private memo: Map<string, number>;

    constructor(match: number, mismatch: number, gap: number) {
        this.match = match;
        this.mismatch = mismatch;
        this.gap = gap;
        this.memo = new Map();
    }

    alignSequences(seq1: string, seq2: string): number {
        this.memo.clear();
        return this.alignRecursive(seq1, seq2, 0, 0);
    }

    private alignRecursive(seq1: string, seq2: string, i: number, j: number): number {
        const key = `${i}_${j}`;
        if (this.memo.has(key)) {
            return this.memo.get(key)!;
        }

        // Base cases
        if (i === seq1.length) {
            const result = (seq2.length - j) * this.gap;
            this.memo.set(key, result);
            return result;
        }

        if (j === seq2.length) {
            const result = (seq1.length - i) * this.gap;
            this.memo.set(key, result);
            return result;
        }

        // Calculate scores for all three options
        const score = seq1[i] === seq2[j] ? this.match : this.mismatch;
        const matchScore = score + this.alignRecursive(seq1, seq2, i + 1, j + 1);
        const deleteScore = this.gap + this.alignRecursive(seq1, seq2, i + 1, j);
        const insertScore = this.gap + this.alignRecursive(seq1, seq2, i, j + 1);

        const result = Math.max(matchScore, Math.max(deleteScore, insertScore));
        this.memo.set(key, result);
        return result;
    }

    getAlignment(seq1: string, seq2: string): {
        aligned1: string;
        aligned2: string;
        score: number;
        matches: number;
        similarity: number;
    } {
        const m = seq1.length;
        const n = seq2.length;
        
        // Create DP table
        const dp: number[][] = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));

        // Initialize base cases
        for (let i = 0; i <= m; i++) {
            dp[i][0] = i * this.gap;
        }
        for (let j = 0; j <= n; j++) {
            dp[0][j] = j * this.gap;
        }

        // Fill DP table
        for (let i = 1; i <= m; i++) {
            for (let j = 1; j <= n; j++) {
                const score = seq1[i - 1] === seq2[j - 1] ? this.match : this.mismatch;
                const matchScore = dp[i - 1][j - 1] + score;
                const deleteScore = dp[i - 1][j] + this.gap;
                const insertScore = dp[i][j - 1] + this.gap;
                
                dp[i][j] = Math.max(matchScore, Math.max(deleteScore, insertScore));
            }
        }

        // Traceback to get alignment
        let aligned1 = '';
        let aligned2 = '';
        let i = m, j = n;
        let matches = 0;

        while (i > 0 && j > 0) {
            if (seq1[i - 1] === seq2[j - 1]) {
                aligned1 = seq1[i - 1] + aligned1;
                aligned2 = seq2[j - 1] + aligned2;
                matches++;
                i--;
                j--;
            } else if (dp[i - 1][j] > dp[i][j - 1]) {
                aligned1 = seq1[i - 1] + aligned1;
                aligned2 = '-' + aligned2;
                i--;
            } else {
                aligned1 = '-' + aligned1;
                aligned2 = seq2[j - 1] + aligned2;
                j--;
            }
        }

        // Handle remaining characters
        while (i > 0) {
            aligned1 = seq1[i - 1] + aligned1;
            aligned2 = '-' + aligned2;
            i--;
        }

        while (j > 0) {
            aligned1 = '-' + aligned1;
            aligned2 = seq2[j - 1] + aligned2;
            j--;
        }

        const similarity = (matches / Math.max(seq1.length, seq2.length)) * 100;

        return {
            aligned1,
            aligned2,
            score: dp[m][n],
            matches,
            similarity: Number(similarity.toFixed(1))
        };
    }

    findConservedRegions(seq1: string, seq2: string, minLength: number = 3): string[] {
        const alignment = this.getAlignment(seq1, seq2);
        const conservedRegions: string[] = [];
        let currentRegion = '';
        let regionLength = 0;

        for (let i = 0; i < alignment.aligned1.length; i++) {
            if (alignment.aligned1[i] === alignment.aligned2[i] && alignment.aligned1[i] !== '-') {
                currentRegion += alignment.aligned1[i];
                regionLength++;
            } else {
                if (regionLength >= minLength) {
                    conservedRegions.push(currentRegion);
                }
                currentRegion = '';
                regionLength = 0;
            }
        }

        // Check final region
        if (regionLength >= minLength) {
            conservedRegions.push(currentRegion);
        }

        return conservedRegions;
    }
}

interface KnapsackItem {
    name: string;
    weight: number;
    value: number;
}

class KnapsackSolver {
    private items: KnapsackItem[];
    private memo: Map<string, number>;

    constructor(items: KnapsackItem[]) {
        this.items = items;
        this.memo = new Map();
    }

    solve(capacity: number): number {
        this.memo.clear();
        return this.solveRecursive(0, capacity);
    }

    private solveRecursive(index: number, remainingCapacity: number): number {
        if (index >= this.items.length || remainingCapacity <= 0) {
            return 0;
        }

        const key = `${index}_${remainingCapacity}`;
        if (this.memo.has(key)) {
            return this.memo.get(key)!;
        }

        const item = this.items[index];

        // Exclude current item
        const exclude = this.solveRecursive(index + 1, remainingCapacity);

        // Include current item (if it fits)
        let include = 0;
        if (item.weight <= remainingCapacity) {
            include = item.value + this.solveRecursive(index + 1, remainingCapacity - item.weight);
        }

        const result = Math.max(include, exclude);
        this.memo.set(key, result);
        return result;
    }

    getOptimalItems(capacity: number): KnapsackItem[] {
        const n = this.items.length;
        const dp: number[][] = Array(n + 1).fill(null).map(() => Array(capacity + 1).fill(0));

        // Fill DP table
        for (let i = 1; i <= n; i++) {
            for (let w = 1; w <= capacity; w++) {
                const item = this.items[i - 1];

                if (item.weight <= w) {
                    dp[i][w] = Math.max(
                        dp[i - 1][w],
                        dp[i - 1][w - item.weight] + item.value
                    );
                } else {
                    dp[i][w] = dp[i - 1][w];
                }
            }
        }

        // Traceback to find which items to include
        const result: KnapsackItem[] = [];
        let w = capacity;
        
        for (let i = n; i > 0 && w > 0; i--) {
            if (dp[i][w] !== dp[i - 1][w]) {
                result.push(this.items[i - 1]);
                w -= this.items[i - 1].weight;
            }
        }

        return result.reverse();
    }

    analyzeItems(): {
        totalItems: number;
        totalWeight: number;
        totalValue: number;
        averageValueToWeightRatio: number;
        bestRatioItem: KnapsackItem;
        worstRatioItem: KnapsackItem;
    } {
        const totalWeight = this.items.reduce((sum, item) => sum + item.weight, 0);
        const totalValue = this.items.reduce((sum, item) => sum + item.value, 0);
        
        const ratios = this.items.map(item => ({
            item,
            ratio: item.value / item.weight
        }));

        ratios.sort((a, b) => b.ratio - a.ratio);

        return {
            totalItems: this.items.length,
            totalWeight,
            totalValue,
            averageValueToWeightRatio: Number((totalValue / totalWeight).toFixed(2)),
            bestRatioItem: ratios[0].item,
            worstRatioItem: ratios[ratios.length - 1].item
        };
    }
}

function demonstrateDynamicProgramming(): void {
    console.log('=== Stock Trading Algorithm Example ===');
    const prices = [7, 1, 5, 3, 6, 4, 2, 8, 9, 3];
    const trader = new StockTrader(prices);

    console.log(`Stock prices: [${prices.join(', ')}]`);

    const maxProfit = trader.maxProfit();
    console.log(`Maximum profit (unlimited transactions): $${maxProfit.toFixed(2)}`);

    const maxProfitCooldown = trader.maxProfitWithCooldown();
    console.log(`Maximum profit (with cooldown): $${maxProfitCooldown.toFixed(2)}`);

    const bestTrade = trader.findBestTradingDays();
    console.log(`Best single trade: Buy day ${bestTrade.buyDay} ($${prices[bestTrade.buyDay]}) -> Sell day ${bestTrade.sellDay} ($${prices[bestTrade.sellDay]}) = $${bestTrade.profit.toFixed(2)} profit`);

    const analysis = trader.getPortfolioAnalysis();
    console.log(`Portfolio Analysis:`);
    console.log(`  Volatility: ${analysis.volatility}`);
    console.log(`  Trend: ${analysis.trend}`);
    console.log(`  Average price: $${analysis.averagePrice}`);
    console.log(`  Price range: $${analysis.priceRange.min} - $${analysis.priceRange.max}`);

    console.log('\n=== LZW Compression Example ===');
    const testStrings = [
        'ABABABA',
        'TOBEORNOTTOBEORTOBEORNOT',
        'ABCABCABCABCABC',
        'The quick brown fox jumps over the lazy dog',
        'AAAAAABBBBBBCCCCCCDDDDDD'
    ];

    testStrings.forEach(text => {
        const compressor = new LZWCompressor();
        const analysis = compressor.analyzeCompression(text);
        const compressed = compressor.compress(text);
        
        console.log(`\nOriginal: "${text}" (${analysis.originalSize} chars)`);
        console.log(`Compressed: [${compressed.slice(0, 10).join(', ')}${compressed.length > 10 ? '...' : ''}] (${analysis.compressedSize} codes)`);
        console.log(`Compression: ${analysis.spaceSaved}% space saved`);
        console.log(`Dictionary size: ${analysis.dictionarySize} entries`);

        // Test decompression
        const decompressed = compressor.decompress(compressed);
        console.log(`Decompression successful: ${decompressed === text}`);
    });

    console.log('\n=== DNA Sequence Alignment Example ===');
    const aligner = new DNAAligner(2, -1, -2); // match: +2, mismatch: -1, gap: -2

    const sequencePairs = [
        ['ACGT', 'ACG'],
        ['GCATGCU', 'GATTACA'],
        ['ATCGATCG', 'ATCCTCG'],
        ['TGCATAT', 'ATCCTAT'],
        ['AGTACGCA', 'TATGC']
    ];

    sequencePairs.forEach(([seq1, seq2]) => {
        const alignment = aligner.getAlignment(seq1, seq2);
        const conservedRegions = aligner.findConservedRegions(seq1, seq2);

        console.log(`\nSequence 1: ${seq1}`);
        console.log(`Sequence 2: ${seq2}`);
        console.log(`Alignment score: ${alignment.score}`);
        console.log(`Optimal alignment:`);
        console.log(`  ${alignment.aligned1}`);
        console.log(`  ${alignment.aligned2}`);
        console.log(`Matches: ${alignment.matches}, Similarity: ${alignment.similarity}%`);
        
        if (conservedRegions.length > 0) {
            console.log(`Conserved regions: ${conservedRegions.join(', ')}`);
        }
    });

    console.log('\n=== Knapsack Problem Example ===');
    const items: KnapsackItem[] = [
        { name: 'Gold Bar', weight: 10, value: 60 },
        { name: 'Silver Coin', weight: 20, value: 100 },
        { name: 'Diamond', weight: 30, value: 120 },
        { name: 'Ruby', weight: 15, value: 80 },
        { name: 'Emerald', weight: 25, value: 110 },
        { name: 'Sapphire', weight: 12, value: 70 },
        { name: 'Pearl', weight: 8, value: 40 },
        { name: 'Platinum Ring', weight: 18, value: 95 }
    ];

    const solver = new KnapsackSolver(items);
    const capacity = 50;

    const maxValue = solver.solve(capacity);
    const optimalItems = solver.getOptimalItems(capacity);
    const analysis = solver.analyzeItems();

    console.log(`Knapsack capacity: ${capacity} units`);
    console.log(`Available items:`);
    items.forEach(item => {
        const ratio = (item.value / item.weight).toFixed(2);
        console.log(`  ${item.name}: Weight=${item.weight}, Value=${item.value} (ratio=${ratio})`);
    });

    console.log(`\nItem Analysis:`);
    console.log(`  Total items: ${analysis.totalItems}`);
    console.log(`  Total weight: ${analysis.totalWeight}, Total value: ${analysis.totalValue}`);
    console.log(`  Average value/weight ratio: ${analysis.averageValueToWeightRatio}`);
    console.log(`  Best ratio: ${analysis.bestRatioItem.name} (${(analysis.bestRatioItem.value / analysis.bestRatioItem.weight).toFixed(2)})`);
    console.log(`  Worst ratio: ${analysis.worstRatioItem.name} (${(analysis.worstRatioItem.value / analysis.worstRatioItem.weight).toFixed(2)})`);

    console.log(`\nOptimal solution (value: ${maxValue}):`);
    let totalWeight = 0;
    let totalValue = 0;
    
    optimalItems.forEach(item => {
        console.log(`  + ${item.name} (Weight: ${item.weight}, Value: ${item.value})`);
        totalWeight += item.weight;
        totalValue += item.value;
    });
    
    console.log(`Total weight: ${totalWeight}/${capacity}, Total value: ${totalValue}`);
    console.log(`Knapsack utilization: ${((totalWeight / capacity) * 100).toFixed(1)}%`);
    console.log(`Efficiency: ${(totalValue / totalWeight).toFixed(2)} value per weight unit`);
}

if (require.main === module) {
    demonstrateDynamicProgramming();
}

export { StockTrader, LZWCompressor, DNAAligner, KnapsackSolver };