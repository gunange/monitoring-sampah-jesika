import chalk from "chalk";
import app from "../app";

console.log(chalk.bold.whiteBright("📌 Daftar Routes:\n"));
let prevGroup = "";
let printedMiddlewareGroups = new Set<string>();
let prevPath = "*";

app.routes.forEach((route) => {
   let color = chalk.white;

   if (route.method === "GET") color = chalk.blueBright;
   if (route.method === "POST") color = chalk.greenBright;
   if (route.method === "PUT") color = chalk.magentaBright;
   if (route.method === "PATCH") color = chalk.yellow;
   if (route.method === "DELETE") color = chalk.redBright;
   if (route.method === "ALL") color = chalk.gray;

   const groupKey = route.path.split("/").slice(0, 3).join("/");

   if (prevGroup && prevGroup !== groupKey) {
      console.log("\n");
   }

   // Middleware detection BEFORE printing the route
   const isMiddleware = route.path.includes("*");
   if (isMiddleware) {
      const parts = route.path.split("/");
      const groupName = parts[2] || "*";

      if (!printedMiddlewareGroups.has(groupName)) {
         console.log(chalk.bgGreenBright(`👮[Middleware ${groupName}]`));
         printedMiddlewareGroups.add(groupName);
      }
   }

   const parts = route.path.split("/");
   if (parts.length >= 4) {
      if (parts[3] !== "*" && parts[3] !== prevPath) {
         console.log(chalk.gray(`\n🔹 Route-Path: ${parts[3] ?? "-"}`));
      }
      prevPath = parts[3];
   }

   console.log(color(`${route.method.padEnd(7)} ${route.path}`));

   prevGroup = groupKey;
});

console.log("\n********* ROUTES *********\n");
