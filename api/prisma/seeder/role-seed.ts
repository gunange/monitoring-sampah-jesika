import { PrismaClient } from "@prisma/client";
const prisma = new PrismaClient();

export async function roleSeed() {
   await prisma.role.upsert({
      where: { id: 1 },
      update: {},
      create: {
         id: 1,
         label: "Owner",
         role: "0wn3r",
      },
   });
   await prisma.role.upsert({
      where: { id: 2 },
      update: {},
      create: {
         id: 2,
         label: "Barista",
         role: "b4r157a",
      },
   });
}
