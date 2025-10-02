export function convertTypes(
   data: Record<string, any>,
   fields: string[] = []
): Record<string, any> {
   return Object.fromEntries(
      Object.entries(data).map(([key, value]) => {
         const normalizedKey = key.endsWith("[]") ? key.slice(0, -2) : key;

         if (fields.includes(normalizedKey)) {
            if (Array.isArray(value)) {
               return [normalizedKey, value];
            }

            // Convert JSON string or comma-separated into array
            if (typeof value === "string" && value.includes(",")) {
               return [normalizedKey, value.split(",").map((v) => v.trim())];
            }

            // Convert JSON string
            try {
               const parsed = JSON.parse(value);
               if (Array.isArray(parsed)) return [normalizedKey, parsed];
            } catch {}

            // Convert boolean
            if (value === "true") return [normalizedKey, true];
            if (value === "false") return [normalizedKey, false];

            // Convert number
            if (!isNaN(value)) return [normalizedKey, Number(value)];
         }

         return [normalizedKey, value];
      })
   );
}
