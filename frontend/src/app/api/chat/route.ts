import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(req: NextRequest) {
  const body = await req.json();

  if (!body.message || typeof body.message !== "string") {
    return NextResponse.json({ error: "Invalid message." }, { status: 400 });
  }

  try {
    const res = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: body.message }),
    });

    if (!res.ok) {
      const err = await res.json();
      return NextResponse.json({ error: err.detail || "Backend error." }, { status: res.status });
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (e) {
    return NextResponse.json({ error: "Could not reach the pitwall backend." }, { status: 503 });
  }
}