import { defineStore } from "pinia";
import { atribut } from "@/services/atribut";
import { StoreDataFormApi } from "@/services/interface";

export const storeId = "admin-store";

export const userStorage = defineStore(storeId, {
   state: (): {
      websocket: WebSocket | null;
      camat: StoreDataFormApi;
      staf: StoreDataFormApi;
   } => ({
      staf: { ...atribut.storeDefault },
      camat: { ...atribut.storeDefault },
      websocket: null,
   }),
});
