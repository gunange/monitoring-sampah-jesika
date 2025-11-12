import { dataEnv } from "@/components/dashboard/petugas/config";
import { delay } from "@/controller/tools";
import { reactive } from "vue";
import { userStorage } from "../../store";
import { TimeApp } from "@/controller/tools";
import { api } from "@/config/apiConfig";
import {
   del,
   get,
   patch,
   post,
} from "@/controller/others/RequestApiController";

export class Controller {
   get pathMl() {
      return `${api.url_api}machine-learning`;
   }

   get time() {
      return new TimeApp();
   }
   get storage() {
      return userStorage().ml_config;
   }
   get urlStorage() {
      return api.url_storage;
   }
}

export class MainData extends Controller {
   get data() {
      return this.storage;
   }
   get machineRunning() {
      return this.data.dataOnly?.running || false;
   }
   get item() {
      return this.data.dataOnly || {};
   }

   async getStatus() {
      if (this.data.load) return;
      this.data.load = true;

      const res = await fetch(`${this.pathMl}`);
      this.data.run = res.status === 200;
      this.data.load = false;
      this.data.dataOnly = await res.json();
   }

   async toggleMachine() {
      try {
         const url = this.machineRunning
            ? `${this.pathMl}/stop`
            : `${this.pathMl}/start`;
         const res = await fetch(url);
         const data = await res.json();
         this.data.dataOnly = data;
      } catch (e) {}
   }
}
