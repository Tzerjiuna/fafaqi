import subprocess
import time
import os

# 下载链接列表
with open("urls.txt", "r") as f:
    urls = [line.strip() for line in f if line.strip()]

# 代理列表
with open("proxies.txt", "r") as f:
    proxies = [line.strip() for line in f if line.strip()]

def test_proxy(proxy_line):
    try:
        host_port, creds = proxy_line.split('@')
        host, port = host_port.split(':')
        user, pwd = creds.split(':')
        proxy_addr = f"{host}:{port}"
        proxy_auth = f"{user}:{pwd}"

        result = subprocess.run([
            "curl",
            "-s",
            "-x", proxy_addr,
            "-U", proxy_auth,
            "ipinfo.io"
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0 and '"ip"' in result.stdout:
            return True, proxy_addr, proxy_auth
    except Exception as e:
        pass
    return False, None, None

def download_with_proxy(proxy_addr, proxy_auth, url, output_file):
    try:
        subprocess.run([
            "wget",
            url,
            "-e", f"use_proxy=yes",
            "-e", f"http_proxy=http://{proxy_auth}@{proxy_addr}",
            "-e", f"https_proxy=http://{proxy_auth}@{proxy_addr}",
            "-O", output_file,
            "-t", "3",
            "-T", "15"
        ], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


        
output_dir = os.path.join("网页")
os.makedirs(output_dir, exist_ok=True)
# 开始下载
for idx, url in enumerate(urls, start=1):
    success = False
    print(f"🔗 开始下载第 {idx} 个链接: {url}")
    for i, proxy in enumerate(proxies):
        print(f"  🔁 尝试代理 [{i+1}/{len(proxies)}]...")
        ok, proxy_addr, proxy_auth = test_proxy(proxy)
        if ok:
            
            filename = os.path.join(output_dir, f"page-{idx}.aspx")
            print(f"  ✅ 代理可用: {proxy_addr}，开始下载为 {filename}")
            success = download_with_proxy(proxy_addr, proxy_auth, url, filename)
            if success:
                print(f"  🎉 下载成功: {filename}")
                time.sleep(5)  # 等待 20 秒，避免触发风控
                break
            else:
                print(f"  ❌ 下载失败，换下一个代理...")
        else:
            print(f"  ❌ 代理无效")

    if not success:
        print(f"  ❌ 最终失败: {url}（所有代理均失败）\n")
