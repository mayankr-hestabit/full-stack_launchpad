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

// Divide a by b
function divide(a, b) {
	return a / b
}

// Raise a to the power of b
function power(a, b) {
  return Math.pow(a, b);
}

// Validate inputs are numbers
function validate(a, b) {
  if (typeof a !== 'number' || typeof b !== 'number') {
    throw new Error('Both inputs must be numbers');
  }
}

// Return absolute value of a
function absolute(a) {
  return Math.abs(a);
}

module.exports = { add, subtract, multiply, divide, power, validate, absolute };
