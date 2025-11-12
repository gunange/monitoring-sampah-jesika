export class Env {
   static get debug() {
      return Bun.env["DEBUG"] === "true";
   }
   static get debug_sql() {
      return Bun.env["DEBUG_SQL"] === "true";
   }
   static get debug_test() {
      return Bun.env["DEBUG_TEST"] === "true";
   }
   static get debug_storage() {
      return Bun.env["DEBUG_STORAGE"] === "true";
   }
   static get debug_stack() {
      return Bun.env["DEBUG_STACK"] === "true";
   }
   static get access_log() {
      return Bun.env["ACCESS_LOG"] === "true";
   }
   static get error_log() {
      return Bun.env["ERROR_LOG"] === "true";
   }
   static get storage_path() {
      return Bun.env["STORAGE_PATH"] || "default/path";
   }
   static get storage_max_size() {
      return parseInt(Bun.env["STORAGE_MAX_SIZE"] || "5242880", 10);
   }
   static get storage_allow_file_type() {
      return JSON.parse(Bun.env["STORAGE_ALLOW_FILE_TYPE"] || "[]");
   }
   static get port() {
      return Number(Bun.env["PORT"]);
   }
   static get hostname() {
      return Bun.env["HOST"];
   }
   static get ml_hostname() {
      return Bun.env["ML_HOST"];
   }
   static get ml_port() {
      return Number(Bun.env["ML_PORT"]);
   }
}
