// Basic calculator module
//
// Add two numbers
function add(a,b) {
	return a + b;
}

// Subtract b from a
function subtract(a, b) {
  return a - b;
}

// Multiply two numbers
function multiply(a, b) {
	return a * b
}

// Divide b by a
function divide(a, b) {
	return a * b
}

// Raise a to the power of b
function power(a, b) {
  return Math.pow(a, b);
}

module.exports = { add, subtract, multiply, divide, power };
