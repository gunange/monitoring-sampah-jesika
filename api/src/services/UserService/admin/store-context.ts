import type { Role, User } from "@prisma/client";

type StoreContext = {
   user?: User & { Role: Role };
   token?: string;
};

export type { StoreContext, User };
