"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Application, ApplicationsApi, Filters, Status } from "./api-types";
import { applicationKeys } from "./query-keys";

export function useApplications(api: ApplicationsApi, filters: Filters) {
  return useQuery({
    queryKey: applicationKeys.list(filters),
    queryFn: ({ signal }) => api.listApplications(filters, { signal }), // signal cancels outdated requests
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}

type MoveVariables = { id: number; status: Status };
type Snapshot = [readonly unknown[], Application[] | undefined][];

export function useMoveStatus(api: ApplicationsApi) {
  const queryClient = useQueryClient();
  return useMutation<Application, Error, MoveVariables, { snapshot: Snapshot }>({
    mutationFn: ({ id, status }) => api.moveStatus(id, status),
    onMutate: async ({ id, status }) => {
      await queryClient.cancelQueries({ queryKey: applicationKeys.lists() }); // don't let an in-flight fetch overwrite us
      const snapshot = queryClient.getQueriesData<Application[]>({ queryKey: applicationKeys.lists() });
      queryClient.setQueriesData<Application[]>({ queryKey: applicationKeys.lists() }, (old) =>
        old?.map((application) => (application.id === id ? { ...application, status } : application)),
      );
      return { snapshot };
    },
    onError: (_error, _variables, context) => {
      context?.snapshot.forEach(([key, data]) => queryClient.setQueryData(key, data));
    },
    onSettled: (_data, _error, { id }) => {
      void queryClient.invalidateQueries({ queryKey: applicationKeys.lists() });
      void queryClient.invalidateQueries({ queryKey: applicationKeys.detail(id) });
    },
  });
}
