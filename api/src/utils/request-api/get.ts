import { request, type RequestOptions } from "./index";

export async function get<T>(url: string, options?: RequestOptions): Promise<T> {
  return request<T>("GET", url, undefined, options);
}