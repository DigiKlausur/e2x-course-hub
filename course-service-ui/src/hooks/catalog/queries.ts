import { useQuery } from "@tanstack/react-query";
import { infrastructureAPI } from "@api";
import type {
  ImageCatalogResponse,
  ResourceCatalogResponse,
  ProfileCatalogResponse,
} from "@api/types";
import { catalogKeys } from "./keys";

export function useImageCatalog() {
  return useQuery<ImageCatalogResponse>({
    queryKey: catalogKeys.images,
    queryFn: () => infrastructureAPI.fetchImageCatalog(),
  });
}

export function useResourceCatalog() {
  return useQuery<ResourceCatalogResponse>({
    queryKey: catalogKeys.resources,
    queryFn: () => infrastructureAPI.fetchResourceCatalog(),
  });
}

export function useProfileCatalog() {
  return useQuery<ProfileCatalogResponse>({
    queryKey: catalogKeys.profiles,
    queryFn: () => infrastructureAPI.fetchProfileCatalog(),
  });
}
