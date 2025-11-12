import { Hono } from "hono";
import { MachineLearningRoute } from "@/controllers/machine-learning";

export const machineLearning = new Hono();

machineLearning.use("/*", async (_, next) => {
   return next();
});


/* ---- machine-learning ---- */
machineLearning.get("/", MachineLearningRoute.MachineCtrl.index);
machineLearning.get("/start", MachineLearningRoute.MachineCtrl.start);
machineLearning.get("/stop", MachineLearningRoute.MachineCtrl.stop);
machineLearning.post("/dataset", MachineLearningRoute.MachineCtrl.storeToMl);
machineLearning.get("/dataset", MachineLearningRoute.MachineCtrl.dataset);
machineLearning.post("/alert", MachineLearningRoute.MachineCtrl.alert);
