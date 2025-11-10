import { request, type RequestOptions } from "./index";

export async function post<T>(
  url: string,
  body?: unknown,
  options?: RequestOptions
): Promise<T> {
  return request<T>("POST", url, body, options);
}