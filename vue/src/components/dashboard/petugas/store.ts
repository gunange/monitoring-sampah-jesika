import { defineStore } from "pinia";
import { atribut } from "@/services/atribut";
import { StoreDataFormApi } from "@/services/interface";

export const storeId = "petugas-store";

export const userStorage = defineStore(storeId, {
   state: (): {
      dataset: StoreDataFormApi;
      info_knn: StoreDataFormApi;
      alert_knn: StoreDataFormApi;
   } => ({
      alert_knn: { ...atribut.storeDefault },
      info_knn: { ...atribut.storeDefault },
      dataset: { ...atribut.storeDefault },
   }),
});
