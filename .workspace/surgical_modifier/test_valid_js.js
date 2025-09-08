function calculateSum(numbers) {
    return numbers.reduce((sum, num) => sum + num, 0);
}

const user = {
    name: 'John Doe',
    age: 30
};

module.exports = { calculateSum, user };