import { defineStore } from "pinia";
import { atribut } from "@/services/atribut";
import { StoreDataFormApi } from "@/services/interface";

export const storeId = "camat-store";

export const userStorage = defineStore(storeId, {
   state: (): {
      websocket: WebSocket | null;
      dataset: StoreDataFormApi;
   } => ({
      dataset: { ...atribut.storeDefault },
      websocket: null,
   }),
});
