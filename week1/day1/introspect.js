// Usage: node introspect.js


// importing os module
const os = require('os');

// Helper: convert raw bytes into a human-readable GB string.
function formatBytes(bytes) {
	return (bytes / (1024 ** 3)).toFixed(2) + 'GB';
}

// Helper: convert raw seconds into h/m/s format
function formatUptime(seconds) {
	const hrs = Math.floor(seconds / 3600);
	const mins = Math.floor((seconds % 3600) / 60);
  	const secs = Math.floor(seconds % 60);
  	return `${hrs}h ${mins}m ${secs}s`;
}

// Kernel name + version
console.log('OS:', os.type(), os.release());

// CPU architecture the Node binary was built for
console.log('Architecture:', os.arch());

// Number of logical CPU cores
console.log('CPU Cores:', os.cpus().length);

// Total system RAM, formatted
console.log('Total Memory:', formatBytes(os.totalmem()));

// Seconds since boot, formatted (WSL2 VM uptime, not host)
console.log('System Uptime:', formatUptime(os.uptime()));

// Username of current OS-level user
console.log('Current Logged User:', os.userInfo().username);

// Absolute path to the running node binary
console.log('Node Path:', process.execPath);
