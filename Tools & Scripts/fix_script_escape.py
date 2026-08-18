with open(r'c:\Data_Projects\Spinning\Spinning Class Builder.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace any literal </script> or </body> or </html> inside the export string template
html = html.replace('</script>\n</body>\n</html>`;', '<' + '/script>\n<' + '/body>\n<' + '/html>`;')
html = html.replace('</script>', '<' + '/script>')

# Restore the actual end of file script and body tags
# Ensure the very last lines are properly closed
if not html.strip().endswith('</html>'):
    html = html.rstrip() + '\n  </' + 'script>\n</body>\n</html>'

with open(r'c:\Data_Projects\Spinning\Spinning Class Builder.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Fixed HTML parser script escaping in Spinning Class Builder.html!")
