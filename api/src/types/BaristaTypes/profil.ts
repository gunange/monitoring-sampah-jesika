import type { Barista, Role, User } from "@prisma/client"

export type BaristaProfile = Barista & {
    User: User & { Role: Role };
};