from bs4 import BeautifulSoup

html = open('cpeinet.html', 'r', encoding='utf-8').read()
soup = BeautifulSoup(html, 'lxml')

# 找所有包含招标/采购的链接
links = soup.find_all('a')
count = 0
for a in links:
    t = a.get_text(strip=True)
    if '招标' in t or '采购' in t:
        count += 1
        if count <= 20:
            href = a.get('href', '')
            parent = a.parent.name
            print(f'TEXT: {t[:60]}')
            print(f'HREF: {href}')
            print(f'PARENT: {parent}')
            print('---')

print(f'\n总计找到 {count} 条招标/采购相关链接')
