<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/bookdock-dark.svg" />
    <img src="./assets/bookdock.svg" alt="书坞" width="64" height="64" />
  </picture>
  <h1>书坞 Agent Skill</h1>
  <p>在对话中查找、上传和分享书坞里的电子书。</p>
  <p>简体中文 · <a href="./README.en.md">English</a></p>
</div>

## 安装

**把下面这段话发给 Agent。**

```text
请从以下仓库安装书坞 Agent Skill。
https://github.com/BookdockDevs/bookdock-skill

使用完整的 skills/bookdock 目录，包括 references。
确认 bookdock 可用，并告诉我在哪里设置
BOOKDOCK_URL 和 BOOKDOCK_TOKEN。
```

手动安装时，可在[发布页](https://github.com/BookdockDevs/bookdock-skill/releases)下载 `bookdock.zip` 并导入，也可以将 [`skills/bookdock/`](skills/bookdock/) 复制到 Agent 的技能目录。

## 连接书坞

在书坞的 **设置 → 集成 → 访问令牌** 创建令牌。浏览书库、搜索和查看详情需要 `ext:libraries`、`ext:books` 和 `ext:book`。下载、分享、上传和移入回收站的权限见 [API 权限表（英文）](skills/bookdock/references/external-api.md#endpoints-and-token-scopes)。

在 Agent 的运行环境中填写实例地址和令牌。

| 配置项 | 填写内容 |
| --- | --- |
| `BOOKDOCK_URL` | Agent 能访问的书坞实例地址 |
| `BOOKDOCK_TOKEN` | 保存到运行环境密钥配置中的访问令牌 |

## 试一试

> 在小说书库里找《三体》，列出有哪些版本。
>
> 把这份 EPUB 上传到我的私有书库，放进「科幻」分类。
>
> 给我选中的版本创建一个有效期为一小时的下载链接。

[更新日志（英文）](CHANGELOG.md) · [MIT 许可证](LICENSE)
