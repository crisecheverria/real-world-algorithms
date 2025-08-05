from typing import List, Dict, Tuple, Optional
import math
from dataclasses import dataclass

@dataclass
class Stock:
    day: int
    price: float

class StockTrader:
    def __init__(self, prices: List[float]):
        self.prices = prices
        self.memo: Dict[str, float] = {}
    
    def max_profit(self) -> float:
        """Calculate maximum profit with unlimited transactions"""
        if len(self.prices) < 2:
            return 0
        
        self.memo.clear()
        return self._max_profit_recursive(0, False)
    
    def _max_profit_recursive(self, day: int, holding: bool) -> float:
        if day >= len(self.prices):
            return 0
        
        key = f"{day}_{holding}"
        if key in self.memo:
            return self.memo[key]
        
        if holding:
            # Can sell or hold
            sell_profit = self.prices[day] + self._max_profit_recursive(day + 1, False)
            hold_profit = self._max_profit_recursive(day + 1, True)
            result = max(sell_profit, hold_profit)
        else:
            # Can buy or wait
            buy_profit = -self.prices[day] + self._max_profit_recursive(day + 1, True)
            wait_profit = self._max_profit_recursive(day + 1, False)
            result = max(buy_profit, wait_profit)
        
        self.memo[key] = result
        return result
    
    def max_profit_with_cooldown(self) -> float:
        """Calculate maximum profit with cooldown period after selling"""
        if len(self.prices) < 2:
            return 0
        
        n = len(self.prices)
        hold = [0] * n  # Maximum profit when holding stock
        sold = [0] * n  # Maximum profit when just sold (cooldown)
        rest = [0] * n  # Maximum profit when resting (can buy)
        
        hold[0] = -self.prices[0]
        sold[0] = 0
        rest[0] = 0
        
        for i in range(1, n):
            hold[i] = max(hold[i-1], rest[i-1] - self.prices[i])
            sold[i] = hold[i-1] + self.prices[i]
            rest[i] = max(rest[i-1], sold[i-1])
        
        return max(sold[n-1], rest[n-1])
    
    def find_best_trading_days(self) -> Tuple[int, int, float]:
        """Find the best single buy-sell transaction"""
        if len(self.prices) < 2:
            return -1, -1, 0
        
        min_price = self.prices[0]
        max_profit = 0
        buy_day = 0
        sell_day = 0
        temp_buy_day = 0
        
        for i in range(1, len(self.prices)):
            if self.prices[i] < min_price:
                min_price = self.prices[i]
                temp_buy_day = i
            elif self.prices[i] - min_price > max_profit:
                max_profit = self.prices[i] - min_price
                buy_day = temp_buy_day
                sell_day = i
        
        return buy_day, sell_day, max_profit
    
    def get_portfolio_analysis(self) -> Dict[str, any]:
        """Analyze portfolio statistics"""
        if not self.prices:
            return {}
        
        min_price = min(self.prices)
        max_price = max(self.prices)
        avg_price = sum(self.prices) / len(self.prices)
        
        # Calculate volatility (standard deviation)
        variance = sum((price - avg_price) ** 2 for price in self.prices) / len(self.prices)
        volatility = math.sqrt(variance)
        
        # Determine trend
        mid_point = len(self.prices) // 2
        first_half_avg = sum(self.prices[:mid_point]) / mid_point
        second_half_avg = sum(self.prices[mid_point:]) / (len(self.prices) - mid_point)
        
        trend_threshold = avg_price * 0.05  # 5% threshold
        if second_half_avg > first_half_avg + trend_threshold:
            trend = 'bullish'
        elif second_half_avg < first_half_avg - trend_threshold:
            trend = 'bearish'
        else:
            trend = 'sideways'
        
        return {
            'volatility': round(volatility, 2),
            'trend': trend,
            'average_price': round(avg_price, 2),
            'price_range': {'min': min_price, 'max': max_price},
            'total_return': round(((self.prices[-1] - self.prices[0]) / self.prices[0]) * 100, 2) if self.prices[0] != 0 else 0
        }

