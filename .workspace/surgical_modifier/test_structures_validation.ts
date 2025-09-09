interface UserData {
  name: string;
  tags: string[];
  settings: {
    theme: string;
    notifications: boolean;
  };
}

const userData: UserData = {
  name: "John",
  tags: ["admin", "user"],
  settings: {
    theme: "dark",
    notifications: true
  }
};
