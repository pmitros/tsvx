import markdown

html = open("docs/index.template").read().format(main_content = markdown.markdown(open("README.md").read()).replace("h1", "h3"))
f = open("docs/index.html", "w")
f.write(html)
f.close()
