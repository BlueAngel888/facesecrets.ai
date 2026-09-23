import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi, test, expect, beforeEach, afterEach } from "vitest";
import App from "./App";

beforeEach(() => {
  global.fetch = vi.fn();
  URL.createObjectURL = vi.fn(() => "blob:portrait-preview");
  Object.defineProperty(navigator, "mediaDevices", { configurable: true, value: undefined });
});
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

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

const cameraTrack = () => ({ stop: vi.fn() });
const cameraStream = track => ({ getTracks: () => [track] });

test("opens a front-facing camera on mobile-compatible constraints and releases it on close", async () => {
  const track = cameraTrack();
  const stream = cameraStream(track);
  const getUserMedia = vi.fn().mockResolvedValue(stream);
  Object.defineProperty(navigator, "mediaDevices", { configurable: true, value: { getUserMedia } });
  const user = userEvent.setup();
  render(<App />);

  await user.click(screen.getByRole("button", { name: /Use camera/i }));
  const dialog = await screen.findByRole("dialog", { name: "Camera capture" });
  const video = dialog.querySelector("video");
  await waitFor(() => expect(video.srcObject).toBe(stream));
  expect(video).toHaveAttribute("playsinline");
  expect(getUserMedia).toHaveBeenCalledWith({ video: { facingMode: { ideal: "user" } }, audio: false });

  await user.click(screen.getByRole("button", { name: "Close camera" }));
  expect(track.stop).toHaveBeenCalledOnce();
  expect(video.srcObject).toBeNull();
});

test.each([
  ["denied", { getUserMedia: vi.fn().mockRejectedValue(new DOMException("Denied", "NotAllowedError")) }, /access was not granted/i],
  ["unavailable", undefined, /not available in this browser/i],
])("shows a usable fallback when camera access is %s", async (_state, mediaDevices, message) => {
  Object.defineProperty(navigator, "mediaDevices", { configurable: true, value: mediaDevices });
  await userEvent.click(render(<App />).getByRole("button", { name: /Use camera/i }));
  expect(await screen.findByText(message)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Capture portrait/i })).toBeDisabled();
});

test("stops a camera stream that resolves after the dialog was closed", async () => {
  let resolveCamera;
  const track = cameraTrack();
  const getUserMedia = vi.fn(() => new Promise(resolve => { resolveCamera = resolve; }));
  Object.defineProperty(navigator, "mediaDevices", { configurable: true, value: { getUserMedia } });
  const user = userEvent.setup();
  render(<App />);

  await user.click(screen.getByRole("button", { name: /Use camera/i }));
  await user.click(screen.getByRole("button", { name: "Cancel" }));
  resolveCamera(cameraStream(track));
  await waitFor(() => expect(track.stop).toHaveBeenCalledOnce());
  await waitFor(() => expect(screen.queryByRole("dialog", { name: "Camera capture" })).not.toBeInTheDocument());
});

test("stops a camera stream that resolves after the component unmounts", async () => {
  let resolveCamera;
  const track = cameraTrack();
  const getUserMedia = vi.fn(() => new Promise(resolve => { resolveCamera = resolve; }));
  Object.defineProperty(navigator, "mediaDevices", { configurable: true, value: { getUserMedia } });
  const user = userEvent.setup();
  const { unmount } = render(<App />);

  await user.click(screen.getByRole("button", { name: /Use camera/i }));
  unmount();
  resolveCamera(cameraStream(track));

  await waitFor(() => expect(track.stop).toHaveBeenCalledOnce());
});

test("captures the natural camera frame without mirroring the saved portrait", async () => {
  const track = cameraTrack();
  Object.defineProperty(navigator, "mediaDevices", { configurable: true, value: { getUserMedia: vi.fn().mockResolvedValue(cameraStream(track)) } });
  const drawImage = vi.fn();
  const toBlob = vi.fn(callback => callback(new Blob(["portrait"], { type: "image/jpeg" })));
  const originalCreateElement = document.createElement.bind(document);
  vi.spyOn(document, "createElement").mockImplementation(tag => tag === "canvas"
    ? { width: 0, height: 0, getContext: () => ({ drawImage }), toBlob }
    : originalCreateElement(tag));
  const user = userEvent.setup();
  const { container } = render(<App />);

  await user.click(screen.getByRole("button", { name: /Use camera/i }));
  const video = container.querySelector("video");
  Object.defineProperties(video, { videoWidth: { configurable: true, value: 720 }, videoHeight: { configurable: true, value: 1280 } });
  fireEvent.click(screen.getByRole("button", { name: /Capture portrait/i }));

  expect(drawImage).toHaveBeenCalledWith(video, 0, 0);
  expect(toBlob).toHaveBeenCalledWith(expect.any(Function), "image/jpeg", .92);
  expect(await screen.findByAltText("Portrait preview")).toBeInTheDocument();
  expect(track.stop).toHaveBeenCalledOnce();
});