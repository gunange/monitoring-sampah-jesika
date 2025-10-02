import type { KepsekProfile } from "@/types/CalonPegawaiTypes";
import type {  User } from "@prisma/client";

type StoreContext = {
   user?: User;
   kepsek?: KepsekProfile;
   token?: string;
};

export type { StoreContext, User };
