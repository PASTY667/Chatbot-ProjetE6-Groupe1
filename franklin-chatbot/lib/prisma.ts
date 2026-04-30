import { PrismaPg } from "@prisma/adapter-pg";

type AnyPrismaClient = {
  [key: string]: unknown;
};

const globalForPrisma = global as unknown as {
  prisma?: AnyPrismaClient | null;
};

function createPrismaClient(): AnyPrismaClient | null {
  try {
    // The generated client can be absent on environments without DB setup.
    // In that case we keep the app bootable for non-DB routes/pages.
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const { PrismaClient } = require("../app/generated/prisma/client");

    const adapter = new PrismaPg({
      connectionString: process.env.DATABASE_URL,
    });

    return new PrismaClient({ adapter });
  } catch {
    return null;
  }
}

const prisma = globalForPrisma.prisma ?? createPrismaClient();

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}

export default prisma;
