import { useQuery } from "@tanstack/react-query";
import { studentJoinAPI } from "@api";
import { studentJoinKeys } from "./keys";

export function useStudentJoinInfo(token: string) {
  return useQuery({
    queryKey: studentJoinKeys.info(token),
    queryFn: () => studentJoinAPI.fetchInfo(token),
    enabled: !!token,
    // An invalid link answers 404, and retrying cannot change that; it would
    // only delay the message by several seconds.
    retry: false,
  });
}
