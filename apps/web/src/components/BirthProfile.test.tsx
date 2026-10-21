import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { BirthProfile } from "./BirthProfile";

describe("birth profile visible validation", () => {
  beforeEach(() => vi.stubGlobal("fetch", vi.fn()));

  it("shows field guidance and prevents an incomplete submission", () => {
    const submit = vi.fn();
    render(<BirthProfile onSubmit={submit} loading={false} />);
    fireEvent.click(screen.getByRole("button", { name: "Create My Horoscope" }));
    expect(screen.getByText("Enter your birth date.")).toBeInTheDocument();
    expect(screen.getByText("Enter your birth time.")).toBeInTheDocument();
    expect(screen.getByText("Enter a birthplace or select a search result.")).toBeInTheDocument();
    expect(screen.getByText("Enter the birthplace's IANA timezone, such as Asia/Kolkata.")).toBeInTheDocument();
    expect(submit).not.toHaveBeenCalled();
  });

  it("permits manual location entry after autocomplete fails", async () => {
    vi.mocked(fetch).mockRejectedValue(new Error("provider internal detail"));
    const submit = vi.fn().mockResolvedValue(undefined);
    render(<BirthProfile onSubmit={submit} loading={false} />);
    fireEvent.change(screen.getByLabelText("Date of Birth"), { target: { value: "1990-01-15" } });
    fireEvent.change(screen.getByLabelText("Time of Birth"), { target: { value: "09:30" } });
    fireEvent.change(screen.getByLabelText(/Place of Birth/), { target: { value: "Mumbai" } });
    expect(await screen.findByText(/Location search is unavailable/)).toBeInTheDocument();
    expect(screen.queryByText("provider internal detail")).not.toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Selected timezone"), { target: { value: "Asia/Kolkata" } });
    fireEvent.change(screen.getByLabelText("Latitude"), { target: { value: "19.076" } });
    fireEvent.change(screen.getByLabelText("Longitude"), { target: { value: "72.8777" } });
    fireEvent.click(screen.getByRole("button", { name: "Create My Horoscope" }));
    await waitFor(() => expect(submit).toHaveBeenCalledOnce());
    expect(submit.mock.calls[0][0]).toMatchObject({ place_name: "Mumbai", timezone: "Asia/Kolkata", latitude: 19.076 });
  });

  it("shows invalid as-of timezone and does not silently use browser time", () => {
    const submit = vi.fn();
    render(<BirthProfile onSubmit={submit} loading={false} />);
    fireEvent.change(screen.getByLabelText("As-of timezone"), { target: { value: "Invalid/Zone" } });
    fireEvent.click(screen.getByRole("button", { name: "Create My Horoscope" }));
    expect(screen.getByText("Enter a valid as-of IANA timezone.")).toBeInTheDocument();
    expect(submit).not.toHaveBeenCalled();
  });
});
