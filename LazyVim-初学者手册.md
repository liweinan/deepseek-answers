# LazyVim 初学者使用手册

## 目录
- [什么是 LazyVim](#什么是-lazyvim)
- [启动和退出](#启动和退出)
- [Vim 基础概念](#vim-基础概念)
- [基本操作](#基本操作)
- [LazyVim 核心快捷键](#lazyvim-核心快捷键)
- [文件操作](#文件操作)
- [代码编辑](#代码编辑)
- [Git 集成](#git-集成)
- [插件管理](#插件管理)
- [LSP 和代码补全](#lsp-和代码补全)
- [常见问题](#常见问题)

---

## 什么是 LazyVim

LazyVim 是一个预配置的 Neovim 发行版，它：
- 开箱即用，无需复杂配置
- 提供现代化的 IDE 功能
- 基于 lazy.nvim 插件管理器
- 高度可定制和扩展

---

## 启动和退出

### 启动 LazyVim
```bash
# 启动 LazyVim
nvim

# 打开文件
nvim filename.txt

# 打开目录
nvim .
```

### 退出 LazyVim
- `:q` - 退出当前窗口
- `:qa` - 退出所有窗口
- `:q!` - 强制退出（不保存）
- `:wq` - 保存并退出
- `ZZ` - 保存并退出（Normal 模式下）

---

## Vim 基础概念

### 四种主要模式

1. **Normal 模式（普通模式）**
   - 默认模式，用于导航和命令
   - 按 `Esc` 返回此模式

2. **Insert 模式（插入模式）**
   - 用于输入文本
   - 按 `i` 进入
   - 按 `Esc` 退出

3. **Visual 模式（可视模式）**
   - 用于选择文本
   - 按 `v` 进入字符选择
   - 按 `V` 进入行选择
   - 按 `Ctrl-v` 进入块选择

4. **Command 模式（命令模式）**
   - 用于执行命令
   - 按 `:` 进入
   - 输入命令后按 `Enter` 执行

---

## 基本操作

### 移动光标（Normal 模式）

**基本移动:**
- `h` - 左移
- `j` - 下移
- `k` - 上移
- `l` - 右移

**快速移动:**
- `w` - 移动到下一个词首
- `b` - 移动到上一个词首
- `e` - 移动到下一个词尾
- `0` - 移动到行首
- `$` - 移动到行尾
- `gg` - 移动到文件开头
- `G` - 移动到文件末尾
- `{数字}G` - 跳转到指定行（如 `10G` 跳到第10行）

**屏幕移动:**
- `Ctrl-u` - 向上翻半页
- `Ctrl-d` - 向下翻半页
- `Ctrl-b` - 向上翻一页
- `Ctrl-f` - 向下翻一页
- `zz` - 将当前行移到屏幕中央

### 进入 Insert 模式

- `i` - 在光标前插入
- `a` - 在光标后插入
- `I` - 在行首插入
- `A` - 在行尾插入
- `o` - 在下方新建一行并插入
- `O` - 在上方新建一行并插入

### 删除和修改

- `x` - 删除光标下的字符
- `dd` - 删除当前行
- `dw` - 删除一个词
- `d$` - 删除到行尾
- `D` - 删除到行尾（同 `d$`）
- `cc` - 删除当前行并进入插入模式
- `cw` - 删除一个词并进入插入模式
- `u` - 撤销
- `Ctrl-r` - 重做

### 复制和粘贴

- `yy` - 复制当前行
- `yw` - 复制一个词
- `y$` - 复制到行尾
- `p` - 在光标后粘贴
- `P` - 在光标前粘贴

### 查找

- `/keyword` - 向下查找 keyword
- `?keyword` - 向上查找 keyword
- `n` - 跳到下一个匹配
- `N` - 跳到上一个匹配
- `*` - 查找光标下的词（向下）
- `#` - 查找光标下的词（向上）

---

## LazyVim 核心快捷键

> **Leader 键**: 在 LazyVim 中，Leader 键默认是 `空格`

### 查看帮助

- `<space>` - 显示所有快捷键（等待一秒会自动显示）
- `<space>?` - 打开快捷键搜索
- `<space>sk` - 搜索快捷键

### 窗口管理

- `<space>w` + 方向键 - 在窗口间移动
- `<space>ww` - 切换到另一个窗口
- `<space>wd` - 删除当前窗口
- `<space>w-` - 水平分割窗口
- `<space>w|` - 垂直分割窗口
- `Ctrl-h/j/k/l` - 在窗口间快速移动

### 标签页（Tab）

- `<space><tab>l` - 列出所有标签页
- `<space><tab><tab>` - 切换到上一个标签页
- `<space><tab>]` - 下一个标签页
- `<space><tab>[` - 上一个标签页
- `<space><tab>d` - 关闭当前标签页
- `<space><tab>n` - 新建标签页

### Buffer 管理

- `<space>bb` - 切换 buffer
- `<space>bd` - 删除当前 buffer
- `<space>,` - 切换到上一个 buffer
- `[b` - 上一个 buffer
- `]b` - 下一个 buffer

---

## 文件操作

### 文件浏览器（Neo-tree）

- `<space>e` - 打开/关闭文件树
- `<space>E` - 打开文件树（聚焦到当前文件）

**在文件树中:**
- `a` - 新建文件/文件夹（以 `/` 结尾创建文件夹）
- `d` - 删除
- `r` - 重命名
- `x` - 剪切
- `c` - 复制
- `p` - 粘贴
- `?` - 显示帮助

### 文件搜索（FzfLua）

- `<space>ff` - 查找文件
- `<space>fr` - 最近打开的文件
- `<space>fb` - 浏览 buffers
- `<space>fF` - 查找所有文件（包括隐藏文件）

### 文本搜索

- `<space>sg` - 全局搜索（Grep）
- `<space>sw` - 搜索当前词
- `<space>ss` - 搜索 Buffer
- `<space>sG` - 在 git 仓库中搜索

### 保存和退出

- `<space>q` - 退出
- `<space>qq` - 退出所有
- 在 Normal 模式: `:w` + Enter 保存
- 在 Normal 模式: `:wq` + Enter 保存并退出

---

## 代码编辑

### 代码导航

- `gd` - 跳转到定义
- `gr` - 查看引用
- `gi` - 跳转到实现
- `gy` - 跳转到类型定义
- `K` - 显示悬停文档
- `Ctrl-o` - 跳回上一个位置
- `Ctrl-i` - 跳到下一个位置

### 代码操作

- `<space>ca` - 代码操作（Code Actions）
- `<space>cr` - 重命名符号
- `<space>cf` - 格式化代码
- `gc` - 注释/取消注释（Visual 模式下选中代码后使用）
- `gcc` - 注释/取消注释当前行

### LSP 功能

- `<space>cd` - 查看诊断信息
- `]d` - 下一个诊断
- `[d` - 上一个诊断
- `<space>cl` - LSP 信息

### 代码补全

在 Insert 模式下:
- `Ctrl-Space` - 手动触发补全
- `Tab` / `Shift-Tab` - 在补全项间导航
- `Enter` - 确认选择
- `Ctrl-e` - 关闭补全菜单

---

## Git 集成

### LazyGit（推荐）

- `<space>gg` - 打开 LazyGit（全功能 Git TUI）
- `<space>gG` - 在当前文件目录打开 LazyGit

**LazyGit 快捷键:**
- `1-5` - 切换面板
- `Enter` - 查看详情
- `Space` - 暂存/取消暂存
- `c` - 提交
- `P` - 推送
- `p` - 拉取
- `?` - 查看帮助

### Gitsigns

- `<space>gb` - 查看 Git blame
- `<space>gB` - 查看完整 blame
- `]h` - 下一个 Git hunk
- `[h` - 上一个 Git hunk
- `<space>ghs` - 暂存 hunk
- `<space>ghr` - 重置 hunk
- `<space>ghS` - 暂存整个文件
- `<space>ghR` - 重置整个文件
- `<space>ghp` - 预览 hunk
- `<space>ghd` - 查看删除的内容

---

## 插件管理

### Lazy.nvim 插件管理器

- `<space>l` - 打开 Lazy 插件管理器

**在 Lazy 界面中:**
- `I` - 安装插件
- `U` - 更新插件
- `S` - 同步插件（更新/删除/安装）
- `X` - 清理未使用的插件
- `C` - 检查更新
- `P` - 查看插件配置
- `?` - 显示帮助

### LazyExtras（可选功能包）

- `:LazyExtras` - 浏览和启用额外功能

常用 Extras:
- `lang.python` - Python 支持
- `lang.typescript` - TypeScript 支持
- `lang.go` - Go 支持
- `lang.rust` - Rust 支持
- `editor.illuminate` - 高亮相同词
- `ui.dashboard` - 启动界面

---

## LSP 和代码补全

### Mason（LSP 服务器管理）

- `:Mason` - 打开 Mason 界面

**在 Mason 界面中:**
- `i` - 安装
- `u` - 卸载
- `U` - 更新
- `/` - 搜索

**推荐安装的 LSP 服务器:**
- `lua-language-server` - Lua
- `pyright` - Python
- `typescript-language-server` - TypeScript/JavaScript
- `bash-language-server` - Bash
- `json-lsp` - JSON
- `yaml-language-server` - YAML
- `dockerfile-language-server` - Dockerfile

### 配置补全引擎（Blink.cmp）

LazyVim 使用 blink.cmp 作为补全引擎，它会自动:
- 显示函数签名
- 提供代码片段
- 显示文档
- 自动导入

---

## 常见问题

### Q: 如何修改配置？

A: LazyVim 配置文件位于 `~/.config/nvim/lua/config/`
- `options.lua` - Vim 选项
- `keymaps.lua` - 自定义快捷键
- `autocmds.lua` - 自动命令

### Q: 如何添加新插件？

A: 在 `~/.config/nvim/lua/plugins/` 目录下创建 `.lua` 文件:
```lua
return {
  {
    "author/plugin-name",
    config = function()
      -- 插件配置
    end,
  },
}
```

### Q: 如何更改主题？

A: 默认主题是 tokyonight，可以修改：
```lua
-- 在 ~/.config/nvim/lua/config/options.lua 添加
vim.cmd([[colorscheme catppuccin]]) -- 或其他主题
```

### Q: 性能优化建议？

A:
- 定期清理不用的插件 `<space>l` -> `X`
- 只安装需要的 LSP 服务器
- 禁用不需要的 extras

### Q: 如何查看健康检查？

A: 运行 `:checkhealth` 查看配置状态

### Q: 忘记快捷键怎么办？

A: 按 `<space>` 等待一秒，会显示所有可用快捷键

---

## 学习路径建议

### 第一天：基础操作
1. 学会启动和退出 nvim
2. 掌握模式切换（Normal、Insert）
3. 练习基本移动（hjkl）
4. 学会保存文件

### 第二天：文件和窗口
1. 使用 `<space>e` 浏览文件
2. 使用 `<space>ff` 快速查找文件
3. 学习窗口分割和切换
4. 练习 buffer 切换

### 第三天：编辑技巧
1. 掌握删除、复制、粘贴
2. 学习撤销和重做
3. 使用 Visual 模式选择文本
4. 练习代码注释

### 第四天：代码功能
1. 安装需要的 LSP 服务器（`:Mason`）
2. 练习跳转到定义（`gd`）
3. 使用代码补全
4. 尝试代码格式化

### 第五天：Git 集成
1. 学习 LazyGit 基本操作
2. 查看文件修改历史
3. 练习提交和推送

---

## 快速参考卡

### 必记快捷键
```
启动: nvim
退出: :q

模式切换:
Esc     → Normal 模式
i       → Insert 模式
v       → Visual 模式

移动:
hjkl    → 左/下/上/右
gg/G    → 文件首/尾

文件:
<space>e  → 文件树
<space>ff → 查找文件
<space>sg → 全局搜索

代码:
gd      → 跳转定义
K       → 查看文档
gcc     → 注释行

Git:
<space>gg → LazyGit

保存:
:w      → 保存
:wq     → 保存并退出
```

---

## 更多资源

- LazyVim 官方文档: https://www.lazyvim.org/
- LazyVim GitHub: https://github.com/LazyVim/LazyVim
- Neovim 官方文档: https://neovim.io/doc/
- Vim 交互式教程: 在终端运行 `vimtutor`

---

**祝你使用愉快！**

记住：Vim 的学习曲线陡峭，但一旦掌握，效率会大幅提升。
不要试图一次学会所有功能，循序渐进是关键。
