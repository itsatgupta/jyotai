import { fireEvent, render, screen } from "@testing-library/react";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import Preview from "./Preview";

beforeAll(() => {
  Element.prototype.scrollIntoView = vi.fn();
  if (!window.PointerEvent) {
    class TestPointerEvent extends MouseEvent {
      pointerId: number;
      pointerType: string;
      constructor(type: string, init: PointerEventInit = {}) {
        super(type, init);
        this.pointerId = init.pointerId ?? 0;
        this.pointerType = init.pointerType ?? "mouse";
      }
    }
    Object.defineProperty(window, "PointerEvent", { value: TestPointerEvent });
  }
});

function setMotionPreference(reduced: boolean) {
  window.matchMedia = vi.fn().mockImplementation(() => ({
    matches: reduced,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  }));
}

beforeEach(() => setMotionPreference(false));

function wheel() {
  return screen.getByRole("group", { name: "Decorative zodiac wheel" });
}

function manualRotation() {
  return wheel().querySelector<HTMLElement>(".orbit-manual")?.style.transform;
}

function setWheelBounds() {
  vi.spyOn(wheel(), "getBoundingClientRect").mockReturnValue({
    left: 0, top: 0, right: 200, bottom: 200, width: 200, height: 200,
    x: 0, y: 0, toJSON: () => ({}),
  });
}

describe("isolated design preview", () => {
  it("links a synthetic planet card to the fixed chart and preserves theme control", () => {
    render(<Preview />);
    fireEvent.click(screen.getByRole("button", { name: /Venus, synthetic/i }));
    expect(screen.getByRole("button", { name: /Venus, synthetic/i }).getAttribute("aria-pressed")).toBe("true");
    expect(screen.getByText("01", { selector: ".insight-fact strong" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Switch to light theme" }));
    expect(document.querySelector(".preview-app")?.getAttribute("data-preview-theme")).toBe("light");
  });

  it("labels period examples without dates and stages questions without generating answers", () => {
    render(<Preview />);
    expect(screen.getByRole("list", { name: /Illustrative Mahadasha order/i }).children).toHaveLength(3);
    expect(screen.getByRole("list", { name: /Illustrative Antardasha order/i }).children).toHaveLength(5);
    expect(screen.getByText(/No conclusion is offered for this sample/i)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "What does my D1 chart show?" }));
    fireEvent.click(screen.getByRole("button", { name: /Preview question/i }));
    expect(screen.getByRole("status").textContent).toMatch(/No analysis was generated or sent/i);
  });

  it("drags in both directions, pauses auto motion during drag, and leaves chart facts fixed", () => {
    render(<Preview />);
    setWheelBounds();
    const chartBefore = document.querySelector(".preview-kundli")?.innerHTML;
    fireEvent.pointerDown(wheel(), { pointerId: 1, pointerType: "mouse", button: 0, clientX: 200, clientY: 100 });
    expect(wheel().getAttribute("data-auto-rotation")).toBe("paused");
    fireEvent.pointerMove(wheel(), { pointerId: 1, pointerType: "mouse", clientX: 100, clientY: 200 });
    expect(manualRotation()).toBe("rotate(45deg)");
    fireEvent.pointerMove(wheel(), { pointerId: 1, pointerType: "mouse", clientX: 200, clientY: 100 });
    expect(manualRotation()).toBe("rotate(0deg)");
    fireEvent.pointerUp(wheel(), { pointerId: 1, pointerType: "mouse" });
    expect(wheel().getAttribute("data-auto-rotation")).toBe("playing");
    expect(document.querySelector(".preview-kundli")?.innerHTML).toBe(chartBefore);
  });

  it("supports touch swipes, keyboard rotation, and reset", () => {
    render(<Preview />);
    setWheelBounds();
    fireEvent.pointerDown(wheel(), { pointerId: 2, pointerType: "touch", clientX: 200, clientY: 100 });
    fireEvent.pointerMove(wheel(), { pointerId: 2, pointerType: "touch", clientX: 100, clientY: 200 });
    fireEvent.pointerUp(wheel(), { pointerId: 2, pointerType: "touch" });
    expect(manualRotation()).toBe("rotate(45deg)");
    fireEvent.keyDown(wheel(), { key: "ArrowLeft" });
    expect(manualRotation()).toBe("rotate(30deg)");
    const autoLayerBeforeReset = wheel().querySelector(".orbit-auto");
    fireEvent.click(screen.getByRole("button", { name: "Reset decorative wheel rotation" }));
    expect(manualRotation()).toBe("rotate(0deg)");
    expect(wheel().querySelector(".orbit-auto")).not.toBe(autoLayerBeforeReset);
    fireEvent.keyDown(wheel(), { key: "ArrowRight" });
    expect(manualRotation()).toBe("rotate(15deg)");
    fireEvent.keyDown(wheel(), { key: "Home" });
    expect(manualRotation()).toBe("rotate(0deg)");
  });

  it("pauses and plays auto motion while keeping manual controls available", () => {
    render(<Preview />);
    expect(wheel().getAttribute("data-auto-rotation")).toBe("playing");
    fireEvent.click(screen.getByRole("button", { name: "Pause automatic wheel rotation" }));
    expect(wheel().getAttribute("data-auto-rotation")).toBe("paused");
    fireEvent.click(screen.getByRole("button", { name: "Rotate wheel anticlockwise 15 degrees" }));
    expect(manualRotation()).toBe("rotate(-15deg)");
    fireEvent.click(screen.getByRole("button", { name: "Play automatic wheel rotation" }));
    expect(wheel().getAttribute("data-auto-rotation")).toBe("playing");
  });

  it("disables automatic movement under reduced motion but allows manual rotation", () => {
    setMotionPreference(true);
    render(<Preview />);
    expect(wheel().getAttribute("data-auto-rotation")).toBe("paused");
    expect((screen.getByRole("button", { name: "Play automatic wheel rotation" }) as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(screen.getByRole("button", { name: "Rotate wheel clockwise 15 degrees" }));
    expect(manualRotation()).toBe("rotate(15deg)");
  });
});
