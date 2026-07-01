// fs module to write the file
const fs = require('fs');

// A pool of words to randomly pick from
const words = [
	'apple', 'bridge', 'cloud', 'dragon', 'engine', 'forest',
  'garden', 'harbor', 'island', 'jungle', 'kernel', 'lemon',
  'market', 'nation', 'orange', 'planet', 'quarter', 'rocket',
  'silver', 'tunnel', 'unique', 'valley', 'winter', 'yellow',
  'abstract', 'boolean', 'cluster', 'dynamic', 'elastic',
  'function', 'generic', 'handler', 'integer', 'library',
  'monitor', 'network', 'operate', 'package', 'request',
  'runtime', 'session', 'terminal', 'uniform', 'variable',
  'webpack', 'express', 'process', 'stream', 'buffer',
  'promise', 'async', 'await', 'thread', 'worker'
];

// Pick a random word from the pool
function randomWord() {
	return words[Math.floor(Math.random() * words.length)];
}

const TARGET_WORDS = 200000;
let corpus = '';

// Build the corpus word by word
for (let i = 0; i< TARGET_WORDS; i++) {
	corpus += randomWord();
	// Add newline every 10 words to keep lines readable
	corpus += (i% 10 ==9) ? '\n' : ' ';
}

// Write to disk
fs.writeFileSync('corpus.txt', corpus);
console.log(`Generated ${TARGET_WORDS} words into corpus.txt`);


