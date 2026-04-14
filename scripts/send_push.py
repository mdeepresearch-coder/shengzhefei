"""
每次 flights.json 更新时，由 GitHub Actions 自动调用此脚本
发送 OneSignal 推送通知 —— 完全在 GitHub 服务器上运行，无需 VPN
"""
import json
import urllib.request
import urllib.error
import sys

OS_APP_ID = '038f7aa0-03bc-4003-904e-a936b91b23df'
OS_API_KEY = 'os_v2_app_aohxviadxraahecove3lsgzd35srdlwldiquahe6exn4hllbctbuiit3276yqqiquduhe7ozwp6w2jqu2ei5tgnawebe7amt76rq6iy'

with open('flights.json', encoding='utf-8') as f:
    flights = json.load(f)

if not flights:
    print('flights.json 为空，跳过推送')
    sys.exit(0)

fl = flights[0]  # 最新一条
from_city = str(fl.get('from', ''))
to_city   = str(fl.get('to',   ''))
price     = str(fl.get('price', ''))

if not from_city or not to_city or not price:
    print('数据不完整，跳过推送')
    sys.exit(0)

payload = json.dumps({
    'app_id': OS_APP_ID,
    'included_segments': ['Total Subscriptions'],
    'headings': {'zh': '✈ 省着飞 · 新低价机票', 'en': '✈ New Flight Deal'},
    'contents': {
        'zh': f'{from_city} → {to_city}  ¥{price}/人，点击查看详情 →',
        'en': f'{from_city} → {to_city} ¥{price}'
    },
    'url': 'https://mdeepresearch-coder.github.io/shengzhefei/',
    'chrome_web_icon': 'https://mdeepresearch-coder.github.io/shengzhefei/icon.png',
}, ensure_ascii=False).encode('utf-8')

req = urllib.request.Request(
    'https://onesignal.com/api/v1/notifications',
    data=payload,
    headers={
        'Authorization': f'Key {OS_API_KEY}',
        'Content-Type': 'application/json; charset=utf-8'
    },
    method='POST'
)

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        recipients = result.get('recipients', 0)
        print(f'✅ 推送成功！已发送给 {recipients} 位订阅用户')
        print(f'   {from_city} → {to_city}  ¥{price}')
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f'❌ 推送失败 (HTTP {e.code}): {error_body}')
    sys.exit(1)
except Exception as e:
    print(f'❌ 推送异常: {e}')
    sys.exit(1)
