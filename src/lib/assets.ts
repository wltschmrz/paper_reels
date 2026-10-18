export const asset = (url: string) =>
  /^https?:\/\//.test(url) || url.startsWith("/api/")
    ? url
    : `${import.meta.env.BASE_URL}${url.replace(/^\//, "")}`;
