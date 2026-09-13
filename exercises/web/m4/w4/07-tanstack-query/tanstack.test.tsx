import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import type { Application, ApplicationsApi, Filters, Status } from "./lib/api-types";
import { ApplicationsPanel } from "./lib/applications-panel";
import { applicationKeys } from "./lib/query-keys";

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: unknown) => void;
  const promise = new Promise<T>((res, rej) => ((resolve = res), (reject = rej)));
  return { promise, resolve, reject };
}

function setup(api: ApplicationsApi, filters: Filters = {}) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  const wrapper = ({ children }: { children: ReactNode }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>;
  const utils = render(<ApplicationsPanel api={api} filters={filters} />, { wrapper });
  return { client, ...utils, rerenderWith: (next: Filters) => utils.rerender(<ApplicationsPanel api={api} filters={next} />) };
}

const APPS: Application[] = [
  { id: 1, role: "Backend Engineer", status: "applied" },
  { id: 2, role: "AI Engineer", status: "saved" },
];

test("query key factory", () => {
  expect(applicationKeys.all).toEqual(["applications"]);
  expect(applicationKeys.lists()).toEqual(["applications", "list"]);
  expect(applicationKeys.list({ status: "offer" })).toEqual(["applications", "list", { status: "offer" }]);
  expect(applicationKeys.detail(7)).toEqual(["applications", "detail", 7]);
});

describe("loading, error and retry", () => {
  test("pending then data", async () => {
    const list = deferred<Application[]>();
    const api: ApplicationsApi = { listApplications: vi.fn(() => list.promise), moveStatus: vi.fn() };
    setup(api, { status: "applied" });
    expect(screen.getByRole("status")).toHaveTextContent("Loading applications…");
    expect(api.listApplications).toHaveBeenCalledWith({ status: "applied" }, expect.objectContaining({ signal: expect.any(AbortSignal) }));
    act(() => list.resolve(APPS));
    expect(await screen.findByText(/Backend Engineer/)).toBeInTheDocument();
    expect(screen.getByLabelText("Status for AI Engineer")).toHaveValue("saved");
  });

  test("error with retry", async () => {
    const api: ApplicationsApi = { listApplications: vi.fn().mockRejectedValueOnce(new Error("500")).mockResolvedValueOnce(APPS), moveStatus: vi.fn() };
    setup(api);
    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn't load applications");
    await userEvent.setup().click(screen.getByRole("button", { name: "Retry" }));
    expect(await screen.findByText(/AI Engineer/)).toBeInTheDocument();
    expect(api.listApplications).toHaveBeenCalledTimes(2);
  });
});

test("keeps previous data while a new filter loads", async () => {
  const second = deferred<Application[]>();
  const api: ApplicationsApi = {
    listApplications: vi.fn().mockResolvedValueOnce(APPS).mockImplementationOnce(() => second.promise),
    moveStatus: vi.fn(),
  };
  const { rerenderWith } = setup(api);
  expect(await screen.findByText(/Backend Engineer/)).toBeInTheDocument();
  rerenderWith({ status: "offer" });
  expect(await screen.findByText("Updating…")).toBeInTheDocument();
  expect(screen.getByText(/Backend Engineer/)).toBeInTheDocument();
  expect(screen.queryByRole("status")).toBeNull();
  act(() => second.resolve([{ id: 9, role: "QA", status: "offer" }]));
  expect(await screen.findByText(/QA/)).toBeInTheDocument();
  await waitFor(() => expect(screen.queryByText("Updating…")).toBeNull());
});

describe("optimistic mutation", () => {
  test("updates immediately, then invalidates", async () => {
    const move = deferred<Application>();
    const api: ApplicationsApi = {
      listApplications: vi.fn().mockResolvedValueOnce(APPS).mockResolvedValue([{ ...APPS[0]!, status: "interview" }, APPS[1]!]),
      moveStatus: vi.fn(() => move.promise),
    };
    const { client } = setup(api);
    const user = userEvent.setup();
    await screen.findByText(/Backend Engineer/);
    await user.selectOptions(screen.getByLabelText("Status for Backend Engineer"), "interview");
    expect(api.moveStatus).toHaveBeenCalledWith(1, "interview");
    expect(screen.getByLabelText("Status for Backend Engineer")).toHaveValue("interview");
    const invalidate = vi.spyOn(client, "invalidateQueries");
    act(() => move.resolve({ ...APPS[0]!, status: "interview" as Status }));
    await waitFor(() => expect(invalidate).toHaveBeenCalledWith({ queryKey: ["applications", "list"] }));
    expect(invalidate).toHaveBeenCalledWith({ queryKey: ["applications", "detail", 1] });
    await waitFor(() => expect(api.listApplications).toHaveBeenCalledTimes(2));
  });

  test("rolls back and shows an error when the move fails", async () => {
    const api: ApplicationsApi = {
      listApplications: vi.fn().mockResolvedValue(APPS),
      moveStatus: vi.fn().mockRejectedValue(new Error("409 invalid_transition")),
    };
    setup(api);
    await screen.findByText(/AI Engineer/);
    await userEvent.setup().selectOptions(screen.getByLabelText("Status for AI Engineer"), "offer");
    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn't move AI Engineer");
    await waitFor(() => expect(screen.getByLabelText("Status for AI Engineer")).toHaveValue("saved"));
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
});
