# 实操手册 02：把教程发布成专业网站

## 网站做什么

GitHub Pages 展示**静态项目文档、作品集、教程与演示**。它不应该成为你主要的电商、商业交易或收费 SaaS 站点。真正的商业服务说明、合同、付款和客户隐私流程，放在你合规运营的独立站点。

## 方案 A：本项目，直接用 Actions 自动部署

本项目已配好 `.github/workflows/pages.yml`，不需要 npm 或构建工具。

1. 创建名为 `github-income-handbook` 的**公开仓库**。
2. 将项目 ZIP 内的**所有文件和目录**上传到仓库**根目录**，确保能在仓库首页直接看见 `index.html`。注意：ZIP 里多一层 `github-income-handbook/` 目录；上传时应进入该目录选中文件，避免多套一层。
3. 进入 **Settings → Pages**，在 **Build and deployment → Source** 选择 **GitHub Actions**。
4. 提交一次 commit，进入 **Actions** 查看名为 `Deploy GitHub Pages` 的工作流是否成功。如果首次未触发，选择 workflow 的 **Run workflow**（需当前账户具有相应权限）。
5. 成功后站点一般位于 `https://<用户名>.github.io/<仓库名>/`。本站规划地址是 `https://aipmandy.github.io/github-income-handbook/`，**只有正式部署成功才能作为有效链接发布**。
6. 实际访问站点，分别检查电脑、手机、微信复制、章节、清单、计算器和第三方官方链接。

## 方案 B：简化版纯静态网页

如果你仅有一个 `index.html`，GitHub 也支持从分支发布，常见入口为 **Settings → Pages → Deploy from a branch**，然后选对分支和目录。此方案不用于本项目，因为我们已有自动部署工作流。

## 四种最常见的 404

1. **仓库根目录里又套了一层项目文件夹**：仓库根部没有 `index.html`。
2. **Pages 没设置或未完成首次部署**：检查 Settings 和 Actions 的结果。
3. **拼错仓库名 / 用户名 / 大小写**：区分当前实际仓库名与链接。
4. **刚改过发布配置**：等工作流完成再验证，不能把尚未成功的 URL 宣称已上线。

## 网站发布检查单

- [ ] 仓库的 `index.html` 在根目录
- [ ] GitHub Actions 显示成功
- [ ] 网站 HTTP 响应可正常打开
- [ ] 无多余横向滚动
- [ ] 7 条路线可点、20 章可搜
- [ ] 16 个清单能勾选并在本地保存
- [ ] 收益计算器仅作假设，不写真实收入
- [ ] 官网 / 微信入口准确，免费教程不用加微信才能看

官方文档：[自定义 Actions 工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)；[GitHub Pages 限制](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)。
