# HTML 翻译工具

版本 1.0 © 2025 CMC-MAC.COM
            
## 本软件的翻译功能依赖于通过Ollama部署的本地LLM
            
- 建议使用ollama run qwen3:14b，运行速度足够快，翻译回答较为简洁，没有开头思考和结束总结，方便程序处理
- 使用了/no_think指令，消除推理过程，但是回答中含有空的`<think> </think>`标签，程序中已经做了处理，不会在翻译结果中出现类似一下标签内容


## 翻译结果存储在源文件所在目录,翻译结果文件名将包含原文件名，后缀为翻译语言的缩写

- 例如：index.html，会被翻译为index_en.html、index_ar.html

## 新的翻译结果将直接覆盖旧的翻译结果，对于文件覆盖不会提示

## 本软件使用了有限的几个组件，请自行检查

如果import部分报错，请自行通过pip install安装以下组件

- beautifulsoup4
- lxml
- requests
- tkinter
- ttkthemes