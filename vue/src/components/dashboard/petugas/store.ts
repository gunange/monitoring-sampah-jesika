import { defineStore } from "pinia";
import { atribut } from "@/services/atribut";
import { StoreDataFormApi } from "@/services/interface";

export const storeId = "petugas-store";

export const userStorage = defineStore(storeId, {
   state: (): {
      dataset: StoreDataFormApi;
      info_knn: StoreDataFormApi;
      alert_knn: StoreDataFormApi;
      ml_config: StoreDataFormApi;
      save_logs: StoreDataFormApi;
   } => ({
      save_logs: atribut.createStoreDefault(),
      ml_config: atribut.createStoreDefault(),
      alert_knn: atribut.createStoreDefault(),
      info_knn: atribut.createStoreDefault(),
      dataset: atribut.createStoreDefault(),
   }),
});
