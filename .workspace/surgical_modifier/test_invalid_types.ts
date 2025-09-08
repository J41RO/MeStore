interface User {
    id: number
    name: string  // Missing semicolon
    email: string;
}

function getUserName(user: User): string {
    return user.name
} // Missing semicolon

export { User };