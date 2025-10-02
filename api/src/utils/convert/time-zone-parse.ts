import { DateTime } from "luxon";

export function timeNow(
  time?: {
    hours?: number;
    min?: number;
    sec?: number;
    ms?: number;
  },
  zona: string = "Asia/Jayapura"
) {
  const now = DateTime.now().setZone(zona);
  
  if (!time) {
    return now;
  }
  const withTime = now.set({
    hour: time?.hours ?? now.hour,
    minute: time?.min ?? now.minute,
    second: time?.sec ?? now.second,
    millisecond: time?.ms ?? now.millisecond,
  });

  return withTime;
}
