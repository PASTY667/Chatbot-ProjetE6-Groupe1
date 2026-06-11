import { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    user: {
      name: string;
      username: string;
      email?: string;
      role: string;
      groups: string[];
    } & DefaultSession["user"];
  }

  interface User {
    role: string;
    groups: string[];
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    username?: string;
    role?: string;
    groups?: string[];
  }
}
