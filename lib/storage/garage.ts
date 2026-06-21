import "server-only"

import {
  DeleteObjectCommand,
  GetObjectCommand,
  PutObjectCommand,
  S3Client,
} from "@aws-sdk/client-s3"

import {
  HAULDR_S3_ACCESS_KEY_ID,
  HAULDR_S3_BUCKET,
  HAULDR_S3_ENDPOINT,
  HAULDR_S3_REGION,
  HAULDR_S3_SECRET_ACCESS_KEY,
} from "@/config/env"

// Thin Garage (S3) helper for the Storage module, Hauldr tier. Path-style
// addressing (Garage requires it); the app talks to the project's bucket with a
// per-project scoped key. Object keys are namespaced under `documentos/`.

export function storageEnabled(): boolean {
  return Boolean(
    HAULDR_S3_ENDPOINT &&
      HAULDR_S3_BUCKET &&
      HAULDR_S3_ACCESS_KEY_ID &&
      HAULDR_S3_SECRET_ACCESS_KEY,
  )
}

let client: S3Client | null = null
function s3(): S3Client {
  if (!client) {
    client = new S3Client({
      endpoint: HAULDR_S3_ENDPOINT,
      region: HAULDR_S3_REGION,
      forcePathStyle: true,
      credentials: {
        accessKeyId: HAULDR_S3_ACCESS_KEY_ID,
        secretAccessKey: HAULDR_S3_SECRET_ACCESS_KEY,
      },
    })
  }
  return client
}

export async function putObject(
  key: string,
  body: Uint8Array,
  contentType: string,
): Promise<void> {
  await s3().send(
    new PutObjectCommand({
      Bucket: HAULDR_S3_BUCKET,
      Key: key,
      Body: body,
      ContentType: contentType,
    }),
  )
}

export type ObjectStream = {
  body: ReadableStream
  contentType: string
  contentLength?: number
  contentRange?: string
  status: number
}

/** Fetch an object (optionally a byte range) as a web ReadableStream. */
export async function getObject(key: string, range?: string): Promise<ObjectStream> {
  const out = await s3().send(
    new GetObjectCommand({
      Bucket: HAULDR_S3_BUCKET,
      Key: key,
      ...(range ? { Range: range } : {}),
    }),
  )
  // In the Node runtime the Body is a stream with transformToWebStream().
  const body = (out.Body as { transformToWebStream: () => ReadableStream }).transformToWebStream()
  return {
    body,
    contentType: out.ContentType || "application/octet-stream",
    contentLength: out.ContentLength,
    contentRange: out.ContentRange,
    status: out.ContentRange ? 206 : 200,
  }
}

export async function deleteObject(key: string): Promise<void> {
  await s3().send(new DeleteObjectCommand({ Bucket: HAULDR_S3_BUCKET, Key: key }))
}