class LZWCompressor:
    def __init__(self):
        self.dictionary: Dict[str, int] = {}
        self.next_code = 256
        
        # Initialize dictionary with single characters
        for i in range(256):
            self.dictionary[chr(i)] = i
    
    def compress(self, text: str) -> List[int]:
        """Compress text using LZW algorithm"""
        if not text:
            return []
        
        result = []
        current = ''
        
        for char in text:
            candidate = current + char
            
            if candidate in self.dictionary:
                current = candidate
            else:
                if current in self.dictionary:
                    result.append(self.dictionary[current])
                
                self.dictionary[candidate] = self.next_code
                self.next_code += 1
                current = char
        
        if current and current in self.dictionary:
            result.append(self.dictionary[current])
        
        return result
    
    def decompress(self, compressed: List[int]) -> str:
        """Decompress LZW compressed data"""
        if not compressed:
            return ''
        
        # Rebuild dictionary for decompression
        reverse_dict = {i: chr(i) for i in range(256)}
        next_code = 256
        
        result = ''
        previous = ''
        
        for i, code in enumerate(compressed):
            if code in reverse_dict:
                entry = reverse_dict[code]
            elif code == next_code:
                entry = previous + previous[0]
            else:
                raise ValueError(f"Invalid compression code: {code}")
            
            result += entry
            
            if i > 0:
                reverse_dict[next_code] = previous + entry[0]
                next_code += 1
            
            previous = entry
        
        return result
    
    def get_compression_ratio(self, original: str, compressed: List[int]) -> float:
        """Calculate compression ratio"""
        original_size = len(original) * 8  # 8 bits per character
        compressed_size = len(compressed) * 16  # 16 bits per code
        
        if original_size == 0:
            return 0
        
        return 1 - (compressed_size / original_size)
    
    def analyze_compression(self, text: str) -> Dict[str, any]:
        """Analyze compression performance"""
        compressed = self.compress(text)
        ratio = self.get_compression_ratio(text, compressed)
        
        # Reset for fresh analysis
        self.__init__()
        
        return {
            'original_size': len(text),
            'compressed_size': len(compressed),
            'compression_ratio': round(ratio, 4),
            'space_saved': round(ratio * 100, 2),
            'dictionary_size': len(self.dictionary),
            'efficiency': 'good' if ratio > 0.3 else 'moderate' if ratio > 0.1 else 'poor'
        }

