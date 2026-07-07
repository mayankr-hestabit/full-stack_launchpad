const fs = require('fs')
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
const path = require('path');

// ---- Worker Thread Code ----
// This block runs inside each worker thread, not the main thread
if (!isMainThread) {
	const { chunk, minLen } = workerData;

	// Split chunk into words and filter by minLen
	const words = chunk
		.toLowerCase()
		.split(/\s+/)
		.filter(w => w.length >= minLen);

	// Build frequency map for this chunk
	const freqMap = {};
	for (const word of words) {
		freqMap[word] = (freqMap[word] || 0) + 1;
	}

	// Send results back to main thread
	parentPort.postMessage({ freqMap, totalWords: words.length });
	process.exit(0);
}

// ---- Main Thread Code ----
// Process one chunk in a worker thread and return a promise
function processChunk(chunk, minLen) {
	return new Promise((resolve, reject) => {
		// Spawn a new worker running THIS same file
		const worker = new Worker(__filename, {
			workerData: { chunk, minLen }
		});
		worker.on('message', resolve);
		worker.on('error', reject);
	});
}

// Merge multiple freqMaps from workers into one combined map
function mergeFreqMaps(maps) {
	const merged = {};
	for (const map of maps) {
		for (const [word, count] of Object.entries(map)) {
			merged[word] = (merged[word] || 0) + count;
		}
	}
	return merged;
}

// Run the full benchmark at a given concurrency level
async function runAtConcurrency(filePath, concurrency, minLen, topN) {
	// Read entire file
	const content = fs.readFileSync(filePath, 'utf-8');

	// Split by lines to avoid cutting words at chunk boundaries
	const lines = content.split('\n');
	const chunkSize = Math.ceil(lines.length / concurrency);
	const chunks = [];
	for (let i = 0; i < concurrency; i++) {
		chunks.push(lines.slice(i * chunkSize, (i + 1) * chunkSize).join('\n'));
	}

	// Start timer
	const start = process.hrtime.bigint();

	// Process all chunks in parallel
	const results = await Promise.all(
    		chunks.map(chunk => processChunk(chunk, minLen))
  	);

  	// Stop timer
  	const end = process.hrtime.bigint();
  	const durationMs = Number(end - start) / 1e6;

  	// Merge all worker results
  	const mergedFreqMap = mergeFreqMaps(results.map(r => r.freqMap));
  	const totalWords = results.reduce((sum, r) => sum + r.totalWords, 0);

  	// Get top N words
  	const topWords = Object.entries(mergedFreqMap)
    		.sort((a, b) => b[1] - a[1])
    		.slice(0, topN)
    		.map(([word, count]) => ({ word, count }));

  	return {
	    	concurrency,
    		durationMs: Number(durationMs.toFixed(2)),
    		totalWords,
    		uniqueWords: Object.keys(mergedFreqMap).length,
    		topWords
  	};
}

// ─── MAIN EXECUTION ───────────────────────────────────────────────
async function main() {
	const filePath = './corpus.txt';
  	const minLen = 5;
  	const topN = 10;
  	const concurrencyLevels = [1, 4, 8];

  	console.log('Running concurrency benchmark...\n');

  	const results = [];

  	// Run benchmark at each concurrency level sequentially
  	for (const level of concurrencyLevels) {
		console.log(`Testing concurrency level: ${level}...`);
		const result = await runAtConcurrency(filePath, level, minLen, topN);
		console.log(`  Done in ${result.durationMs}ms`);
		results.push(result);
	}

  	// Print summary table
  	console.log('\n========== CONCURRENCY BENCHMARK ==========');
  	console.log('Level | Duration (ms) | Total Words | Unique Words');
  	console.log('------|---------------|-------------|-------------');
  	for (const r of results) {
  		console.log(
      		`  ${r.concurrency}   | ${r.durationMs.toString().padStart(13)} | ${r.totalWords.toString().padStart(11)} | ${r.uniqueWords}`
    );
	}
	console.log('===========================================\n');

	// Save to logs
	const report = {
		timestamp: new Date().toISOString(),
		file: filePath,
		filters: { minLen, topN },
		results
	};

	fs.mkdirSync('./logs', { recursive: true });
	fs.writeFileSync('./logs/perf-summary.json', JSON.stringify(report, null, 2));
	console.log('Saved to logs/perf-summary.json');
}

main();
