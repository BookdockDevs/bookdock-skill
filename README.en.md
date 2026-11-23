<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/bookdock-dark.svg" />
    <img src="./assets/bookdock.svg" alt="Bookdock" width="64" height="64" />
  </picture>
  <h1>Bookdock Agent Skill</h1>
  <p>Find, upload, and share Bookdock books from your agent.</p>
  <p><a href="./README.md">简体中文</a> · English</p>
</div>

## Install

**Paste this into your agent.**

```text
Install the Bookdock Agent Skill from
https://github.com/BookdockDevs/bookdock-skill

Copy the full skills/bookdock directory,
including references. Confirm it is available
and show me where to set BOOKDOCK_URL and
BOOKDOCK_TOKEN.
```

For manual installation, import `bookdock.zip` from [Releases](https://github.com/BookdockDevs/bookdock-skill/releases) or copy [`skills/bookdock/`](skills/bookdock/) into your agent's skills directory.

## Connect to Bookdock

Create a token in Bookdock under **Settings → Integrations → Access tokens**. Grant `ext:libraries`, `ext:books`, and `ext:book` for browsing, search, and book details. See the [API permissions table](skills/bookdock/references/external-api.md#endpoints-and-token-scopes) for download, sharing, upload, and trash permissions.

Set the instance URL and access token in your agent's execution environment.

| Setting | Value |
| --- | --- |
| `BOOKDOCK_URL` | The Bookdock URL your agent can reach |
| `BOOKDOCK_TOKEN` | The access token saved in the runtime's secret configuration |

## Try it

> Find *The Three-Body Problem* in my Fiction library and list the editions.
>
> Upload this EPUB to the Science Fiction category in my private library.
>
> Create a one-hour download link for the edition I picked.

[Changelog](CHANGELOG.md) · [MIT license](LICENSE)
