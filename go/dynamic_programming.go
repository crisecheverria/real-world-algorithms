package main

import (
	"fmt"
	"math"
	"strings"
)

type Stock struct {
	Day   int
	Price float64
}

type StockTrader struct {
	prices []float64
	memo   map[string]float64
}

func NewStockTrader(prices []float64) *StockTrader {
	return &StockTrader{
		prices: prices,
		memo:   make(map[string]float64),
	}
}

func (st *StockTrader) MaxProfit() float64 {
	if len(st.prices) < 2 {
		return 0
	}
	
	return st.maxProfitRecursive(0, false)
}

func (st *StockTrader) maxProfitRecursive(day int, holding bool) float64 {
	if day >= len(st.prices) {
		return 0
	}
	
	key := fmt.Sprintf("%d_%t", day, holding)
	if val, exists := st.memo[key]; exists {
		return val
	}
	
	var result float64
	
	if holding {
		sellProfit := st.prices[day] + st.maxProfitRecursive(day+1, false)
		holdProfit := st.maxProfitRecursive(day+1, true)
		result = math.Max(sellProfit, holdProfit)
	} else {
		buyProfit := -st.prices[day] + st.maxProfitRecursive(day+1, true)
		waitProfit := st.maxProfitRecursive(day+1, false)
		result = math.Max(buyProfit, waitProfit)
	}
	
	st.memo[key] = result
	return result
}

func (st *StockTrader) MaxProfitWithCooldown() float64 {
	if len(st.prices) < 2 {
		return 0
	}
	
	n := len(st.prices)
	
	hold := make([]float64, n)
	sold := make([]float64, n)
	rest := make([]float64, n)
	
	hold[0] = -st.prices[0]
	sold[0] = 0
	rest[0] = 0
	
	for i := 1; i < n; i++ {
		hold[i] = math.Max(hold[i-1], rest[i-1]-st.prices[i])
		sold[i] = hold[i-1] + st.prices[i]
		rest[i] = math.Max(rest[i-1], sold[i-1])
	}
	
	return math.Max(sold[n-1], rest[n-1])
}

func (st *StockTrader) FindBestTradingDays() (int, int, float64) {
	if len(st.prices) < 2 {
		return -1, -1, 0
	}
	
	minPrice := st.prices[0]
	maxProfit := 0.0
	buyDay := 0
	sellDay := 0
	tempBuyDay := 0
	
	for i := 1; i < len(st.prices); i++ {
		if st.prices[i] < minPrice {
			minPrice = st.prices[i]
			tempBuyDay = i
		} else if st.prices[i]-minPrice > maxProfit {
			maxProfit = st.prices[i] - minPrice
			buyDay = tempBuyDay
			sellDay = i
		}
	}
	
	return buyDay, sellDay, maxProfit
}

type LZWCompressor struct {
	dictionary map[string]int
	nextCode   int
}

func NewLZWCompressor() *LZWCompressor {
	comp := &LZWCompressor{
		dictionary: make(map[string]int),
		nextCode:   256,
	}
	
	for i := 0; i < 256; i++ {
		comp.dictionary[string(rune(i))] = i
	}
	
	return comp
}

func (lzw *LZWCompressor) Compress(input string) []int {
	if len(input) == 0 {
		return []int{}
	}
	
	result := []int{}
	current := ""
	
	for _, char := range input {
		candidate := current + string(char)
		
		if _, exists := lzw.dictionary[candidate]; exists {
			current = candidate
		} else {
			if code, exists := lzw.dictionary[current]; exists {
				result = append(result, code)
			}
			
			lzw.dictionary[candidate] = lzw.nextCode
			lzw.nextCode++
			current = string(char)
		}
	}
	
	if current != "" {
		if code, exists := lzw.dictionary[current]; exists {
			result = append(result, code)
		}
	}
	
	return result
}

func (lzw *LZWCompressor) CompressionRatio(original string, compressed []int) float64 {
	originalSize := len(original) * 8
	compressedSize := len(compressed) * 16
	
	if originalSize == 0 {
		return 0
	}
	
	return 1.0 - (float64(compressedSize) / float64(originalSize))
}

type DNAAligner struct {
	match    int
	mismatch int
	gap      int
	memo     map[string]int
}

func NewDNAAligner(match, mismatch, gap int) *DNAAligner {
	return &DNAAligner{
		match:    match,
		mismatch: mismatch,
		gap:      gap,
		memo:     make(map[string]int),
	}
}

func (dna *DNAAligner) AlignSequences(seq1, seq2 string) int {
	return dna.alignRecursive(seq1, seq2, 0, 0)
}

