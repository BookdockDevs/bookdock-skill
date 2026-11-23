# Bookdock Agent Skill

[简体中文](README.md)

Search your Bookdock libraries, inspect book editions, download or share books, upload EPUB and TXT files, and move works in your private library to the trash.

## Install

Paste this into your agent:

```text
Install the Bookdock Agent Skill from https://github.com/BookdockDevs/bookdock-skill.
Install the full skills/bookdock directory, including its references, using your usual skill installation method. Verify that the bookdock skill is available, then tell me where to set BOOKDOCK_URL and BOOKDOCK_TOKEN.
```

To install manually, download `bookdock.zip` from [Releases](https://github.com/BookdockDevs/bookdock-skill/releases) and import it into your agent, or copy [`skills/bookdock/`](skills/bookdock/) into your agent's skills directory.

## Connect to Bookdock

1. In Bookdock, open **Settings → Integrations → Access tokens** and create a token. For library browsing, search, and book details, grant `ext:libraries`, `ext:books`, and `ext:book`. To enable other operations, see the [permission table](skills/bookdock/references/external-api.md#endpoints-and-token-scopes).
2. In your agent's execution environment, set `BOOKDOCK_URL` to your instance address, such as `https://books.example.com`, and store the token as `BOOKDOCK_TOKEN` in the runtime's secret configuration.

The agent needs an HTTP tool or shell that can reach your Bookdock instance.

## Try it

- “Find *The Three-Body Problem* in my Fiction library and list the available editions.”
- “Upload this EPUB to the Science Fiction category in my private library.”
- “Create a one-hour download link for the edition I picked.”

[Changelog](CHANGELOG.md) · [MIT license](LICENSE)
