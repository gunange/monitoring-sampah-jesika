import { dataEnv } from "@/components/dashboard/petugas/config";
import { delay } from "@/controller/tools";
import { reactive } from "vue";
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
   get items(){
      return this.storage.data;
   }
   handleWsData(wsData : any){
      if(wsData.type == "add"){
         this.storage.data.push(wsData.data);
      }
   }
}
export const alertCtrl = new AlertController();
