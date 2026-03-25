# Claude Config Backup 设计系统

本文档定义了 Claude Config Backup 的视觉设计规范。

---

## 设计理念

**核心风格**: 深色科技风 - 以深蓝黑为底，霓虹青为主色调

**设计原则**:
1. **清晰的信息层级** - 用户一眼看到最重要的信息
2. **即时的反馈** - 所有操作都有明确的状态反馈
3. **舒适的可读性** - 充足的留白和行高
4. **精致的一致性** - 所有组件遵循统一的视觉语言

---

## 颜色系统

### 主色调

| 名称 | 变量 | 值 | 用途 |
|------|------|-----|------|
| Primary | `--primary` | `#00d4ff` | 主要操作、高亮 |
| Primary Hover | `--primary-hover` | `#00b8e6` | 主色调悬停 |
| Primary Glow | `--primary-glow` | `rgba(0, 212, 255, 0.3)` | 发光效果 |

### 语义色

| 名称 | 值 | 用途 |
|------|-----|------|
| Success | `#00ff88` | 成功状态、确认 |
| Error | `#ff4466` | 错误状态、危险操作 |
| Warning | `#ffaa00` | 警告、注意事项 |
| Info | `#00d4ff` | 信息提示 |

### 背景色

| 名称 | 值 | 用途 |
|------|-----|------|
| Base | `#0d1117` | 最底层背景 |
| Surface | `#161b22` | 卡片、面板背景 |
| Elevated | `#21262d` | 悬浮元素背景 |
| Hover | `#30363d` | 悬停状态背景 |

### 文字色

| 名称 | 值 | 用途 |
|------|-----|------|
| Text Primary | `#f0f6fc` | 主要文字 |
| Text Secondary | `#8b949e` | 次要文字、说明 |
| Text Muted | `#6e7681` | 禁用、提示文字 |

### 边框

| 名称 | 值 | 用途 |
|------|-----|------|
| Border Default | `#30363d` | 默认边框 |
| Border Muted | `#21262d` | 淡边框 |

---

## 间距系统

使用 4px 基础单位：

| 名称 | 值 | 用途 |
|------|-----|------|
| xs | `4px` | 最小间距 |
| sm | `8px` | 紧凑间距 |
| md | `16px` | 标准间距 |
| lg | `24px` | 宽松间距 |
| xl | `32px` | 区块间距 |

---

## 圆角

| 名称 | 值 | 用途 |
|------|-----|------|
| sm | `4px` | 小元素 |
| md | `8px` | 按钮、输入框 |
| lg | `12px` | 卡片、面板 |

---

## 排版

### 字体栈

```css
font-family: "Segoe UI", "Microsoft YaHei UI", -apple-system, sans-serif;
```

代码/路径使用等宽字体：
```css
font-family: "JetBrains Mono", "Fira Code", "Consolas", monospace;
```

### 字号

| 名称 | 值 | 用途 |
|------|-----|------|
| xs | `11px` | 辅助信息 |
| sm | `12px` | 次要文字 |
| base | `14px` | 正文 |
| lg | `16px` | 小标题 |
| xl | `18px` | 大标题 |
| xxl | `24px` | 页面标题 |

---

## 组件规范

### 按钮

**高度**: 44px（默认）、52px（大号）

**状态**:
- Default: 背景色 Elevated，边框 Border Default
- Hover: 背景色 Hover，边框 Text Muted
- Active: 背景色 Primary，文字 Base
- Disabled: 背景色 Elevated，文字 Muted

**类型**:
| 类型 | 样式 | 用途 |
|------|------|------|
| Primary | Primary 背景，Base 文字 | 主要操作 |
| Secondary | 透明背景，Secondary 边框 | 次要操作 |
| Success | Success 边框，Success 文字 | 确认操作 |
| Danger | Error 边框，Error 文字 | 危险操作 |

### 输入框

**高度**: 44px

**内边距**: 0 16px

**状态**:
- Default: Base 背景，Border Default 边框
- Hover: Border Muted 边框
- Focus: Primary 边框，2px 宽度
- Error: Error 边框
- Disabled: Elevated 背景，Muted 文字

### 复选框 / 单选按钮

**尺寸**: 24x24px

**状态**:
- Unchecked: Base 背景，Border Default 边框
- Hover: Primary 边框
- Checked: Primary 背景，Primary 边框
- Disabled: Elevated 背景，Border Muted 边框

### 卡片 / 分组框

**内边距**: 24px

**边框**: 1px solid Border Default

**圆角**: lg (12px)

**标题**: Primary 颜色，加粗

---

## 交互状态

### 空状态

每个列表/内容区域都应有友好的空状态：

```
┌──────────────────────────────────────┐
│                                      │
│              [图标]                   │
│           主标题                      │
│        简短描述说明                   │
│                                      │
│         [主要操作按钮]                │
│                                      │
└──────────────────────────────────────┘
```

**示例**:
- 历史页面无备份: "暂无备份记录" + "创建第一个备份"
- 模块列表无内容: "没有可备份的模块" + "检查配置"

### 加载状态

**按钮加载**:
- 禁用按钮
- 显示 "⏳ 操作中..."
- 可选：显示进度条

**列表加载**:
- 显示骨架屏
- 或显示 "加载中..." 占位符

### 成功状态

- Toast 通知（右上角）
- 3-5 秒自动消失
- 包含成功图标和简短说明

### 错误状态

- 内联错误提示（表单字段下方）
- 红色边框标识
- 错误原因说明
- 可选：解决方案建议

---

## 动画规范

### 过渡时间

| 类型 | 时长 | 用途 |
|------|------|------|
| Fast | `100ms` | 按钮状态、焦点 |
| Normal | `200ms` | 悬停、展开 |
| Slow | `300ms` | 页面切换、弹窗 |

### 缓动函数

```css
/* 标准缓动 */
transition-timing-function: ease-out;

/* 入场 */
transition-timing-function: ease-in-out;
```

---

## 无障碍规范

### 颜色对比度

- 主要文字 vs 背景: ≥ 4.5:1
- 次要文字 vs 背景: ≥ 3:1
- 交互元素: ≥ 3:1

### 触摸目标

- 最小尺寸: 44x44px
- 按钮间距: ≥ 8px

### 键盘导航

- Tab: 焦点移动
- Enter: 激活/确认
- Escape: 关闭弹窗
- Space: 切换复选框

### 焦点指示

```css
:focus-visible {
    outline: 2px solid var(--primary);
    outline-offset: 2px;
}
```

---

## 图标规范

当前使用 Emoji 作为图标，未来可迁移到 SVG 图标：

| 位置 | 当前 | 说明 |
|------|------|------|
| 备份 Tab | 📦 | 包裹/存储 |
| 恢复 Tab | 📥 | 下载 |
| 历史 Tab | 📋 | 列表 |
| 设置 Tab | ⚙️ | 齿轮 |
| 成功 | ✅ / ✓ | 确认 |
| 错误 | ❌ | 错误 |
| 加载 | ⏳ | 等待 |

---

## 响应式断点

| 名称 | 宽度 | 说明 |
|------|------|------|
| Compact | < 600px | Tab 堆叠 |
| Standard | 600-900px | 默认布局 |
| Wide | > 900px | 宽屏布局 |

---

## 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-03-25 | 初始设计系统 |