class DNAAligner:
    def __init__(self, match_score: int = 2, mismatch_penalty: int = -1, gap_penalty: int = -2):
        self.match_score = match_score
        self.mismatch_penalty = mismatch_penalty
        self.gap_penalty = gap_penalty
        self.memo: Dict[str, int] = {}
    
    def align_sequences(self, seq1: str, seq2: str) -> int:
        """Calculate optimal alignment score using dynamic programming"""
        self.memo.clear()
        return self._align_recursive(seq1, seq2, 0, 0)
    
    def _align_recursive(self, seq1: str, seq2: str, i: int, j: int) -> int:
        key = f"{i}_{j}"
        if key in self.memo:
            return self.memo[key]
        
        # Base cases
        if i == len(seq1):
            result = (len(seq2) - j) * self.gap_penalty
            self.memo[key] = result
            return result
        
        if j == len(seq2):
            result = (len(seq1) - i) * self.gap_penalty
            self.memo[key] = result
            return result
        
        # Calculate scores for all three options
        score = self.match_score if seq1[i] == seq2[j] else self.mismatch_penalty
        match_score = score + self._align_recursive(seq1, seq2, i + 1, j + 1)
        delete_score = self.gap_penalty + self._align_recursive(seq1, seq2, i + 1, j)
        insert_score = self.gap_penalty + self._align_recursive(seq1, seq2, i, j + 1)
        
        result = max(match_score, delete_score, insert_score)
        self.memo[key] = result
        return result
    
    def get_alignment(self, seq1: str, seq2: str) -> Dict[str, any]:
        """Get optimal alignment with traceback"""
        m, n = len(seq1), len(seq2)
        
        # Create DP table
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Initialize base cases
        for i in range(m + 1):
            dp[i][0] = i * self.gap_penalty
        for j in range(n + 1):
            dp[0][j] = j * self.gap_penalty
        
        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                score = self.match_score if seq1[i-1] == seq2[j-1] else self.mismatch_penalty
                match_score = dp[i-1][j-1] + score
                delete_score = dp[i-1][j] + self.gap_penalty
                insert_score = dp[i][j-1] + self.gap_penalty
                
                dp[i][j] = max(match_score, delete_score, insert_score)
        
        # Traceback to get alignment
        aligned1, aligned2 = '', ''
        i, j = m, n
        matches = 0
        
        while i > 0 and j > 0:
            if seq1[i-1] == seq2[j-1]:
                aligned1 = seq1[i-1] + aligned1
                aligned2 = seq2[j-1] + aligned2
                matches += 1
                i -= 1
                j -= 1
            elif dp[i-1][j] > dp[i][j-1]:
                aligned1 = seq1[i-1] + aligned1
                aligned2 = '-' + aligned2
                i -= 1
            else:
                aligned1 = '-' + aligned1
                aligned2 = seq2[j-1] + aligned2
                j -= 1
        
        # Handle remaining characters
        while i > 0:
            aligned1 = seq1[i-1] + aligned1
            aligned2 = '-' + aligned2
            i -= 1
        
        while j > 0:
            aligned1 = '-' + aligned1
            aligned2 = seq2[j-1] + aligned2
            j -= 1
        
        similarity = (matches / max(len(seq1), len(seq2))) * 100
        
        return {
            'aligned1': aligned1,
            'aligned2': aligned2,
            'score': dp[m][n],
            'matches': matches,
            'similarity': round(similarity, 1),
            'identity': round((matches / len(aligned1)) * 100, 1) if aligned1 else 0
        }
    
    def find_conserved_regions(self, seq1: str, seq2: str, min_length: int = 3) -> List[str]:
        """Find conserved regions in the alignment"""
        alignment = self.get_alignment(seq1, seq2)
        conserved_regions = []
        current_region = ''
        region_length = 0
        
        for i in range(len(alignment['aligned1'])):
            if (alignment['aligned1'][i] == alignment['aligned2'][i] and 
                alignment['aligned1'][i] != '-'):
                current_region += alignment['aligned1'][i]
                region_length += 1
            else:
                if region_length >= min_length:
                    conserved_regions.append(current_region)
                current_region = ''
                region_length = 0
        
        # Check final region
        if region_length >= min_length:
            conserved_regions.append(current_region)
        
        return conserved_regions
    
    def analyze_sequences(self, seq1: str, seq2: str) -> Dict[str, any]:
        """Comprehensive sequence analysis"""
        alignment = self.get_alignment(seq1, seq2)
        conserved = self.find_conserved_regions(seq1, seq2)
        
        # Calculate composition
        def get_composition(sequence):
            total = len([c for c in sequence if c != '-'])
            if total == 0:
                return {}
            return {
                'A': sequence.count('A') / total * 100,
                'T': sequence.count('T') / total * 100,
                'G': sequence.count('G') / total * 100,
                'C': sequence.count('C') / total * 100
            }
        
        return {
            'alignment': alignment,
            'conserved_regions': conserved,
            'conserved_count': len(conserved),
            'seq1_composition': get_composition(seq1),
            'seq2_composition': get_composition(seq2),
            'alignment_length': len(alignment['aligned1']),
            'gaps_seq1': alignment['aligned1'].count('-'),
            'gaps_seq2': alignment['aligned2'].count('-')
        }

@dataclass
class KnapsackItem:
    name: str
    weight: int
    value: int
    
    @property
    def value_to_weight_ratio(self) -> float:
        return self.value / self.weight if self.weight > 0 else 0

