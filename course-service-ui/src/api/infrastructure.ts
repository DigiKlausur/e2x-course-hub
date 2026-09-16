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
    return requests.get<ImageCatalogResponse>(
      urlJoin(infrastructure_url, "image-catalog"),
    );
  },
  fetchResourceCatalog: async (): Promise<ResourceCatalogResponse> => {
    return requests.get<ResourceCatalogResponse>(
      urlJoin(infrastructure_url, "resource-tiers"),
    );
  },
  fetchProfileCatalog: async (): Promise<ProfileCatalogResponse> => {
    return requests.get<ProfileCatalogResponse>(
      urlJoin(infrastructure_url, "profile-catalog"),
    );
  },
};
