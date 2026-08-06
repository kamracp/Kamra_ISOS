/**
 * FastAPI returns validation errors (HTTP 422) with `detail` as an
 * ARRAY of Pydantic error objects, not a string — e.g.
 * [{ type, loc, msg, input, ctx }]. Every other error (400/404/500
 * from our own HTTPException calls) has `detail` as a plain string.
 *
 * Passing the array form directly into toast.error() or rendering it
 * in JSX crashes the whole page (React error #31: "Objects are not
 * valid as a React child"). This helper always returns a safe string
 * to display, regardless of which shape the backend sent.
 */
export function getApiErrorMessage(error: any, fallback: string): string {
  const detail = error?.response?.data?.detail;

  if (!detail) return fallback;
  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((e) => {
        const field = Array.isArray(e?.loc) ? e.loc[e.loc.length - 1] : e?.loc;
        return field ? `${field}: ${e?.msg ?? "Invalid value"}` : e?.msg ?? "Invalid value";
      })
      .join("; ");
  }

  return fallback;
}