class KnapsackSolver:
    def __init__(self, items: List[KnapsackItem]):
        self.items = items
        self.memo: Dict[str, int] = {}
    
    def solve(self, capacity: int) -> int:
        """Solve knapsack problem using dynamic programming"""
        self.memo.clear()
        return self._solve_recursive(0, capacity)
    
    def _solve_recursive(self, index: int, remaining_capacity: int) -> int:
        if index >= len(self.items) or remaining_capacity <= 0:
            return 0
        
        key = f"{index}_{remaining_capacity}"
        if key in self.memo:
            return self.memo[key]
        
        item = self.items[index]
        
        # Exclude current item
        exclude = self._solve_recursive(index + 1, remaining_capacity)
        
        # Include current item (if it fits)
        include = 0
        if item.weight <= remaining_capacity:
            include = item.value + self._solve_recursive(index + 1, remaining_capacity - item.weight)
        
        result = max(include, exclude)
        self.memo[key] = result
        return result
    
    def get_optimal_items(self, capacity: int) -> List[KnapsackItem]:
        """Get the optimal set of items to include"""
        n = len(self.items)
        dp = [[0] * (capacity + 1) for _ in range(n + 1)]
        
        # Fill DP table
        for i in range(1, n + 1):
            for w in range(1, capacity + 1):
                item = self.items[i - 1]
                
                if item.weight <= w:
                    dp[i][w] = max(
                        dp[i - 1][w],
                        dp[i - 1][w - item.weight] + item.value
                    )
                else:
                    dp[i][w] = dp[i - 1][w]
        
        # Traceback to find which items to include
        result = []
        w = capacity
        
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                result.append(self.items[i - 1])
                w -= self.items[i - 1].weight
        
        return list(reversed(result))
    
    def analyze_items(self) -> Dict[str, any]:
        """Analyze the knapsack items"""
        if not self.items:
            return {}
        
        total_weight = sum(item.weight for item in self.items)
        total_value = sum(item.value for item in self.items)
        
        ratios = [(item, item.value_to_weight_ratio) for item in self.items]
        ratios.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'total_items': len(self.items),
            'total_weight': total_weight,
            'total_value': total_value,
            'average_value_to_weight_ratio': round(total_value / total_weight, 2) if total_weight > 0 else 0,
            'best_ratio_item': ratios[0][0] if ratios else None,
            'worst_ratio_item': ratios[-1][0] if ratios else None,
            'weight_distribution': {
                'min': min(item.weight for item in self.items),
                'max': max(item.weight for item in self.items),
                'avg': round(total_weight / len(self.items), 1)
            },
            'value_distribution': {
                'min': min(item.value for item in self.items),
                'max': max(item.value for item in self.items),
                'avg': round(total_value / len(self.items), 1)
            }
        }
    
    def solve_fractional_knapsack(self, capacity: int) -> Tuple[float, List[Tuple[KnapsackItem, float]]]:
        """Solve fractional knapsack for comparison"""
        # Sort items by value-to-weight ratio
        sorted_items = sorted(self.items, key=lambda x: x.value_to_weight_ratio, reverse=True)
        
        total_value = 0.0
        result_items = []
        remaining_capacity = capacity
        
        for item in sorted_items:
            if remaining_capacity <= 0:
                break
            
            if item.weight <= remaining_capacity:
                # Take the whole item
                total_value += item.value
                result_items.append((item, 1.0))
                remaining_capacity -= item.weight
            else:
                # Take fraction of the item
                fraction = remaining_capacity / item.weight
                total_value += item.value * fraction
                result_items.append((item, fraction))
                remaining_capacity = 0
        
        return total_value, result_items

