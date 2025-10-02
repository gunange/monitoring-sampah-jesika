export function jsonToStringArray(value: unknown, fallback: string[] = []): string[] {
    if (Array.isArray(value) && value.every((item) => typeof item === "string")) {
       return value;
    }
    return fallback;
 }
 