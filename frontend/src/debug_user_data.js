// Simple debug script to check localStorage user data
console.log('=== DEBUG USER DATA ===');

// Check localStorage
const authStorage = localStorage.getItem('auth-storage');
if (authStorage) {
    const parsed = JSON.parse(authStorage);
    console.log('Auth Storage:', parsed);
    console.log('User Type:', parsed.state?.user?.user_type);
    console.log('User Object:', parsed.state?.user);
} else {
    console.log('No auth storage found');
}

// Check other localStorage keys
const authToken = localStorage.getItem('auth_token');
if (authToken) {
    console.log('Auth Token:', authToken);
} else {
    console.log('No auth token found');
}

console.log('=== END DEBUG ===');