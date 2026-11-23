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
| `POST /api/v1/ext/books/:versionId/download-link` | `ext:download-link` | Get or create a share URL, or revoke it |
| `GET /api/v1/ext/reading-archives` | `ext:reading-archives` | Personal reading overview or one book's archive |
| `POST /api/v1/ext/books` | `ext:upload` | Upload result |
| `PATCH /api/v1/ext/books/:versionId` | `ext:update-book` | Update a work in a specific library |
| `DELETE /api/v1/ext/books/:versionId` | `ext:delete` | Move the private work to trash |

Token scopes and the account's library permissions both apply. The editable catalog, reading archives, link revocation, and new catalog query options require a server with those API updates. Check the granted scopes in `data.tokenPermissions` from `GET /api/v1/auth/me`.

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

bd --get --data-urlencode "libraryId=$LIBRARY_ID" "$api/books/$VERSION_ID"
```

Set `BOOK_QUERY` to the search keyword, `LIBRARY_ID` to a library ID, and `VERSION_ID` to a returned `bookVersionId`. The following list parameters are optional:

| Parameter | Values and behavior |
| --- | --- |
| `q` | One keyword or phrase, 1–200 characters after trimming. Matches title, author and other metadata. Omit it for browsing. |
| `libraryId` | Scope to one browsable library. Omit it to search all browsable libraries. An inaccessible ID can produce an empty page. |
| `format` | `epub` or `txt`, the source format. |
| `author` | Exact author name, including matches in the edition's author list. |
| `categoryPath` | URL-encoded JSON array of one or two category names, such as `["Fiction","Science fiction"]`. Matching follows each library's category rules. |
| `tag`, `shelfId` | Tag name or private shelf ID. These can be combined with other filters. |
| `sortBy` | `title`, `createdAt`, `updatedAt` or `size`. |
| `sortOrder` | `asc` or `desc`. |
| `sortScope` | `library` (default) groups by library and preserves pin priority. `global` sorts all matching editions together without pin priority. |
| `updatedSince` | Nonnegative Unix timestamp in milliseconds. Filters by work or content-revision updates. |
| `page`, `pageSize` | One-based page (default 1). Page size is 1–100 (default 50). |

Read `data.items`, `data.total`, `data.page`, `data.pageSize` and `data.hasMore`. Items include `bookVersionId`, `libraryId`, `libraryName`, `title`, `author`, `authors`, `versionName`, `sourceFormat`, `size`, `hasCover`, `categoryName`, optional `shelfName`, `tags`, `hidden`, `wordCount`, `createdAt` and `updatedAt`. Counts are for edition rows. Detail adds `description`, `bookmeta`, the original uploaded `fileName` when known, and `cover` (a thumbnail data URI or null). With an explicit `libraryId`, detail resolves that library's edition or returns an error. Without it, detail prefers an accessible private copy.

## Download an authenticated file

```sh
bd --head "$api/books/$VERSION_ID/file"
bd --output downloaded-book.epub "$api/books/$VERSION_ID/file"
```

Use a fresh writable destination for a new download, confirm the response succeeded, then deliver the saved file. Use `Content-Disposition` if suggesting a filename. The response is always `application/epub+zip`, including when `sourceFormat` is `txt`. The download is the stored EPUB. A single `Range: bytes=...` can return `206`. An invalid or unsatisfiable range can return `416`. `HEAD` reports metadata such as `Content-Length` without a body.

## Get, create, or revoke a share link

```sh
bd --json '{"duration":"1h","libraryId":"REPLACE_WITH_LIBRARY_ID"}' \
  "$api/books/$VERSION_ID/download-link"
```

Pass JSON with required `duration` (`1h`, `1d`, `7d`, `30d`, or `permanent`) and optional `libraryId`. Use the selected row's library to pin the source. A private source must belong to the account and be its own file. A shared source requires library management permission. A readable book may therefore return `BOOK_NOT_FOUND` for sharing.

Read `data.url`, `data.duration` and `data.expiresAt` (Unix milliseconds, or null for permanent). An existing valid link for the source and revision can be reused with its original expiration. The URL works without authentication and whoever has it can download the book. The download preserves EPUB or TXT format and skips text replacement rules. The host in the returned URL must be reachable by the recipient. Use the Web UI to replace an existing link.

To revoke, send `action: "revoke"` with the same source library. The existing `ext:download-link` scope covers both calls. Successful and repeated revocations return `{"data":null}`.

```sh
bd --json '{"action":"revoke","libraryId":"REPLACE_WITH_LIBRARY_ID"}' \
  "$api/books/$VERSION_ID/download-link"
