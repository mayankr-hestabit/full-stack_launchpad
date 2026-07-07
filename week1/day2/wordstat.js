// Parses terminal flags into a clean object
const minimist = require('minimist');
const fs = require('fs');
const path = require('path');

// Read and parse all flags passed in terminal
const args = minimist(process.argv.slice(2));

// Show help menu if --help flag is passed
if (args.help) {
  console.log(`
Usage: node wordstat.js [options]

Options:
  --file    <path>    Path to the text file to analyze (required)
  --top     <number>  Show top N most repeated words (default: 10)
  --minLen  <number>  Only count words with minimum N characters (default: 1)
  --unique            Show only words that appear exactly once
  --help              Show this help menu

Examples:
  node wordstat.js --file corpus.txt
  node wordstat.js --file corpus.txt --top 5 --minLen 4
  node wordstat.js --file corpus.txt --top 10 --minLen 5 --unique
  `);
  process.exit(0);
}

// --file is required, exit with clear error if missing
if (!args.file) {
  console.error('Error: --file flag is required');
  console.error('Usage: node wordstat.js --file corpus.txt --top 10 --minLen 5 --unique');
  process.exit(1);
}

// Validate --top is a number if provided
if (args.top !== undefined && typeof args.top !== 'number') {
  console.error('Error: --top requires a numeric value e.g. --top 10');
  process.exit(1);
}

// Validate --minLen is a number if provided
if (args.minLen !== undefined && typeof args.minLen !== 'number') {
  console.error('Error: --minLen requires a numeric value e.g. --minLen 5');
  process.exit(1);
}

// Read defaults for optional flags
const filePath = args.file;
const topN = args.top || 10;
const minLen = args.minLen || 1;
const uniqueOnly = args.unique || false;

// Read the file
console.log(`Reading file: ${filePath}...`);
const content = fs.readFileSync(filePath, 'utf-8');

// Split into words — regex handles multiple spaces, newlines, punctuation
let words = content
  .toLowerCase()
  .split(/\s+/)
  .filter(word => word.length > 0);

// Apply minLen filter
words = words.filter(word => word.length >= minLen);

if (words.length === 0) {
	console.error(`Error: no words found with minimum length of ${minLen} characters. Try a lower --minLen value`);
	process.exit(1);
}


// Build frequency map first (needed for --unique filter)
const freqMap = {};
for (const word of words) {
  freqMap[word] = (freqMap[word] || 0) + 1;
}

// If --unique flag passed, deduplicate — each word type counted once
if (uniqueOnly) {
  words = [...new Set(words)];
  console.log(`Unique filter applied: ${words.length} unique word types found`);
}

// Guard: if all words were filtered out, exit cleanly
if (words.length === 0) {
  console.error(`Error: no words remaining after filters. Try adjusting --minLen or --unique`);
  process.exit(1);
}

// Total word count (after all filters)
const totalWords = words.length;

// Unique words array
const uniqueWords = Object.keys(freqMap);
const totalUnique = uniqueWords.length;

// Longest and shortest word
const longest = words.reduce((a, b) => a.length >= b.length ? a : b);
const shortest = words.reduce((a, b) => a.length <= b.length ? a : b);

// Top N most repeated words
// Sort by frequency descending, take first N
const topWords = Object.entries(freqMap)
  .sort((a, b) => b[1] - a[1])
  .slice(0, topN)
  .map(([word, count]) => ({ word, count }));

// Print results to terminal
console.log('\n========== WORD STATS ==========');
console.log(`Total Words:    ${totalWords}`);
console.log(`Unique Words:   ${totalUnique}`);
console.log(`Longest Word:   ${longest} (${longest.length} chars)`);
console.log(`Shortest Word:  ${shortest} (${shortest.length} chars)`);
console.log(`\nTop ${topN} most repeated words:`);
topWords.forEach((entry, i) => {
  console.log(`  ${i + 1}. "${entry.word}" — ${entry.count} times`);
});
console.log('=================================\n');

// Build results object
const results = {
  timestamp: new Date().toISOString(),
  file: filePath,
  filters: { minLen, topN, uniqueOnly },
  stats: {
    totalWords,
    totalUnique,
    longestWord: { word: longest, length: longest.length },
    shortestWord: { word: shortest, length: shortest.length },
    topWords
  }
};

// Save to output/stats.json
const outputPath = path.join('output', 'stats.json');
fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
console.log(`Results saved to ${outputPath}`);
