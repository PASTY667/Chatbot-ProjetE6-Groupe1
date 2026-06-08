import NextAuth, { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { authenticateLDAP } from "@/lib/ldap";

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: "LDAP",

      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },

      async authorize(credentials) {
        try {
          if (!credentials?.username || !credentials?.password) return null;

          const user = await authenticateLDAP(
            credentials.username,
            credentials.password,
          );

          if (!user) return null;

          return {
            id: String(user.id),
            name: user.name ?? credentials.username,
            email: user.email ?? null,
            role: user.role ?? "user",
            groups: user.groups ?? [],
          };
        } catch (error) {
          console.error("LDAP authorize error:", error);
          return null;
        }
      },
    }),
  ],

  debug: true,
  logger: {
    error(code, ...message) {
      console.error(code, ...message);
    },
    warn(code, ...message) {
      console.warn(code, ...message);
    },
    debug(code, ...message) {
      console.log(code, ...message);
    },
  },

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
