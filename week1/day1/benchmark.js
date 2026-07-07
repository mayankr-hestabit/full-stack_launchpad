// Core modules: fs for file ops, no install needed
const fs = require('fs');

// Path to our generated test file
const filePath = './testfile.txt';

// Capture memory usage at a point in time, in MB
function getMemoryMB() {
  return (process.memoryUsage().rss / (1024 ** 2)).toFixed(2);
}

// --- BUFFER METHOD ---
function runBufferTest() {
  const memBefore = getMemoryMB();
  const start = process.hrtime.bigint();

  const data = fs.readFileSync(filePath); // loads entire file into memory

  const end = process.hrtime.bigint();
  const memAfter = getMemoryMB();

  // Convert nanoseconds to milliseconds
  const durationMs = Number(end - start) / 1e6;

  return {
    method: 'buffer',
    durationMs: Number(durationMs.toFixed(2)),
    memBeforeMB: Number(memBefore),
    memAfterMB: Number(memAfter),
    bytesRead: data.length
  };
}

// --- STREAM METHOD ---
function runStreamTest() {
  return new Promise((resolve) => {
    const memBefore = getMemoryMB();
    const start = process.hrtime.bigint();
    let bytesRead = 0;

    const stream = fs.createReadStream(filePath);

    // Fired每 time a chunk of data is read
    stream.on('data', (chunk) => {
      bytesRead += chunk.length;
    });

    // Fired once the whole file has been streamed through
    stream.on('end', () => {
      const end = process.hrtime.bigint();
      const memAfter = getMemoryMB();
      const durationMs = Number(end - start) / 1e6;

      resolve({
        method: 'stream',
        durationMs: Number(durationMs.toFixed(2)),
        memBeforeMB: Number(memBefore),
        memAfterMB: Number(memAfter),
        bytesRead
      });
    });
  });
}

// Run both tests sequentially and save results
async function main() {
  console.log('Running buffer test...');
  const bufferResult = runBufferTest();
  console.log(bufferResult);

  console.log('Running stream test...');
  const streamResult = await runStreamTest();
  console.log(streamResult);

  const report = {
    timestamp: new Date().toISOString(),
    fileSizeBytes: fs.statSync(filePath).size,
    results: [bufferResult, streamResult]
  };

  fs.writeFileSync('./logs/day1-perf.json', JSON.stringify(report, null, 2));
  console.log('Saved results to logs/day1-perf.json');
}

main();