def demonstrate_dynamic_programming():
    print("=== Stock Trading Algorithm Example ===")
    prices = [7.0, 1.0, 5.0, 3.0, 6.0, 4.0, 2.0, 8.0, 9.0, 3.0]
    trader = StockTrader(prices)
    
    print(f"Stock prices: {prices}")
    
    max_profit = trader.max_profit()
    print(f"Maximum profit (unlimited transactions): ${max_profit:.2f}")
    
    max_profit_cooldown = trader.max_profit_with_cooldown()
    print(f"Maximum profit (with cooldown): ${max_profit_cooldown:.2f}")
    
    buy_day, sell_day, best_profit = trader.find_best_trading_days()
    print(f"Best single trade: Buy day {buy_day} (${prices[buy_day]:.2f}) -> Sell day {sell_day} (${prices[sell_day]:.2f}) = ${best_profit:.2f} profit")
    
    analysis = trader.get_portfolio_analysis()
    print(f"Portfolio Analysis:")
    for key, value in analysis.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")

    print("\n=== LZW Compression Example ===")
    test_strings = [
        "ABABABA",
        "TOBEORNOTTOBEORTOBEORNOT", 
        "ABCABCABCABCABC",
        "The quick brown fox jumps over the lazy dog",
        "AAAAAABBBBBBCCCCCCDDDDDD",
        "Programming is fun and challenging"
    ]
    
    for text in test_strings:
        compressor = LZWCompressor()
        analysis = compressor.analyze_compression(text)
        compressed = compressor.compress(text)
        
        print(f"\nOriginal: \"{text}\" ({analysis['original_size']} chars)")
        print(f"Compressed: {compressed[:10]}{'...' if len(compressed) > 10 else ''} ({analysis['compressed_size']} codes)")
        print(f"Compression: {analysis['space_saved']}% space saved ({analysis['efficiency']})")
        print(f"Dictionary size: {analysis['dictionary_size']} entries")
        
        # Test decompression
        try:
            decompressed = compressor.decompress(compressed)
            print(f"Decompression successful: {decompressed == text}")
        except Exception as e:
            print(f"Decompression failed: {e}")

    print("\n=== DNA Sequence Alignment Example ===")
    aligner = DNAAligner(match_score=2, mismatch_penalty=-1, gap_penalty=-2)
    
    sequence_pairs = [
        ("ACGT", "ACG"),
        ("GCATGCU", "GATTACA"),
        ("ATCGATCG", "ATCCTCG"),
        ("TGCATAT", "ATCCTAT"),
        ("AGTACGCA", "TATGC"),
        ("CGTACGTTCG", "CGTTACG")
    ]
    
    for seq1, seq2 in sequence_pairs:
        analysis = aligner.analyze_sequences(seq1, seq2)
        alignment = analysis['alignment']
        
        print(f"\nSequence 1: {seq1}")
        print(f"Sequence 2: {seq2}")
        print(f"Alignment score: {alignment['score']}")
        print(f"Optimal alignment:")
        print(f"  {alignment['aligned1']}")
        print(f"  {alignment['aligned2']}")
        print(f"Matches: {alignment['matches']}, Similarity: {alignment['similarity']}%, Identity: {alignment['identity']}%")
        
        if analysis['conserved_regions']:
            print(f"Conserved regions ({analysis['conserved_count']}): {', '.join(analysis['conserved_regions'])}")
        
        print(f"Alignment length: {analysis['alignment_length']}, Gaps: seq1={analysis['gaps_seq1']}, seq2={analysis['gaps_seq2']}")

    print("\n=== Knapsack Problem Example ===")
    items = [
        KnapsackItem("Gold Bar", 10, 60),
        KnapsackItem("Silver Coin", 20, 100),
        KnapsackItem("Diamond", 30, 120),
        KnapsackItem("Ruby", 15, 80),
        KnapsackItem("Emerald", 25, 110),
        KnapsackItem("Sapphire", 12, 70),
        KnapsackItem("Pearl", 8, 40),
        KnapsackItem("Platinum Ring", 18, 95),
        KnapsackItem("Topaz", 22, 85),
        KnapsackItem("Opal", 14, 75)
    ]
    
    solver = KnapsackSolver(items)
    capacity = 50
    
    max_value = solver.solve(capacity)
    optimal_items = solver.get_optimal_items(capacity)
    analysis = solver.analyze_items()
    
    print(f"Knapsack capacity: {capacity} units")
    print(f"Available items:")
    for item in items:
        print(f"  {item.name}: Weight={item.weight}, Value={item.value} (ratio={item.value_to_weight_ratio:.2f})")
    
    print(f"\nItem Analysis:")
    print(f"  Total items: {analysis['total_items']}")
    print(f"  Total weight: {analysis['total_weight']}, Total value: {analysis['total_value']}")
    print(f"  Average value/weight ratio: {analysis['average_value_to_weight_ratio']}")
    if analysis['best_ratio_item']:
        print(f"  Best ratio: {analysis['best_ratio_item'].name} ({analysis['best_ratio_item'].value_to_weight_ratio:.2f})")
        print(f"  Worst ratio: {analysis['worst_ratio_item'].name} ({analysis['worst_ratio_item'].value_to_weight_ratio:.2f})")
    
    print(f"\n0/1 Knapsack Optimal Solution (value: {max_value}):")
    total_weight = 0
    total_value = 0
    
    for item in optimal_items:
        print(f"  + {item.name} (Weight: {item.weight}, Value: {item.value})")
        total_weight += item.weight
        total_value += item.value
    
    print(f"Total weight: {total_weight}/{capacity}, Total value: {total_value}")
    print(f"Knapsack utilization: {(total_weight / capacity) * 100:.1f}%")
    print(f"Efficiency: {total_value / total_weight:.2f} value per weight unit")
    
    # Compare with fractional knapsack
    fractional_value, fractional_items = solver.solve_fractional_knapsack(capacity)
    print(f"\nFractional Knapsack Comparison (value: {fractional_value:.2f}):")
    for item, fraction in fractional_items[:5]:  # Show first 5
        if fraction == 1.0:
            print(f"  + {item.name} (100%)")
        else:
            print(f"  + {item.name} ({fraction*100:.1f}%)")
    
    print(f"Improvement over 0/1: {((fractional_value - max_value) / max_value) * 100:.1f}%")

if __name__ == "__main__":
    demonstrate_dynamic_programming()