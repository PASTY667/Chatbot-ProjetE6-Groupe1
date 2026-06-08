type PrismaClientLike = unknown;
type PrismaClientConstructor = new () => PrismaClientLike;

const globalForPrisma = globalThis as unknown as {
  prisma?: PrismaClientLike;
};

export async function getPrismaClient(): Promise<PrismaClientLike | null> {
  if (!process.env.DATABASE_URL) {
    return null;
  }

  if (!globalForPrisma.prisma) {
    const clientModulePath = "../app/generated/prisma/client";
    const { PrismaClient } = (await import(clientModulePath)) as {
      PrismaClient: PrismaClientConstructor;
    };

    globalForPrisma.prisma = new PrismaClient();
  }

  return globalForPrisma.prisma;
}
