import { getToken } from "next-auth/jwt";
import type { NextRequest } from "next/server";

export async function getSessionUsername(request: NextRequest) {
  const token = await getToken({ req: request, secret: process.env.NEXTAUTH_SECRET });
  const username = typeof token?.username === "string" ? token.username : token?.name;

  return typeof username === "string" && username.trim() ? username.trim() : null;
}
