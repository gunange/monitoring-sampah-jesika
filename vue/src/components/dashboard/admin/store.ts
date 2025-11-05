import { defineStore } from "pinia";
import { atribut } from "@/services/atribut";
import { StoreDataFormApi } from "@/services/interface";

export const storeId = "admin-store";

export const userStorage = defineStore(storeId, {
   state: (): {
      websocket: WebSocket | null;
      petugas: StoreDataFormApi;
   } => ({
      petugas: { ...atribut.storeDefault },
      websocket: null,
   }),
});
