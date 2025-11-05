import * as utils from "@/utils";

import { AsyncLocalStorage } from "async_hooks";

import type { StoreContext, User } from "./store-context";
import { PetugasRepo } from "@/repositories/PetugasRepo";
import type { PetugasProfile } from "@/types/PetugasTypes";

const storage = new AsyncLocalStorage<StoreContext>();
export const store = {
   // Bungkus setiap request
   run: <T>(fn: () => T | Promise<T>) => storage.run({}, fn),

   // Setter
   setup: async (context: utils.Context) => {
      const store = storage.getStore();

      const user = context.get("user");
      const token = context.get("token");

      if (store) {
         if (user) store.user = user;
         if (token) store.token = token;

         const kepsek = await PetugasRepo.getByUserId(user.id);
         if (kepsek) store.kepsek = kepsek;
      }
   },

   setToken: (token: string) => {
      const store = storage.getStore();
      if (store) store.token = token;
   },

   // Getters
   get user(): User | undefined {
      return storage.getStore()?.user;
   },

   get profil(): PetugasProfile {
      return storage.getStore()?.kepsek as PetugasProfile;
   },

   get token(): string | undefined {
      return storage.getStore()?.token;
   },
};
