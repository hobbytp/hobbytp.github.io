启停Hugo服务请使用make命令。
启动Hugo服务前，请先停止已经启动的Hugo服务。
本地python环境由uv + venv管理。
严格遵守TDD规范，所有python代码都必须通过测试。
开发新功能时，必须使用openspec开发change proposal。必须先编写对应的测试用例，然后实现功能代码。
提交Hugo网站相关功能（非博客文章本身）必须使用新的git branch进行提交到github的PR。
开发的网页功能，必须通过chrome-devtools进行调试来验证其正确性。
最后的openspec验收必须和用户确认后，才能achieve。