```

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

## Edit book information

```sh
bd --request PATCH --json '{"title":"Revised title","categoryPath":["Fiction"]}' \
  "$api/books/$VERSION_ID?libraryId=$LIBRARY_ID"
```

The `libraryId` query parameter and management permission in that library are required. Use a version from the selected library. The request can set `title`, `author` or `authors`, `description`, `categoryPath`, `tags`, and `shelfId` (private libraries only). Omitted fields keep their values. Use `null` to clear the category or shelf and `[]` to clear tags. Sending `tags` replaces the entire set. Use an empty description to clear a private book's override and restore the file's description. Shared work edits follow the catalog editor's default edition. Success returns `data.libraryId`, `data.bookVersionId`, and `data.libraryBookId`.

## Move a private work to trash

```sh
bd --request DELETE --get --data-urlencode "libraryId=$LIBRARY_ID" \
  "$api/books/$VERSION_ID"
```

Use a version ID from the account's private library. Pass that library's ID when the target comes from a search result. An explicit `libraryId` identifies the operation's target, and shared-library targets are rejected. Omitting it targets the account's private library. The operation moves the whole private work and its editions into recoverable trash, which must be enabled. Success returns `data.bookVersionId`. Restoration and permanent deletion are managed in the Web UI.

## Read personal reading archives

Call without an archive ID for overview and search. Set date bounds as inclusive `YYYY-MM-DD` dates in a specified IANA timezone. The example shows a calendar month.

```sh
bd --get --data-urlencode 'from=2026-10-01' --data-urlencode 'to=2026-10-31' \
  --data-urlencode 'timezone=Asia/Shanghai' --data-urlencode 'pageSize=1' "$api/reading-archives"
bd --get --data-urlencode "search=$BOOK_QUERY" "$api/reading-archives"
```

- `data.overview.counts` contains highlight, bookmark, idea, and review counts. `data.overview.totalBooks` is the full archive count regardless of the date or list filters.
- `data.overview.reading.summary.scope` contains totals for the requested dates, including `totalSeconds`, `totalBooks`, `totalDays` and `finishedBooks`. The summary also contains lifetime and calendar-week/month fields outside `scope`. `reading.daily`, `reading.hourly`, `reading.byCategory`, and `reading.byTag` are the date-scoped breakdowns.
- `data.entries`, `data.page`, and `data.hasMore` contain the book list. `search`, `type`, `readStatus`, `tag`, `sort`, `page` and `pageSize` filter or paginate the list. Dates also affect the overview. Use the server summary for account totals because the book list can follow different visibility rules.

Use the list's `archiveId` for detail. Local-only device books are outside the server archive. Imported and retained personal archives may exist after the original book becomes unavailable.

```sh
bd --get --data-urlencode "archiveId=$ARCHIVE_ID" --data-urlencode 'view=notes' "$api/reading-archives"
bd --get --data-urlencode "archiveId=$ARCHIVE_ID" --data-urlencode 'view=data' \
  --data-urlencode 'from=2026-10-01' --data-urlencode 'to=2026-10-31' "$api/reading-archives"
```

For `view=notes`, read `data.annotations` and `data.reviews`. For `view=data` (the default), read `data.data.ledger`, `data.data.stats` and `data.data.sessions` for rounds, scoped statistics, and the initial session page. An archive with only notes can return `data.data: null`. Both views accept the same date bounds and timezone as the overview.

## Handle errors

- `401` means authentication did not succeed. Check the instance and the token configuration without printing its value.
- `403` can indicate a missing scope or insufficient library access. For integrations pinned to a specific library, verify the target and the account's role.
- `404` can mean an inaccessible or missing book, or a route missing from an older deployment. Read the server error code and check the deployed capability when a route is suspect.
- `400` validation errors and `413` upload limits need corrected input. After an uncertain write, verify the resulting state instead of blindly repeating the request.

The owning sources in [Bookdock](https://github.com/BookdockDevs/bookdock) are `packages/shared/src/access-tokens.ts`, `packages/shared/src/ext.ts`, `apps/server/src/modules/ext/ext.routes.ts` and `apps/server/src/modules/ext/ext.service.ts`.
