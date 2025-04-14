import subprocess
from bs4 import BeautifulSoup


def search_bioconda_package(package_name):
    try:
        result = subprocess.run(
            ["conda", "search", "-c", "bioconda", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"



import requests
from bs4 import BeautifulSoup

def search_recipe_of_bioconda_package(package_name):
    base_url = "https://bioconda.github.io/recipes/"
    package_url = f"{base_url}{package_name}/README.html#package-{package_name}"
    
    try:
        # 发送 HTTP GET 请求
        response = requests.get(package_url)
        response.raise_for_status()
        
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取关键信息
        result = {}
        
        # 提取描述信息 (第一个 dl.conda.recipe 下的第一个 p)
        recipe_desc = soup.find('dl', class_='conda recipe').find('p')
        result['description'] = recipe_desc.text.strip() if recipe_desc else "No description available"
        
        # 提取字段信息 (Homepage, Documentation, License等)
        field_list = soup.find('dl', class_='field-list')
        if field_list:
            for dt, dd in zip(field_list.find_all('dt'), field_list.find_all('dd')):
                field_name = dt.text.strip(':').lower()
                if dd.find('a'):
                    result[field_name] = dd.find('a')['href']
                else:
                    result[field_name] = dd.text.strip()
        
        # 提取版本信息 (在 package 部分)
        package_info = soup.find('dl', class_='conda package')
        if package_info:
            versions_dt = package_info.find('dt', string=lambda s: 'versions' in s.lower() if s else False)
            if versions_dt:
                versions_dd = versions_dt.find_next_sibling('dd')
                if versions_dd:
                    versions = versions_dd.text.strip()
                    result['versions'] = [v.strip().strip('`').strip() for v in versions.split(',')]
        
        # 提取安装信息
        installation_section = soup.find('p', string=lambda t: t and 'conda-compatible package manager' in t if t else False)
        if installation_section:
            install_text = []
            current = installation_section
            
            while current and not (current.name == 'h2' or current.name == 'section'):
                if current.name in ['p', 'pre']:
                    text = current.get_text(strip=True)
                    if text:
                        install_text.append(text)
                current = current.find_next_sibling()
            
            result['installation'] = '\n\n'.join(install_text)
        
        return result
    
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error during parsing: {e}"
    

if __name__ == "__main__":
        
    # 示例：搜索 "bwa"
    print(search_bioconda_package("x"))
    # 示例：搜索 "xpore"
    print(search_recipe_of_bioconda_package("export2graphlan"))
        
