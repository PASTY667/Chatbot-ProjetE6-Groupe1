import NextAuth, { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { authenticateLDAP } from "@/lib/ldap";

export const authOptions: NextAuthOptions = {
  secret: process.env.NEXTAUTH_SECRET,
  providers: [
    CredentialsProvider({
      name: "LDAP",

      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },

      async authorize(credentials) {
        if (!credentials) return null;

        const { username, password } = credentials;

        if (!username || !password) return null;

        const user = await authenticateLDAP(username, password);

        if (!user) return null;

        return {
          id: user.id,
          name: user.name,
          email: user.email,
          role: user.role,
          groups: user.groups,
        };
      },
    }),
  ],

  session: {
    strategy: "jwt",
  },

  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = user.role;
        token.groups = user.groups;
      }
      return token;
    },

    async session({ session, token }) {
      if (session.user) {
        session.user.role = token.role as string;
        session.user.groups = token.groups as string[];
      }
      return session;
    },
  },

  pages: {
    signIn: "/login",
  },
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
