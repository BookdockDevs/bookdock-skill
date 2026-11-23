# 书坞 Agent Skill

[English](README.en.md)

在对话中搜索书坞书库、查看不同版本、下载或分享书籍、上传 EPUB 或 TXT，以及将私有书库中的作品移入回收站。

## 安装

把下面这段话发给 Agent：

```text
请从 https://github.com/BookdockDevs/bookdock-skill 安装书坞 Skill。
按你支持的方式安装完整的 skills/bookdock 目录，包含 references。确认 bookdock 技能可用后，告诉我在哪里配置 BOOKDOCK_URL 和 BOOKDOCK_TOKEN。
```

手动安装时，从 [Releases](https://github.com/BookdockDevs/bookdock-skill/releases) 下载 `bookdock.zip` 并导入，或将 [`skills/bookdock/`](skills/bookdock/) 整个目录复制到 Agent 的技能目录。

## 连接书坞

1. 在书坞打开 **设置 → 集成 → 访问令牌**，创建一个令牌。浏览书库、搜索和查看详情需要 `ext:libraries`、`ext:books` 和 `ext:book`。其他操作所需的权限见 [API 权限表（英文）](skills/bookdock/references/external-api.md#endpoints-and-token-scopes)。
2. 在 Agent 的运行环境中，将 `BOOKDOCK_URL` 设为书坞实例地址，例如 `https://books.example.com`，并在密钥配置中将令牌保存为 `BOOKDOCK_TOKEN`。

Agent 需要能通过 HTTP 工具或终端访问你的书坞实例。

## 试一试

- “在小说书库里找《三体》，列出有哪些版本。”
- “把这个 EPUB 上传到我的私有书库，放在‘科幻’分类下。”
- “给我选中的这个版本创建一小时有效的下载链接。”

[更新日志（英文）](CHANGELOG.md) · [MIT 许可证](LICENSE)
