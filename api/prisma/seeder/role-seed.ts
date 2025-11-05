import { PrismaClient } from "@prisma/client";
const prisma = new PrismaClient();

export async function roleSeed() {
   await prisma.role.upsert({
      where: { id: 1 },
      update: {},
      create: {
         id: 1,
         label: "Administrator",
         role: "4dm1n",
      },
   });
   await prisma.role.upsert({
      where: { id: 2 },
      update: {},
      create: {
         id: 2,
         label: "Petugas",
         role: "p3tug45",
      },
   });
}
