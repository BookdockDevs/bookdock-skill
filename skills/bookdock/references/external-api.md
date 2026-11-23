# Bookdock external API

All paths below are relative to the configured Bookdock instance. Send `Authorization: Bearer <access-token>` on authenticated requests. The examples use a POSIX shell and curl. With an HTTP tool, use the same methods, query parameters and bodies through its configured authentication.

```sh
base=${BOOKDOCK_URL:?Configure BOOKDOCK_URL in the execution environment}
base=${base%/}
api="$base/api/v1/ext"

bd() {
  : "${BOOKDOCK_TOKEN:?Configure BOOKDOCK_TOKEN in the execution environment}"
  printf 'Authorization: Bearer %s\n' "$BOOKDOCK_TOKEN" |
    curl --silent --show-error --fail-with-body --connect-timeout 10 --header @- "$@"
}
```

Use the configured origin for authenticated calls. Redirects are disabled in these examples. JSON successes use `{"data": ...}`. JSON errors use `{"error":{"code":"...","message":"...","details": ...}}`, where `details` is optional. File responses are binary.

## Endpoints and token scopes

| Method and path | Required scope | Result |
| --- | --- | --- |
| `GET /api/v1/auth/me` | Any valid Bookdock access token | Account identity and a connection check |
| `GET /api/v1/ext/libraries` | `ext:libraries` | Browsable libraries and taxonomy |
| `GET /api/v1/ext/books` | `ext:books` | Paginated book editions |
| `GET /api/v1/ext/books/:versionId` | `ext:book` | One edition's metadata and thumbnail |
| `GET /api/v1/ext/books/:versionId/file` | `ext:file` | Stored EPUB bytes |
| `HEAD /api/v1/ext/books/:versionId/file` | `ext:file` | EPUB headers |
| `POST /api/v1/ext/books/:versionId/download-link` | `ext:download-link` | Existing or newly created share URL |
| `POST /api/v1/ext/books` | `ext:upload` | Upload result |
| `DELETE /api/v1/ext/books/:versionId` | `ext:delete` | Move the private work to trash |

Token scopes and the account's library permissions both apply. Extra Web API routes are generally unavailable to access tokens.

## Check the connection and discover libraries

```sh
bd "$base/api/v1/auth/me"
bd "$api/libraries"
```

`data.libraries` contains the account's private library and joined shared libraries. Each row includes `id`, `name`, `type` (`private` or `shared`), `role`, `canWrite`, `workCount`, `categories`, `shelves` and `tags`. `workCount` counts works. For upload, a category's `path` is an array of names and a shelf's `id` is its actual identifier.

## Search and inspect editions

```sh
bd --get --data-urlencode "q=$BOOK_QUERY" --data-urlencode "libraryId=$LIBRARY_ID" \
  --data-urlencode 'page=1' --data-urlencode 'pageSize=10' "$api/books"

bd "$api/books/$VERSION_ID"
```

Set `BOOK_QUERY` to the search keyword, `LIBRARY_ID` to a library ID, and `VERSION_ID` to a returned `bookVersionId`. The following list parameters are optional:

| Parameter | Values and behavior |
| --- | --- |
| `q` | One keyword or phrase, 1–200 characters after trimming. Matches title, author and other metadata. Omit it for browsing. |
| `libraryId` | Scope to one browsable library. Omit it to search all browsable libraries. An inaccessible ID can produce an empty page. |
| `format` | `epub` or `txt`, the source format. |
| `sortBy` | `title`, `createdAt`, `updatedAt` or `size`. Across libraries, results are grouped by library and sorted within each library. |
| `sortOrder` | `asc` or `desc`. |
| `updatedSince` | Nonnegative Unix timestamp in milliseconds. Filters by work or content-revision updates. |
| `page`, `pageSize` | One-based page (default 1). Page size is 1–100 (default 50). |

