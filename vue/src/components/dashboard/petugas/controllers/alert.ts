import { dataEnv } from "@/components/dashboard/petugas/config";
import { toastStore } from "@/stores/services/toast-store";
import { userStorage } from "../store";
import { TimeApp } from "@/controller/tools";
import { api } from "@/config/apiConfig";

class AlertController {
   get collection() {
      return `${dataEnv.path_api}/dataset`;
   }
   get time() {
      return new TimeApp();
   }
   get storage() {
      return userStorage().alert_knn;
   }
   get urlStorage() {
      return api.url_storage;
   }
   get items() {
      return this.storage.data;
   }
   get toast() {
      return toastStore().toast;
   }
   async handleWsData(wsData: any) {
      if (wsData.type == "add") {
         this.storage.data.push(wsData.data);
         const data = wsData.data;
         await this.toast.add({
            severity: "error",
            summary: data.label,
            detail: `Segera Periksa Di menu Monitor`,
            life: 3000,
         });
      }
   }
}
export const alertCtrl = new AlertController();
