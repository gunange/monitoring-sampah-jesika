import { roleSeed } from "./role-seed";
import { userSeed } from "./user-seed";

import { PrismaClient } from "@prisma/client";
const prisma = new PrismaClient();
async function main() {
   await roleSeed();
   await userSeed();
}
main()
   .then(async () => {
      await prisma.$disconnect();
   })
   .catch(async (e) => {
      console.error(e);
      await prisma.$disconnect();
      process.exit(1);
   });
