import { HTTPException } from "hono/http-exception";
import { get } from "./get";
import { post } from "./post";

export interface RequestOptions {
  headers?: Record<string, string>;
  query?: Record<string, string | number | boolean | null | undefined>;
  timeoutMs?: number; // default 15000 ms
  name?: string; // nama endpoint untuk pesan error/logging
}

/**
 * Tambahkan query string ke URL (mendukung URL relatif).
 */
function withQuery(url: string, query?: RequestOptions["query"]): string {
  if (!query) return url;
  const params = new URLSearchParams();
  Object.entries(query).forEach(([k, v]) => {
    if (v === null || v === undefined) return;
    params.append(k, String(v));
  });
  const sep = url.includes("?") ? "&" : "?";
  return params.toString() ? `${url}${sep}${params.toString()}` : url;
}

/**
 * Parse JSON respons dan throw Error berisi status jika tidak OK.
 */
async function parseJsonOrThrow<T>(res: Response, name?: string): Promise<T> {
  const text = await res.text();
  if (!res.ok) {
    throw new HTTPException(403, { message: `Request API ${name || 'Unknown'} Failed` });
  }
  try {
    return JSON.parse(text) as T;
  } catch {
    return text as unknown as T;
  }
}

/**
 * Request generik untuk GET/POST.
 */
export async function request<T>(
  method: "GET" | "POST",
  url: string,
  body?: unknown,
  options?: RequestOptions
): Promise<T> {
  const timeoutMs = options?.timeoutMs ?? 15000;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const finalUrl = withQuery(url, options?.query);
    const headers: Record<string, string> = {
      Accept: "application/json",
      ...(options?.headers ?? {}),
    };
    const init: RequestInit = {
      method,
      headers,
      signal: controller.signal,
    };

    if (method === "POST") {
      const isFormData = typeof FormData !== "undefined" && body instanceof FormData;
      if (!isFormData) {
        headers["Content-Type"] = headers["Content-Type"] ?? "application/json";
        init.body = body !== undefined ? JSON.stringify(body) : undefined;
      } else {
        init.body = body as FormData;
      }
    }

    try {
      const res = await fetch(finalUrl, init);
      return await parseJsonOrThrow<T>(res, options?.name);
    } catch (_) {
      throw new HTTPException(403, { message: `Request API ${options?.name || 'Unknown'} Failed` });
    }
  } finally {
    clearTimeout(timer);
  }
}

export const requestApi = {
    get,
    post
}