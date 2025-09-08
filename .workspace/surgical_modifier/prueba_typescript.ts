interface User {
  id: number;
  name: string;
}

type Status = 'active' | 'inactive';

function createUser(name: string): User {
  return { id: Date.now(), name };
}