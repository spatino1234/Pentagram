import { put } from "@vercel/blob";
import crypto from "crypto";
import { NextResponse } from "next/server";
// Ignoring the eslint rule for unused variables
/* eslint-disable @typescript-eslint/no-unused-vars */
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { text } = body;

    // const apiSecret = request.headers.get("X-API-SECRET");

    // if (apiSecret !== process.env.API_SECRET) {
    //   return NextResponse.json({ error: "Unathorized" }, { status: 401 });
    // }

    console.log(text);
    const url = new URL(
      "https://spatino1234--sdxl-turbo-model-generate.modal.run/"
    );

    url.searchParams.set("prompt", text);
    console.log("Requesting URL", url.toString);

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        "X-API-KEY": process.env.API_KEY || "",
        Accept: "image/jpeg",
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("API Response:", errorText);
      throw new Error(
        `HTTP error! status: ${response.status}, message: ${errorText}`
      );
    }

    const imageBuffer = await response.arrayBuffer();

    const filename = `${crypto.randomUUID()}.jpg`;

    const blob = await put(filename, imageBuffer, {
      access: "public",
      contentType: "image/jpeg",
    });

    return NextResponse.json({
      success: true,
      imageUrl: blob.url,
      // message: `Received: ${text}`,
    });
  } catch (_error) {
    return NextResponse.json(
      { success: false, _error: "Failed to process request" },
      { status: 500 }
    );
  }
}