Read `data.items`, `data.total`, `data.page`, `data.pageSize` and `data.hasMore`. Items include `bookVersionId`, `libraryId`, `libraryName`, `title`, `author`, `authors`, `versionName`, `sourceFormat`, `size`, `hasCover`, `categoryName`, optional `shelfName`, `tags`, `hidden`, `wordCount`, `createdAt` and `updatedAt`. Counts are for edition rows. Detail adds `description`, `bookmeta`, the original uploaded `fileName` when known, and `cover` (a thumbnail data URI or null). The detail endpoint resolves by version ID alone. When a version belongs to multiple libraries, the returned library can differ from the search row.

## Download an authenticated file

```sh
bd --head "$api/books/$VERSION_ID/file"
bd --output downloaded-book.epub "$api/books/$VERSION_ID/file"
```

Use a fresh writable destination for a new download, confirm the response succeeded, then deliver the saved file. Use `Content-Disposition` if suggesting a filename. The response is always `application/epub+zip`, including when `sourceFormat` is `txt`. The download is the stored EPUB. A single `Range: bytes=...` can return `206`. An invalid or unsatisfiable range can return `416`. `HEAD` reports metadata such as `Content-Length` without a body.

## Get or create a share link

```sh
bd --json '{"duration":"1h","libraryId":"REPLACE_WITH_LIBRARY_ID"}' \
  "$api/books/$VERSION_ID/download-link"
```

Pass JSON with required `duration` (`1h`, `1d`, `7d`, `30d`, or `permanent`) and optional `libraryId`. Use the selected row's library to pin the source. A private source must belong to the account and be its own file. A shared source requires library management permission. A readable book may therefore return `BOOK_NOT_FOUND` for sharing.

Read `data.url`, `data.duration` and `data.expiresAt` (Unix milliseconds, or null for permanent). An existing valid link for the source and revision can be reused with its original expiration. The URL works without authentication and whoever has it can download the book. The download preserves EPUB or TXT format and skips text replacement rules. The host in the returned URL must be reachable by the recipient. Use the Web UI for link replacement or revocation.

## Upload EPUB or TXT

```sh
bd --form 'file=@./example.epub' --form-string "libraryId=$LIBRARY_ID" \
  --form-string 'categoryPath=["Fiction","Science fiction"]' "$api/books"
```

Send a multipart request with required `file` and optional fields:

- `libraryId` selects the destination. Omit it to upload to the token account's private library. A named shared library requires management permission.
- `categoryPath` is a JSON array string of one or two category names, such as `["Fiction","Science fiction"]`.
- `shelfId` is an ID returned under `shelves` for a private library.

Success is `201` with `data.bookVersionId`, `title`, `author`, `sourceFormat`, `size` and `duplicated`. A duplicate is a successful response with `duplicated: true`. The instance and account can impose upload limits.

## Move a private work to trash

```sh
bd --request DELETE --get --data-urlencode "libraryId=$LIBRARY_ID" \
  "$api/books/$VERSION_ID"
```

Use a version ID from the account's private library. The optional `libraryId` is checked for management access. It does not switch the deletion to a shared library. The operation moves the whole private work into its recoverable trash. Trash must be enabled. A shared-only work is rejected. Success returns `data.bookVersionId`. Restoration and permanent deletion are managed in the Web UI.

## Handle errors

- `401` means authentication did not succeed. Check the instance and the token configuration without printing its value.
- `403` can indicate a missing scope or insufficient library access. For integrations pinned to a specific library, verify the target and the account's role.
- `404` can mean an inaccessible or missing book, or a route missing from an older deployment. Read the server error code and check the deployed capability when a route is suspect.
- `400` validation errors and `413` upload limits need corrected input. After an uncertain write, verify the resulting state instead of blindly repeating the request.

The owning sources in [Bookdock](https://github.com/BookdockDevs/bookdock) are `packages/shared/src/access-tokens.ts`, `packages/shared/src/ext.ts`, `apps/server/src/modules/ext/ext.routes.ts` and `apps/server/src/modules/ext/ext.service.ts`.