func (dna *DNAAligner) alignRecursive(seq1, seq2 string, i, j int) int {
	key := fmt.Sprintf("%d_%d", i, j)
	if val, exists := dna.memo[key]; exists {
		return val
	}
	
	if i == len(seq1) {
		dna.memo[key] = (len(seq2) - j) * dna.gap
		return dna.memo[key]
	}
	
	if j == len(seq2) {
		dna.memo[key] = (len(seq1) - i) * dna.gap
		return dna.memo[key]
	}
	
	var score int
	if seq1[i] == seq2[j] {
		score = dna.match
	} else {
		score = dna.mismatch
	}
	
	match := score + dna.alignRecursive(seq1, seq2, i+1, j+1)
	delete1 := dna.gap + dna.alignRecursive(seq1, seq2, i+1, j)
	delete2 := dna.gap + dna.alignRecursive(seq1, seq2, i, j+1)
	
	result := max(match, max(delete1, delete2))
	dna.memo[key] = result
	return result
}

func (dna *DNAAligner) GetAlignment(seq1, seq2 string) (string, string, int) {
	m, n := len(seq1), len(seq2)
	dp := make([][]int, m+1)
	for i := range dp {
		dp[i] = make([]int, n+1)
	}
	
	for i := 0; i <= m; i++ {
		dp[i][0] = i * dna.gap
	}
	for j := 0; j <= n; j++ {
		dp[0][j] = j * dna.gap
	}
	
	for i := 1; i <= m; i++ {
		for j := 1; j <= n; j++ {
			var score int
			if seq1[i-1] == seq2[j-1] {
				score = dna.match
			} else {
				score = dna.mismatch
			}
			
			match := dp[i-1][j-1] + score
			delete1 := dp[i-1][j] + dna.gap
			delete2 := dp[i][j-1] + dna.gap
			
			dp[i][j] = max(match, max(delete1, delete2))
		}
	}
	
	aligned1 := ""
	aligned2 := ""
	i, j := m, n
	
	for i > 0 && j > 0 {
		if seq1[i-1] == seq2[j-1] {
			aligned1 = string(seq1[i-1]) + aligned1
			aligned2 = string(seq2[j-1]) + aligned2
			i--
			j--
		} else if dp[i-1][j] > dp[i][j-1] {
			aligned1 = string(seq1[i-1]) + aligned1
			aligned2 = "-" + aligned2
			i--
		} else {
			aligned1 = "-" + aligned1
			aligned2 = string(seq2[j-1]) + aligned2
			j--
		}
	}
	
	for i > 0 {
		aligned1 = string(seq1[i-1]) + aligned1
		aligned2 = "-" + aligned2
		i--
	}
	
	for j > 0 {
		aligned1 = "-" + aligned1
		aligned2 = string(seq2[j-1]) + aligned2
		j--
	}
	
	return aligned1, aligned2, dp[m][n]
}

type KnapsackSolver struct {
	items []KnapsackItem
	memo  map[string]int
}

type KnapsackItem struct {
	Name   string
	Weight int
	Value  int
}

func NewKnapsackSolver(items []KnapsackItem) *KnapsackSolver {
	return &KnapsackSolver{
		items: items,
		memo:  make(map[string]int),
	}
}

func (ks *KnapsackSolver) Solve(capacity int) int {
	return ks.solveRecursive(0, capacity)
}

func (ks *KnapsackSolver) solveRecursive(index, remainingCapacity int) int {
	if index >= len(ks.items) || remainingCapacity <= 0 {
		return 0
	}
	
	key := fmt.Sprintf("%d_%d", index, remainingCapacity)
	if val, exists := ks.memo[key]; exists {
		return val
	}
	
	item := ks.items[index]
	
	exclude := ks.solveRecursive(index+1, remainingCapacity)
	
	var include int
	if item.Weight <= remainingCapacity {
		include = item.Value + ks.solveRecursive(index+1, remainingCapacity-item.Weight)
	}
	
	result := max(include, exclude)
	ks.memo[key] = result
	return result
}

