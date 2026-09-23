import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi, test, expect, beforeEach, afterEach } from "vitest";
import App from "./App";

beforeEach(() => {
  global.fetch = vi.fn();
  URL.createObjectURL = vi.fn(() => "blob:portrait-preview");
});
afterEach(() => cleanup());

test("renders the private reflection experience and language selector", () => {
  render(<App />);
  expect(screen.getByText(/Read what/i)).toBeInTheDocument();
  expect(screen.getByRole("combobox", { name: "Language" })).toBeInTheDocument();
  expect(screen.getByText(/Five lenses/i)).toBeInTheDocument();
});

test("shows validation notice when analysis starts without an image", async () => {
  render(<App />);
  await userEvent.click(screen.getAllByRole("button", { name: /Begin private reflection/i })[0]);
  expect(screen.getByText(/Choose a clear portrait/i)).toBeInTheDocument();
  expect(global.fetch).not.toHaveBeenCalled();
});

test("renders completion and cancellation states", () => {
  const { rerender } = render(<App page="success" />);
  expect(screen.getByText(/Your reflection is ready/i)).toBeInTheDocument();
  rerender(<App page="cancel" />);
  expect(screen.getByText(/No charge was made/i)).toBeInTheDocument();
});

test("free analysis redirects to the generated report after upload", async () => {
  const navigate = vi.fn();
  global.fetch
    .mockResolvedValueOnce(new Response(JSON.stringify({ success: true, free_analysis: true }), { status: 200 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ success: true }), { status: 200 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ success: true, redirect_url: "/success" }), { status: 200 }));
  const user = userEvent.setup();
  const { container } = render(<App navigate={navigate} />);

  await user.type(screen.getByRole("textbox", { name: /Promo code/i }), "letsgo");
  await user.click(screen.getByRole("button", { name: "Apply" }));
  expect(await screen.findByText(/Access granted/i)).toBeInTheDocument();

  const fileInput = container.querySelector('input[type="file"]');
  await user.upload(fileInput, new File(["portrait"], "portrait.jpg", { type: "image/jpeg" }));
  await user.click(screen.getByRole("button", { name: /Use unlocked analysis/i }));

  await waitFor(() => expect(navigate).toHaveBeenCalledWith("/success"));
  expect(global.fetch).toHaveBeenNthCalledWith(3, "/free-analysis", expect.objectContaining({ method: "POST" }));
});