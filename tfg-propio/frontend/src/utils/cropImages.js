import { API_URL } from "../api/api";

export const defaultCropImage = `${API_URL}/uploads/crops/default.jpg`;

export const resolveCropImageSrc = (imageUrl) => {
  if (!imageUrl) return defaultCropImage;
  if (imageUrl.startsWith("http://") || imageUrl.startsWith("https://")) {
    return imageUrl;
  }
  if (imageUrl.startsWith("/")) {
    return `${API_URL}${imageUrl}`;
  }
  return imageUrl;
};
