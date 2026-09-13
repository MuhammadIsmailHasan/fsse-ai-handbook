"use client";
// Query and mutation hooks. See README.md.
import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Application, ApplicationsApi, Filters, Status } from "./api-types";
import { applicationKeys } from "./query-keys";

export function useApplications(api: ApplicationsApi, filters: Filters) {
  throw new Error("TODO");
}

export function useMoveStatus(api: ApplicationsApi) {
  throw new Error("TODO");
}
