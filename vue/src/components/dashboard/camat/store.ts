import { defineStore } from "pinia";
import { atribut } from "@/services/atribut";
import { StoreDataFormApi } from "@/services/interface";

export const storeId = "camat-store";

export const userStorage = defineStore(storeId, {
   state: (): {
      websocket: WebSocket | null;
      surat_masuk: StoreDataFormApi;
      surat_keluar: StoreDataFormApi;
   } => ({
      surat_keluar: { ...atribut.storeDefault },
      surat_masuk: { ...atribut.storeDefault },
      websocket: null,
   }),
});