func (ks *KnapsackSolver) GetOptimalItems(capacity int) []KnapsackItem {
	dp := make([][]int, len(ks.items)+1)
	for i := range dp {
		dp[i] = make([]int, capacity+1)
	}
	
	for i := 1; i <= len(ks.items); i++ {
		for w := 1; w <= capacity; w++ {
			item := ks.items[i-1]
			
			if item.Weight <= w {
				dp[i][w] = max(dp[i-1][w], dp[i-1][w-item.Weight]+item.Value)
			} else {
				dp[i][w] = dp[i-1][w]
			}
		}
	}
	
	result := []KnapsackItem{}
	w := capacity
	for i := len(ks.items); i > 0 && w > 0; i-- {
		if dp[i][w] != dp[i-1][w] {
			result = append(result, ks.items[i-1])
			w -= ks.items[i-1].Weight
		}
	}
	
	return result
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func demonstrateDynamicProgramming() {
	fmt.Println("=== Stock Trading Algorithm Example ===")
	prices := []float64{7.0, 1.0, 5.0, 3.0, 6.0, 4.0, 2.0, 8.0, 9.0, 3.0}
	trader := NewStockTrader(prices)
	
	fmt.Printf("Stock prices: %v\n", prices)
	
	maxProfit := trader.MaxProfit()
	fmt.Printf("Maximum profit (unlimited transactions): $%.2f\n", maxProfit)
	
	maxProfitCooldown := trader.MaxProfitWithCooldown()
	fmt.Printf("Maximum profit (with cooldown): $%.2f\n", maxProfitCooldown)
	
	buyDay, sellDay, bestProfit := trader.FindBestTradingDays()
	fmt.Printf("Best single trade: Buy day %d ($%.2f) -> Sell day %d ($%.2f) = $%.2f profit\n", 
		buyDay, prices[buyDay], sellDay, prices[sellDay], bestProfit)

	fmt.Println("\n=== LZW Compression Example ===")
	compressor := NewLZWCompressor()
	
	testStrings := []string{
		"ABABABA",
		"TOBEORNOTTOBEORTOBEORNOT",
		"ABCABCABCABCABC",
		"The quick brown fox jumps over the lazy dog",
	}
	
	for _, text := range testStrings {
		compressed := compressor.Compress(text)
		ratio := compressor.CompressionRatio(text, compressed)
		
		fmt.Printf("Original: \"%s\" (%d chars)\n", text, len(text))
		fmt.Printf("Compressed: %v (%d codes)\n", compressed[:min(10, len(compressed))], len(compressed))
		if len(compressed) > 10 {
			fmt.Printf("... (showing first 10 codes)\n")
		}
		fmt.Printf("Compression ratio: %.2f%% space saved\n\n", ratio*100)
		
		compressor = NewLZWCompressor()
	}

	fmt.Println("=== DNA Sequence Alignment Example ===")
	aligner := NewDNAAligner(2, -1, -2) // match: +2, mismatch: -1, gap: -2
	
	sequences := [][]string{
		{"ACGT", "ACG"},
		{"GCATGCU", "GATTACA"},
		{"ATCGATCG", "ATCCTCG"},
		{"TGCATAT", "ATCCTAT"},
	}
	
	for _, seqs := range sequences {
		seq1, seq2 := seqs[0], seqs[1]
		score := aligner.AlignSequences(seq1, seq2)
		aligned1, aligned2, alignScore := aligner.GetAlignment(seq1, seq2)
		
		fmt.Printf("Sequence 1: %s\n", seq1)
		fmt.Printf("Sequence 2: %s\n", seq2)
		fmt.Printf("Alignment score: %d\n", score)
		fmt.Printf("Optimal alignment:\n")
		fmt.Printf("  %s\n", aligned1)
		fmt.Printf("  %s\n", aligned2)
		
		matches := 0
		for i := 0; i < len(aligned1); i++ {
			if aligned1[i] == aligned2[i] && aligned1[i] != '-' {
				matches++
			}
		}
		similarity := float64(matches) / float64(max(len(seq1), len(seq2))) * 100
		fmt.Printf("Similarity: %.1f%%\n", similarity)
		fmt.Println()
		
		aligner = NewDNAAligner(2, -1, -2)
	}

	fmt.Println("=== Knapsack Problem Example ===")
	items := []KnapsackItem{
		{"Gold Bar", 10, 60},
		{"Silver Coin", 20, 100},
		{"Diamond", 30, 120},
		{"Ruby", 15, 80},
		{"Emerald", 25, 110},
		{"Sapphire", 12, 70},
		{"Pearl", 8, 40},
		{"Platinum Ring", 18, 95},
	}
	
	solver := NewKnapsackSolver(items)
	capacity := 50
	
	maxValue := solver.Solve(capacity)
	optimalItems := solver.GetOptimalItems(capacity)
	
	fmt.Printf("Knapsack capacity: %d units\n", capacity)
	fmt.Printf("Available items:\n")
	for _, item := range items {
		fmt.Printf("  %s: Weight=%d, Value=%d (ratio=%.2f)\n", 
			item.Name, item.Weight, item.Value, float64(item.Value)/float64(item.Weight))
	}
	
	fmt.Printf("\nOptimal solution (value: %d):\n", maxValue)
	totalWeight := 0
	totalValue := 0
	for _, item := range optimalItems {
		fmt.Printf("  + %s (Weight: %d, Value: %d)\n", item.Name, item.Weight, item.Value)
		totalWeight += item.Weight
		totalValue += item.Value
	}
	fmt.Printf("Total weight: %d/%d, Total value: %d\n", totalWeight, capacity, totalValue)
	fmt.Printf("Knapsack utilization: %.1f%%\n", float64(totalWeight)/float64(capacity)*100)
}

func main() {
	demonstrateDynamicProgramming()
}