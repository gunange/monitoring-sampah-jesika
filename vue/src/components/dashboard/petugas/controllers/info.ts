import { dataEnv } from "@/components/dashboard/petugas/config";
import { userStorage } from "../store";
import { TimeApp } from "@/controller/tools";
import { api } from "@/config/apiConfig";

class InfoController {
   get collection() {
      return `${dataEnv.path_api}/dataset`;
   }
   get time() {
      return new TimeApp();
   }
   get storage() {
      return userStorage().info_knn;
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
      const len = this.storage.data.length;
      if(len > 80){
         this.storage.data = this.storage.data.slice(0, len - 30);
      }
   }
}
export const infoCtrl = new InfoController();