import { requests } from "./client";
import { urlJoin } from "./http";
import { config } from "../config";
import type {
  ImageCatalogResponse,
  ResourceCatalogResponse,
  ProfileCatalogResponse,
} from "./types";

const base_url = config.apiUrl;
const infrastructure_url = urlJoin(base_url, "catalogs");

export const infrastructureAPI = {
  fetchImageCatalog: async (): Promise<ImageCatalogResponse> => {
    const url = urlJoin(infrastructure_url, "image-catalog");
    return requests.get(url) as Promise<ImageCatalogResponse>;
  },
  fetchResourceCatalog: async (): Promise<ResourceCatalogResponse> => {
    const url = urlJoin(infrastructure_url, "resource-tiers");
    return requests.get(url) as Promise<ResourceCatalogResponse>;
  },
  fetchProfileCatalog: async (): Promise<ProfileCatalogResponse> => {
    const url = urlJoin(infrastructure_url, "profile-catalog");
    return requests.get(url) as Promise<ProfileCatalogResponse>;
  },
};
