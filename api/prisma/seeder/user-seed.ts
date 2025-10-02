
import { PrismaClient } from "@prisma/client";
const prisma = new PrismaClient();

export async function userSeed() {
    await prisma.user.upsert({
        where: { id: 1 },
        update: {},
        create: {
           id: 1,
           role_id : 1,
           username : "admin",
           password : await Bun.password.hash("12345", {
            algorithm : "bcrypt",
            cost : 10
           }),
        },
     });
     console.log("Create User Seeder");
}