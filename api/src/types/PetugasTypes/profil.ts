import type { Petugas, Role, User } from "@prisma/client"

export type PetugasProfile = Petugas & {
    User: User & { Role: Role };
};

import type { Petugas, Role, User } from "@prisma/client"

export type PetugasProfile = Petugas & {
    User: User & { Role: Role };
};