import { delay } from "@/controller/tools";
import { reactive } from "vue";

import { TimeApp } from "@/controller/tools";
import { get } from "@/controller/others/RequestApiController";
import { api } from "@/config/apiConfig";
import { ApiResponse } from "@/controller/others/RequestApiController/interface";

export class Controller {
   get time() {
      return new TimeApp();
   }

   get urlStorage() {
      return api.url_storage;
   }
}
export class Cruds extends Controller {
   modal = reactive({
      show: false,
      label: "Label",
      act: null,
      proses_form: false,
      uid: null,
   });

   async open(): Promise<void> {
      await delay(50);
      this.modal.show = true;
   }
   async close(): Promise<void> {
      await delay(50);
      await this.reset();
   }

   async reset(): Promise<void> {
      this.modal.act = null;
      this.modal.proses_form = false;
      this.modal.label = "Label";
      this.modal.show = false;
      this.modal.uid = null;

      delay(100);
   }
   setUid(uid) {
      this.modal.uid = uid;
   }

   get uid() {
      return this.modal.uid;
   }

   /*
    * Fungsi daari crud yanng sebenarnnya adda dibawah ini
    */

   async getFileInfo(uid): Promise<ApiResponse> {
      return await get(`${api.url_storage}/${uid}/info`);
   }
}
